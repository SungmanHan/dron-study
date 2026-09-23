r"""53. 군집비행 — 드론 2대 ⚠️ 실제로 이륙한다

25 강 예제1. 이륙 → 호버링 → 앞/뒤 → LED → 좌/우 → 호버링 → 착륙을 **두 대가 같이** 한다.

    DRY_RUN = True   드론 없이 순서와 시간만 확인 (명령은 콘솔에만) ← 먼저 이걸로
    PORTS = []       비워 두면 자동 탐색. 순서를 직접 정하려면 경로를 적는다

[군집의 전부는 "객체를 여러 개 만든다" 이다]
드론 N 대 = 조종기 N 대 = 시리얼 포트 N 개 = `Drone` 객체 N 개.
새 함수는 하나도 없다. 지금까지 쓰던 명령을 객체마다 부르는 것뿐이다.

    drone1 = Drone(); drone1.open(포트1)
    drone2 = Drone(); drone2.open(포트2)

라이브러리 쪽도 상태가 전부 인스턴스 변수(`self._serialport`, `self._receiver` …)라
객체끼리 섞이지 않는다. 열 때마다 **수신 스레드가 한 개씩 더 생긴다**(2 대면 2 개).

[⚠️ `open()` 을 인자 없이 부르면 안 된다]
    drone.open()    # 포트를 안 주면 comports() 의 **마지막 장치**를 잡는다
한 대일 때도 위험하지만 군집에서는 두 객체가 같은 포트를 잡거나 엉뚱한 장치를 잡는다.
포트를 명시하고, `open()` 의 반환값(`False` = 실패)을 확인한다.

[어느 포트가 몇 번 드론인지는 이름으로 알 수 없다]
포트 이름의 숫자는 꽂는 USB 포트에 따라 바뀐다. 그래서 이 파일은 이륙 전에
**드론마다 LED 를 순서대로 켜서** 코드상의 drone1 이 실제로 어느 자리인지 눈으로 확인한다.
`LED_CHECK = False` 로 끌 수 있지만, 배치가 걸린 6·7 단계가 있으므로 켜 두길 권한다.

[⚠️ 좌우 이동은 배치에 따라 충돌이 된다 — y+ 가 왼쪽]
6 단계에서 drone1 은 왼쪽(+y)으로, drone2 는 오른쪽(−y)으로 1 m 씩 간다.

    drone1 을 왼쪽, drone2 를 오른쪽에 두면  →  2 m 에서 4 m 로 벌어진다 ✅
    반대로 두면                              →  서로를 향해 1 m 씩 다가와 **충돌** ❌

[`sendControlWhile` 은 블로킹이다 — 군집에서는 이게 함정]
라이브러리를 열어 보면 `timeMs` 동안 **20 ms 간격으로 `sendControl` 을 반복**하고
그 시간이 다 지나야 반환한다. 즉 drone1 에 1 초를 보낸 **뒤에야** drone2 로 넘어간다.

    "3 초 호버링" 루프  →  2 대 × 1 초 × 3 회 = 실제 약 6 초
    4 대면              →  약 12 초 (54 참고)

제자리(0, 0, 0, 0)라 호버링에서는 문제가 없지만, **이동 명령을 이 함수로 주면
두 대의 움직임이 1 초씩 엇갈린다.** 동시에 움직이려면 논블로킹인 `sendControlPosition` 을
연달아 보내고 `sleep` 으로 기다린다(3·4·6·7 단계가 그 방식이다).
명령 프레임은 20 바이트 남짓이고 57600 baud 이므로 한 대당 전송은 4 ms 안쪽 —
두 대의 출발 시차는 사람이 볼 수 없는 수준이다.

[슬라이드 오탈자]
- 4 단계 `print('Step.4| Drone1/2 Backward")` — 따옴표 짝이 안 맞아 **SyntaxError**. 실행조차 안 된다.
- 6·7 단계의 `print` 가 `[Step.3]`, `[Step.2]` 로 적혀 있다(단계 번호 오타).
- 8·9 단계 주석과 출력이 `drone3/4` 로 되어 있다 — 4 대 코드에서 복사한 흔적.
- 예외 처리가 없어서 중간에 멈추면 **드론은 마지막 명령을 유지한 채 떠 있고 포트도 안 닫힌다.**
  이 파일은 `try/finally` 로 착륙·소등·close 를 보장한다.
"""

from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import DeviceType, LightFlagsDrone

from drone_util import find_ports

DRY_RUN = True  # True = 드론 없이 순서만 확인. 확인 뒤 False
PORTS = []  # 예: ["/dev/cu.usbmodem...1", "/dev/cu.usbmodem...2"]. 비우면 자동 탐색
LED_CHECK = True  # 이륙 전에 드론마다 LED 를 켜서 포트-자리 짝 확인
DRONE_COUNT = 2

MOVE_M = 1.0  # 앞뒤·좌우 이동 거리 (m)
SPEED = 0.5  # 위치 명령 속도 (m/s). 권장 0.5~2.0
MOVE_WAIT = 3  # 1.0 m ÷ 0.5 m/s = 2 초 + 여유

COLORS = {"red": LightFlagsDrone.BodyRed, "blue": LightFlagsDrone.BodyBlue,
          "green": LightFlagsDrone.BodyGreen}


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
        sleep(0)  # 진짜는 time_ms 동안 블로킹한다 — DRY 에서는 기다리지 않는다
        print(f"  [DRY] {self.name} while({roll},{pitch},{yaw},{throttle}, {time_ms}ms)")

    def sendControlPosition(self, x, y, z, velocity, heading, rotational):
        print(f"  [DRY] {self.name} position({x}, {y}, {z}, {velocity})")

    def sendLightManual(self, device, flags, brightness):
        print(f"  [DRY] {self.name} light(flags=0x{flags:02X}, brightness={brightness})")

    def close(self):
        print(f"  [DRY] {self.name} close")


def connect_all():
    """드론 수만큼 객체를 만들고 각각 다른 포트로 연다."""
    if DRY_RUN:
        return [FakeDrone(f"drone{i}") for i in range(1, DRONE_COUNT + 1)]

    ports = PORTS or find_ports(DRONE_COUNT)
    drones = []
    for i, port in enumerate(ports[:DRONE_COUNT], start=1):
        drone = Drone()
        if not drone.open(port):  # 실패해도 예외가 아니라 False 다
            for opened in drones:
                opened.close()
            raise SystemExit(f"drone{i} 연결 실패: {port}")
        print(f"  drone{i} <- {port}")
        drones.append(drone)
    return drones


def led(drones, color=None, brightness=100):
    """색 이름으로 드론 LED 를 한꺼번에 제어한다. color=None 이면 전체 소등.

    `flags` 는 켤 LED 를 고르는 비트다. 0xFF 는 전부, `LightFlagsDrone.BodyRed.value` 는 빨강.
    `brightness` 와 `flags` 는 **int 여야** 한다 — enum 을 그대로 넣으면 조용히 무시된다(17 참고).
    """
    flags = 0xFF if color is None else COLORS[color].value
    level = 0 if color is None else brightness
    for drone in drones:
        drone.sendLightManual(DeviceType.Drone, flags, level)


def led_check(drones):
    """드론을 하나씩 빨갛게 켠다 — 코드상의 번호와 실제 자리를 맞춰 보는 단계."""
    print("[확인] 포트-드론 짝 맞추기 (빨갛게 켜지는 순서 = drone1, 2 …)")
    for i, drone in enumerate(drones, start=1):
        print(f"  drone{i}")
        led([drone], "red")
        sleep(0 if DRY_RUN else 1.5)
        led([drone], None)
        sleep(0 if DRY_RUN else 0.3)


def step(number, text):
    """지금 몇 단계인지 찍는다 — 드론이 여러 대면 눈으로 못 따라간다."""
    print(f"[Step.{number}] {text}")


def hover(drones, seconds=3):
    """1 초짜리 호버링 명령을 seconds 번. 블로킹이라 실제로는 대수 × seconds 초 걸린다."""
    for i in range(seconds, 0, -1):
        print(f"  {i}")
        for drone in drones:
            drone.sendControlWhile(0, 0, 0, 0, 1000)  # 네 값 모두 int
        sleep(0.01)


def move(drones, x=0.0, y=0.0, z=0.0):
    """모든 드론에 같은 위치 명령. 논블로킹이라 거의 동시에 움직인다."""
    for drone in drones:
        drone.sendControlPosition(x, y, z, SPEED, 0, 0)
    sleep(MOVE_WAIT)


def main():
    drones = connect_all()
    flying = False
    try:
        if LED_CHECK:
            led_check(drones)

        step(1, "Drone1/2 Takeoff")
        for drone in drones:
            drone.sendTakeOff()
        flying = True
        for i in range(5, 0, -1):  # 이륙에는 시간이 걸린다
            print(f"  {i}")
            sleep(0 if DRY_RUN else 1)

        step(2, "Drone1/2 Hovering")
        hover(drones)

        step(3, "Drone1/2 Forward")
        move(drones, x=MOVE_M)

        step(4, "Drone1/2 Backward")  # 슬라이드는 여기서 따옴표가 깨져 SyntaxError 다
        move(drones, x=-MOVE_M)

        step(5, "Drone1/2 LED")
        for _ in range(3):
            led(drones, None)
            sleep(0 if DRY_RUN else 1)
            led(drones, "red")
            sleep(0 if DRY_RUN else 1)
            led(drones, "blue")
            sleep(0 if DRY_RUN else 1)

        # ⚠️ drone1 은 왼쪽(+y), drone2 는 오른쪽(−y). 배치가 반대면 서로에게 다가간다
        step(6, "Drone1/2 Left, Right")
        drones[0].sendControlPosition(0, MOVE_M, 0, SPEED, 0, 0)
        drones[1].sendControlPosition(0, -MOVE_M, 0, SPEED, 0, 0)
        sleep(MOVE_WAIT)

        step(7, "Drone1/2 Right, Left")  # 원위치
        drones[0].sendControlPosition(0, -MOVE_M, 0, SPEED, 0, 0)
        drones[1].sendControlPosition(0, MOVE_M, 0, SPEED, 0, 0)
        sleep(MOVE_WAIT)

        step(8, "Drone1/2 Hovering")
        hover(drones)

        step(9, "Drone1/2 Landing")
        for drone in drones:
            drone.sendLanding()
        flying = False
        for i in range(5, 0, -1):
            print(f"  {i}")
            sleep(0 if DRY_RUN else 1)
    except KeyboardInterrupt:
        print("Ctrl+C — 착륙합니다")
    finally:
        # 중간에 멈췄어도 착륙 → 소등 → 포트 닫기까지 보장한다
        if flying:
            for drone in drones:
                drone.sendLanding()
            sleep(0 if DRY_RUN else 5)
        led(drones, None)
        sleep(0.1)
        for drone in drones:
            drone.close()


if __name__ == "__main__":
    main()
