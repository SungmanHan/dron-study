"""38. [과제] 경로 비행 중 장애물 반응 시스템   ⚠️ 실제로 이륙한다

    버튼 입력 → 이륙 → 5구간 경로 비행(방향 전환 4회) → 지정 위치 착륙
    3구간에서 전방 장애물을 만나면 오른쪽으로 비켜 지나간 뒤 경로로 복귀

[과제 조건과 구현 위치]
    1. 자유 경로, 방향 전환 4회 이상  →  LEGS (전진 → 우 → 전진 → 좌 → 후진)
    2. 버튼 입력 시 이륙 + 자율주행   →  wait_for_button()  (35~37 은 실행 즉시 이륙)
    3. 전방 장애물                    →  3구간 중간에 설치
    4. 장애물 회피                    →  avoid_obstacle()
    5. LED 안전=초록 / 경고=빨강      →  led_safe() / led_warning() / led_ready()
    6. 지정 위치 착륙                 →  이동을 전부 거리(m)로 계산 + 초과분 보정

[코스 배치도]  위에서 본 모습, 위쪽이 드론 앞(+X)

           (2) 오른쪽
        ┌──────────────┐
        │              │ (3) 전진 ← 이 구간만 전방 센서를 본다
     (1)│              │     [장애물]
     전진│              │
        │  (5) 후진    │
      [S]   ▼ [L] ◀────┘
     출발   착륙  (4) 왼쪽

    [S] 출발 = 바닥에 표시   [L] 착륙 = 출발점 정면으로 (1구간 + 3구간 − 5구간)

[왜 heading 을 끝까지 0 으로 두나]
모든 이동이 `sendControlPosition(X, Y, 0, 속도, 0, 0)` 이라 기체는 **계속 앞(+X)을 본 채로
게걸음**을 한다. 회전하면 그때마다 전방 센서가 다른 쪽을 보게 되는데, 3구간에서 앞을
감시하려면 센서가 진행 방향을 보고 있어야 한다. 그래서 돌지 않는다.

[왜 3구간만 STEP 씩 끊어 가나]
36 처럼 `sendControl` 로 계속 전진하면 **몇 m 왔는지 알 수가 없다.** 장애물이 어디서
나오든 착륙 지점은 같아야 하므로, 여기서는 0.1 m 씩 위치 명령으로 끊어 가며
`traveled` 를 센다. 센서는 한 조각마다 한 번 본다.

[착륙 지점을 고정하는 방법이 이 과제의 핵심이다]
회피는 "오른쪽 → 전진 `AVOID_FORWARD` → 왼쪽" 이라, 옆으로 나간 만큼은 되돌아오지만
**앞으로 간 거리는 남는다.** 그래서
    ① 회피 전진분을 `traveled` 에 더해 3구간에서 그만큼 덜 간다
    ② 그래도 3구간 목표를 넘겼으면(`overshoot`) 5구간 후진에서 그만큼 더 물러난다
②가 필요한 이유는, 넘어간 자리에서 그냥 뒤로 물러나면 **방금 피한 장애물에 다시 부딪히기**
때문이다. 옆으로 빠진 뒤(4구간)에 보정해야 안전하다.

[좁은 방이면 ROOM = "NARROW"]
거리를 대략 1/3 로 줄인 값이다. 다만 **속도는 1/3 로 줄이면 안 된다** — 위치 명령의 권장
속도는 0.5~2.0 m/s 인데 NARROW 의 0.17 / 0.1 m/s 는 그보다 한참 아래다.
라이브러리는 막지 않지만(위치 명령은 범위 검사가 없다) 기체가 굼뜨거나 한 조각을
제자리에서 흘려보낼 수 있다. 0.05 m 같은 짧은 조각도 마찬가지다.
**넓은 곳에서는 WIDE 로 돌릴 것.** NARROW 는 "좁아서 어쩔 수 없을 때" 의 타협이다.

[중단]
대기 중 Ctrl+C → `finally` 에서 정지 → 착륙 → 소등 → close.
창을 그냥 닫으면 파이썬만 죽고 드론은 마지막 명령을 유지한 채 계속 난다.

실행:  .venv/bin/python 38_assignment_route_obstacle.py
"""

from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import (
    ButtonEvent,
    ButtonFlagController,
    DataType,
    DeviceType,
    LightModeDrone,
)

from drone_util import find_port

ROOM = "WIDE"  # "WIDE" = 원래 설계값 / "NARROW" = 좁은 실내용 축소판

SETTINGS = {
    # 구간 거리(m) ·  3구간 전진 거리 · 속도 · 조각 · 조각 속도 · 감지 거리(mm) · 회피
    "WIDE": dict(
        leg1=1.0, side=1.0, leg3=1.5, leg5=0.5,
        speed=0.5, step=0.1, step_speed=0.3,
        stop_mm=400, avoid_side=-0.5, avoid_forward=0.8,
    ),
    "NARROW": dict(
        leg1=0.33, side=0.33, leg3=0.5, leg5=0.17,
        speed=0.17, step=0.05, step_speed=0.1,  # ⚠️ 권장 속도(0.5~2.0) 아래
        stop_mm=150, avoid_side=-0.17, avoid_forward=0.27,
    ),
}
CFG = SETTINGS[ROOM]

SPEED = CFG["speed"]
STEP = CFG["step"]
STEP_SPEED = CFG["step_speed"]
LEG3_M = CFG["leg3"]
STOP_MM = CFG["stop_mm"]
AVOID_SIDE = CFG["avoid_side"]  # 음수 = 오른쪽. 장애물 폭÷2 + 기체 폭÷2 + 여유
AVOID_FORWARD = CFG["avoid_forward"]  # 장애물 길이 + 기체 길이 + 여유

BUTTON_TIMEOUT = 60  # 버튼을 기다리는 최대 시간(초)

dron = Drone()
front_mm = 0  # 가장 최근 전방 거리 — event_range 가 갱신
button_pressed = False  # 조종기 버튼이 눌렸는지 — event_button 이 갱신


# ── 이벤트 핸들러 (백그라운드 수신 스레드가 호출 — 플래그만 세운다) ──────────

def event_range(range_data):
    global front_mm
    front_mm = range_data.front


def event_button(button):
    global button_pressed
    # 전원 버튼(TopRight, 0x0020)은 제외. "누르기 시작(Down)" 만 본다 —
    # 누르고 있으면 Press 가 계속 들어오기 때문이다.
    if (button.event == ButtonEvent.Down
            and button.button != 0
            and button.button != ButtonFlagController.TopRight.value):
        print(f"버튼 입력 : 0x{button.button:04X}")
        button_pressed = True


# ── LED — 색은 펌웨어가 만든다. interval·r·g·b 는 **int 전용** ──────────────

def led_ready():
    """대기 : 파랑 디밍 (interval = 디밍 속도)"""
    dron.sendLightModeColor(LightModeDrone.BodyDimming, 3, 0, 0, 255)


def led_safe():
    """안전 : 초록 점등 (Hold 모드의 interval = 밝기 0~255)"""
    dron.sendLightModeColor(LightModeDrone.BodyHold, 200, 0, 255, 0)


def led_warning():
    """경고 : 빨강 점멸 (Flicker 모드의 interval = 점멸 주기 ms)"""
    dron.sendLightModeColor(LightModeDrone.BodyFlicker, 150, 255, 0, 0)


def led_off():
    """소등 — 모드 계열은 끌 때까지 유지되므로 끝에 반드시 꺼 준다."""
    dron.sendLightManual(DeviceType.Drone, 0xFF, 0)


# ── 이동 ────────────────────────────────────────────────────────────────

def move(label, x=0.0, y=0.0, speed=None):
    """(x, y) m 만큼 이동하고 도착할 때까지 기다린다."""
    speed = speed or SPEED
    distance = max(abs(x), abs(y))
    if distance == 0:
        return
    print(f"{label} : X={x:+.2f} Y={y:+.2f} m")
    dron.sendControlPosition(x, y, 0, speed, 0, 0)
    sleep(distance / speed + 1.0)  # 거리 ÷ 속도 + 여유


def read_front():
    """전방 거리를 요청하고 최신 값을 돌려준다 (mm).

    돌려주는 건 요청의 응답이 아니라 **콜백이 마지막으로 써 둔 값**이다.
    응답이 늦으면 직전 값이 나오므로, 0.15초 정도는 기다려 준다.
    """
    dron.sendRequest(DeviceType.Drone, DataType.Range)
    sleep(0.15)
    return front_mm


def avoid_obstacle():
    """오른쪽으로 비킴 → 전진 → 원래 줄로 복귀. 앞으로 간 거리를 돌려준다."""
    led_warning()
    print(f"!! 장애물 {front_mm} mm → 회피")
    sleep(1.0)  # 멈춘 채로 1초 (빨간불을 눈으로 확인)

    move("  회피-옆으로", 0.0, AVOID_SIDE)
    move("  회피-전진", AVOID_FORWARD, 0.0)
    move("  회피-복귀", 0.0, -AVOID_SIDE)

    led_safe()
    print("회피 완료")
    return AVOID_FORWARD


def leg3_with_sensing():
    """3구간 : STEP 씩 전진하며 전방 감시. 목표를 넘어간 거리를 돌려준다."""
    traveled = 0.0
    avoided = False  # 회피는 한 번만

    print(f"3구간 전진 {LEG3_M} m (전방 감시)")
    while traveled < LEG3_M - 0.001:
        front = read_front()
        print(f"  진행 {traveled:.2f} m / 전방 {front} mm")

        if not avoided and 0 < front < STOP_MM:  # 0 은 측정 실패
            traveled += avoid_obstacle()
            avoided = True
            continue

        # 마지막 조각은 남은 만큼만. 부동소수 오차로 0.0999999… 같은 값이 나가지 않게 반올림
        step = round(min(STEP, LEG3_M - traveled), 3)
        dron.sendControlPosition(step, 0, 0, STEP_SPEED, 0, 0)
        sleep(step / STEP_SPEED + 0.3)
        traveled += step

    overshoot = max(0.0, traveled - LEG3_M)
    if overshoot > 0:
        print(f"  3구간 {overshoot:.2f} m 초과 → 5구간에서 보정")
    return overshoot


def wait_for_button():
    """조종기 버튼을 기다린다. 제한 시간 안에 안 눌리면 False."""
    print(f"조종기 아무 버튼(전원 제외)을 누르면 출발합니다 — 최대 {BUTTON_TIMEOUT}초")
    for _ in range(BUTTON_TIMEOUT * 10):
        if button_pressed:
            return True
        sleep(0.1)
    return False


# ── 메인 ────────────────────────────────────────────────────────────────

if not dron.open(find_port()):
    raise SystemExit("드론 연결 실패 — USB 연결을 확인하세요")

dron.setEventHandler(DataType.Range, event_range)
dron.setEventHandler(DataType.Button, event_button)

flying = False  # 이륙했는지 — finally 에서 착륙 여부를 가른다

try:
    print(f"=== ROOM = {ROOM} / 착륙 지점은 출발점 정면 "
          f"{CFG['leg1'] + LEG3_M - CFG['leg5']:.2f} m ===")

    led_ready()
    if not wait_for_button():
        print("버튼 입력이 없어 종료합니다")
    else:
        led_safe()
        print("TakeOff")
        dron.sendTakeOff()
        flying = True
        sleep(5)  # 이륙·호버링 안정화

        move("1구간 전진", x=CFG["leg1"])  # ─┐
        move("2구간 오른쪽", y=-CFG["side"])  # 전환 1
        overshoot = leg3_with_sensing()  # 전환 2 (+ 회피 시 추가 전환)
        move("4구간 왼쪽", y=CFG["side"])  # 전환 3
        move("5구간 후진", x=-(CFG["leg5"] + overshoot))  # 전환 4 + 초과분 보정

        print("착륙 지점 도착")

except KeyboardInterrupt:
    print("사용자 중단")
    led_warning()

finally:
    if flying:
        dron.sendControl(0, 0, 0, 0)  # 남은 이동 명령 중립화
        sleep(0.1)
        print("Landing")
        dron.sendLanding()
        sleep(5)
    led_off()
    sleep(0.1)
    dron.close()
    print("포트 닫음")
