"""35. 미션 1·2·3 — 목적지 원 안에 착륙하기   ⚠️ 실제로 이륙한다

    MISSION = 1   이륙 → 전진 → 착륙                    (게이트 없음)
    MISSION = 2   이륙 → 상승 → 전진 → 착륙             (게이트 정중앙 통과)
    MISSION = 3   이륙 → 상승 → 전진 → 옆 이동 → 착륙   (게이트 너머 옆의 원)

세 미션은 서로 다른 프로그램이 아니라 **같은 뼈대에 단계가 하나씩 붙은 것**이다.
그래서 한 파일에 담고 `MISSION` 으로 고른다. 쓰는 명령은 32 와 같은 위치 이동뿐이고,
새로 할 일은 "우리 코스의 숫자를 정하는 것" 이다.

    코스 : Start ──(약 2 m)──> Goal 원(지름 60~80 cm), 2·3 은 중간에 게이트

[미션의 핵심은 코드가 아니라 숫자다]
슬라이드 예제는 전부 **1 m 전진**(`sendControlPosition16(10, 0, 0, 5, 0, 0)`)인데
Start 에서 Goal 원 중심까지는 **2 m** 다. 그대로 돌리면 원 앞에서 내린다.
- 전진 : `FORWARD_M` 을 2.0 근처로. 이·착륙 중에도 기체가 흐르므로 1.8~2.2 에서 보정한다.
- 상승 : 게이트 가로대 **사이 정중앙**이 되게 정한다. 이륙 직후 호버링 높이는 매번 다르니
  먼저 21 번으로 `rangeHeight` 를 찍어 보고 `UP_M` 을 정하는 쪽이 빠르다.
- 옆   : 게이트 중심선과 Goal 원 중심 사이의 **가로 거리**. 좌 **+** / 우 **−**.

대기 시간은 아래에서 거리 ÷ 속도로 계산하므로 거리를 바꿔도 같이 늘어난다.
(2 m 면 이동만 4초라 슬라이드의 5초 대기로는 빠듯하다)

[슬라이드 오탈자 — 인자 7개]
    drone.sendControlPosition16(0, 0, 3, 0, 5, 0, 0)   # 미션 2·3 슬라이드
`sendControlPosition16` 은 인자가 6개다. 7개를 넣으면

    TypeError: Drone.sendControlPosition16() takes 7 positional arguments but 8 were given

위치 명령에서 **예외가 나는 드문 경우**다. 인자 개수는 파이썬이 잡아 주지만,
타입(32 의 int 규칙)과 범위는 아무도 안 잡아 준다. 의도대로면 `(0, 0, 3, 5, 0, 0)`.

[두 함수는 단위만 다르다]
    sendControlPosition16(10, 0, 0, 5, 0, 0)  ==  sendControlPosition(1.0, 0, 0, 0.5, 0, 0)
강의 실습 코드는 상승·전진은 16 버전, 옆 이동은 실수 버전으로 섞어 쓴다.
여기서는 헷갈리지 않게 **실수 버전 하나로 통일**했다 (32 에 두 버전 비교가 있다).

[Z=0 은 "높이 유지" 다]
상승 다음의 전진 명령은 `positionZ` 가 0 이라 **올라간 높이를 그대로 유지**한 채 앞으로 간다.
게이트를 스치면 기체가 튕기므로, 처음에는 게이트 없이 높이·거리부터 맞춰 본다.

실행:  .venv/bin/python 35_mission_goal_circle.py
"""

import math
from time import sleep

from CodingDrone.drone import Drone

from drone_util import countdown, find_port

MISSION = 1  # 1 = 전진만 / 2 = 상승 + 전진 / 3 = 상승 + 전진 + 옆 이동

# 미션별 이동 계획 — (상승 m, 전진 m, 옆 이동 m)
#   상승 : 위 + / 아래 −      옆 이동 : 좌 + / 우 −
#   전진 값은 슬라이드 원본(1.0)이다. 실제 Goal 원까지는 2.0 전후가 필요하다.
PLANS = {
    1: (0.0, 1.0, 0.0),
    2: (0.3, 1.0, 0.0),
    3: (0.5, 1.0, -1.0),
}

UP_M, FORWARD_M, SIDE_M = PLANS[MISSION]
SPEED = 0.5  # 이동 속도 (m/s)


def wait_for(distance_m):
    """이동 대기 = 거리 ÷ 속도 + 여유 3초."""
    return math.ceil(abs(distance_m) / SPEED) + 3


def move(label, x=0.0, y=0.0, z=0.0):
    """한 구간 이동하고 도착할 때까지 기다린다. 0 이면 건너뛴다."""
    distance = max(abs(x), abs(y), abs(z))
    if distance == 0:
        return
    print(f"{label} {distance} meter")
    # (X 앞뒤, Y 좌우, Z 상하, 속도, heading 0, 회전속도 0)
    dron.sendControlPosition(x, y, z, SPEED, 0, 0)
    countdown(wait_for(distance), "이동 대기")


dron = Drone()

if not dron.open(find_port()):
    raise SystemExit("드론 연결 실패 — USB 연결을 확인하세요")

try:
    print(f"=== 미션 {MISSION} : 상승 {UP_M} / 전진 {FORWARD_M} / 옆 {SIDE_M} (m) ===")

    print("TakeOff")
    dron.sendTakeOff()
    countdown(5, "이륙 안정화")

    move("Go Up", z=UP_M)  # 미션 2·3 — 게이트 높이 맞추기
    move("Go Front", x=FORWARD_M)  # 전진 (게이트 통과)
    move("Go Side", y=SIDE_M)  # 미션 3 — 원이 옆으로 비껴 있을 때

    print("Landing")
    dron.sendLanding()
    countdown(5, "착지 대기")

finally:
    dron.sendLanding()
    sleep(0.1)
    dron.close()
    print("포트 닫음")
