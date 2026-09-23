"""34. 패턴 비행 — 정사각형 두 가지 방법   ⚠️ 실제로 이륙한다

    MODE = 1   전진 → 오른쪽 → 후진 → 왼쪽      (강의 예제6-1)
               드론은 앞을 본 채로 네 방향으로 미끄러진다
    MODE = 2   (전진 → 우회전 90°) × 4           (강의 예제6-2)
               모서리마다 몸을 돌린다. 자동차가 코너를 도는 모습

둘 다 한 변 1 m 짜리 정사각형을 그리고 출발점으로 돌아온다. 결과는 같고 방식이 다르다.

| | MODE 1 방향 이동 | MODE 2 heading 회전 |
|---|---|---|
| 명령 종류 | 전진·우·후진·좌 4가지 | **전진 + 우회전 2가지** |
| 드론 앞쪽 | 계속 처음 방향 | 모서리마다 90°씩 바뀜 |
| 확장 | 임의의 경로 | 정다각형 (회전각 = 360 ÷ 변의 수) |

[MODE 1 — 부호만 외우면 된다]
    전진 X +1.0 |  후진 X −1.0 |  왼쪽 Y +1.0 |  오른쪽 Y −1.0
Y축은 **좌 + / 우 −** 로 직관과 반대다. 네 변의 합이 0 이 되므로 리턴홈(33) 없이도
출발점으로 돌아온다 — 다만 이동 오차가 누적되어 실제로는 조금 어긋난다.

[MODE 2 — 회전 명령]
    dron.sendControlPosition(0, 0, 0, 0, -90, 45)
                             └ 위치 3개 0 = 제자리 ┘  │    └ 45°/s
                                                    └ heading −90 = 우회전 90°
heading 도 Y축처럼 **좌 + / 우 −** 다. `velocity` 는 이동할 때만 의미가 있어서 0 을 넣는다.
`heading` 과 `rotationalVelocity` 는 **int 전용**이다 — `-90.0` 을 넣으면 예외 없이
조용히 무시된다(32 의 함정 ① 참고).

[MODE 2 가 성립하는 이유]
위치 이동은 **드론이 지금 바라보는 방향** 기준이다("바디 기준"). 그래서 회전한 뒤의
전진은 새 방향으로 나아가고, 같은 명령 두 개만 반복해도 도형이 된다.
`SIDES` 를 3 이나 6 으로 바꾸면 정삼각형·정육각형이 된다 — 회전각은 자동으로 맞춘다.

[대기 시간은 두 종류다]
    이동 = 거리 ÷ 속도 + 여유        1 m ÷ 0.5 m/s  = 2초
    회전 = 회전각 ÷ 회전속도 + 여유   90° ÷ 45°/s    = 2초
둘 다 비블로킹이라 기다리지 않으면 다음 명령이 앞 명령을 덮어쓴다.
회전 속도를 줄이면 회전 시간이 길어지므로 대기도 같이 늘어난다(아래 계산에 반영).

[공간]
한 변 1 m 면 최소 2 m × 2 m 는 비어 있어야 한다. 좁은 곳에서는 `SIDE_M` 을 0.5 로.

실행:  .venv/bin/python 34_pattern_square.py
"""

import math
from time import sleep

from CodingDrone.drone import Drone

from drone_util import countdown, find_port

MODE = 1  # 1 = 방향 이동 / 2 = heading 회전

SIDE_M = 1.0  # 한 변 길이 (m)
SPEED = 0.5  # 이동 속도 (m/s)
SIDES = 4  # MODE 2 전용 — 3=정삼각형 4=정사각형 6=정육각형
ROT_SPEED = 45  # MODE 2 전용 — 회전 속도 (°/s). int 여야 한다

MOVE_WAIT = math.ceil(SIDE_M / SPEED) + 3  # 거리 ÷ 속도 + 여유

TURN = -(360 // SIDES)  # 음수 = 우회전. 360÷4 = 90 → -90
TURN_WAIT = math.ceil(abs(TURN) / ROT_SPEED) + 3  # 회전각 ÷ 회전속도 + 여유

# MODE 1 의 네 변 — 강의는 같은 모양의 블록 4개를 나열하지만,
# 방향 값만 다르므로 목록으로 두고 한 번만 돌린다.
LEGS = [
    ("Go Front", SIDE_M, 0),  # 앞 +
    ("Go Right", 0, -SIDE_M),  # 우 −
    ("Go Back", -SIDE_M, 0),  # 뒤 −
    ("Go Left", 0, SIDE_M),  # 좌 +
]

dron = Drone()

if not dron.open(find_port()):
    raise SystemExit("드론 연결 실패 — USB 연결을 확인하세요")

try:
    print("TakeOff")
    dron.sendTakeOff()
    countdown(5, "이륙 안정화")

    if MODE == 1:
        # ── 방향 이동 — 드론은 회전하지 않는다 ────────────────────
        for label, x, y in LEGS:
            print(f"{label} {SIDE_M} meter")
            dron.sendControlPosition(x, y, 0, SPEED, 0, 0)
            countdown(MOVE_WAIT, "이동 대기")

    else:
        # ── heading 회전 — 전진 + 우회전을 변의 수만큼 반복 ────────
        for i in range(SIDES):
            print(f"[{i + 1}/{SIDES}] Go Front {SIDE_M} meter")
            dron.sendControlPosition(SIDE_M, 0, 0, SPEED, 0, 0)
            countdown(MOVE_WAIT, "이동 대기")

            print(f"[{i + 1}/{SIDES}] Turn {TURN} degree")
            dron.sendControlPosition(0, 0, 0, 0, TURN, ROT_SPEED)
            countdown(TURN_WAIT, "회전 대기")

    # 마지막 변까지 끝나면 이륙 지점으로 돌아와 있다. 어긋났다면
    # 33 처럼 sendFlightEvent(FlightEvent.Return) 을 한 번 넣어도 된다.
    print("Landing")
    dron.sendLanding()
    countdown(5, "착지 대기")

finally:
    dron.sendLanding()
    sleep(0.1)
    dron.close()
    print("포트 닫음")
