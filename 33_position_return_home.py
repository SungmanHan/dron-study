"""33. 리턴홈 — 이륙 지점으로 스스로 돌아오기   ⚠️ 실제로 이륙한다

    이륙 → 호버링 → 앞으로 1 m → 오른쪽으로 1 m → **리턴홈** → 착륙

32 의 "ㄱ" 자 경로 끝에 리턴홈을 붙이면 경로가 삼각형이 된다.
돌아갈 거리(대각선 약 1.4 m)와 방향을 우리가 계산할 필요가 없다는 것이 요점이다.

[새 함수 — sendFlightEvent]
    dron.sendFlightEvent(FlightEvent.Return)

`sendFlightEvent(flightEvent)` 는 `CommandType.FlightEvent` + 이벤트 번호를 보낸다.
사실 이미 쓰고 있던 함수다 — `sendTakeOff()` / `sendLanding()` 이 각각
`FlightEvent.TakeOff`(0x11) / `FlightEvent.Landing`(0x12) 을 감싼 래퍼다.
래퍼가 없는 나머지 이벤트는 이 함수로 직접 보낸다.

    Return(0x18)        이륙 지점으로 복귀        ← 이번 예제
    Reverse(0x13)       뒤집기
    FlipFront/Rear/Left/Right(0x14~0x17)  공중제비 — 충분한 높이와 공간이 필요
    ResetHeading(0xA0)  기준 방향 초기화
    Stop(0x10)          ⚠️ 이 값은 있지만, 모터 정지는 `sendStop()`(CommandType.Stop) 을 쓴다

[함정 — 인자는 반드시 FlightEvent enum]
    dron.sendFlightEvent(0x18)   # int → 조용히 None. 아무 일도 안 일어난다
라이브러리가 `isinstance(flightEvent, FlightEvent)` 를 검사하고 아니면 그냥 리턴한다.
LED 의 `flags` 가 `.value` 를 안 붙이면 무시되던 것과 반대 방향의 같은 함정이다.
`FlightEvent` 는 `CodingDrone.protocol` 에 있다.

[리턴홈도 비블로킹이다]
보내고 바로 리턴하므로 복귀가 끝나기 전에 `sendLanding()` 이 나가면 중간에 착륙한다.
이동 거리가 길면 대기 시간도 늘릴 것.

[돌아오는 지점은 정확하지 않다]
드론이 **스스로 추정한** 위치 기준이다. 하방 옵티컬 플로우 센서가 바닥 무늬의 움직임을
보고 이동량을 누적하는 방식이라, 단색·유광·어두운 바닥에서는 추정이 어긋난다.
수십 cm 정도 빗나갈 수 있으니 착륙 지점 주변을 비워 둘 것.

실행:  .venv/bin/python 33_position_return_home.py
"""

import math
from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import FlightEvent

from drone_util import countdown, find_port

DIST_M = 1.0
SPEED = 0.5
MOVE_WAIT = math.ceil(DIST_M / SPEED) + 3  # 거리 ÷ 속도 + 여유

# 리턴홈은 대각선 √2 m 를 돌아온다. 속도는 드론이 정하므로 넉넉히 기다린다.
RETURN_WAIT = math.ceil(DIST_M * math.sqrt(2) / SPEED) + 3

dron = Drone()

if not dron.open(find_port()):
    raise SystemExit("드론 연결 실패 — USB 연결을 확인하세요")

try:
    # 1) 이륙 — 이 지점이 나중에 돌아올 "홈" 이 된다.
    print("TakeOff")
    dron.sendTakeOff()
    countdown(5, "이륙 안정화")

    # 2) 호버링 — 3.6초간 블로킹
    print("Hovering")
    dron.sendControlWhile(0, 0, 0, 0, 3600)

    # 3) 앞으로 1 m  (앞 +)
    print(f"Go Front {DIST_M} meter")
    dron.sendControlPosition(DIST_M, 0, 0, SPEED, 0, 0)
    countdown(MOVE_WAIT, "이동 대기")

    # 4) 오른쪽으로 1 m  (Y축은 좌 + / 우 − → 오른쪽은 음수)
    print(f"Go Right {DIST_M} meter")
    dron.sendControlPosition(0, -DIST_M, 0, SPEED, 0, 0)
    countdown(MOVE_WAIT, "이동 대기")

    # 5) 리턴홈 — 좌표를 계산해 넣을 필요 없이 한 줄이다.
    print("Return Home")
    dron.sendFlightEvent(FlightEvent.Return)
    countdown(RETURN_WAIT, "복귀 대기")

    # 6) 착륙 — 이륙 지점 근처에서 내린다.
    print("Landing")
    dron.sendLanding()
    countdown(5, "착지 대기")

finally:
    dron.sendLanding()
    sleep(0.1)
    dron.close()
    print("포트 닫음")
