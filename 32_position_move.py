"""32. 거리로 움직이기 — `sendControlPosition` / `sendControlPosition16`   ⚠️ 실제로 이륙한다

    이륙 → 호버링 → 앞으로 1 m → 오른쪽으로 1 m → 착륙   ("ㄱ" 자 경로)

28 까지 쓴 `sendControl(roll, pitch, yaw, throttle)` 은 **조종기 스틱을 얼마나 기울일지**를
보내는 것이라, "얼마나 갈지" 는 시간으로 가늠할 수밖에 없었다.
여기서 쓰는 위치 명령은 **거리(m)와 속도(m/s)를 직접** 지정한다.

    sendControlPosition(positionX, positionY, positionZ, velocity, heading, rotationalVelocity)

| 인자 | 단위 | 범위(펌웨어) | 의미 |
|---|---|---|---|
| positionX | m | -10.0 ~ 10.0 | 앞 + / 뒤 −   |
| positionY | m | -10.0 ~ 10.0 | **좌 + / 우 −**  ← 직관과 반대 |
| positionZ | m | -10.0 ~ 10.0 | 위 + / 아래 − |
| velocity  | m/s | 0.5 ~ 2.0  | 이동 속도 |
| heading   | ° | -360 ~ 360   | **좌회전 + / 우회전 −** (34 에서 사용) |
| rotationalVelocity | °/s | 10 ~ 360 | 회전 속도 |

[함정 ① — 한 호출 안에서 int 규칙이 갈린다]
라이브러리 검사(`CodingDrone/drone.py`)를 그대로 옮기면,

    sendControlPosition     x·y·z·velocity 는 float 또는 int 허용
                            **heading·rotationalVelocity 는 int 전용**  (내부 pack '<ffffhh')
    sendControlPosition16   **여섯 개 전부 int 전용**                    (내부 pack '<hhhhhh')

어긋나면 부저·LED 와 똑같이 **예외 없이 `None` 을 반환하고 끝난다.** 드론은 가만히 있고
에러도 안 나므로 "명령이 안 먹네" 로만 보인다. 특히 아래 두 줄이 조용히 실패한다.

    dron.sendControlPosition(1.0, 0, 0, 0.5, -90.0, 45)   # heading 이 float → 무시
    dron.sendControlPosition16(10, 0, 0, 0.5, 0, 0)       # velocity 가 float → 무시

[함정 ② — 범위를 넘겨도 에러가 안 난다]
`sendControl` 은 내부가 `pack('<bbbb')` 라 100 을 넘기면 `struct.error` 로 터졌다.
위치 명령은 int16(±32767) / float 이라 **웬만한 값이 다 통과한다.** 검사도 없다.
표의 "-10.0 ~ 10.0" 은 펌웨어 쪽 제한이지 라이브러리가 막아 주는 값이 아니다.
→ 단위를 잘못 쓰면 **에러 대신 드론이 날아간다.** 슬라이드에 "거리 100 이 1미터" 라고
적힌 오탈자를 그대로 따라 쓰면 `sendControlPosition16(100, ...)` = 10 m 전진이 된다.
실습 코드 쪽이 맞다 — **1 m = 10, 0.5 m/s = 5** (×10 한 정수).

[함정 ③ — 비블로킹이다]
`sendControlWhile` 과 달리 위치 명령은 보내고 **바로 리턴**한다. 기다리지 않고 다음
명령을 보내면 앞 명령을 덮어써서 대각선으로 가거나 그냥 무시된다.

    대기 시간 = 거리 ÷ 속도 + 여유 2~3초        1 m ÷ 0.5 m/s = 2초 → 5초 대기

[두 함수는 같은 명령이다]
`sendControlPosition` 은 20바이트(`<ffffhh`), `sendControlPosition16` 은 12바이트(`<hhhhhh`)로
둘 다 `DataType.Control` 로 나간다 — 드론은 길이를 보고 구분한다. 어느 쪽을 써도 결과는 같다.
아래 코드는 전진에 `16` 을, 우이동에 실수판을 써서 둘을 나란히 보여준다(강의 예제4 그대로).

[위치 이동은 드론 기준이다]
"앞" 은 방의 고정된 방향이 아니라 **드론이 지금 바라보는 쪽**이다. 그래서 전진 뒤의
우이동은 전진이 끝난 지점에서 시작되고, 경로가 "ㄱ" 자가 된다. 34 는 이 성질을 쓴다.

실행:  .venv/bin/python 32_position_move.py
"""

import math
from time import sleep

from CodingDrone.drone import Drone

from drone_util import countdown, find_port

DIST_M = 1.0  # 한 번에 이동할 거리 (m)
SPEED = 0.5  # 이동 속도 (m/s)

# 거리 ÷ 속도 + 여유. 거리를 늘리면 대기도 같이 늘어난다.
MOVE_WAIT = math.ceil(DIST_M / SPEED) + 3

# ×10 정수판에 넘길 값. int() 로 자르면 0.1 같은 값에서 밀릴 수 있어 round() 를 쓴다.
DIST_10 = round(DIST_M * 10)  # 1.0 m → 10
SPEED_10 = round(SPEED * 10)  # 0.5 m/s → 5

dron = Drone()

if not dron.open(find_port()):
    raise SystemExit("드론 연결 실패 — USB 연결을 확인하세요")

try:
    # 1) 이륙
    print("TakeOff")
    dron.sendTakeOff()
    countdown(5, "이륙 안정화")

    # 2) 호버링 — 이동 전에 자세를 안정시킨다. 3.6초간 블로킹.
    print("Hovering")
    dron.sendControlWhile(0, 0, 0, 0, 3600)

    # 3) 앞으로 1 m — ×10 정수판. 여섯 값 모두 int 여야 한다.
    print(f"Go Front {DIST_M} meter")
    dron.sendControlPosition16(DIST_10, 0, 0, SPEED_10, 0, 0)
    countdown(MOVE_WAIT, "이동 대기")

    # 4) 오른쪽으로 1 m — 실수판. Y축은 좌 + / 우 − 이므로 오른쪽은 음수다.
    #    heading·rotationalVelocity 자리의 0 은 int 여야 한다(0.0 이면 조용히 무시).
    print(f"Go Right {DIST_M} meter")
    dron.sendControlPosition(0, -DIST_M, 0, SPEED, 0, 0)
    countdown(MOVE_WAIT, "이동 대기")

    # 5) 착륙
    print("Landing")
    dron.sendLanding()
    countdown(5, "착지 대기")

finally:
    dron.sendLanding()
    sleep(0.1)
    dron.close()
    print("포트 닫음")
