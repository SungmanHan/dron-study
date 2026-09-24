r"""69. 마스크를 화면에 덮기 — 분할 결과를 눈에 보이게 하는 법

33 강의 절반은 이 처리다. 모델도 카메라도 없이, **bool 마스크 한 장을 반투명하게 얹는** 연습.

[분할 결과는 박스가 아니라 마스크다]
탐지(30~32 강)는 `(x1, y1, x2, y2)` 네 숫자였다. 분할은 **픽셀마다 참/거짓**인 배열
(`H x W` bool)이 나온다. 그래서 그리는 법도 다르다 — 사각형을 그리는 게 아니라
참인 자리만 색칠한 반투명 판을 만들어 영상 위에 덮는다.

[방법 1 — 강의 방식: 픽셀 배열을 직접 건드린다]
    surf = pygame.Surface((W, H), pygame.SRCALPHA)   # 알파를 쓰려면 SRCALPHA
    rgb   = pygame.surfarray.pixels3d(surf)          # (W, H, 3)  ← 여기서 surface 가 **잠긴다**
    alpha = pygame.surfarray.pixels_alpha(surf)      # (W, H)
    rgb[m] = (0, 255, 0)
    alpha[m] = 128
    del rgb, alpha                                    # 참조를 지워야 잠금이 풀린다
    screen.blit(surf, (0, 0))

**`del` 을 빼먹으면 blit 에서 터진다.** 직접 해 보면 이렇게 나온다:

    pygame.error: pygame_Blit: Surfaces must not be locked during blit

`surf.get_locked()` 가 `True` → `del` 후 `False` 가 되는 것도 아래에서 확인한다.

[방법 2 — RGBA 배열을 만들어 한 번에 넘긴다]
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[mask] = (0, 255, 0, 128)
    surf = pygame.image.frombuffer(rgba.tobytes(), (W, H), "RGBA")

잠금이 아예 없고 결과도 같다. 640x480 마스크로 200 번씩 재 보면
**픽셀 직접 접근 5.65 ms / RGBA frombuffer 4.67 ms** — 크게 빠르진 않지만 함정이 없다.

[축이 또 바뀐다]
numpy 마스크는 `(높이, 너비)` = `[y][x]`, `surfarray` 는 `(너비, 높이)` = `[x][y]` 다.
영상과 마찬가지로 **마스크도 `swapaxes(0, 1)`** 해야 자리가 맞는다(62 의 그 이야기).
RGBA 방식은 `frombuffer` 가 알아서 읽으므로 전치가 필요 없다.

[알파 값이 그대로 섞인다]
검은 화면 위에 초록(0,255,0)을 알파 128 로 얹으면 `(0, 128, 0)` 이 된다 — 255 x 128/255.
66 의 블라인드에서 흰 배경 위 알파 180 이 75 가 되던 것과 같은 계산이다.
"""

import os
import tempfile

import numpy as np
import pygame

WIDTH, HEIGHT = 640, 480
COLOR = (0, 255, 0)
ALPHA = 128
SAVE = True


def make_mask():
    """가운데에 원, 오른쪽 아래에 사각형이 있는 bool 마스크 (분할 결과인 셈)."""
    yy, xx = np.mgrid[0:HEIGHT, 0:WIDTH]
    circle = (xx - 240) ** 2 + (yy - 200) ** 2 < 120 ** 2
    rect = (xx > 400) & (xx < 580) & (yy > 300) & (yy < 430)
    return circle | rect


def overlay_pixels(mask):
    """강의 방식 — pixels3d / pixels_alpha 로 직접 칠하고 del 로 잠금을 푼다."""
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))  # 완전 투명
    swapped = mask.swapaxes(0, 1)  # (y, x) -> (x, y)
    rgb = pygame.surfarray.pixels3d(surf)
    alpha = pygame.surfarray.pixels_alpha(surf)
    rgb[swapped] = COLOR
    alpha[swapped] = ALPHA
    locked = surf.get_locked()
    del rgb, alpha  # 이 줄이 없으면 blit 에서 에러가 난다
    return surf, locked


def overlay_rgba(mask):
    """RGBA 배열을 만들어 한 번에 Surface 로. 잠금이 없다."""
    rgba = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
    rgba[mask] = (*COLOR, ALPHA)
    return pygame.image.frombuffer(rgba.tobytes(), (WIDTH, HEIGHT), "RGBA")


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    mask = make_mask()
    area = int(mask.sum())
    print(f"[마스크] shape {mask.shape} (높이, 너비)  True {area:,}픽셀 "
          f"({area / mask.size * 100:.1f}%)")

    # 1) 잠금 확인 — del 전에는 blit 이 안 된다
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    rgb = pygame.surfarray.pixels3d(surf)
    print(f"\n[잠금] pixels3d 를 잡은 뒤 get_locked() = {surf.get_locked()}")
    try:
        screen.blit(surf, (0, 0))
        print("  blit 성공 (예상과 다름)")
    except pygame.error as exc:
        print(f"  blit 실패 -> {exc}")
    del rgb
    print(f"  del 후 get_locked() = {surf.get_locked()}  -> 이제 blit 가능")

    # 2) 두 방법의 결과 비교
    print("\n[두 방법]")
    for name, surface in (("pixels3d+alpha", overlay_pixels(mask)[0]),
                          ("RGBA frombuffer", overlay_rgba(mask))):
        screen.fill((0, 0, 0))  # 검은 배경 위에 얹어 본다
        screen.blit(surface, (0, 0))
        inside = tuple(int(v) for v in screen.get_at((240, 200))[:3])
        outside = tuple(int(v) for v in screen.get_at((20, 20))[:3])
        print(f"  {name:16s} 마스크 안 {inside}  밖 {outside}")
    print(f"  → 알파 {ALPHA} 면 검은 배경 위에서 255 x {ALPHA}/255 = {255 * ALPHA // 255} 가 된다")

    # 3) 축을 안 바꾸면 어떻게 되나
    print("\n[축을 안 바꾸면]")
    wrong = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    rgb = pygame.surfarray.pixels3d(wrong)
    try:
        rgb[mask] = COLOR  # (y, x) 마스크를 (x, y) 배열에 그대로 쓴다
        print("  통과했지만 자리가 뒤집힌다")
    except (IndexError, ValueError) as exc:
        print(f"  {type(exc).__name__}: {exc}")
    del rgb

    if SAVE:
        screen.fill((40, 40, 40))
        screen.blit(overlay_rgba(mask), (0, 0))
        path = os.path.join(tempfile.gettempdir(), "mask_overlay.png")
        pygame.image.save(screen, path)
        print(f"\n[저장] {path}")
    pygame.quit()


if __name__ == "__main__":
    main()
