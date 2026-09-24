r"""64. 이미지 추론 — 탐지 결과를 화면에 그리기

30 강. 62 가 띄운 그림 위에 **박스와 라벨**을 얹는다. 드론도 카메라도 쓰지 않는다.

    DETECTOR = "yolo"   ultralytics 로 실제 추론 (설치 + 가중치 필요)
    DETECTOR = "demo"   미리 넣어 둔 박스로 그리기만 확인 — **설치 없이 돌아간다** (기본값)

[흐름]
    imread -> 리사이즈 -> BGR2RGB -> Surface -> blit -> **추론** -> 박스·라벨 그리기 -> flip

박스는 `pygame.draw.rect` 로, 라벨은 `font.render` + `blit` 으로 그린다. 둘 다 **blit 다음**이라야
영상 위에 온다(28: 나중에 그린 것이 위).

[좌표는 "어느 그림에서 추론했는지" 에 매여 있다 — 이 강의의 핵심]
`box.xyxy` 는 **추론에 넣은 이미지 기준 픽셀**이다. 원본(810x1080)으로 추론하고 화면에는
줄인 그림(360x480)을 띄우면, 박스만 2.25 배 크게 그려져 엉뚱한 자리에 간다.

    INFER_ON = "resized"    줄인 그림으로 추론 → 좌표가 화면과 그대로 맞는다 (강의 방식, 권장)
    INFER_ON = "original"   원본으로 추론 → **좌표에 scale 을 곱해야** 화면과 맞는다

둘 다 넣어 두고 화면 좌표가 같은지 확인한다(직접 돌려 보면 소수점 반올림만 다르다).
원본으로 추론하면 작은 물체를 더 잘 잡는 대신 느리다 — 무엇을 택하든 **좌표 변환을 빼먹지 않는 것**이 요점.

[라벨이 화면 밖으로 나간다]
객체가 맨 위에 있으면 `y1 - 20` 이 음수가 되어 글자가 잘린다 → `max(y1 - 20, 0)`.
밝은 배경에서는 흰 글자가 안 보인다 → `font.render(label, True, 글자색, 배경색)` 으로 배경을 깔면 된다.
이 파일은 박스와 같은 색으로 라벨 배경을 깐다.

[신뢰도 임계값]
`model(frame, conf=0.5)` — 50% 미만은 버린다. 낮추면 많이(오탐 포함), 높이면 확실한 것만.
NMS 도 `iou=` 로 조절한다. 58 에서 손으로 짠 그 후처리를 인자로 여는 것뿐이다.

[강의 자료 사이에서 모델이 다르다]
29 강은 `yolo11n.pt`(YOLO11), 30 강은 `yolov8n.pt`(YOLOv8) 를 쓴다. 둘 다 같은 API 라
그대로 돌아가지만, **가중치 파일을 두 번 받게 된다.** 하나로 맞추는 편이 낫다(이 파일은 `MODEL_FILE`).

[ultralytics 가 없으면]
설치는 torch 까지 딸려 와 무겁다(63 참고). 그래서 이 파일은 `DETECTOR = "demo"` 를 기본값으로 두고,
**탐지기 자리만 가짜로 채워** 좌표 변환·그리기·라벨 처리를 전부 확인할 수 있게 했다.
`demo` 의 박스는 고정값이므로 "인식이 됐다" 는 뜻이 아니다 — 화면에 제대로 얹히는지를 보는 용도다.
"""

import os
import tempfile

import cv2 as cv
import numpy as np
import pygame

DETECTOR = "demo"  # "yolo" (실제 추론) / "demo" (고정 박스로 그리기만 확인)
INFER_ON = "resized"  # "resized" (권장) / "original" (좌표에 scale 을 곱한다)
MODEL_FILE = "yolo11n.pt"  # 29 강과 같은 파일로 맞춘다 (강의 30 은 yolov8n.pt)
CONF = 0.5  # 신뢰도 임계값
IMAGE_PATH = ""  # 비우면 샘플 이미지를 그려서 쓴다
WIDTH, HEIGHT = 640, 480
SAVE = True  # 결과 화면을 파일로 저장
MAX_SECONDS = 0  # 0 = 무제한. 숫자를 주면 그 시간 뒤 자동 종료

# demo 탐지기가 돌려줄 박스 — **원본 이미지 좌표**, (x1, y1, x2, y2, 신뢰도, 이름)
DEMO_BOXES = [(60, 120, 750, 880, 0.91, "bus"),
              (120, 220, 690, 520, 0.68, "window"),
              (90, 860, 230, 1000, 0.55, "wheel")]


def make_sample_image(w=810, h=1080):
    """29 강 bus.jpg 자리에 쓸 샘플. DEMO_BOXES 좌표가 이 그림에 맞춰져 있다."""
    img = np.full((h, w, 3), 235, np.uint8)
    cv.rectangle(img, (60, 120), (w - 60, h - 200), (170, 120, 60), cv.FILLED)
    cv.rectangle(img, (120, 220), (w - 120, 520), (230, 220, 200), cv.FILLED)
    for i in range(3):
        cv.circle(img, (160 + i * 240, h - 150), 70, (60, 60, 60), cv.FILLED)
    path = os.path.join(tempfile.gettempdir(), "sample_photo.jpg")
    cv.imwrite(path, img)
    return path


def letterbox(frame, target_w, target_h):
    """비율을 지켜 창에 맞춘다. (줄인 그림, 배율, 붙일 좌표) — 62 와 같은 계산."""
    orig_h, orig_w = frame.shape[:2]
    scale = min(target_w / orig_w, target_h / orig_h)
    new_w, new_h = int(orig_w * scale), int(orig_h * scale)
    resized = cv.resize(frame, (new_w, new_h), interpolation=cv.INTER_AREA)
    offset = ((target_w - new_w) // 2, (target_h - new_h) // 2)
    return resized, scale, offset


def detect_demo(_frame, scale):
    """가짜 탐지기. 원본 좌표를 그때그때 배율에 맞춰 돌려준다."""
    return [(int(x1 * scale), int(y1 * scale), int(x2 * scale), int(y2 * scale), conf, name)
            for x1, y1, x2, y2, conf, name in DEMO_BOXES]


def detect_yolo(frame, model):
    """ultralytics 결과를 (x1, y1, x2, y2, conf, name) 목록으로 바꾼다."""
    detections = []
    for result in model(frame, conf=CONF):  # model.predict(...) 와 같다
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # 텐서 -> 정수 픽셀
            detections.append((x1, y1, x2, y2, float(box.conf[0]),
                               model.names[int(box.cls[0])]))
    return detections


def draw_detections(screen, font, detections, offset, scale_to_screen=1.0):
    """박스와 라벨을 화면에 그린다. 좌표는 '화면 기준' 으로 들어와야 한다."""
    ox, oy = offset
    for x1, y1, x2, y2, conf, name in detections:
        x1, y1 = int(x1 * scale_to_screen) + ox, int(y1 * scale_to_screen) + oy
        x2, y2 = int(x2 * scale_to_screen) + ox, int(y2 * scale_to_screen) + oy
        pygame.draw.rect(screen, (0, 255, 0), (x1, y1, x2 - x1, y2 - y1), 2)  # (x, y, 너비, 높이)
        label = f"{name} {int(conf * 100)}%"
        # 배경색을 같이 주면 밝은 그림 위에서도 글자가 보인다
        text = font.render(label, True, (255, 255, 255), (0, 128, 0))
        screen.blit(text, (x1, max(y1 - text.get_height(), 0)))  # 위로 잘리지 않게
        print(f"  {label:16s} ({x1}, {y1}) - ({x2}, {y2})")


def main():
    path = IMAGE_PATH or make_sample_image()
    frame = cv.imread(path)
    if frame is None:  # imread 는 실패해도 None 을 돌려준다(40)
        raise SystemExit(f"이미지를 읽지 못했습니다: {path}")
    resized, scale, offset = letterbox(frame, WIDTH, HEIGHT)
    print(f"[이미지] {path}  {frame.shape[1]}x{frame.shape[0]} -> "
          f"{resized.shape[1]}x{resized.shape[0]} (배율 {scale:.3f}), 붙일 좌표 {offset}")

    model = None
    if DETECTOR == "yolo":
        try:
            from ultralytics import YOLO
        except ImportError:
            raise SystemExit("ultralytics 가 없습니다.  pip install ultralytics  (63 참고)\n"
                             '  설치 없이 보려면 DETECTOR = "demo"')
        model = YOLO(MODEL_FILE)  # 파일이 없으면 자동으로 내려받는다 (인터넷 필요)

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption("64 YOLO image inference")
    font = pygame.font.SysFont(None, 24)  # 기본 폰트에 한글은 없다(61)
    clock = pygame.time.Clock()

    rgb = cv.cvtColor(resized, cv.COLOR_BGR2RGB)
    surface = pygame.image.frombuffer(rgb.tobytes(), (rgb.shape[1], rgb.shape[0]), "RGB")
    screen.fill((0, 0, 0))
    screen.blit(surface, offset)  # 그림 먼저

    # 어느 그림으로 추론하느냐에 따라 좌표 기준이 달라진다
    if INFER_ON == "original":
        source, to_screen = frame, scale  # 원본 좌표 -> 화면 좌표로 줄여야 한다
    else:
        source, to_screen = resized, 1.0  # 이미 화면과 같은 크기다
    print(f"[추론] {DETECTOR} / {INFER_ON} (conf={CONF})")
    detections = (detect_demo(source, scale if INFER_ON == "resized" else 1.0)
                  if DETECTOR == "demo" else detect_yolo(source, model))
    draw_detections(screen, font, detections, offset, to_screen)
    pygame.display.flip()

    if SAVE:
        out = os.path.join(tempfile.gettempdir(), f"inference_{INFER_ON}.png")
        pygame.image.save(screen, out)
        print(f"[저장] {out}")

    running = True
    started = pygame.time.get_ticks()
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
            clock.tick(30)  # 강의 코드에는 없다 — 없으면 빈 루프가 CPU 를 태운다(28)
            if MAX_SECONDS and pygame.time.get_ticks() - started > MAX_SECONDS * 1000:
                running = False
    finally:
        pygame.quit()
        print("종료")


if __name__ == "__main__":
    main()
