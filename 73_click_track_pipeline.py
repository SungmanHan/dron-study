r"""73. 클릭 한 번으로 따라가기 — 분할(무거움) + 추적(가벼움) 📷

35 강. 강의의 최종 구조를 그대로 만든다.

    [프레임] -> (클릭) -> [분할] -> [마스크 -> bbox] -> [추적기 init]
                                                          |
                          매 프레임 [tracker.update()] -> 박스 갱신 / 놓치면 해제

    SEGMENTER = "demo"   floodFill 로 흉내 (설치 없이 돌아간다, 기본값)
    SEGMENTER = "sam"    ultralytics SAM
    SOURCE    = "demo"   물체가 좌우로 움직이는 합성 영상 (기본값)
    왼쪽 클릭 대상 지정 / 오른쪽 클릭·C 해제 / ESC 종료

**분할은 처음 한 번만, 추적은 매 프레임** 이 핵심이다. 실행하면 둘의 비용이 같이 찍힌다.
이 기계에서는 분할(floodFill) 1 ms · 추적(MIL) 60 ms 였다 — 즉 여기서는 분할이 더 싸다.
이 구조가 이득인 건 **분할이 SAM 처럼 비쌀 때**(초 단위) 뿐이다. 근거는 72 참고.

[강의와 다르게 만든 것]

1. **CSRT 를 쓰지 않는다.** 이 환경의 `opencv-python` 에는 CSRT 도 `cv2.legacy` 도
   없다(72 에서 확인). `create_tracker()` 가 CSRT -> KCF -> MIL 순으로 있는 것을 쓴다.
2. **`success` 를 믿지 않는다.** 가림 실험에서 MIL 은 물체를 완전히 놓친 뒤에도
   119 프레임 내내 `success = True` 를 돌려줬다. 그래서 첫 박스의 색 분포와
   현재 박스를 비교해 `LOST_TH` 미만이 `LOST_K` 프레임 연속이면 놓친 것으로 본다.
3. **너무 작은 박스로 init 하지 않는다** (`MIN_BOX`). 배경을 잘못 클릭하면 몇 픽셀짜리
   박스가 나오고, 그걸로 학습한 추적기는 곧바로 엉뚱한 데로 흘러간다.
4. **클릭하면 이전 추적을 먼저 지운다.** 원본은 tracker 를 남겨 둬서 분할이 실패해도
   이전 박스가 되살아난다.
5. `sam_processing = None` -> `False`, 마스크 해상도 보정(`INTER_NEAREST`),
   `try/finally` 로 카메라 해제 — 34 강(71)에서 고친 것과 같다.

[상태 표시]
화면 왼쪽 위에 `IDLE / TRACKING / LOST` 와 `offset=(dx, dy)` 를 찍는다.
`offset` 은 박스 중심과 화면 중앙의 차이다. 다음 단계에서
좌우 오차는 yaw, 상하 오차는 throttle, 박스 크기 변화는 pitch 로 바꾸면 추적 비행이 된다.
그때 필요한 건 비례 게인·최대값 제한·데드존, 그리고 **항상 준비된 비상 정지**다.
"""

import sys
import time

import cv2 as cv
import numpy as np
import pygame

SEGMENTER = "demo"  # "demo" / "sam"
SOURCE = "demo"  # 0 (카메라) / "demo" / "파일경로"
MODEL_NAME = "sam2_t.pt"
WIDTH, HEIGHT = 640, 480
FPS = 30
MIN_AREA = 100  # 이보다 작은 윤곽선은 노이즈
MIN_BOX = 10  # 이보다 작은 박스로는 추적기를 초기화하지 않는다
FLOOD_TOLERANCE = 12
LOST_TH = 0.5  # 히스토그램 유사도 임계
LOST_K = 5  # 연속 몇 프레임 미달이면 놓침으로 선언
OCCLUSION = True  # demo 영상 중간에 기둥을 세워 가림을 만든다
MAX_SECONDS = 0  # 0 = 무제한

TRACKER_ORDER = ["TrackerCSRT_create", "TrackerKCF_create", "TrackerMIL_create"]


def create_tracker():
    """이 환경에서 만들 수 있는 추적기. CSRT 는 contrib 에만 있다 (72 참고)."""
    for name in TRACKER_ORDER:
        factory = getattr(cv, name, None)
        if factory is None:
            continue
        try:
            return factory(), name
        except cv.error:  # 가중치 파일이 필요한 종류
            continue
    return None, None


def get_bbox(mask, min_area=MIN_AREA):
    """bool 마스크 -> (x, y, w, h). 쓸 만한 윤곽선이 없으면 None. (71 과 같다)"""
    if mask is None or not np.any(mask):
        return None
    contours, _ = cv.findContours(mask.astype(np.uint8) * 255,
                                  cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    largest = max(contours, key=cv.contourArea)
    if cv.contourArea(largest) < min_area:
        return None
    return cv.boundingRect(largest)


def fit_mask(mask, shape):
    """마스크 해상도가 프레임과 다르면 맞춘다. 0/1 이라 INTER_NEAREST."""
    h, w = shape[:2]
    if mask.shape == (h, w):
        return mask
    return cv.resize(mask.astype(np.uint8), (w, h), interpolation=cv.INTER_NEAREST).astype(bool)


def pick_mask(masks, point, shape):
    """여러 후보 중 클릭한 점을 포함하는 것을 고른다. 없으면 첫 번째."""
    h, w = shape[:2]
    chosen = None
    x, y = point
    for mask in masks:
        mask = fit_mask(np.asarray(mask).astype(bool), shape)
        if chosen is None:
            chosen = mask
        if 0 <= y < h and 0 <= x < w and mask[y, x]:
            return mask
    return chosen


def patch_hist(frame, box):
    """박스 안쪽 색 분포 — 추적기가 딴 데를 잡았는지 보는 외부 확인용"""
    x, y, w, h = (int(v) for v in box)
    x, y = max(0, x), max(0, y)
    patch = frame[y:y + h, x:x + w]
    if patch.size == 0:
        return None
    hist = cv.calcHist([cv.cvtColor(patch, cv.COLOR_BGR2HSV)], [0, 1], None,
                       [16, 16], [0, 180, 0, 256])
    cv.normalize(hist, hist, 0, 1, cv.NORM_MINMAX)
    return hist


def similarity(ref, frame, box):
    cur = patch_hist(frame, box)
    if ref is None or cur is None:
        return 0.0
    return cv.compareHist(ref, cur, cv.HISTCMP_CORREL)


def demo_frames():
    """물체가 좌우로 지나가는 합성 영상 — 추적을 보려면 움직여야 한다."""
    rng = np.random.default_rng(7)
    small = rng.integers(40, 110, (HEIGHT // 16, WIDTH // 16, 3), dtype=np.int16).astype(np.uint8)
    background = cv.resize(small, (WIDTH, HEIGHT), interpolation=cv.INTER_CUBIC)
    period = 160
    i = 0
    while True:
        phase = (i % period) / period
        frame = background.copy()
        x = int(60 + (WIDTH - 180) * phase)
        y = int(HEIGHT / 2 - 60 + 70 * np.sin(phase * 2 * np.pi))
        cv.rectangle(frame, (x, y), (x + 60, y + 60), (40, 90, 230), cv.FILLED)
        if OCCLUSION and 0.42 < phase < 0.58:  # 기둥 뒤로 잠깐 사라진다
            cv.rectangle(frame, (WIDTH // 2 - 45, 0), (WIDTH // 2 + 45, HEIGHT), (70, 70, 70), cv.FILLED)
        i += 1
        yield True, frame


def segment_demo(frame, point):
    """floodFill 로 흉내 낸 분할 (SAM 이 아니다 — 70 참고)."""
    flood = np.zeros((HEIGHT + 2, WIDTH + 2), np.uint8)
    tol = (FLOOD_TOLERANCE,) * 3
    cv.floodFill(frame.copy(), flood, tuple(point), 255, tol, tol,
                 cv.FLOODFILL_MASK_ONLY | (255 << 8))
    mask = flood[1:-1, 1:-1] > 0
    return mask if mask.any() else None


def segment_sam(model, frame, point):
    """SAM 결과에서 클릭 점을 포함하는 마스크를 고른다."""
    try:
        results = model(frame, points=[list(point)], labels=[1], verbose=False)
    except Exception as exc:  # 추론이 실패해도 프로그램은 계속 돈다
        print(f"SAM error: {exc}")
        return None
    if not results or results[0].masks is None:
        return None
    return pick_mask(results[0].masks.data.cpu().numpy(), point, frame.shape)


def main():
    tracker_probe, tracker_name = create_tracker()
    if tracker_probe is None:
        raise SystemExit("쓸 수 있는 추적기가 없습니다.  pip install opencv-contrib-python  (72 참고)")
    print(f"추적기: cv.{tracker_name}()"
          + ("" if tracker_name.startswith("TrackerCSRT") else "   (CSRT 없음 — 72 참고)"))

    model = None
    if SEGMENTER == "sam":
        try:
            from ultralytics import SAM
        except ImportError:
            raise SystemExit("ultralytics 가 없습니다.  pip install ultralytics  (63 참고)\n"
                             '  설치 없이 보려면 SEGMENTER = "demo"')
        model = SAM(MODEL_NAME)

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption("73 click -> segment -> track")
    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()

    frames = demo_frames() if SOURCE == "demo" else None
    cap = None if frames else cv.VideoCapture(SOURCE)
    if cap is not None:
        cap.set(cv.CAP_PROP_FRAME_WIDTH, WIDTH)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        if not cap.isOpened():
            pygame.quit()
            raise SystemExit("카메라를 열지 못했습니다. (시스템 환경설정 > 보안 > 카메라 권한)")

    click_point = None
    tracker = None
    current_box = None
    ref_hist = None
    miss = 0  # 유사도 미달이 몇 프레임 연속인지
    status = "IDLE  L click: pick target"
    update_ms = []
    running, count, tracked = True, 0, 0
    started = pygame.time.get_ticks()

    try:
        while running:
            ok, frame = next(frames) if frames else cap.read()
            if not ok:
                print("프레임을 읽지 못했습니다.")
                break
            if frame.shape[1] != WIDTH or frame.shape[0] != HEIGHT:
                frame = cv.resize(frame, (WIDTH, HEIGHT))
            count += 1

            # 1) 클릭이 있으면 분할 -> bbox -> 추적기 초기화 (여기만 무겁다)
            if click_point:
                t0 = time.perf_counter()
                mask = (segment_demo(frame, click_point) if SEGMENTER == "demo"
                        else segment_sam(model, frame, click_point))
                mask = None if mask is None else fit_mask(mask, frame.shape)
                box = get_bbox(mask)
                took = (time.perf_counter() - t0) * 1000

                if box and box[2] >= MIN_BOX and box[3] >= MIN_BOX:
                    tracker, _ = create_tracker()
                    tracker.init(frame, box)  # 첫 박스로 학습
                    current_box = box
                    ref_hist = patch_hist(frame, box)  # 나중에 비교할 기준
                    miss = 0
                    status = "TRACKING"
                    print(f"  click {tuple(click_point)} -> bbox {box}  분할 {took:.1f} ms  추적 시작")
                else:
                    tracker, current_box, ref_hist = None, None, None
                    status = "FAILED  click again"
                    print(f"  click {tuple(click_point)} -> 쓸 만한 박스 없음 ({took:.1f} ms)")
                click_point = None

            # 2) 추적 갱신 — 매 프레임 여기만 돈다 (가볍다)
            elif tracker is not None:
                t0 = time.perf_counter()
                ok_track, box = tracker.update(frame)
                update_ms.append((time.perf_counter() - t0) * 1000)
                box = tuple(map(int, box))
                score = similarity(ref_hist, frame, box) if ok_track else 0.0
                miss = miss + 1 if score < LOST_TH else 0

                if not ok_track or miss >= LOST_K:
                    # success 만 보면 영영 안 걸린다 — 유사도 가드가 실제로 잡는 쪽이다
                    why = "update()=False" if not ok_track else f"유사도 {score:.2f} x{miss}"
                    tracker, current_box, ref_hist, miss = None, None, None, 0
                    status = "LOST  click again"
                    print(f"  {count} 프레임: 추적 해제 ({why})")
                else:
                    current_box = box
                    tracked += 1

            # 3) 화면 출력
            rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            screen.blit(pygame.image.frombuffer(rgb.tobytes(), (WIDTH, HEIGHT), "RGB"), (0, 0))
            pygame.draw.line(screen, (90, 90, 90), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
            pygame.draw.line(screen, (90, 90, 90), (0, HEIGHT // 2), (WIDTH, HEIGHT // 2))

            info = status
            if current_box:
                x, y, w, h = current_box
                pygame.draw.rect(screen, (0, 255, 0), current_box, 2)
                cx, cy = x + w // 2, y + h // 2
                pygame.draw.circle(screen, (255, 0, 0), (cx, cy), 4)  # 박스 중심 = 제어 기준
                dx, dy = cx - WIDTH // 2, cy - HEIGHT // 2
                info = f"{status}  offset=({dx:+d},{dy:+d})  box=({x},{y},{w},{h})"
            screen.blit(font.render(info, True, (255, 255, 0)), (10, 10))

            pygame.display.flip()
            clock.tick(FPS)

            # 4) 이벤트
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_c:
                        tracker, current_box, ref_hist, miss = None, None, None, 0
                        status = "IDLE  L click: pick target"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        click_point = list(event.pos)
                        # 새로 고를 때는 이전 추적을 먼저 버린다 (원본은 남겨 둔다)
                        tracker, current_box, ref_hist, miss = None, None, None, 0
                        status = "SEGMENTING..."
                    elif event.button == 3:
                        tracker, current_box, ref_hist, miss = None, None, None, 0
                        status = "IDLE  L click: pick target"

            if MAX_SECONDS and pygame.time.get_ticks() - started > MAX_SECONDS * 1000:
                running = False
    finally:
        if cap is not None:
            cap.release()
        pygame.quit()
        if update_ms:
            mean_ms = sum(update_ms) / len(update_ms)
            print(f"{count} 프레임 중 {tracked} 프레임 추적  "
                  f"update 평균 {mean_ms:.1f} ms ({1000 / mean_ms:.0f} fps)")
        else:
            print(f"{count} 프레임 / 추적 없음")


if __name__ == "__main__":
    main()
    sys.exit()
