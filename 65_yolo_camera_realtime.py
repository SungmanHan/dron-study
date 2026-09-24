r"""65. 실시간 추론 — 카메라 영상에 탐지 결과 그리기 📷

31 강. 64 는 사진 한 장이었고, 이번에는 **매 프레임** 추론한다. 구조는 60(영상 출력)과 같고
`blit` 과 `flip` 사이에 추론과 그리기가 들어갈 뿐이다.

    DETECTOR = "yolo"   ultralytics 로 실제 추론 (설치 + 가중치 필요)
    DETECTOR = "demo"   합성 영상에서 **색으로** 찾아 같은 모양의 결과를 만든다 (기본값)
    SOURCE   = 0        카메라 / "demo" 합성 영상 / "경로" 동영상

`demo` 탐지기는 22~24 강의 색 검출이다 — YOLO 가 아니다. 좌표 변환·그리기·FPS 처리를
설치 없이 확인하기 위한 자리끼움이다.

[한 프레임 안의 순서]
    read -> BGR2RGB -> Surface -> blit -> **추론** -> 박스·라벨 -> FPS -> flip -> tick
그리기는 반드시 `blit` **다음**이라야 영상 위에 온다. `flip` 은 맨 마지막 한 번.

[⚠️ 모델에는 RGB 가 아니라 원본 BGR 을 넘긴다]
화면용으로 만든 `frame_rgb` 를 그대로 추론에 넣기 쉬운데, **ultralytics 는 numpy 입력을 BGR 로 간주한다.**
RGB 를 넣으면 색이 뒤집힌 그림으로 추론하는 셈이라 결과가 나빠진다.
화면 변환과 추론 입력을 분리해 둘 것. (이 문서는 강의·ultralytics 문서를 따른 것이고,
모델이 없어 직접 재 보지는 못했다.)

[FPS 가 30 에 못 미치면 추론이 병목이다]
`clock.tick(30)` 으로 상한을 걸어 두었으니 `clock.get_fps()` 가 30 근처면 여유가 있는 것이고,
5~10 이면 추론이 프레임을 다 못 따라간다는 뜻이다(GPU 없는 노트북에서 흔하다). 줄이는 방법:

    classes=[0]        사람만 찾게 한다 (클래스를 줄이면 후처리가 가벼워진다)
    conf=0.5           임계값을 올려 후보를 줄인다
    INFER_EVERY = 2    두 프레임에 한 번만 추론하고 결과를 재사용한다 (이 파일의 상수)
    imgsz=320          입력 해상도를 줄인다 (작은 물체는 놓친다)

[색은 라이브러리마다 순서가 다르다]
같은 `(255, 0, 0)` 이 **pygame 에서는 빨강, OpenCV 에서는 파랑**이다.
이 파일의 박스·글자는 전부 pygame 이므로 RGB 로 읽으면 된다.

[강의 코드에서 고친 것]
- `cap.release()` 가 없다. 안 하면 다음 실행에서 카메라가 "사용 중" 으로 안 열린다 → `try/finally`.
- 라벨이 화면 위로 잘린다(`y1 - 20` 이 음수) → `max(y1 - 글자높이, 0)`.
- 6 단계 슬라이드의 라벨이 `Conf: {model.names[cls]}%` 로 되어 있어 `Conf: person%` 가 찍힌다
  → 클래스 자리에 이름, Conf 자리에 신뢰도.
- 카메라가 640x480 을 못 주면 영상이 창과 어긋난다 → 받은 프레임 크기를 확인해 맞춘다.
"""

import time

import cv2 as cv
import numpy as np
import pygame

DETECTOR = "demo"  # "yolo" / "demo"
SOURCE = "demo"  # 0 (카메라) / "demo" / "파일경로"
MODEL_FILE = "yolo11n.pt"
CONF = 0.5  # 신뢰도 임계값
ONLY_PERSON = False  # True 면 사람만 찾는다 (classes=[0]) — 빠르다
INFER_EVERY = 1  # n 프레임마다 한 번만 추론 (1 = 매 프레임)
WIDTH, HEIGHT = 640, 480
FPS = 30
MIRROR = True
MAX_SECONDS = 0  # 0 = 무제한

BOX_COLOR = (0, 255, 0)  # pygame 은 RGB — 초록
LABEL_COLOR = (255, 0, 0)  # 빨강 (OpenCV 였다면 같은 값이 파랑이다)
FPS_COLOR = (0, 0, 255)  # 파랑
# demo 탐지기가 찾을 색 (합성 영상의 물체) — 22 강의 그 HSV 범위
DEMO_HSV = ((95, 80, 80), (115, 255, 255))


def demo_frames():
    """카메라 대신 쓸 영상 — '사람' 노릇을 할 파란 기둥이 좌우로 움직인다."""
    i = 0
    while True:
        frame = np.full((HEIGHT, WIDTH, 3), 70, np.uint8)
        cv.rectangle(frame, (0, HEIGHT - 80), (WIDTH, HEIGHT), (90, 90, 90), cv.FILLED)
        x = int(WIDTH / 2 + 180 * np.sin(i / 30.0))
        cv.rectangle(frame, (x - 45, 120), (x + 45, 400), (200, 120, 40), cv.FILLED)
        cv.circle(frame, (x, 95), 35, (200, 120, 40), cv.FILLED)
        i += 1
        yield True, frame


def detect_demo(frame):
    """색으로 찾는 자리끼움 탐지기. (x1, y1, x2, y2, conf, name) 목록."""
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    mask = cv.inRange(hsv, np.array(DEMO_HSV[0]), np.array(DEMO_HSV[1]))
    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    out = []
    for contour in contours:
        if cv.contourArea(contour) < 1000:
            continue
        x, y, w, h = cv.boundingRect(contour)
        out.append((x, y, x + w, y + h, 0.9, "person"))  # 이름만 person 인 척한다
    return out


def detect_yolo(frame, model):
    """ultralytics 결과를 같은 모양으로 바꾼다. 입력은 **BGR 원본**."""
    kwargs = {"conf": CONF, "verbose": False}
    if ONLY_PERSON:
        kwargs["classes"] = [0]  # COCO 0 = person
    detections = []
    for result in model(frame, **kwargs):
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # 텐서 -> 정수
            detections.append((x1, y1, x2, y2, float(box.conf[0]),
                               model.names[int(box.cls[0])]))
    return detections


def main():
    model = None
    if DETECTOR == "yolo":
        try:
            from ultralytics import YOLO
        except ImportError:
            raise SystemExit("ultralytics 가 없습니다.  pip install ultralytics  (63 참고)\n"
                             '  설치 없이 보려면 DETECTOR = "demo"')
        model = YOLO(MODEL_FILE)  # 없으면 자동으로 내려받는다 (인터넷 필요)

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption("65 YOLO realtime")
    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()

    frames = demo_frames() if SOURCE == "demo" else None
    cap = None if frames else cv.VideoCapture(SOURCE)
    if cap is not None:
        cap.set(cv.CAP_PROP_FRAME_WIDTH, WIDTH)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        if not cap.isOpened():
            pygame.quit()  # 창부터 닫는다
            raise SystemExit("카메라를 열지 못했습니다. (시스템 환경설정 > 보안 > 카메라 권한)")

    running = True
    count = 0
    detections = []
    infer_ms = 0.0
    started = pygame.time.get_ticks()
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            ok, frame = next(frames) if frames else cap.read()
            if not ok:
                print("프레임을 읽지 못했습니다.")
                break
            if frame.shape[1] != WIDTH or frame.shape[0] != HEIGHT:
                frame = cv.resize(frame, (WIDTH, HEIGHT))  # 카메라가 다른 크기를 줄 수 있다
            if MIRROR:
                frame = cv.flip(frame, 1)
            count += 1

            # 화면용 변환과 추론 입력은 따로다 — 모델에는 BGR 원본을 넘긴다
            rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            screen.blit(pygame.image.frombuffer(rgb.tobytes(), (WIDTH, HEIGHT), "RGB"), (0, 0))

            if count % INFER_EVERY == 0:  # 건너뛴 프레임은 직전 결과를 그대로 쓴다
                t0 = time.perf_counter()
                detections = detect_demo(frame) if DETECTOR == "demo" else detect_yolo(frame, model)
                infer_ms = (time.perf_counter() - t0) * 1000

            for x1, y1, x2, y2, conf, name in detections:
                pygame.draw.rect(screen, BOX_COLOR, (x1, y1, x2 - x1, y2 - y1), 2)  # (x,y,w,h)
                label = f"Class: {name}, Conf: {int(conf * 100)}%"
                text = font.render(label, True, LABEL_COLOR)
                screen.blit(text, (x1, max(y1 - text.get_height(), 0)))  # 위로 잘리지 않게

            info = f"FPS: {clock.get_fps():5.2f}  infer {infer_ms:5.1f} ms  objects {len(detections)}"
            screen.blit(font.render(info, True, FPS_COLOR), (10, 10))

            pygame.display.flip()
            clock.tick(FPS)  # 상한. 여기 못 미치면 추론이 병목이다
            if MAX_SECONDS and pygame.time.get_ticks() - started > MAX_SECONDS * 1000:
                running = False
    finally:
        # 여기까지 안 오면 카메라가 잡힌 채로 남는다
        if cap is not None:
            cap.release()
        pygame.quit()
        print(f"{count} 프레임 / 마지막 추론 {infer_ms:.1f} ms / 탐지 {len(detections)}개")


if __name__ == "__main__":
    main()
