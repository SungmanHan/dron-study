"""37. 미션 6 — 전진하다 하방에 높은 목적지가 있으면 그 위에 착륙   ⚠️ 실제로 이륙한다

    이륙 → 전진 → 발밑 거리가 뚝 떨어짐(= 상자 위) → 착륙

36 과 구조는 똑같고 **보는 센서만 앞에서 아래로** 바뀐다. 바뀌는 건 네 줄이다.

| | 36 (미션 4·5) | 37 (미션 6) |
|---|---|---|
| 요청 | `DataType.Range` | `DataType.Altitude` |
| 콜백 | `event_range(range_data)` | `event_altitude(altitude)` |
| 값 | `range_data.front` | `altitude.rangeHeight` |
| 단위 | **mm** (정수, 400) | **m** (실수, 0.4) |

숫자가 1000배 차이 난다. 단위를 헷갈리면 영영 감지되지 않거나 이륙하자마자 착륙한다.

[altitude 가 두 개다]
    altitude.altitude     기압으로 구한 해발고도 — 상자 위를 지나도 거의 안 변한다
    altitude.rangeHeight  하방 거리 센서로 잰 발밑까지 거리  ← 이 미션이 쓰는 값
같은 높이를 `Range.bottom`(mm) 으로도 볼 수 있다. 23 번과 같은 값, 다른 단위다.

[감지 기준값 정하기]
    바닥 위     rangeHeight ≈ 호버링 높이            (예: 0.8 m)
    상자 위     rangeHeight ≈ 호버링 높이 − 상자 높이 (예: 0.8 − 0.45 = 0.35 m)

    DETECT_HEIGHT = 호버링 높이 − 상자 높이 + 여유

호버링 높이는 기체·바닥·배터리에 따라 매번 다르다. 먼저 21 번으로 이륙 후
`rangeHeight` 를 찍어 보고 정하는 게 빠르다. 원본의 `0.3 ~ 0.4` 는 예시일 뿐이다.

[강의 원본의 가장 위험한 버그 — NameError]
콜백은 `isDetected` 를 쓰는데 메인 루프는 `if value == False` 로 **정의된 적 없는 변수**를
검사한다(미션 4 코드를 복사하다 남은 줄이다). 첫 반복에서 `NameError` 가 나고,
`except KeyboardInterrupt` 는 그걸 안 잡고, `finally` 에는 `close()` 밖에 없다.

    → 드론은 전진 명령을 받은 채 공중에 남고, 연결만 끊긴다.

조용히 무시되는 함정들과 달리 이건 예외가 나는데도 결과가 더 나쁘다.
`finally` 에서 정지·착륙까지 해야 하는 이유가 이것이다. (`global` 누락, 좁은 감지 구간,
콜백에서 착륙 — 36 과 같은 문제도 그대로 있다)

[미션 포인트]
- 감지되는 순간은 상자 **모서리**에 막 들어선 때다. 상자가 작으면 착륙하며 미끄러진다.
  `EXTRA_M` 을 0.1 정도 주면 조금 더 들어가서 내린다 (슬라이드가 제안한 방법).
- 상자 윗면이 무늬 없는 단색이면 옵티컬 플로우가 흔들린다.
- 바닥의 다른 높은 물건(가방, 의자 다리)도 목적지로 오인한다. 경로를 비워 둘 것.

실행:  .venv/bin/python 37_mission_land_on_target.py
"""

from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import DataType, DeviceType

from drone_util import countdown, find_port

DETECT_HEIGHT = 0.4  # m. 발밑이 이보다 가까워지면 "목적지 위" — 호버링 높이 − 상자 높이 + 여유
FORWARD_POWER = 25  # 전진 세기 (int 전용)
INTERVAL = 0.1  # 요청·전진 주기(초)

EXTRA_M = 0.0  # 감지 후 더 들어갈 거리 (m). 상자가 작으면 0.1 정도
EXTRA_SPEED = 0.3

dron = Drone()
height_m = 0.0  # 가장 최근 발밑 거리 (m)
detected = False


def event_altitude(altitude):
    global height_m, detected  # ← 36 과 같은 자리의 같은 함정

    height_m = altitude.rangeHeight
    print(f"rangeHeight : {height_m:.2f} m")

    if 0 < height_m < DETECT_HEIGHT:  # 0 은 측정 실패라 제외
        detected = True


if not dron.open(find_port()):
    raise SystemExit("드론 연결 실패 — USB 연결을 확인하세요")

dron.setEventHandler(DataType.Altitude, event_altitude)

try:
    print("TakeOff — 중단하려면 Ctrl+C (Jupyter 는 중단 ■)")
    dron.sendTakeOff()
    countdown(5, "이륙 안정화")

    # 1) 발밑을 보며 전진
    while not detected:
        dron.sendRequest(DeviceType.Drone, DataType.Altitude)
        sleep(INTERVAL)
        dron.sendControl(0, FORWARD_POWER, 0, 0)
        sleep(INTERVAL)
        print("FORWARD")

    print(f"목적지 감지 : {height_m:.2f} m")

    # 2) 전진을 끊는다
    dron.sendControl(0, 0, 0, 0)
    sleep(0.5)

    # 3) 모서리에서 미끄러지지 않게 조금 더 들어간다 (선택)
    if EXTRA_M > 0:
        print(f"Go Front {EXTRA_M} meter")
        dron.sendControlPosition(EXTRA_M, 0, 0, EXTRA_SPEED, 0, 0)
        countdown(3, "진입 대기")

    print("Landing")
    dron.sendLanding()
    countdown(5, "착지 대기")

finally:
    dron.sendControl(0, 0, 0, 0)
    sleep(0.1)
    dron.sendLanding()  # 원본은 여기가 비어 있어 드론이 공중에 남았다
    sleep(0.1)
    dron.close()
    print("포트 닫음")
