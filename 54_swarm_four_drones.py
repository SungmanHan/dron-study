r"""54. 군집비행 — 드론 4대, 높이 교차 ⚠️ 실제로 이륙한다

25 강 예제2. 1/2 번이 먼저 뜨고 3/4 번이 뒤따라 떠서 **두 조가 높이를 맞바꾼 뒤**
1/2 번 → 3/4 번 순으로 내려온다. 53 과 코드 구조는 같고 **대수와 안무만 다르다.**

[단계별 높이] — 이륙 직후 높이를 H 라고 할 때

| 단계 | 동작 | drone1/2 | drone3/4 |
|---|---|---|---|
| 1 | 1/2 이륙 | H | 바닥 |
| 2 | 1/2 호버링 | H | 바닥 |
| 3 | 1/2 상승 1.4 + 3/4 이륙 | H+1.4 | H |
| 4 | 전체 호버링 | H+1.4 | H |
| 5 | 1/2 하강 1.0 + 3/4 상승 1.4 (**교차**) | H+0.4 | H+1.4 |
| 6 | 전체 호버링 | H+0.4 | H+1.4 |
| 7 | 1/2 착륙 + 3/4 하강 1.0 | 바닥 | H+0.4 |
| 8 | 3/4 호버링 | 바닥 | H+0.4 |
| 9 | 3/4 착륙 | 바닥 | 바닥 |

⚠️ 최고 높이가 **이륙 높이 + 1.4 m** 다. 천장을 먼저 확인할 것.
⚠️ 5 단계에서 두 조가 높이를 스쳐 지나간다. 대각선 배치(아래)를 지켜 같은 수직선에 겹치지 않게 한다.

    drone4 ·········· drone2        1/2 조와 3/4 조가 대각선으로 엇갈리게.
        :                :          드론 사이 간격은 **2 m 이상** —
        :                :          더 가까우면 서로의 프로펠러 바람에 자세가 흔들린다.
    drone1 ·········· drone3

[4 대가 되면 `sendControlWhile` 의 비용이 눈에 보인다]
이 함수는 `timeMs` 동안 20 ms 간격으로 조종값을 반복 전송하고 **그동안 반환하지 않는다.**
한 대에 보내는 동안 나머지는 마지막 명령(제자리)을 유지할 뿐이다.

    "3 초 호버링" 루프  →  2 대면 약 6 초, **4 대면 약 12 초**

높이를 바꾸는 3·5·7 단계는 논블로킹인 `sendControlPosition` 이라 네 대가 거의 동시에 움직인다.

[포트 4 개를 꽂으면서 생기는 문제]
- **충전 전용 케이블은 포트가 잡히지 않는다.** 데이터 전송용인지 먼저 확인.
- USB 허브를 거치면 인식이 불안정하다. 가능하면 전원 공급형 허브를 쓴다.
- 포트 이름의 숫자는 꽂는 자리에 따라 바뀐다 — **이름만 보고 몇 번 드론인지 알 수 없다.**
  그래서 이륙 전에 LED 를 하나씩 켜서 짝을 확인한다(`LED_CHECK`).
- 네 대가 동시에 뜨므로 **배터리를 전부 확인**한다. 한 대만 약해도 대형이 깨진다.

[슬라이드 오탈자]
4 대 코드 자체에는 오탈자가 없다. 2 대 코드(53)의 8·9 단계 주석이 `drone3/4` 로 되어 있는 것이
이 파일에서 복사해 간 흔적이다.
"""

from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import DeviceType, LightFlagsDrone

from drone_util import find_ports

DRY_RUN = True  # True = 드론 없이 순서만 확인. 확인 뒤 False
PORTS = []  # 네 개를 직접 적으면 그 순서가 drone1~4 다. 비우면 자동 탐색
LED_CHECK = True
DRONE_COUNT = 4

UP_M = 1.4  # 상승 높이 (m)
DOWN_M = 1.0  # 하강 높이 (m)
SPEED = 0.5  # 위치 명령 속도 (m/s)
MOVE_WAIT = 5  # 1.4 m ÷ 0.5 m/s = 2.8 초 + 이륙 여유


class FakeDrone:
    """DRY_RUN 용. 실제 Drone 과 같은 이름·반환값을 흉내 낸다."""

    def __init__(self, name):
        self.name = name

    def open(self, port=None):
        print(f"  [DRY] {self.name} open {port}")
        return True

    def sendTakeOff(self):
        print(f"  [DRY] {self.name} takeOff")

    def sendLanding(self):
        print(f"  [DRY] {self.name} landing")

    def sendControlWhile(self, roll, pitch, yaw, throttle, time_ms):
        print(f"  [DRY] {self.name} while({roll},{pitch},{yaw},{throttle}, {time_ms}ms)")

    def sendControlPosition(self, x, y, z, velocity, heading, rotational):
        print(f"  [DRY] {self.name} position(z={z:+.1f}, {velocity} m/s)")

    def sendLightManual(self, device, flags, brightness):
        print(f"  [DRY] {self.name} light(flags=0x{flags:02X}, brightness={brightness})")

    def close(self):
        print(f"  [DRY] {self.name} close")


def connect_all():
    """드론 수만큼 객체를 만들고 각각 다른 포트로 연다 — 군집의 전부는 이것뿐이다."""
    if DRY_RUN:
        return [FakeDrone(f"drone{i}") for i in range(1, DRONE_COUNT + 1)]

    ports = PORTS or find_ports(DRONE_COUNT)
    drones = []
    for i, port in enumerate(ports[:DRONE_COUNT], start=1):
        drone = Drone()
        if not drone.open(port):  # 포트를 명시하고 반환값을 확인한다
            for opened in drones:
                opened.close()
            raise SystemExit(f"drone{i} 연결 실패: {port}")
        print(f"  drone{i} <- {port}")
        drones.append(drone)
    return drones


def led(drones, color=None, brightness=100):
    """color=None 이면 전체 소등. flags·brightness 는 int 여야 한다(17 참고)."""
    flags = 0xFF if color is None else LightFlagsDrone.BodyRed.value
    for drone in drones:
        drone.sendLightManual(DeviceType.Drone, flags, 0 if color is None else brightness)


def led_check(drones):
    print("[확인] 포트-드론 짝 맞추기 (빨갛게 켜지는 순서 = drone1, 2, 3, 4)")
    for i, drone in enumerate(drones, start=1):
        print(f"  drone{i}")
        led([drone], "red")
        sleep(0 if DRY_RUN else 1.5)
        led([drone], None)
        sleep(0 if DRY_RUN else 0.3)


def step(number, text):
    print(f"[Step.{number}] {text}")


def wait(seconds):
    for i in range(seconds, 0, -1):
        print(f"  {i}")
        sleep(0 if DRY_RUN else 1)


def hover(drones, seconds=3):
    """블로킹이라 실제로는 (대수 × seconds) 초 걸린다 — 4 대면 약 12 초."""
    for i in range(seconds, 0, -1):
        print(f"  {i}")
        for drone in drones:
            drone.sendControlWhile(0, 0, 0, 0, 1000)
        sleep(0.01)


def move_z(drones, dz):
    """높이만 바꾼다. 논블로킹이라 여러 대가 거의 동시에 움직인다."""
    for drone in drones:
        drone.sendControlPosition(0, 0, dz, SPEED, 0, 0)


def main():
    drones = connect_all()
    group_a, group_b = drones[:2], drones[2:]  # 1/2 조, 3/4 조
    flying = []
    try:
        if LED_CHECK:
            led_check(drones)

        step(1, "Drone1/2 Takeoff")
        for drone in group_a:
            drone.sendTakeOff()
        flying = list(group_a)
        wait(5)

        step(2, "Drone1/2 Hovering")
        hover(group_a)

        step(3, "Drone1/2 Going up + Drone3/4 Takeoff")
        move_z(group_a, UP_M)  # H -> H+1.4
        for drone in group_b:
            drone.sendTakeOff()
        flying = list(drones)
        wait(5)

        step(4, "All Drones Hovering")
        hover(drones)  # 4 대 × 1 초 × 3 회 ≈ 12 초

        step(5, "Drone1/2 Going down + Drone3/4 Going up")  # 높이 교차
        move_z(group_a, -DOWN_M)  # H+1.4 -> H+0.4
        move_z(group_b, UP_M)  # H     -> H+1.4
        wait(5)

        step(6, "All Drones Hovering")
        hover(drones)

        step(7, "Drone1/2 Landing + Drone3/4 Going down")
        for drone in group_a:
            drone.sendLanding()
        move_z(group_b, -DOWN_M)  # H+1.4 -> H+0.4
        flying = list(group_b)
        wait(5)

        step(8, "Drone3/4 Hovering")
        hover(group_b)

        step(9, "Drone3/4 Landing")
        for drone in group_b:
            drone.sendLanding()
        flying = []
        wait(5)
    except KeyboardInterrupt:
        print("Ctrl+C — 떠 있는 드론을 착륙시킵니다")
    finally:
        # 어디서 멈췄든 그 시점에 떠 있는 드론만 착륙시킨다
        for drone in flying:
            drone.sendLanding()
        if flying:
            sleep(0 if DRY_RUN else 5)
        led(drones, None)
        sleep(0.1)
        for drone in drones:
            drone.close()


if __name__ == "__main__":
    main()
