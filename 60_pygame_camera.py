r"""60. 카메라 영상을 Pygame 창에 — 그 위에 덧그리면 AR 📷

28 강 예제2. OpenCV 로 읽고 Pygame 으로 그린다.

    SOURCE = 0        카메라
    SOURCE = "demo"   움직이는 합성 영상 — **카메라 없이 확인용** (기본값)
    SOURCE = "경로"   동영상 파일

[핵심 흐름]
    cap.read()  ->  BGR to RGB  ->  Surface  ->  blit  ->  도형·글자 덧그리기  ->  flip

OpenCV 는 BGR, Pygame 은 RGB 다(22 강의 그 이야기). 색을 바꾸지 않으면 파랑과 빨강이 뒤집힌다.

[축을 맞춰야 한다 — `swapaxes(0, 1)`]
OpenCV 프레임은 `(높이, 너비, 3)` = `[y][x]` 인데 `pygame.surfarray` 는 `(너비, 높이, 3)` = `[x][y]` 로 읽는다.
그냥 넣으면 **전치된다.** 가로로 긴 띠를 그려 넣고 확인해 보면:

    swapaxes 없이     Surface 크기 (480, 640)   가로 띠가 세로로 선다
    swapaxes(0, 1)    Surface 크기 (640, 480)   제대로 나온다

[더 빠른 길 — `pygame.image.frombuffer`]
전치는 공짜가 아니다. 640x480 프레임 200 장으로 재 본 값:

    make_surface + swapaxes   4.72 ms/프레임   (초당 212 장이 한계)
    image.frombuffer          0.12 ms/프레임   (초당 8,177 장)

**약 39 배** 차이다. `frombuffer` 는 메모리 배치가 이미 맞으므로 전치 없이 그대로 읽는다.
위 값은 변환 함수만 잰 것이고, 이 파일이 찍는 값은 **BGR→RGB 까지 포함**해서
`frombuffer` 0.6 ms / `make_surface` 4.0 ms 였다(합성 영상, 640x480).
30 fps 라면 한 프레임에 33 ms 가 있으니 강의 방식으로도 충분하지만, 얼굴 인식(48)이나
색 추적(50) 같은 처리를 함께 돌리면 이 4.7 ms 가 아깝다.
`SURFACE_MODE` 로 두 방식을 바꿔 가며 실제 시간을 찍어 준다.

[영상 위에 그리는 것이 AR 이다]
`blit` 으로 영상을 깔고 **그다음에** 도형·글자를 그린다(나중에 그린 것이 위에 온다).
강의가 `screen.fill()` 을 주석 처리한 것도 영상이 화면 전체를 덮기 때문이다 —
영상이 창보다 작으면 지우지 않은 자리에 이전 프레임이 남는다.

[정리하지 않으면]
`break` 로 루프를 빠져나온 뒤 `cap.release()` 를 안 하면 **카메라 LED 가 켜진 채 남는다.**
강의 예제2 는 종료 경로가 세 군데(QUIT / ESC / break)라 빠뜨리기 쉽다 → `try/finally` 한 곳으로 모았다.
"""

import time

import cv2 as cv
import numpy as np
import pygame

SOURCE = "demo"  # 0 (카메라) / "demo" / "파일경로"
SURFACE_MODE = "frombuffer"  # "frombuffer" (빠름) / "make_surface" (강의 방식)
WIDTH, HEIGHT = 640, 480
FPS = 30
MIRROR = True  # 거울 모드 — 내 오른쪽이 화면 오른쪽
MAX_SECONDS = 0  # 0 = 무제한. 숫자를 주면 그 시간 뒤 자동 종료


def demo_frames():
    """카메라 대신 쓸 영상 — 공이 좌우로 움직인다."""
    i = 0
    while True:
        frame = np.full((HEIGHT, WIDTH, 3), 60, np.uint8)
        x = int(WIDTH / 2 + (WIDTH / 2 - 80) * np.sin(i / 20.0))
        cv.circle(frame, (x, HEIGHT // 2), 60, (0, 200, 255), -1)
        cv.putText(frame, f"demo {i}", (10, HEIGHT - 20), cv.FONT_HERSHEY_SIMPLEX,
                   0.7, (255, 255, 255), 2)
        i += 1
        yield True, frame


def to_surface(frame_bgr):
    """OpenCV 프레임(BGR) → Pygame Surface. 걸린 시간(ms)도 같이 돌려준다."""
    started = time.perf_counter()
    rgb = cv.cvtColor(frame_bgr, cv.COLOR_BGR2RGB)  # 색 순서 맞추기
    if SURFACE_MODE == "make_surface":
        surface = pygame.surfarray.make_surface(rgb.swapaxes(0, 1))  # 축 맞추기
    else:
        surface = pygame.image.frombuffer(rgb.tobytes(), (rgb.shape[1], rgb.shape[0]), "RGB")
    return surface, (time.perf_counter() - started) * 1000


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption("60 OpenCV + Pygame")
    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()

    frames = demo_frames() if SOURCE == "demo" else None
    cap = None if frames else cv.VideoCapture(SOURCE)
    if cap is not None:
        cap.set(cv.CAP_PROP_FRAME_WIDTH, WIDTH)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        if not cap.isOpened():
            pygame.quit()  # 창부터 닫고 끝낸다 — 강의 코드는 창을 남긴 채 sys.exit() 한다
            raise SystemExit("카메라를 열지 못했습니다. (시스템 환경설정 > 보안 > 카메라 권한)")

    running = True
    count = 0
    convert_ms = 0.0
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
                frame = cv.resize(frame, (WIDTH, HEIGHT))  # 카메라가 1280x720 을 줄 수도 있다
            if MIRROR:
                frame = cv.flip(frame, 1)

            surface, ms = to_surface(frame)
            convert_ms += ms
            count += 1
            screen.blit(surface, (0, 0))  # 영상 먼저

            # 그다음에 덧그린다 = AR
            pygame.draw.rect(screen, (0, 255, 0), (100, 100, 200, 150), 2)
            screen.blit(font.render("Press ESC to exit", True, (255, 255, 255)), (10, 10))
            info = f"{SURFACE_MODE}  {ms:.2f} ms  |  {clock.get_fps():4.1f} fps"
            screen.blit(font.render(info, True, (255, 255, 0)), (10, 34))

            pygame.display.flip()
            clock.tick(FPS)
            if MAX_SECONDS and pygame.time.get_ticks() - started > MAX_SECONDS * 1000:
                running = False
    finally:
        # 종료 경로가 몇 개든 여기로 모인다
        if cap is not None:
            cap.release()
        pygame.quit()
        if count:
            print(f"{count} 프레임 / 변환 평균 {convert_ms / count:.2f} ms ({SURFACE_MODE})")


if __name__ == "__main__":
    main()
