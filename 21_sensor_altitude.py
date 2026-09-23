"""21. 센서 읽기 — 고도 Altitude (17강 예제1)

센서값은 "요청 → 응답 → 핸들러" 로 받는다. 세 줄이 전부다.

    dron.setEventHandler(DataType.Altitude, event_altitude)   # ① 등록 (1회)
    dron.sendRequest(DeviceType.Drone, DataType.Altitude)     # ② 요청 (반복)
    def event_altitude(altitude): ...                         # ③ 응답이 오면 자동 호출

**sendRequest 의 반환값은 센서값이 아니다.** 19번에서 본 것과 같이 방금 보낸 프레임이고,
드론의 응답은 백그라운드 수신 스레드가 받아 핸들러로 넘긴다.
그래서 `Drone()` 이어야 한다. `Drone(False)` 면 요청은 나가지만 핸들러가 영영 안 불린다(03번).

[Altitude 필드 — 전부 Float32]
    temperature  온도(℃)
    pressure     기압
    altitude     기압을 해발고도로 환산한 값(m)
    rangeHeight  하방 거리센서가 잰 바닥까지의 높이(m)

**altitude 와 rangeHeight 는 다른 값이다.** altitude 는 기압 기반 해발고도라 실내에서도
수십 m 로 나오고 계속 흔들린다. "바닥에서 얼마나 떠 있나" 는 rangeHeight 를 본다.

[이륙 토글]
강의 예제는 이륙 후 호버링하며 고도를 찍지만, 센서값 확인만 할 거면 책상 위에서도 된다.
TAKEOFF 를 True 로 바꾸면 강의 예제와 같아진다. 이륙 시에는 공간 확보 + 비상정지 준비.
"""

from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import DataType, DeviceType

from drone_util import find_port

TAKEOFF = False  # True 로 바꾸면 이륙한다 (강의 예제1과 동일)
REPEAT = 10
INTERVAL = 0.5


def event_altitude(altitude):
    print("eventAltitude()")
    print("-  Temperature: {0:.3f}".format(altitude.temperature))
    print("-     Pressure: {0:.3f}".format(altitude.pressure))
    print("-     Altitude: {0:.3f}".format(altitude.altitude))  # 해발고도(m)
    print("- Range Height: {0:.3f}".format(altitude.rangeHeight))  # 바닥까지(m)


def main():
    dron = Drone()  # 백그라운드 수신 ON — 핸들러 동작 조건
    try:
        dron.open(find_port())
        dron.setEventHandler(DataType.Altitude, event_altitude)

        if TAKEOFF:
            for i in range(3, 0, -1):
                print(f"이륙 {i}...")
                sleep(1)
            dron.sendTakeOff()
            sleep(5)  # 호버링 안정화

        for i in range(REPEAT, 0, -1):
            print(i)
            dron.sendRequest(DeviceType.Drone, DataType.Altitude)
            sleep(INTERVAL)
    finally:
        if TAKEOFF:
            print("Landing")
            dron.sendLanding()
            sleep(3)
        sleep(0.1)
        dron.close()


if __name__ == "__main__":
    main()
