"""24. 센서로 제어 — 전방 거리로 자동 착륙 (17강 예제5)

⚠️ 실제로 이륙한다. 앞쪽 공간을 1m 이상 확보하고 비상정지(`dron.sendStop()`)를 준비할 것.

23번과 같은 "읽고 판단해서 명령" 구조이고 센서만 전방으로 바뀐다.
드론 **앞**에 손이나 벽이 20~40cm 로 들어오면 착륙한다.

[Range — Int16 6방향]
    left / front / right / rear / top / bottom   단위 mm
전방은 `range.front`. **하방 거리도 `range.bottom` 으로 같이 들어온다.**
(23번의 `Altitude.rangeHeight` 는 m 단위 Float32 — 같은 높이를 다른 단위로 본다)

[단위가 예제마다 다르다]
    하방 rangeHeight < 0.3      m  → 30cm
    전방 200 < front < 400      mm → 20~40cm
숫자 크기가 1000배 차이 나는 이유다. 헷갈리면 값이 안 잡히거나 즉시 착륙한다.

[하한 200 의 의미]
앞에 아무것도 없거나 측정이 실패하면 0 근처 값이 나온다. 그 비정상값을 걸러내려고 하한을 둔다.
따라서 손을 20cm 보다 더 가까이 붙이면 조건에서 빠져 착륙하지 않는다.

[강의 원본에서 정리한 것]
- 핸들러 매개변수 이름이 `range` 였다 — 파이썬 내장 `range()` 를 가린다 → `range_data`
- `rangeValue = range.front` 에 global 이 없어 전역이 갱신되지 않았다 (23번과 같은 함정.
  다만 여기서는 대입이 사용보다 먼저라 에러는 안 나고 조용히 전역만 0 으로 남는다)
- 강의 **화면** 버전은 Ctrl+C 때 `sendLanding()` 이 없어 **계속 호버링**한다 → 착륙을 넣었다
- 핸들러 등록을 루프 밖 1회로, 감지 시 break, close() 추가
"""

from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import DataType, DeviceType

from drone_util import find_port

MIN_FRONT = 200  # mm. 이보다 작으면 측정 이상으로 보고 무시
MAX_FRONT = 400  # mm. 이보다 가까우면 착륙
INTERVAL = 0.1  # 판단 주기(초) — 강의 화면 버전과 같은 빠른 주기

dron = Drone()
isDetected = False


def event_range(range_data):  # 원본 인자명 range → 내장 함수를 가린다
    global isDetected

    front = range_data.front
    print(f"eventRange() / front : {front} mm")

    if MIN_FRONT < front < MAX_FRONT:  # 파이썬은 비교를 이어 쓸 수 있다
        isDetected = True
        dron.sendLanding()
        print("Landing")


def main():
    try:
        dron.open(find_port())
        dron.setEventHandler(DataType.Range, event_range)

        print("전방 센서 측정 — 중단하려면 Ctrl+C (Jupyter 는 중단 ■)")
        for i in range(3, 0, -1):
            print(f"이륙 {i}...")
            sleep(1)
        print("TakeOff")
        dron.sendTakeOff()
        sleep(5)

        while True:
            dron.sendRequest(DeviceType.Drone, DataType.Range)
            sleep(INTERVAL)
            if isDetected:
                print("전방 물체 감지 → 착륙")
                break
    except KeyboardInterrupt:
        dron.sendLanding()  # 화면 버전에는 이 줄이 없었다
        print("중단 → 착륙")
    finally:
        sleep(3)
        dron.close()


if __name__ == "__main__":
    main()
