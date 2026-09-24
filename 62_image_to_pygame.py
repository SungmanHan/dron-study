r"""62. 이미지를 Pygame 창에 — 비율 유지해서 창에 맞추기

29 강 예제. 드론도 카메라도 쓰지 않는다. `IMAGE_PATH` 를 비우면 샘플을 그려서 쓴다.

28 강은 카메라 프레임을 그대로 창 크기로 늘렸다. 이번에는 **사진 한 장을 비율을 지키며** 넣는다.
다음 강의에서 YOLO 결과 이미지(`results[0].plot()`)를 이 자리에 넣을 것이므로, 그 준비 단계다.

[레터박스 — 두 비율 중 작은 쪽]
    ratio_w = 창너비 / 원본너비
    ratio_h = 창높이 / 원본높이
    scale   = min(ratio_w, ratio_h)      # 큰 쪽을 쓰면 잘린다

810x1080 사진을 640x480 창에 넣으면 `min(0.790, 0.444) = 0.444` → **360x480**.
남는 좌우 140 픽셀씩이 검은 여백이다. 강의 코드는 `(0, 0)` 에 붙여서 여백이 **오른쪽에 몰리는데**,
`((창너비 − 새너비) // 2, (창높이 − 새높이) // 2)` 로 붙이면 가운데에 온다.

[축 순서가 라이브러리마다 다르다 — 이미지가 눕는 원인의 90%]

    frame.shape      (높이, 너비, 채널)     numpy
    cv.resize(…, (w, h))  (너비, 높이)      OpenCV 함수 인자
    surfarray        (너비, 높이, 채널)      pygame

그래서 `cv.resize` 에 넘길 때는 `(new_w, new_h)`, `make_surface` 에 넘길 때는 `swapaxes(0, 1)` 이다.
`pygame.image.frombuffer(bytes, (w, h), "RGB")` 를 쓰면 전치가 필요 없고 훨씬 싸다(28 에서 잰 값: 39 배).

[축소에는 INTER_AREA]
`cv.resize` 의 기본 보간은 `INTER_LINEAR` 다. **줄일 때는 `INTER_AREA`** 가 깨끗하다
(주변 픽셀을 평균 내서 줄인다). 키울 때는 `INTER_LINEAR`/`INTER_CUBIC`.

[정지 이미지는 루프 밖에서 한 번만 그린다]
사진은 변하지 않으므로 `blit` + `flip` 을 루프 안에서 반복할 이유가 없다.
루프는 이벤트만 받으면 된다 — 대신 `clock.tick()` 은 넣어야 한다(28: 없으면 초당 수천 번 돈다).
영상으로 넘어가면 읽기~blit~flip 이 전부 루프 안으로 들어간다(60).

[강의 코드에서 손본 것]
- `clock` 을 만들어 두고 `tick()` 을 부르지 않는다 → 빈 루프가 CPU 를 태운다.
- 이미지를 `(0, 0)` 에 붙여 여백이 한쪽으로 몰린다 → 가운데 정렬.
- `sys.exit(1)` 로 끝내면 주피터에서 커널 종료 경고가 뜬다 → 스크립트로 실행하고 `SystemExit` 메시지로.
- `checks()` 는 ultralytics 설치 점검용이라 이 파일에는 필요 없다(63 으로 옮겼다).
"""

import os
import tempfile

import cv2 as cv
import numpy as np
import pygame

IMAGE_PATH = ""  # 비우면 샘플 이미지를 그려서 쓴다
WIDTH, HEIGHT = 640, 480
CENTER = True  # False 면 강의처럼 (0, 0) 에 붙인다
SURFACE_MODE = "frombuffer"  # "frombuffer" (빠름) / "make_surface" (강의 방식)
MAX_SECONDS = 0  # 0 = 무제한. 숫자를 주면 그 시간 뒤 자동 종료


def make_sample_image(w=810, h=1080):
    """세로로 긴 사진 한 장 (강의의 bus.jpg 와 비슷한 비율)."""
    img = np.full((h, w, 3), 235, np.uint8)
    cv.rectangle(img, (60, 120), (w - 60, h - 200), (170, 120, 60), cv.FILLED)
    cv.rectangle(img, (120, 220), (w - 120, 520), (230, 220, 200), cv.FILLED)
    for i in range(3):
        cv.circle(img, (160 + i * 240, h - 150), 70, (60, 60, 60), cv.FILLED)
    cv.putText(img, "SAMPLE", (110, h - 380), cv.FONT_HERSHEY_SIMPLEX, 2.4, (40, 40, 40), 6)
    path = os.path.join(tempfile.gettempdir(), "sample_photo.jpg")
    cv.imwrite(path, img)
    return path


def letterbox(frame, target_w, target_h):
    """비율을 유지한 채 창 안에 전부 들어가게 줄인다. (줄인 이미지, 붙일 좌표)"""
    orig_h, orig_w = frame.shape[:2]  # shape 는 (높이, 너비) 순서
    scale = min(target_w / orig_w, target_h / orig_h)  # 작은 쪽을 써야 잘리지 않는다
    new_w, new_h = int(orig_w * scale), int(orig_h * scale)
    # resize 의 크기 인자는 (너비, 높이). 줄일 때는 INTER_AREA
    resized = cv.resize(frame, (new_w, new_h), interpolation=cv.INTER_AREA)
    if CENTER:
        offset = ((target_w - new_w) // 2, (target_h - new_h) // 2)
    else:
        offset = (0, 0)
    print(f"  {orig_w}x{orig_h} -> {new_w}x{new_h}  (배율 {scale:.3f})  붙일 좌표 {offset}")
    return resized, offset


def to_surface(frame_bgr):
    """OpenCV BGR 배열 → Pygame Surface."""
    rgb = cv.cvtColor(frame_bgr, cv.COLOR_BGR2RGB)  # 안 하면 빨강·파랑이 뒤바뀐다
    if SURFACE_MODE == "make_surface":
        return pygame.surfarray.make_surface(rgb.swapaxes(0, 1))  # (h,w,3) -> (w,h,3)
    return pygame.image.frombuffer(rgb.tobytes(), (rgb.shape[1], rgb.shape[0]), "RGB")


def main():
    path = IMAGE_PATH or make_sample_image()
    frame = cv.imread(path)
    if frame is None:  # imread 는 실패해도 예외 없이 None 을 돌려준다(40)
        raise SystemExit(f"이미지를 읽지 못했습니다: {path}")
    print(f"[이미지] {path}  shape {frame.shape}")

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption("62 image to pygame")
    clock = pygame.time.Clock()

    resized, offset = letterbox(frame, WIDTH, HEIGHT)
    surface = to_surface(resized)

    # 정지 이미지라 한 번만 그린다. 루프는 이벤트만 받는다
    screen.fill((0, 0, 0))  # 여백을 검게 (지우지 않으면 쓰레기 픽셀이 남을 수 있다)
    screen.blit(surface, offset)
    pygame.display.flip()

    running = True
    started = pygame.time.get_ticks()
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
            clock.tick(30)  # 없으면 빈 루프가 CPU 를 100% 쓴다(28에서 측정: 초당 8,884회)
            if MAX_SECONDS and pygame.time.get_ticks() - started > MAX_SECONDS * 1000:
                running = False
    finally:
        pygame.quit()
        print("종료")


if __name__ == "__main__":
    main()
