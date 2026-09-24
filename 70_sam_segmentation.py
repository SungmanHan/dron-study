r"""70. SAM — 클릭한 것을 분할하기 📷

33 강. 클릭(점)이나 드래그(박스)를 **프롬프트**로 주면 그 객체의 마스크가 나온다.

    SEGMENTER = "sam"    ultralytics SAM 으로 실제 분할 (설치 + 가중치 필요)
    SEGMENTER = "demo"   OpenCV 로 흉내 — **설치 없이 돌아간다** (기본값)
    SOURCE    = 0        카메라 / "demo" 합성 영상 / "경로"

    왼쪽 클릭  전경점 추가 (이 영역을 포함)
    오른쪽 클릭 배경점 추가 (이 영역을 제외) — 전경점이 먼저 있어야 한다
    왼쪽 드래그 박스 프롬프트
    N 현재 객체 확정 / C 전체 지우기 / ESC 종료

[SAM 이 앞의 모델들과 다른 점]
YOLO 는 **미리 정한 80 종**을 찾는다. SAM 은 클래스를 모른다 — "여기" 라고 찍어 주면 그 덩어리를
분할한다(제로샷). 그래서 출력이 클래스·박스가 아니라 **픽셀 마스크**다.

    Image Encoder   이미지를 한 번 인코딩 (가장 무겁다)
    Prompt Encoder  점·박스·마스크 프롬프트를 인코딩
    Mask Decoder    둘을 합쳐 마스크를 빠르게 출력

이미지 인코딩은 한 번, 프롬프트가 바뀔 때는 가벼운 디코더만 다시 돈다 — 클릭할 때마다 즉시
반응하는 대화형 사용이 가능한 이유다. 점 하나는 "셔츠" 일 수도 "사람 전체" 일 수도 있어서
SAM 은 **여러 후보 마스크와 점수**를 함께 내놓는다(모호성 해결).

[ultralytics 호출 — 괄호 깊이가 의미를 바꾼다]
    model(frame, points=[[x1, y1], [x2, y2]], labels=[1, 1])     점마다 **따로** 분할 (마스크 2개)
    model(frame, points=[[[x1, y1], [x2, y2]]], labels=[[1, 0]]) **한 객체**의 전경·배경 점 (마스크 1개)
    model(frame, bboxes=[x1, y1, x2, y2])                        박스 프롬프트

원하지 않는 부분을 빼려면 **한 겹 더 감싼** 두 번째 형태여야 한다. 결과는
`results[0].masks.data[0].cpu().numpy().astype(bool)` 로 꺼낸다 (GPU 텐서일 수 있어 `.cpu()`).

[⚠️ 마스크는 그 순간에 고정된다]
클릭한 프레임으로 한 번만 추론하므로, 이후 물체가 움직여도 마스크는 그 자리에 남는다.
매 프레임 분할하면 따라가지만 느려서 못 쓴다(SAM 2 의 영상 추적 기능은 별개다).
**정지된 장면에서 실습하는 게 맞다.**

[추론하는 동안 화면이 멈춘다]
메인 루프 안에서 도는 데다 CPU 환경이면 수 초가 걸린다. 그래서 이 파일은 요청을 `pending` 에
적어 두고 **다음 프레임에서** 처리하며, 추론 직전에 "Inferencing..." 을 먼저 그려 둔다.

[demo 모드는 SAM 이 아니다]
설치 없이 "프롬프트 → 마스크 → 반투명 오버레이" 흐름만 확인하려고 OpenCV 로 흉내 낸 것이다.

    점 프롬프트  cv.floodFill   클릭한 색과 이어진 비슷한 영역을 채운다
    박스 프롬프트 cv.grabCut     박스 안에서 전경을 갈라낸다 (3회 반복, 박스 크기에 따라 130~400 ms)

색과 연결성만 보는 고전 방식이라 **의미를 모른다** — 26 강에서 본 수동 특징의 한계 그대로다.
SAM 과 결과가 다른 게 당연하고, 그 차이를 보는 것도 공부가 된다.

[강의 코드에서 고친 것]
- 원본에는 `cap.release()` / `pygame.quit()` 가 없다 → `try/finally`.
- 카메라가 640x480 을 안 주면 **마스크 크기와 화면 크기가 어긋나 인덱싱 오류**가 난다 →
  `cv.resize` 로 고정.
- 마스크 오버레이의 `del pixels_rgb, pixels_alpha` 를 빼면 blit 에서
  `Surfaces must not be locked during blit` 가 난다(69 에서 확인). 이 파일은 잠금이 없는 RGBA 방식.
"""

import sys
import time

import cv2 as cv
import numpy as np
import pygame

SEGMENTER = "demo"  # "sam" / "demo"
SOURCE = "demo"  # 0 (카메라) / "demo" / "파일경로"
MODEL_PATH = "sam2_t.pt"  # CPU 면 tiny. GPU 있으면 sam2_s / sam2_b
WIDTH, HEIGHT = 640, 480
FPS = 30
MASK_ALPHA = 128
DRAG_THRESHOLD = 10  # 이보다 많이 움직이면 클릭이 아니라 드래그(박스)
FLOOD_TOLERANCE = 12  # demo 점 프롬프트의 색 허용 오차
GRABCUT_ITER = 3  # demo 박스 프롬프트 반복 횟수
MAX_SECONDS = 0  # 0 = 무제한

COLORS = [(0, 255, 0), (255, 0, 0), (0, 128, 255), (255, 255, 0), (255, 0, 255)]
HELP = "L:add  R:remove  drag:box  N:next  C:clear  ESC:quit"


def demo_frames():
    """정지된 장면 — 분할 실습은 움직이지 않는 그림이 낫다."""
    frame = np.full((HEIGHT, WIDTH, 3), 60, np.uint8)
    cv.circle(frame, (200, 200), 90, (200, 120, 40), cv.FILLED)
    cv.rectangle(frame, (380, 120), (560, 300), (60, 180, 90), cv.FILLED)
    cv.rectangle(frame, (150, 330), (480, 430), (40, 60, 200), cv.FILLED)
    while True:
        yield True, frame.copy()


def segment_demo(frame, points, labels, bbox):
    """OpenCV 로 흉내 낸 분할. SAM 이 아니다."""
    if bbox is not None:  # 박스 -> grabCut
        x1, y1, x2, y2 = bbox
        if x2 - x1 < 5 or y2 - y1 < 5:
            return None
        grab = np.zeros(frame.shape[:2], np.uint8)
        bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
        cv.grabCut(frame, grab, (x1, y1, x2 - x1, y2 - y1), bgd, fgd,
                   GRABCUT_ITER, cv.GC_INIT_WITH_RECT)
        return (grab == cv.GC_FGD) | (grab == cv.GC_PR_FGD)

    mask = np.zeros(frame.shape[:2], bool)
    for (x, y), label in zip(points, labels):  # 점 -> floodFill
        flood = np.zeros((HEIGHT + 2, WIDTH + 2), np.uint8)
        tol = (FLOOD_TOLERANCE,) * 3
        cv.floodFill(frame.copy(), flood, (x, y), 255, tol, tol,
                     cv.FLOODFILL_MASK_ONLY | (255 << 8))
        region = flood[1:-1, 1:-1] > 0
        mask = mask | region if label == 1 else mask & ~region  # 배경점은 빼낸다
    return mask if mask.any() else None


def segment_sam(model, frame, points, labels, bbox):
    """ultralytics SAM. 마스크 한 장을 bool 배열로 돌려준다."""
    if bbox is not None:
        results = model(frame, bboxes=[list(bbox)], verbose=False)
    else:
        # 한 겹 더 감싸야 '한 객체의 점들' 로 해석된다
        results = model(frame, points=[[list(p) for p in points]], labels=[list(labels)],
                        verbose=False)
    if results and results[0].masks is not None and len(results[0].masks.data) > 0:
        return results[0].masks.data[0].cpu().numpy().astype(bool)  # GPU 텐서일 수 있다
    return None


def mask_surface(mask, color):
    """bool 마스크 -> 반투명 Surface. RGBA 배열이라 잠금 함정이 없다(69)."""
    rgba = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
    rgba[mask] = (*color, MASK_ALPHA)
    return pygame.image.frombuffer(rgba.tobytes(), (WIDTH, HEIGHT), "RGBA")


def draw_text(screen, font, text, pos=(8, 8)):
    """검은 칸 위에 흰 글씨 (기본 폰트에 한글은 없다 — 61 참고)."""
    label = font.render(text, True, (255, 255, 255))
    back = pygame.Surface((label.get_width() + 8, label.get_height() + 4))
    back.fill((0, 0, 0))
    screen.blit(back, (pos[0] - 4, pos[1] - 2))
    screen.blit(label, pos)


def main():
    model = None
    if SEGMENTER == "sam":
        try:
            from ultralytics import SAM
        except ImportError:
            raise SystemExit("ultralytics 가 없습니다.  pip install ultralytics  (63 참고)\n"
                             '  설치 없이 보려면 SEGMENTER = "demo"')
        model = SAM(MODEL_PATH)  # 없으면 자동으로 내려받는다 (인터넷 필요)

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption("70 SAM segmentation")
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

    objects = []  # 확정된 마스크들
    points, labels = [], []  # 지금 만들고 있는 객체의 점 프롬프트
    current = None  # 지금 마스크
    pending = None  # ("points",) 또는 ("box", bbox) — 다음 프레임에서 처리
    drag_start = drag_now = None
    status = "Click an object"
    running, count = True, 0
    started = pygame.time.get_ticks()

    try:
        while running:
            ok, frame = next(frames) if frames else cap.read()
            if not ok:
                print("프레임을 읽지 못했습니다.")
                break
            # 카메라가 설정을 무시해도 마스크와 화면 크기가 어긋나지 않게 고정한다
            if frame.shape[1] != WIDTH or frame.shape[0] != HEIGHT:
                frame = cv.resize(frame, (WIDTH, HEIGHT))
            count += 1

            rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            screen.blit(pygame.image.frombuffer(rgb.tobytes(), (WIDTH, HEIGHT), "RGB"), (0, 0))

            if pending is not None:
                draw_text(screen, font, "Inferencing...")  # 멈추기 전에 먼저 보여 준다
                pygame.display.flip()
                t0 = time.perf_counter()
                bbox = pending[1] if pending[0] == "box" else None
                if SEGMENTER == "demo":
                    current = segment_demo(frame, points, labels, bbox)
                else:
                    current = segment_sam(model, frame, points, labels, bbox)
                took = (time.perf_counter() - t0) * 1000
                area = 0 if current is None else int(current.sum())
                status = ("No mask found" if current is None
                          else f"Object {len(objects) + 1}: {area:,}px  ({took:.0f} ms)")
                print(f"  {pending[0]:6s} -> {status}")
                pending = None

            for i, mask in enumerate(objects):  # 확정된 것들
                screen.blit(mask_surface(mask, COLORS[i % len(COLORS)]), (0, 0))
            if current is not None:  # 지금 것
                screen.blit(mask_surface(current, COLORS[len(objects) % len(COLORS)]), (0, 0))

            for (x, y), label in zip(points, labels):  # 초록 = 전경점, 빨강 = 배경점
                pygame.draw.circle(screen, (0, 255, 0) if label == 1 else (255, 0, 0), (x, y), 5)
                pygame.draw.circle(screen, (255, 255, 255), (x, y), 5, 1)

            if drag_start and drag_now:
                x1, y1 = drag_start
                x2, y2 = drag_now
                pygame.draw.rect(screen, (255, 255, 0),
                                 pygame.Rect(min(x1, x2), min(y1, y2),
                                             abs(x2 - x1), abs(y2 - y1)), 2)

            draw_text(screen, font, status)
            draw_text(screen, font, HELP, pos=(8, HEIGHT - 26))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_n:  # 확정하고 다음 객체로
                        if current is not None:
                            objects.append(current)
                        points, labels, current = [], [], None
                        status = f"Saved {len(objects)} object(s)"
                    elif event.key == pygame.K_c:  # 전부 지우기
                        objects.clear()
                        points, labels, current = [], [], None
                        status = "Cleared"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        drag_start = drag_now = event.pos
                    elif event.button == 3:  # 배경점 — 전경점이 먼저 있어야 의미가 있다
                        if points:
                            points.append(list(event.pos))
                            labels.append(0)
                            pending = ("points",)
                        else:
                            status = "Add a foreground point first"
                elif event.type == pygame.MOUSEMOTION and drag_start:
                    drag_now = event.pos
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and drag_start:
                    (x1, y1), (x2, y2) = drag_start, event.pos
                    if max(abs(x2 - x1), abs(y2 - y1)) >= DRAG_THRESHOLD:
                        points, labels = [], []  # 박스와 점을 섞지 않는다
                        pending = ("box", (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)))
                    else:
                        points.append(list(event.pos))
                        labels.append(1)
                        pending = ("points",)
                    drag_start = drag_now = None

            clock.tick(FPS)
            if MAX_SECONDS and pygame.time.get_ticks() - started > MAX_SECONDS * 1000:
                running = False
    finally:
        # 예외가 나도 카메라와 창을 정리한다 (원본에는 없다)
        if cap is not None:
            cap.release()
        pygame.quit()
        print(f"{count} 프레임 / 확정한 객체 {len(objects)}개")


if __name__ == "__main__":
    main()
    sys.exit()
