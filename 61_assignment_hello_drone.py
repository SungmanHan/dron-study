r"""61. [과제] Hello Drone — 카메라 영상 위에 메시지 띄우기 📷

28 강 과제. 웹캠 영상을 Pygame 창에 실시간으로 띄우고 "Hello Drone" 을 얹는다.
종료는 창 닫기(X) 또는 ESC.

    SOURCE = 0        카메라 (제출용)
    SOURCE = "demo"   합성 영상 — 카메라 없이 화면 구성만 볼 때

[과제 코드에서 고친 것]

1. **카메라 열기에 실패하면 창이 남는다.** 원본은 `pygame.init()` 으로 창을 띄운 뒤
   `cap.isOpened()` 가 거짓이면 `sys.exit()` 만 부른다. `pygame.quit()` 이 없어서
   macOS 에서는 응답 없는 창이 떠 있게 된다 → 먼저 닫고 끝낸다.
2. **정리 코드가 정상 종료 경로에만 있다.** 중간에 예외가 나면 `cap.release()` 가
   실행되지 않아 **카메라 LED 가 켜진 채 남는다** → `try/finally`.
3. **`make_surface` + `swapaxes` 대신 `image.frombuffer`.** 같은 결과인데 훨씬 싸다
   (측정값은 60 참고). 남는 시간은 인식 처리에 쓰는 편이 낫다.
4. 거울 모드(`MIRROR`)와 FPS 표시를 넣었다. 영상이 거울이 아니면 손을 오른쪽으로 옮길 때
   화면에서는 왼쪽으로 간다(24 강에서 roll 부호가 뒤집히던 그 문제).
5. `font.render` 를 매 프레임 새로 만들 필요는 없다 — 고정 문구는 루프 밖에서 한 번만
   만들어 두고 `blit` 만 한다(이 파일은 고정 문구 하나를 그렇게 처리했다).

[한글은 기본 폰트로 안 나온다]
`pygame.font.SysFont(None, 48)` 의 기본 폰트에는 한글 글리프가 없어서 네모로 나온다.
한글을 띄우려면 시스템 폰트 이름을 직접 준다 — macOS 는 `"applegothic"`,
없으면 `pygame.font.match_font("applegothic")` 로 확인한 뒤 `pygame.font.Font(경로, 크기)`.
`MESSAGE` 를 한글로 바꾸고 싶으면 `FONT_NAME` 도 함께 바꾼다.
"""

import cv2 as cv
import numpy as np
import pygame

SOURCE = 0  # 0 (카메라) / "demo" (합성 영상)
WIDTH, HEIGHT = 640, 480
FPS = 30
MIRROR = True
MESSAGE = "Hello Drone"
FONT_NAME = None  # None = 기본 폰트(영문만). 한글은 "applegothic" 등
MAX_SECONDS = 0  # 0 = 무제한


def demo_frames():
    """카메라 없이 화면 구성을 볼 때 쓰는 영상."""
    i = 0
    while True:
        frame = np.full((HEIGHT, WIDTH, 3), 50, np.uint8)
        x = int(WIDTH / 2 + 200 * np.sin(i / 25.0))
        cv.circle(frame, (x, 320), 70, (180, 120, 40), -1)
        i += 1
        yield True, frame


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption("Hello Drone - OpenCV + Pygame")
    font = pygame.font.SysFont(FONT_NAME, 48)
    small = pygame.font.SysFont(FONT_NAME, 22)
    clock = pygame.time.Clock()

    # 고정 문구는 한 번만 만들어 두고 매 프레임 blit 만 한다
    message = font.render(MESSAGE, True, (255, 255, 0))
    message_rect = message.get_rect(center=(WIDTH // 2, 40))

    frames = demo_frames() if SOURCE == "demo" else None
    cap = None if frames else cv.VideoCapture(SOURCE)
    if cap is not None:
        cap.set(cv.CAP_PROP_FRAME_WIDTH, WIDTH)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        if not cap.isOpened():
            pygame.quit()  # 창부터 닫는다 — 안 그러면 응답 없는 창이 남는다
            raise SystemExit("카메라를 열지 못했습니다. (시스템 환경설정 > 보안 > 카메라 권한)")

    running = True
    count = 0
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
                frame = cv.resize(frame, (WIDTH, HEIGHT))
            if MIRROR:
                frame = cv.flip(frame, 1)

            rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)  # OpenCV BGR -> Pygame RGB
            surface = pygame.image.frombuffer(rgb.tobytes(), (WIDTH, HEIGHT), "RGB")
            screen.blit(surface, (0, 0))  # 영상 먼저
            screen.blit(message, message_rect)  # 그 위에 메시지
            screen.blit(small.render(f"{clock.get_fps():4.1f} fps   ESC to exit",
                                     True, (255, 255, 255)), (10, HEIGHT - 26))

            pygame.display.flip()
            clock.tick(FPS)
            count += 1
            if MAX_SECONDS and pygame.time.get_ticks() - started > MAX_SECONDS * 1000:
                running = False
    finally:
        # 어떤 경로로 끝나든 카메라와 창을 확실히 해제한다
        if cap is not None:
            cap.release()
        pygame.quit()
        print(f"{count} 프레임 출력 후 종료")


if __name__ == "__main__":
    main()
