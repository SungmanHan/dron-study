"""36. 미션 4·5 — 전진하다 장애물을 만나면 멈추고 반응한다   ⚠️ 실제로 이륙한다

    MODE = 1   전진 → 장애물 감지 → 착륙                (미션 4)
    MODE = 2   전진 → 장애물 감지 → 옆으로 1 m → 착륙   (미션 5)

35 까지는 **정해진 거리**를 갔다. 여기서는 얼마나 가야 하는지 모른 채 출발해서
전방 센서가 "이제 멈춰" 라고 할 때까지 간다. 24 와 센서는 같지만 24 는 제자리
호버링 중 손을 대는 것이었고, 여기서는 **움직이면서** 본다.

[이동 방식 두 가지를 한 비행에서 섞는다]
    전진 : sendControl(0, POWER, 0, 0)          거리를 모르니 "세기" 로 간다
    회피 : sendControlPosition(0, SIDE, 0, ...)  거리를 아니까 "거리" 로 간다
둘 다 `DataType.Control` 이라 나중에 보낸 쪽이 이긴다. 그래서 회피 전에
`sendControl(0, 0, 0, 0)` 으로 전진을 끊고, 관성이 죽도록 0.5초 쉰 뒤 옆으로 보낸다.
(슬라이드 그림의 "20% 출력으로 이동" 이 이 세기 값이다 — 코드 값은 25)

[구조 — 콜백은 플래그만 세운다]
    setEventHandler(DataType.Range, event_range)   ① 등록 (루프 밖 1회)
    sendRequest(DeviceType.Drone, DataType.Range)  ② 요청 (루프 안 반복)
    def event_range(range_data): ...               ③ 응답이 오면 수신 스레드가 호출
콜백은 **백그라운드 수신 스레드**에서 불린다. 거기서 비행 명령까지 처리하면 안 된다.

[강의 원본에서 고친 것]
① `global` 누락 — 콜백 안에서 `value = False` 라고 쓰면 파이썬은 그 이름을 **지역 변수**로
   만든다. 전역 `value` 는 끝까지 True 라 메인 루프의 `if value == False: break` 가
   **영영 실행되지 않는다.** 콜백이 착륙시켜 놓고도 루프는 계속 전진 명령을 보낸다.
② 감지 구간이 좁다 — `300 < front < 400` 은 30~40 cm 구간에서만 반응한다. 빠르게 지나가면
   그 구간을 건너뛴다 → `0 < front < STOP_DISTANCE` (0 은 측정 실패라 제외).
③ 콜백 안의 `sleep(2)` (미션 5) — 수신 스레드가 2초 멈추면 그동안 들어온 데이터가 전부
   밀린다. 게다가 콜백은 값이 올 때마다 불려서 이동·착륙 명령이 중복된다.
   → 콜백은 플래그만, 정지·회피·착륙은 메인 루프에서 한 번만.
④ `finally` 에 `close()` 뿐 — Ctrl+C 로 멈추면 드론이 전진 명령을 받은 채 연결만 끊긴다.
   → 정지 → 착륙 → close.
⑤ 핸들러를 루프 안에서 매번 재등록 → 밖으로. 오타 `"FORWORD"` → `"FORWARD"`.

[미션 포인트]
- `STOP_DISTANCE` 와 `FORWARD_POWER` 는 같이 조정한다. 빠를수록 멈추는 데 거리가 더 든다.
- 장애물은 **센서 높이에 걸리는 크기**여야 한다. 낮은 물체는 드론 밑으로 지나간다.
- MODE 2 에서 정지 거리가 너무 짧으면 옆으로 빠지다가 장애물 모서리에 걸린다.
  장애물 폭의 절반 + 기체 폭의 절반 + 여유만큼 옆으로 가야 한다.
- 처음에는 `FORWARD_POWER` 를 15~20 으로 낮추고 손을 대 보며 반응 거리를 확인한다.

실행:  .venv/bin/python 36_mission_obstacle_stop.py
"""

from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import DataType, DeviceType

from drone_util import countdown, find_port

MODE = 1  # 1 = 감지 후 착륙 / 2 = 감지 후 옆으로 피한 뒤 착륙

STOP_DISTANCE = 400  # mm. 전방이 이보다 가까우면 장애물 (400 mm = 40 cm)
FORWARD_POWER = 25  # 전진 세기 — sendControl 의 pitch (-100 ~ 100, **int 전용**)
INTERVAL = 0.1  # 요청·전진 주기(초)

SIDE_M = -1.0  # MODE 2 — 회피 거리 (m). 좌 + / 우 −
SIDE_SPEED = 0.5  # MODE 2 — 회피 속도 (m/s)
SIDE_WAIT = 5  # 1 m ÷ 0.5 m/s = 2초 + 여유 (원본 2초는 여유가 없다)

dron = Drone()
front_mm = 0  # 가장 최근 전방 거리
detected = False  # 콜백이 세우는 플래그


def event_range(range_data):  # 원본 인자명 range → 내장 함수 range() 를 가린다
    global front_mm, detected  # ← 이 줄이 없으면 아래 대입이 전부 지역 변수가 된다

    front_mm = range_data.front
    print(f"front : {front_mm} mm")

    if 0 < front_mm < STOP_DISTANCE:
        detected = True  # 콜백이 하는 일은 여기까지. 명령은 메인 루프에서.


if not dron.open(find_port()):
    raise SystemExit("드론 연결 실패 — USB 연결을 확인하세요")

dron.setEventHandler(DataType.Range, event_range)  # 루프 밖에서 1회

try:
    print("TakeOff — 중단하려면 Ctrl+C (Jupyter 는 중단 ■)")
    dron.sendTakeOff()
    countdown(5, "이륙 안정화")

    # 1) 센서를 보며 전진 — 멈출 지점은 센서가 정한다
    while not detected:
        dron.sendRequest(DeviceType.Drone, DataType.Range)
        sleep(INTERVAL)  # 응답이 와서 콜백이 실행될 시간
        dron.sendControl(0, FORWARD_POWER, 0, 0)  # 유지되지 않으므로 계속 보낸다
        sleep(INTERVAL)
        print("FORWARD")

    print(f"장애물 감지 : {front_mm} mm")

    # 2) 전진을 끊는다 — 이 한 줄이 없으면 마지막 전진 명령이 계속 살아 있다
    dron.sendControl(0, 0, 0, 0)
    sleep(0.5)  # 관성이 죽을 시간

    # 3) MODE 2 — 옆으로 피해 Goal 원 위로
    if MODE == 2:
        print(f"Go Side {abs(SIDE_M)} meter")
        dron.sendControlPosition(0, SIDE_M, 0, SIDE_SPEED, 0, 0)
        countdown(SIDE_WAIT, "회피 대기")

    print("Landing")
    dron.sendLanding()
    countdown(5, "착지 대기")

finally:
    dron.sendControl(0, 0, 0, 0)  # 남은 이동 명령 중립화
    sleep(0.1)
    dron.sendLanding()  # 원본 finally 에는 close() 밖에 없었다
    sleep(0.1)
    dron.close()
    print("포트 닫음")
