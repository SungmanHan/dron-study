r"""59. Pygame 기본 창 — 렌더링 루프와 더블 버퍼링

28 강 예제1. 카메라도 드론도 쓰지 않는다. 창 하나를 띄우고 도형과 글자를 그린다.

    pip install pygame        # venv 안에서

[역할 나누기]
    OpenCV  입력 — 카메라 제어, 영상 분석
    Pygame  출력 — 그리기, 키·마우스 이벤트
영상 위에 도형·글자를 얹으면 그게 곧 간단한 AR 화면이다(60·61).

[렌더링 루프는 네 줄이다]
    1) 이벤트 처리   pygame.event.get()
    2) 뒤 버퍼에 그리기  fill / draw / blit
    3) 화면 교체     pygame.display.flip()
    4) 속도 제한     clock.tick(30)

**더블 버퍼링** — 보이는 버퍼(front)와 그리는 버퍼(back)를 따로 둔다. 뒤에서 한 장을 다 그린 뒤
`flip()` 으로 통째로 바꾸므로 그리는 중간 과정이 보이지 않는다(깜빡임·찢어짐 없음).
일부만 바뀌면 `display.update(rect)` 가 싸지만, 카메라 영상처럼 전체가 바뀌면 `flip()` 이 맞다.

[Surface 가 전부다]
`set_mode()` 가 돌려주는 화면도 Surface, 글자(`font.render`)도 Surface, 카메라 프레임도 Surface 다.
`blit(무엇을, 어디에)` 로 붙인다. **나중에 그린 것이 위에 온다** — 영상 위에 도형을 얹으려면
영상을 먼저 `blit` 하고 도형을 나중에 그린다.

[강의 코드에서 고친 것]
1. **`import sys` 가 빠진 채 `exit()` 를 부른다.** `exit()` 는 대화형 셸용 헬퍼라
   스크립트·주피터에서는 동작이 불안정하다 → `sys.exit()`.
2. **`clock` 을 만들어 놓고 `tick()` 을 안 부른다.** 그러면 루프가 최대 속도로 돈다.
   headless 로 재 보니 **tick 없이 1 초에 8,884 회, `tick(30)` 이면 29 회** — 300 배 차이다.
   보이는 결과는 같은데 CPU 만 태운다.
3. 순서가 "그리기 → flip → 이벤트" 인데, 보통은 **이벤트 → 그리기 → flip → tick** 으로 쓴다.
   결과는 같지만 이벤트를 먼저 받아야 그 프레임에 바로 반영된다.
4. 종료 경로가 `pygame.quit()` + `sys.exit()` 두 곳에 흩어져 있다 → `running` 플래그 하나로.
   **주피터에서는 `pygame.quit()` 을 안 부르면 창이 남은 채 멈춘다.**

[이벤트를 안 꺼내면 창이 멈춘다]
`pygame.event.get()` 은 "창 닫기 눌렸나" 를 확인하는 일만 하는 게 아니라, OS 의 이벤트 큐를
비워 주는 역할도 한다. 루프에서 이걸 빼면 macOS 는 창을 **응답 없음**으로 판단한다.
23 강의 `cv.waitKey()` 가 창을 그려 주던 것과 같은 자리다.
"""

import sys

import pygame

WIDTH, HEIGHT = 640, 480
FPS = 30
MAX_SECONDS = 0  # 0 = 무제한. 숫자를 주면 그 시간 뒤 자동 종료 (창 없이 동작 확인용)


def main():
    pygame.init()
    # DOUBLEBUF 는 기본 동작이지만 의도를 드러내려고 명시한다
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption("59 pygame window")
    font = pygame.font.SysFont(None, 24)  # None = 기본 폰트. 한글은 안 나온다
    clock = pygame.time.Clock()

    running = True
    frames = 0
    started = pygame.time.get_ticks()
    try:
        while running:
            # 1) 이벤트 — 이걸 안 꺼내면 창이 '응답 없음' 이 된다
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # 창 닫기(X)
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            # 2) 뒤 버퍼에 그리기 — 안 지우면 이전 프레임이 남는다
            screen.fill((0, 0, 0))
            # rect(대상, 색, (x, y, 너비, 높이), 두께) — 두께 0 이면 속을 채운다
            pygame.draw.rect(screen, (0, 255, 0), (100, 100, 200, 150), 2)
            pygame.draw.circle(screen, (255, 80, 80), (450, 300), 60, 0)

            text = font.render("Press ESC to exit", True, (255, 255, 255))
            screen.blit(text, (10, 10))  # 나중에 그린 것이 위에 온다
            fps_text = font.render(f"{clock.get_fps():5.1f} fps", True, (200, 200, 0))
            screen.blit(fps_text, (10, HEIGHT - 24))

            # 3) 앞뒤 버퍼 교체 — 여기서 비로소 화면에 나타난다
            pygame.display.flip()

            # 4) 속도 제한 — 없으면 같은 그림을 초당 수천 번 그린다
            clock.tick(FPS)
            frames += 1
            if MAX_SECONDS and pygame.time.get_ticks() - started > MAX_SECONDS * 1000:
                running = False
    finally:
        # 이걸 안 부르면(특히 주피터) 창이 남은 채 멈춘다
        pygame.quit()
        print(f"{frames} 프레임 그리고 종료")


if __name__ == "__main__":
    main()
    sys.exit()
