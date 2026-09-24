r"""71. 마스크를 바운딩 박스로 — 추적·제어가 쓰기 좋은 네 숫자 📷

34 강. 33 강에서 얻은 **픽셀 마스크**를 `(x, y, w, h)` 네 숫자로 줄인다.
드론이 물체를 따라가려면 "화면 중앙에서 얼마나 벗어났는가" 만 알면 되기 때문이다.

    SEGMENTER = "demo"   OpenCV floodFill 로 흉내 (설치 없이 돌아간다, 기본값)
    SEGMENTER = "sam"    ultralytics SAM
    왼쪽 클릭 대상 선택 / 오른쪽 클릭·C 지우기 / ESC 종료

[변환 흐름]
    mask(bool) -> astype(uint8)*255 -> findContours -> 가장 큰 윤곽선 -> boundingRect

`findContours` 는 **uint8 이진 이미지**를 받는다(bool 을 그대로 주면 안 된다).
`RETR_EXTERNAL` 로 바깥 윤곽만, `CHAIN_APPROX_SIMPLE` 로 직선 구간의 중간 점은 버린다.
SAM 마스크에는 작은 조각이 섞이므로 **가장 큰 덩어리**를 대상으로 본다.

[bbox 는 요약이라 정보가 샌다 — 직접 재 본 값]

    도형          마스크      bbox 면적    채움 비율
    사각형        27,661      27,661      100.0%
    원            31,397      39,601       79.3%   (= π/4)
    **대각선 막대**  14,651     103,753      **14.1%**

비스듬한 물체는 박스의 **86% 가 배경**이다. 박스 중심을 물체 중심으로 믿고 드론을 돌리면
그만큼 어긋난다는 뜻이다. 그래서 이 파일은 bbox 와 함께 **마스크의 무게중심**도 찍는다.

[작은 조각은 버린다]
`MIN_AREA` 보다 작은 윤곽선은 bbox 로 만들지 않는다(원본에는 없는 가드).
6x6 짜리 조각만 있을 때 `min_area=100` 이면 `None`, `min_area=10` 이면 `(10, 10, 6, 6)` 이 나온다.

[⚠️ 마스크 크기가 프레임과 다를 수 있다]
모델이 다른 해상도로 마스크를 주면 bbox 좌표가 그 해상도 기준이라 화면과 어긋난다.
절반 크기 마스크로 시험하면 bbox 가 `(101, 71, 99, 99)` — 원본 `(201, 141, 199, 199)` 의 절반이다.
`cv.resize(..., INTER_NEAREST)` 로 프레임 크기에 맞춘 뒤 변환하면 ±1 픽셀 안에서 복원된다
(마스크는 0/1 이라 보간을 하면 안 되므로 **INTER_NEAREST**).

[여러 마스크가 나오면 클릭한 점을 포함하는 것을 고른다]
SAM 은 한 프롬프트에 여러 후보를 낸다(모호성 해결). 무조건 `[0]` 을 쓰면 엉뚱한 조각이 잡힐 수 있다.

[강의 원본 코드의 문제]
- `sam_processing = None` — `not None` 이 True 라 **우연히** 동작할 뿐, 의도는 `False` 다.
- `get_bbox_from_mask` 가 윤곽선이 없을 때 반환을 명시하지 않는다(암묵적 `None`).
- 카메라 해상도가 640x480 이 아니면 클릭 좌표와 박스가 어긋난다 → `cv.resize` 로 고정.
- 예외가 나면 카메라가 잡힌 채로 남는다 → `try/finally`.
- 박스를 지울 방법이 없다 → 오른쪽 클릭 / `C`.

[다음 단계]
SAM 은 무거워서 매 프레임 돌릴 수 없다. 실제 추적은 **SAM 으로 첫 bbox 만 만들고,
가벼운 추적기(`cv.TrackerCSRT` 등)로 그 박스를 따라가는** 구조가 보통이다.
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
FLOOD_TOLERANCE = 12
REPORT = True  # 시작할 때 변환 실험 결과를 찍는다
MAX_SECONDS = 0  # 0 = 무제한


def get_bbox(mask, min_area=MIN_AREA):
    """bool 마스크 -> (x, y, w, h). 쓸 만한 윤곽선이 없으면 None."""
    if mask is None or not np.any(mask):
        return None
    # findContours 는 uint8 이진 이미지를 받는다
    contours, _ = cv.findContours(mask.astype(np.uint8) * 255,
                                  cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    largest = max(contours, key=cv.contourArea)  # 가장 큰 덩어리 = 대상
    if cv.contourArea(largest) < min_area:
        return None  # 원본은 여기서 암묵적으로 None 이 나간다
    return cv.boundingRect(largest)


def fit_mask(mask, shape):
    """마스크 해상도가 프레임과 다르면 맞춘다. 0/1 이라 보간 없이 INTER_NEAREST."""
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


def centroid(mask):
    """마스크의 무게중심. bbox 중심과 얼마나 다른지 보려고."""
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return None
    return int(xs.mean()), int(ys.mean())


def report():
    """도형 세 개로 '마스크 -> bbox' 가 무엇을 잃는지 보여 준다."""
    yy, xx = np.mgrid[0:HEIGHT, 0:WIDTH]
    shapes = {
        "사각형": (abs(xx - 300) < 100) & (abs(yy - 240) < 70),
        "원": ((xx - 300) ** 2 + (yy - 240) ** 2) < 100 ** 2,
        "대각선 막대": (abs((xx - 300) - (yy - 240)) < 25) & (abs(xx - 300) < 150),
    }
    print("[마스크 -> bbox] 채움 비율 = 마스크 면적 / bbox 면적")
    for name, mask in shapes.items():
        box = get_bbox(mask)
        area, box_area = int(mask.sum()), box[2] * box[3]
        print(f"  {name:8s} 마스크 {area:6,d}px  bbox {box}  채움 {area / box_area * 100:5.1f}%")
    print("  → 비스듬한 물체는 박스의 대부분이 배경이다. 중심점도 그만큼 어긋난다.")

    noisy = shapes["원"].copy()
    noisy[10:16, 10:16] = True  # 6x6 조각
    only = np.zeros((HEIGHT, WIDTH), bool)
    only[10:16, 10:16] = True
    print(f"\n[작은 조각] 원+조각 -> {get_bbox(noisy)} (큰 덩어리 선택)")
    print(f"  조각만 있을 때  min_area=100 -> {get_bbox(only, 100)}   min_area=10 -> {get_bbox(only, 10)}")

    half = cv.resize(shapes["원"].astype(np.uint8), (WIDTH // 2, HEIGHT // 2),
                     interpolation=cv.INTER_NEAREST).astype(bool)
    print(f"\n[크기 불일치] 절반 크기 마스크 bbox {get_bbox(half)}  <- 화면과 어긋난다")
    print(f"  fit_mask 후 {get_bbox(fit_mask(half, (HEIGHT, WIDTH)))}  (원본 {get_bbox(shapes['원'])})")


def demo_frames():
    """정지 장면 — 클릭해서 고를 물체 셋."""
    frame = np.full((HEIGHT, WIDTH, 3), 60, np.uint8)
    cv.circle(frame, (180, 180), 80, (200, 120, 40), cv.FILLED)
    cv.rectangle(frame, (380, 110), (560, 260), (60, 180, 90), cv.FILLED)
    pts = np.array([[120, 300], [300, 300], [420, 430], [240, 430]], np.int32)
    cv.fillPoly(frame, [pts], (40, 60, 200))
    while True:
        yield True, frame.copy()


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
    if REPORT:
        report()
        print()

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
    pygame.display.set_caption("71 mask -> bbox")
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
    current_box = None
    current_center = None
    processing = False  # 원본은 여기에 None 을 넣어 우연히 동작한다
    running, count = True, 0
    started = pygame.time.get_ticks()

    try:
        while running:
            ok, frame = next(frames) if frames else cap.read()
            if not ok:
                print("프레임을 읽지 못했습니다.")
                break
            # 카메라가 요청을 무시해도 클릭 좌표와 프레임 좌표가 같도록 고정
            if frame.shape[1] != WIDTH or frame.shape[0] != HEIGHT:
                frame = cv.resize(frame, (WIDTH, HEIGHT))
            count += 1

            if click_point and not processing:
                processing = True
                t0 = time.perf_counter()
                mask = (segment_demo(frame, click_point) if SEGMENTER == "demo"
                        else segment_sam(model, frame, click_point))
                mask = None if mask is None else fit_mask(mask, frame.shape)
                current_box = get_bbox(mask)
                current_center = centroid(mask) if mask is not None else None
                took = (time.perf_counter() - t0) * 1000
                if current_box:
                    x, y, w, h = current_box
                    fill = int(mask.sum()) / (w * h) * 100
                    print(f"  click {tuple(click_point)} -> bbox {current_box} "
                          f"채움 {fill:.1f}%  ({took:.0f} ms)")
                else:
                    print(f"  click {tuple(click_point)} -> 쓸 만한 마스크 없음 ({took:.0f} ms)")
                click_point = None
                processing = False  # 원본의 None 을 False 로

            rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            screen.blit(pygame.image.frombuffer(rgb.tobytes(), (WIDTH, HEIGHT), "RGB"), (0, 0))

            if current_box:
                x, y, w, h = current_box
                pygame.draw.rect(screen, (0, 255, 0), current_box, 2)  # (x, y, w, h) 그대로 된다
                cx, cy = x + w // 2, y + h // 2
                pygame.draw.circle(screen, (255, 0, 0), (cx, cy), 4)  # bbox 중심
                if current_center:
                    pygame.draw.circle(screen, (255, 255, 0), current_center, 4)  # 무게중심
                # 화면 중앙과의 오차 — 다음 강의에서 드론을 돌릴 기준이 된다
                dx, dy = cx - WIDTH // 2, cy - HEIGHT // 2
                info = f"bbox=({x},{y},{w},{h}) center=({cx},{cy}) offset=({dx:+d},{dy:+d})"
            else:
                info = "L click: select | R click/C: clear | ESC: quit"
            screen.blit(font.render(info, True, (255, 255, 0)), (10, 10))
            pygame.draw.line(screen, (90, 90, 90), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
            pygame.draw.line(screen, (90, 90, 90), (0, HEIGHT // 2), (WIDTH, HEIGHT // 2))

            pygame.display.flip()
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_c:
                        current_box = current_center = None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and not processing:
                        click_point = list(event.pos)
                        current_box = current_center = None
                    elif event.button == 3:
                        current_box = current_center = None

            if MAX_SECONDS and pygame.time.get_ticks() - started > MAX_SECONDS * 1000:
                running = False
    finally:
        # 예외가 나도 카메라와 창을 정리한다 (원본에는 없다)
        if cap is not None:
            cap.release()
        pygame.quit()
        print(f"{count} 프레임 / 마지막 bbox {current_box}")


if __name__ == "__main__":
    main()
    sys.exit()
