r"""74. AR 게임의 숫자 — 점수·유도·충돌을 돌려보기 전에 재 본다

36 강 과제(미사일 피하기). 게임은 카메라와 드론이 있어야 해 보지만,
**게임을 게임으로 만드는 부분은 전부 숫자**다. 이 파일은 카메라 없이 그 숫자만 검증한다.
실제 게임은 `75` 에 있다.

[1) 점수 = delta_tick 누적이 왜 성립하나]

    delta_tick = clock.tick(fps)   # 직전 tick 이후 실제로 흐른 ms 를 돌려준다
    elapsed_ms += delta_tick       # PLAY 상태에서만 누적 -> 그게 곧 점수

`clock.tick()` 은 **FPS 제한과 경과 시간 측정을 겸한다.** 125 ms 짜리 작업을 끼워 넣고
불러 보면 그대로 `125` 가 나온다 — 느린 PC 에서도 점수는 실시간(초)과 같다.
디스플레이를 안 열어도 동작하므로 이 파일에서 바로 확인할 수 있다.

[2) ⚠️ 점수는 실시간인데 물리는 상한이 걸려 있다]

원본은 `dt = min(delta_tick / 1000, MAX_DT)` 로 이동 계산용 `dt` 를 0.1 초에서 자른다
(한 프레임에 순간이동하는 것을 막는 흔한 처리다). 그런데 **점수는 자르지 않은 값**을 더한다.

    10 fps 미만에서 세계는 느려지는데 점수는 그대로 오른다 -> 느린 PC 가 유리하다

이 파일이 프레임레이트별로 그 어긋남을 표로 찍는다. 강의 안내가 "Intel Mac 은 느리다" 이므로
그냥 넘길 문제가 아니다. `75` 는 **점수도 같은 `dt` 로 누적**해 둘을 일치시켰다.

[3) "선회각 제한이 피할 수 있게 만드는 핵심" 인가 — 아니었다]

원본 설명은 미사일이 한 프레임에 돌 수 있는 각도를 `MISSILE_TURN_RATE`(100°/s)로 제한한 것이
회피를 가능하게 만든 장치라고 말한다. 직접 재 보면 **100°/s 는 무제한과 결과가 같다.**

    표적이 옆으로 v px/s 로 움직일 때 미사일의 최근접 거리(px), 미사일 90 px/s
        선회        40      80     120     160
        무제한     0.0     7.2    72.7    84.4
        100°/s     1.0     7.2    72.7    84.4
        30°/s     16.8    57.4    77.4    86.2

회피를 가르는 건 **속도비**다. 표적이 미사일(90 px/s)보다 빠르면 선회를 무제한으로 허용해도
빗나가고, 느리면 100°/s 로 제한해도 맞는다. 제한이 실제로 일하기 시작하는 건 30°/s 부근이다.

그래서 이 게임에는 **시간 상한**이 있다. 속도가 `90 + 4t` 로 올라 220 에서 멈추므로
`t = 32.5` 초부터는 미사일이 화면상 220 px/s — 카메라 앞 드론이 낼 수 없는 속도다.
그 뒤로는 실력이 아니라 **미사일이 수명(7초)으로 사라지기를 기다리는 게임**이 된다.

[4) 충돌 판정 — 원과 사각형]

    nx = clamp(cx, x, x + w);  ny = clamp(cy, y, y + h)      # 사각형 위 최근접점
    hit = (cx - nx)^2 + (cy - ny)^2 < r^2

이 한 줄이 맞는지 **사각형 전체를 격자로 훑어 구한 최소 거리**와 대조한다(아래 [4] 출력).
모서리 근처가 특히 틀리기 쉬운 자리다.
`HITBOX_SCALE = 0.7` 은 **면적으로는 49%** 다 — 박스에는 드론 주변 배경이 섞여 있기 때문에
줄이는 것이지만, 절반으로 줄인다는 사실은 알고 쓰는 편이 낫다(71 의 채움 비율 이야기와 같다).
"""

import math
import random
import time

import pygame

WIDTH, HEIGHT = 640, 480
MISSILE_RADIUS = 7
MISSILE_SPEED_START = 90.0
MISSILE_SPEED_MAX = 220.0
MISSILE_SPEED_UP = 4.0
MISSILE_LIFETIME = 7.0
HITBOX_SCALE = 0.7
MAX_DT = 0.1


# ---------------------------------------------------------------- 게임 규칙
def missile_speed(t):
    return min(MISSILE_SPEED_START + MISSILE_SPEED_UP * t, MISSILE_SPEED_MAX)


def turn_toward(angle, desired, max_turn):
    """가까운 쪽으로 돌되 한 번에 max_turn 까지만 — 유도 미사일의 전부"""
    diff = (desired - angle + math.pi) % (2 * math.pi) - math.pi  # -π ~ π 로 정리
    return angle + max(-max_turn, min(max_turn, diff))


def hitbox(box, scale=HITBOX_SCALE):
    """박스를 중심 기준으로 줄인다 (배경이 섞인 만큼 보정)"""
    x, y, w, h = box
    sw, sh = w * scale, h * scale
    return (x + (w - sw) / 2, y + (h - sh) / 2, sw, sh)


def circle_rect_hit(center, radius, rect):
    """사각형 위에서 원 중심과 가장 가까운 점까지의 거리로 판정"""
    x, y, w, h = rect
    nx = min(max(center[0], x), x + w)
    ny = min(max(center[1], y), y + h)
    return (center[0] - nx) ** 2 + (center[1] - ny) ** 2 < radius ** 2


# ---------------------------------------------------------------- 실험
def check_tick():
    print("[1] clock.tick() 은 실제 경과 ms 를 돌려준다 (창을 안 열어도 된다)")
    pygame.init()
    clock = pygame.time.Clock()
    for _ in range(3):
        clock.tick(30)
    print(f"    쉬면서 tick(30)      -> {clock.tick(30)} ms")
    deadline = time.perf_counter() + 0.125  # 125 ms 짜리 작업 흉내
    while time.perf_counter() < deadline:
        pass
    print(f"    125ms 작업 뒤 tick(30) -> {clock.tick(30)} ms   (FPS 제한이 아니라 실측값이다)")
    pygame.quit()


def check_dt_clamp():
    print("\n[2] ⚠️ 점수는 안 자르고 물리만 자른다 — 10 fps 밑에서 어긋난다")
    print("    fps   delta_tick   점수 가산   물리 dt   세계 진행")
    for fps in (30, 15, 10, 8, 5):
        delta = 1000 / fps
        dt = min(delta / 1000, MAX_DT)
        ratio = dt / (delta / 1000) * 100
        mark = "" if ratio > 99.9 else "   <- 느린 PC 가 유리"
        print(f"    {fps:3d}   {delta:7.1f}ms   {delta:7.1f}ms   {dt * 1000:6.1f}ms   {ratio:5.1f}%{mark}")


def closest_approach(turn_deg, target_speed, trigger=100.0, dt=1 / 240, life=MISSILE_LIFETIME):
    """미사일이 trigger px 안에 들어온 뒤에만 옆으로 피하는 '늦게 피하기' 시나리오"""
    max_rate = 1e9 if turn_deg is None else math.radians(turn_deg)
    mx, my = 0.0, 240.0  # 왼쪽 가장자리에서 출발
    tx, ty = 320.0, 240.0  # 표적은 화면 중앙
    angle = math.atan2(ty - my, tx - mx)
    best, t = 1e9, 0.0
    while t < life:
        if math.hypot(tx - mx, ty - my) < trigger:
            ty += target_speed * dt
        angle = turn_toward(angle, math.atan2(ty - my, tx - mx), max_rate * dt)
        mx += math.cos(angle) * MISSILE_SPEED_START * dt
        my += math.sin(angle) * MISSILE_SPEED_START * dt
        best = min(best, math.hypot(tx - mx, ty - my))
        t += dt
    return best


def check_turn_rate():
    print("\n[3] 선회각 제한이 정말 회피의 핵심인가 — 최근접 거리(px)")
    speeds = (40, 80, 120, 160)
    print("    표적 속도(px/s)" + "".join(f"{v:>9d}" for v in speeds))
    for turn in (None, 300, 200, 100, 60, 30):
        label = "무제한" if turn is None else f"{turn}°/s"
        row = "".join(f"{closest_approach(turn, v):9.1f}" for v in speeds)
        print(f"    {label:>12s}{row}")
    print(f"    (드론 히트박스 반지름은 대략 {60 * HITBOX_SCALE / 2:.0f} px — 그보다 크면 회피 성공)")
    print("    → 100°/s 는 무제한과 같다. 가르는 건 선회 제한이 아니라 **속도비**다.")
    limit = (MISSILE_SPEED_MAX - MISSILE_SPEED_START) / MISSILE_SPEED_UP
    print(f"    → 속도는 90 + 4t 로 올라 {MISSILE_SPEED_MAX:.0f} px/s 에서 멈춘다 "
          f"= {limit:.1f} 초부터는 속도로 못 피한다.")


def check_collision(trials=2_000, grid=200, seed=0):
    """공식 판정 vs 사각형을 격자로 훑어 구한 최소 거리 — 두 방법이 같은지 본다"""
    import numpy as np

    print("\n[4] 원-사각형 충돌 공식 검증 — 사각형을 격자로 훑은 결과와 대조")
    rng = random.Random(seed)
    x, y, w, h = rect = (200.0, 150.0, 120.0, 90.0)
    gx = np.linspace(x, x + w, grid)
    gy = np.linspace(y, y + h, grid)
    px, py = np.meshgrid(gx, gy)
    cell = max(w, h) / (grid - 1)  # 격자 간격 — 이보다 가까운 차이는 구분 못 한다
    mismatch = checked = 0
    for _ in range(trials):
        cx = rng.uniform(x - 40, x + w + 40)
        cy = rng.uniform(y - 40, y + h + 40)
        fast = circle_rect_hit((cx, cy), MISSILE_RADIUS, rect)
        slow_d = float(np.sqrt((px - cx) ** 2 + (py - cy) ** 2).min())
        if abs(slow_d - MISSILE_RADIUS) < cell:
            continue  # 격자 오차 안쪽이라 판정 불가 — 세지 않는다
        checked += 1
        if fast != (slow_d < MISSILE_RADIUS):
            mismatch += 1
    print(f"    무작위 {trials:,} 회 중 판정 가능한 {checked:,} 건에서 불일치 {mismatch} 건")
    print(f"    HITBOX_SCALE {HITBOX_SCALE} = 한 변 {HITBOX_SCALE * 100:.0f}% 지만 "
          f"**면적은 {HITBOX_SCALE ** 2 * 100:.0f}%** — 절반으로 줄여 판정한다는 뜻")
    print(f"    60x60 박스 -> 판정 박스 {hitbox((0, 0, 60, 60))}")


def main():
    check_tick()
    check_dt_clamp()
    check_turn_rate()
    check_collision()
    print("\n[5] 정리")
    print("    - 점수는 clock.tick 누적으로 충분하다. 단 물리 dt 와 같은 값을 써야 한다.")
    print("    - 난이도를 만드는 건 미사일 속도이지 선회각 제한이 아니다.")
    print("    - 32.5 초를 넘기면 속도로는 못 피한다 — 수명 7초를 버티는 게임이 된다.")


if __name__ == "__main__":
    main()
