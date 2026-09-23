"""23. 센서로 제어 — 하방 거리로 자동 착륙 (17강 예제4)

⚠️ 실제로 이륙한다. 넓은 실내, 프로펠러 가드, 비상정지(`dron.sendStop()`) 준비.

호버링 중 드론 **아래**에 손이나 상자를 넣으면 하방 거리가 줄고, 기준치보다 가까워지면 착륙한다.
21~22번이 센서를 "읽기만" 했다면 여기서 처음 "읽고 판단해서 명령" 한다.

[⚠️ 강의 원본의 버그 — global 누락]
    def eventAltitude(altitude):
        if altitude.rangeHeight < 0.3:
            isDetected = True          # ← 대입이 있으면 파이썬은 이 이름을 지역 변수로 본다
        if isDetected == True:         # ← 그래서 평상시(대입 안 될 때)엔 여기서 터진다

    UnboundLocalError: cannot access local variable 'isDetected' ...

0.3 미만일 때는 대입이 먼저 일어나 우연히 동작하므로, **착륙은 되는데 평소엔 계속 에러가 찍히는**
상태가 된다. 그리고 전역 isDetected 는 끝까지 False 다. 해결은 함수 첫 줄 `global isDetected`.

[그 밖에 정리한 것]
- 핸들러 등록을 루프 밖으로 (원본은 1초마다 재등록 — 무해하지만 의미 없다)
- 감지되면 break (원본은 착륙 후에도 요청·착륙 명령을 계속 보낸다)
- close() 추가 (원본에 없어서 다음 실행 때 포트가 물린다)

[하방 거리는 두 군데서 볼 수 있다]
    Altitude.rangeHeight  m  단위 Float32   ← 이 예제
    Range.bottom          mm 단위 Int16     ← 24번의 Range 프레임에 같이 들어온다
"""

from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import DataType, DeviceType

from drone_util import find_port

LANDING_HEIGHT = 0.3  # m. 이보다 가까워지면 착륙. 호버링이 낮으면 0.2 로 낮춘다
INTERVAL = 1.0  # 판단 주기(초). 줄이면 반응이 빨라진다

dron = Drone()  # 핸들러에서도 쓰므로 모듈 수준
isDetected = False


def event_altitude(altitude):
    global isDetected  # ★ 원본에 없던 줄

    print(f"eventAltitude() / Range Height : {altitude.rangeHeight:.3f} m")

    if altitude.rangeHeight < LANDING_HEIGHT:
        isDetected = True

    if isDetected:
        dron.sendLanding()


def main():
    try:
        dron.open(find_port())
        dron.setEventHandler(DataType.Altitude, event_altitude)

        for i in range(3, 0, -1):
            print(f"이륙 {i}...")
            sleep(1)
        print("TakeOff")
        dron.sendTakeOff()
        sleep(5)  # 호버링 안정화. 이륙 중에는 높이가 기준보다 낮으므로 요청하지 않는다

        while True:
            dron.sendRequest(DeviceType.Drone, DataType.Altitude)
            sleep(INTERVAL)
            if isDetected:
                print("하방 물체 감지 → 착륙")
                break
    except KeyboardInterrupt:
        dron.sendLanding()
        print("중단 → 착륙")
    finally:
        sleep(3)  # 착륙 완료 대기
        dron.close()


if __name__ == "__main__":
    main()
