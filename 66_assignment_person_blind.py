r"""66. [과제] 사람만 찾아서 가리기 📷

31 강 과제. 영상을 추론해서 클래스가 **person 이면 사각형으로 덮는다.** 나머지는 평소처럼 박스+라벨.

    ESC / 창 닫기   종료
    S               지금 화면을 PNG 로 저장 (제출용 캡처)

    DETECTOR = "demo"   설치 없이 확인 (색으로 찾는 자리끼움 — 65 와 같다)
    BLIND_MODE = "fill" / "alpha" / "mosaic"

[과제의 핵심은 `width` 인자 하나다]
    pygame.draw.rect(surface, color, rect, width=0)
`width` 는 **테두리 두께**이고, 생략하면 기본값 0 = **채우기**다. 직접 재 보면:

    width 생략 → 사각형 안쪽 픽셀 (0, 0, 0)     ← 꽉 찼다
    width = 2  → 안쪽은 원래 색, 테두리만 검정

그래서 사람일 때는 두께를 빼고, 아닐 때는 2 를 준다. 그게 전부다.

[세 가지 가리는 법 — 직접 확인한 값]

    fill     draw.rect 를 두께 없이. 완전히 가린다
    alpha    SRCALPHA Surface 를 만들어 fill((0,0,0,180)) 후 blit
             흰 배경(255) 위에 알파 180 을 얹으면 **75** 가 된다 = 255 x (1 − 180/255). 뒤가 살짝 비친다
    mosaek   OpenCV 쪽에서 그 영역만 작게 줄였다가 INTER_NEAREST 로 다시 키운다
             120x120 을 8x8 로 줄였다 키우면 15x15 블록 안이 **모두 같은 값**이 된다

`mosaic` 만 **영상을 Surface 로 바꾸기 전에** 처리해야 한다 — pygame 으로 그리는 게 아니라
프레임 자체를 고치는 것이기 때문이다. 나머지 둘은 `blit` 뒤에 화면 위에 덮는다.

[가장자리가 새면 여유를 준다]
박스가 사람에 딱 붙어 나오면 머리카락·어깨가 조금 삐져나온다. `PAD` 만큼 넓혀서 덮는다.
화면 밖으로 나가지 않게 잘라 주는 것도 잊지 말 것(`clamp`).

[사람만 찾게 하면 빨라진다]
    model(frame, classes=[0], conf=0.5, verbose=False)
찾을 클래스를 사람 하나로 줄이면 후처리가 가벼워진다. 가리는 게 목적이라면 나머지 79 종을
굳이 찾을 이유가 없다(`ONLY_PERSON`).

[과제 코드에서 손본 것]
- 종료 경로에서만 `cap.release()` 를 한다 → 예외가 나면 카메라가 잡힌 채 남는다. `try/finally` 로.
- 카메라가 640x480 을 못 주면 화면과 좌표가 어긋난다 → 받은 크기를 확인해 맞춘다.
- 캡처 파일이 실행 폴더에 쌓인다 → `capture_*.png` 를 `.gitignore` 에 넣었다.
- 사람이 여러 명일 때를 세어 화면에 표시한다(원본도 하고 있다).
"""

import os
from datetime import datetime

import cv2 as cv
import numpy as np
import pygame

DETECTOR = "demo"  # "yolo" (실제 추론) / "demo" (색으로 찾는 자리끼움)
SOURCE = "demo"  # 0 (카메라) / "demo" / "파일경로"
MODEL_FILE = "yolo11n.pt"
CONF = 0.5
ONLY_PERSON = True  # 사람만 찾는다 (classes=[0]) — 가리는 게 목적이면 이게 빠르다
BLIND_MODE = "fill"  # "fill" / "alpha" / "mosaic"
BLIND_COLOR = (0, 0, 0)  # pygame 은 RGB
ALPHA = 180  # alpha 모드의 불투명도 0~255
MOSAIC_BLOCKS = 8  # mosaic 모드에서 한 변을 몇 칸으로 줄일지 (작을수록 굵다)
PAD = 8  # 박스를 이만큼 넓혀서 덮는다 (가장자리 새는 것 방지)
WIDTH, HEIGHT = 640, 480
FPS = 30
MIRROR = True
SAVE_ON_EXIT = False  # True 면 끝날 때 화면을 한 장 저장 (S 키를 못 누르는 환경용)
MAX_SECONDS = 0  # 0 = 무제한

PERSON_CLASS_ID = 0  # COCO 기준 0 = person
DEMO_HSV = ((95, 80, 80), (115, 255, 255))


def demo_frames():
    """'사람' 노릇을 할 파란 기둥이 좌우로 움직이는 영상."""
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
    """색으로 찾는 자리끼움. 이름만 person 인 척한다 — YOLO 가 아니다."""
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    mask = cv.inRange(hsv, np.array(DEMO_HSV[0]), np.array(DEMO_HSV[1]))
    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    return [(*cv.boundingRect(c)[:2],
             cv.boundingRect(c)[0] + cv.boundingRect(c)[2],
             cv.boundingRect(c)[1] + cv.boundingRect(c)[3],
             0.9, PERSON_CLASS_ID, "person")
            for c in contours if cv.contourArea(c) >= 1000]


def detect_yolo(frame, model):
    """(x1, y1, x2, y2, conf, cls, name) 목록. 입력은 BGR 원본(65 참고)."""
    kwargs = {"conf": CONF, "verbose": False}
    if ONLY_PERSON:
        kwargs["classes"] = [PERSON_CLASS_ID]
    out = []
    for result in model(frame, **kwargs):
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls = int(box.cls[0])
            out.append((x1, y1, x2, y2, float(box.conf[0]), cls, model.names[cls]))
    return out


def clamp_box(x1, y1, x2, y2, pad=0):
    """여유를 주되 화면 밖으로 나가지 않게 자른다."""
    return (max(x1 - pad, 0), max(y1 - pad, 0),
            min(x2 + pad, WIDTH), min(y2 + pad, HEIGHT))


def mosaic_area(frame, box):
    """프레임의 그 영역만 모자이크로 만든다 — Surface 로 바꾸기 **전에** 해야 한다."""
    x1, y1, x2, y2 = box
    if x2 <= x1 or y2 <= y1:
        return
    area = frame[y1:y2, x1:x2]
    small = cv.resize(area, (MOSAIC_BLOCKS, MOSAIC_BLOCKS), interpolation=cv.INTER_AREA)
    frame[y1:y2, x1:x2] = cv.resize(small, (x2 - x1, y2 - y1), interpolation=cv.INTER_NEAREST)


def blind_fill(screen, box):
    x1, y1, x2, y2 = box
    # ★ 과제 핵심: 두께를 생략하면 기본값 0 = 채우기
    pygame.draw.rect(screen, BLIND_COLOR, (x1, y1, x2 - x1, y2 - y1))


def blind_alpha(screen, box):
    x1, y1, x2, y2 = box
    overlay = pygame.Surface((x2 - x1, y2 - y1), pygame.SRCALPHA)  # 알파를 쓰려면 SRCALPHA
    overlay.fill((*BLIND_COLOR, ALPHA))
    screen.blit(overlay, (x1, y1))


def main():
    model = None
    if DETECTOR == "yolo":
        try:
            from ultralytics import YOLO
        except ImportError:
            raise SystemExit("ultralytics 가 없습니다.  pip install ultralytics  (63 참고)\n"
                             '  설치 없이 보려면 DETECTOR = "demo"')
        model = YOLO(MODEL_FILE)

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption("Person Blind - ESC: quit / S: capture")
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

    running = True
    count = 0
    blinded = 0
    started = pygame.time.get_ticks()
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_s:  # 제출용 캡처
                        name = f"capture_{datetime.now():%Y%m%d_%H%M%S}.png"
                        pygame.image.save(screen, name)
                        print(f"저장: {os.path.abspath(name)}")

            ok, frame = next(frames) if frames else cap.read()
            if not ok:
                print("프레임을 읽지 못했습니다.")
                break
            if frame.shape[1] != WIDTH or frame.shape[0] != HEIGHT:
                frame = cv.resize(frame, (WIDTH, HEIGHT))
            if MIRROR:
                frame = cv.flip(frame, 1)
            count += 1

            detections = detect_demo(frame) if DETECTOR == "demo" else detect_yolo(frame, model)
            people = [d for d in detections if d[5] == PERSON_CLASS_ID]

            # 모자이크는 프레임 자체를 고치는 것이라 Surface 로 바꾸기 전에 처리한다
            if BLIND_MODE == "mosaic":
                for x1, y1, x2, y2, _conf, _cls, _name in people:
                    mosaic_area(frame, clamp_box(x1, y1, x2, y2, PAD))

            rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            screen.blit(pygame.image.frombuffer(rgb.tobytes(), (WIDTH, HEIGHT), "RGB"), (0, 0))

            blinded = 0
            for x1, y1, x2, y2, conf, cls, name in detections:
                box = clamp_box(x1, y1, x2, y2, PAD if cls == PERSON_CLASS_ID else 0)
                if cls == PERSON_CLASS_ID:
                    blinded += 1
                    if BLIND_MODE == "fill":
                        blind_fill(screen, box)
                    elif BLIND_MODE == "alpha":
                        blind_alpha(screen, box)
                    # mosaic 은 위에서 이미 처리했다
                else:  # 사람이 아닌 것은 평소대로 테두리 + 라벨
                    pygame.draw.rect(screen, (0, 255, 0),
                                     (box[0], box[1], box[2] - box[0], box[3] - box[1]), 2)
                    text = font.render(f"{name} {int(conf * 100)}%", True, (255, 0, 0))
                    screen.blit(text, (box[0], max(box[1] - text.get_height(), 0)))

            info = (f"FPS: {clock.get_fps():5.2f}  blinded: {blinded}  mode: {BLIND_MODE}"
                    f"{'  (DEMO)' if DETECTOR == 'demo' else ''}")
            screen.blit(font.render(info, True, (0, 0, 255)), (10, 10))

            pygame.display.flip()
            clock.tick(FPS)
            if MAX_SECONDS and pygame.time.get_ticks() - started > MAX_SECONDS * 1000:
                running = False
        if SAVE_ON_EXIT:
            name = f"capture_{datetime.now():%Y%m%d_%H%M%S}.png"
            pygame.image.save(screen, name)
            print(f"저장: {os.path.abspath(name)}")
    finally:
        if cap is not None:
            cap.release()
        pygame.quit()
        print(f"{count} 프레임 / 마지막 프레임에서 가린 사람 {blinded}명 / 모드 {BLIND_MODE}")


if __name__ == "__main__":
    main()
