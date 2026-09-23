r"""55. 군집 패턴 — 이륙 · 웨이브 · 확장/축소 · 사각 회전 ⚠️ 실제로 이륙한다

25 강 4 장(군집 제어 패턴). 드론쇼에서 보는 움직임들을 **지금까지 쓴 명령만으로** 만든다.
새 함수는 없다. 달라지는 건 "드론마다 어떤 값을 주느냐" 뿐이다.

    PATTERN = "takeoff_seq"   순차 이륙 — sendTakeOff() 사이에 sleep 을 넣는다
    PATTERN = "symmetric"     대칭 이륙 — 이륙 후 드론마다 z 를 다르게 (V자 / ∧자)
    PATTERN = "wave"          웨이브   — z 를 조금씩 다르게 올렸다 내린다
    PATTERN = "swarm_move"    군집 이동 — 전원에게 같은 (x, y)
    PATTERN = "expand"        확장     — 각자 바깥쪽으로
    PATTERN = "contract"      축소     — 각자 안쪽으로
    PATTERN = "square"        사각 회전 — 네 대가 다음 꼭짓점으로 한 칸씩

[대형 좌표를 먼저 적어 둔다]
드론 좌표계는 **x 앞(+), y 왼쪽(+), z 위(+)** 다. 사각 대형을 이렇게 놓았다고 본다
(간격 `GAP` = 2 m. 사람이 서 있는 쪽에서 본 그림).

        (앞)
    d3 ····· d2         d1 = (0,   0  )   뒤·오른쪽
     :        :         d2 = (GAP, 0  )   앞·오른쪽
     :        :         d3 = (GAP, GAP)   앞·왼쪽
    d4 ····· d1         d4 = (0,   GAP)   뒤·왼쪽
        (뒤)

확장/축소와 사각 회전은 이 표에서 **계산으로 나온다.**

- **확장** : 대형 중심에서 자기 자리로 향하는 방향으로 간다.
  d1 은 중심의 뒤·오른쪽이니 `(-, -)`, d3 은 앞·왼쪽이니 `(+, +)`.
- **사각 회전** : 각자 "다음 꼭짓점 좌표 − 지금 좌표". 반시계로 한 칸 돌면
  d1 은 앞으로, d2 는 왼쪽으로, d3 은 뒤로, d4 는 오른쪽으로 `GAP` 만큼 간다.

[동시에 움직여야 안 부딪힌다]
사각 회전처럼 서로 자리를 바꾸는 패턴은 **네 대가 같이 움직여야** 경로가 겹치지 않는다.
그래서 블로킹인 `sendControlWhile` 이 아니라 논블로킹 `sendControlPosition` 을 연달아 보내고
`sleep` 으로 기다린다(53·54 와 같은 이유).

[이 파일은 항상 제자리로 돌아온다]
패턴을 한 번 수행한 뒤 **부호를 뒤집어 원위치**시킨다(`RETURN = True`).
위치 명령은 절대 좌표가 아니라 "지금 위치에서 얼마" 라서, 돌아오지 않으면 대형이 계속 밀린다.
옵티컬센서는 바닥 무늬를 보고 이동량을 재므로 **무늬 없는 바닥·반사·어두운 곳에서는 위치가 흐른다.**
몇 번 반복하면 오차가 쌓인다는 뜻이다. 넓게 잡고, 이상하면 바로 착륙시킨다.

⚠️ 간격 2 m 이상, 천장 높이 확인, 배터리 전량 확인. `DRY_RUN = True` 로 먼저 순서를 본다.
"""

from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import DeviceType, LightFlagsDrone

from drone_util import find_ports

DRY_RUN = True  # True = 드론 없이 순서만 확인. 확인 뒤 False
PATTERN = "wave"  # 위 목록 중 하나
PORTS = []  # 적어 둔 순서가 drone1~4 다. 비우면 자동 탐색
DRONE_COUNT = 4
LED_CHECK = True
RETURN = True  # 패턴 뒤 원위치

GAP = 2.0  # 대형 간격 (m). 2 m 아래로는 프로펠러 바람이 서로를 흔든다
STEP_M = 0.6  # 이동 패턴의 기본 거리 (m)
SPEED = 0.5  # 위치 명령 속도 (m/s). 권장 0.5~2.0
SEQ_GAP = 1.0  # 순차 이륙 간격 (초)

# 사각 대형에서의 자리 (x 앞+, y 왼쪽+)
FORMATION = [(0.0, 0.0), (GAP, 0.0), (GAP, GAP), (0.0, GAP)]


class FakeDrone:
    def __init__(self, name):
        self.name = name

    def open(self, port=None):
        print(f"  [DRY] {self.name} open {port}")
        return True

    def sendTakeOff(self):
        print(f"  [DRY] {self.name} takeOff")

    def sendLanding(self):
        print(f"  [DRY] {self.name} landing")

    def sendControlPosition(self, x, y, z, velocity, heading, rotational):
        print(f"  [DRY] {self.name} position(x={x:+.1f}, y={y:+.1f}, z={z:+.1f})")

    def sendLightManual(self, device, flags, brightness):
        print(f"  [DRY] {self.name} light(flags=0x{flags:02X}, brightness={brightness})")

    def close(self):
        print(f"  [DRY] {self.name} close")


def connect_all():
    if DRY_RUN:
        return [FakeDrone(f"drone{i}") for i in range(1, DRONE_COUNT + 1)]

    ports = PORTS or find_ports(DRONE_COUNT)
    drones = []
    for i, port in enumerate(ports[:DRONE_COUNT], start=1):
        drone = Drone()
        if not drone.open(port):
            for opened in drones:
                opened.close()
            raise SystemExit(f"drone{i} 연결 실패: {port}")
        print(f"  drone{i} <- {port}")
        drones.append(drone)
    return drones


def led(drones, on=False, brightness=100):
    flags = LightFlagsDrone.BodyBlue.value if on else 0xFF
    for drone in drones:
        drone.sendLightManual(DeviceType.Drone, flags, brightness if on else 0)


def led_check(drones):
    print("[확인] 포트-드론 짝 맞추기 (켜지는 순서 = drone1, 2, 3, 4)")
    for i, drone in enumerate(drones, start=1):
        print(f"  drone{i}")
        led([drone], on=True)
        sleep(0 if DRY_RUN else 1.5)
        led([drone], on=False)
        sleep(0 if DRY_RUN else 0.3)


def offsets(pattern):
    """패턴 이름 → 드론별 (x, y, z) 이동량. 대형 좌표에서 계산한다."""
    cx = sum(x for x, _ in FORMATION) / len(FORMATION)  # 대형 중심
    cy = sum(y for _, y in FORMATION) / len(FORMATION)

    if pattern == "symmetric":  # 양 끝은 높게, 가운데는 낮게 (V자)
        return [(0, 0, z) for z in (0.8, 0.3, 0.3, 0.8)]
    if pattern == "wave":  # 드론마다 조금씩 다른 높이
        return [(0, 0, z) for z in (0.2, 0.5, 0.2, -0.2)]
    if pattern == "swarm_move":  # 대형을 유지한 채 전원 같은 방향
        return [(STEP_M, 0, 0)] * len(FORMATION)
    if pattern in ("expand", "contract"):
        sign = 1 if pattern == "expand" else -1
        moves = []
        for x, y in FORMATION:  # 중심에서 자기 자리로 향하는 방향 (부호만 쓴다)
            dx = STEP_M * sign * (1 if x > cx else -1)
            dy = STEP_M * sign * (1 if y > cy else -1)
            moves.append((dx, dy, 0))
        return moves
    if pattern == "square":  # 다음 꼭짓점 − 지금 꼭짓점
        moves = []
        for i, (x, y) in enumerate(FORMATION):
            nx, ny = FORMATION[(i + 1) % len(FORMATION)]
            moves.append((nx - x, ny - y, 0))
        return moves
    return [(0, 0, 0)] * len(FORMATION)  # takeoff_sync / takeoff_seq 는 이동이 없다


def apply_moves(drones, moves, wait=None):
    """드론마다 다른 위치 명령을 연달아 보낸다 — 논블로킹이라 거의 동시에 출발한다."""
    longest = max((max(abs(v) for v in m) for m in moves), default=0.0)
    if longest == 0:
        return
    for drone, (dx, dy, dz) in zip(drones, moves):
        drone.sendControlPosition(dx, dy, dz, SPEED, 0, 0)
        print(f"    {getattr(drone, 'name', 'drone')}: x={dx:+.1f} y={dy:+.1f} z={dz:+.1f}")
    sleep(0 if DRY_RUN else (wait if wait else longest / SPEED + 2))


def take_off(drones):
    """동시 이륙은 한꺼번에, 순차 이륙은 사이에 sleep 을 넣는다 — 차이는 이것뿐이다."""
    if PATTERN == "takeoff_seq":
        for i, drone in enumerate(drones, start=1):
            print(f"  drone{i} takeoff")
            drone.sendTakeOff()
            sleep(0 if DRY_RUN else SEQ_GAP)
    else:
        for drone in drones:
            drone.sendTakeOff()
    sleep(0 if DRY_RUN else 5)


def main():
    drones = connect_all()
    flying = False
    try:
        if LED_CHECK:
            led_check(drones)

        print(f"[패턴] {PATTERN}")
        take_off(drones)
        flying = True
        sleep(0 if DRY_RUN else 2)  # 자세가 안정될 때까지

        moves = offsets(PATTERN)
        print("  이동")
        apply_moves(drones, moves)

        if RETURN:
            print("  원위치")  # 위치 명령은 "지금 위치에서 얼마" 라 되돌리지 않으면 대형이 밀린다
            apply_moves(drones, [(-x, -y, -z) for x, y, z in moves])

        print("  착륙")
        for drone in drones:
            drone.sendLanding()
        flying = False
        sleep(0 if DRY_RUN else 5)
    except KeyboardInterrupt:
        print("Ctrl+C — 착륙합니다")
    finally:
        if flying:
            for drone in drones:
                drone.sendLanding()
            sleep(0 if DRY_RUN else 5)
        led(drones, on=False)
        sleep(0.1)
        for drone in drones:
            drone.close()


if __name__ == "__main__":
    main()
