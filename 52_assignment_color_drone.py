r"""52. [과제] 색상 인식으로 드론 상하좌우 제어 ⚠️ 실제로 이륙한다

24 강 과제 제출본. 물체(하늘색 컵 등) 하나를 색으로 추적해서 드론을 그 방향으로 움직인다.
화면 가운데 40% 는 정지 영역이고, 물체를 놓치면 잠깐 뒤 제자리 호버링으로 돌아온다.

키:  `t` 이륙   `l` 착륙   `space` 비상 정지   `ESC` 착륙 후 종료
    (OpenCV 창을 클릭해 포커스를 준 뒤, **영문 입력 상태**에서)

[실행 순서 — 이 순서를 지킬 것]
    1) TUNE = True, DRY_RUN = True   트랙바로 **물체만 하얗게** 남도록 맞춘다.
                                     콘솔에 찍힌 값을 COLOR_RANGES 에 옮겨 적는다.
    2) TUNE = False, DRY_RUN = True  방향 판정(UP/DOWN/LEFT/RIGHT)이 맞는지 화면으로 확인.
    3) DRY_RUN = False               드론을 띄운다. 처음에는 세기를 20 정도로 낮춰서.

[51 과 무엇이 다른가]

| | `51` (강의 예제) | `52` (과제) |
|---|---|---|
| HSV 범위 | 상수로 고정 | **트랙바로 그 자리에서 조절**(`TUNE`) |
| 화면 저장 | 없음 | `result.mp4` 로 녹화 (제출용) |
| 판단 | 예제2 = 이착륙 / 예제3 = 이동 | 이동 한 가지 |

[과제 원본 코드에서 고친 것]

1. **포트를 하드코딩하지 않는다.** 원본은 `DRONE_PORT = "/dev/cu.usbmodem31A9388730351"` 인데
   USB 포트를 바꿔 꽂으면 숫자가 달라진다. 저장소 공통 `find_port()` 로 매번 탐색한다.
2. **`open()` 의 반환값을 본다.** `Drone.open()` 은 실패해도 예외를 던지지 않고 `False` 를
   돌려준다(01~03 참고). 확인하지 않으면 연결도 안 된 채 이륙 명령을 보내며 계속 돈다.
3. **녹화 fps 를 20 으로 고정하지 않는다.** 색 추적이 무거우면 실제로는 초당 10 장 남짓인데
   20 으로 저장하면 **빨리 감기처럼** 재생된다(47 참고). 측정한 처리 속도를 쓴다.
4. 키 확인용 `print("key:", key)` 디버그 줄을 뺐다. 매 프레임 콘솔을 채운다.

[녹화 크기는 화면과 같아야 한다]
저장하는 그림은 원본과 마스크를 가로로 붙인 것이라 너비가 두 배다.
`VideoWriter` 에 `(FRAME_W * 2, FRAME_H)` 를 넘기지 않으면 **에러 없이 빈 파일**이 된다(47).

[안전]
- 비상 정지(`space`)는 모터를 즉시 끈다 — 드론은 **그 자리에서 떨어진다.** 낮게 띄워서 연습할 것.
- `finally` 에서 정지 → 착륙 → `close()` 까지 보장한다. 창을 그냥 닫지 말고 `ESC` 로 끝낼 것.
- 프로펠러 가드, 넓은 실내. 물체는 드론이 아니라 **카메라 앞**에서 움직인다.
"""

from time import sleep, time

import cv2 as cv
import numpy as np

DRY_RUN = True  # True = 드론 없이 인식·판단만. 확인 뒤 False
TUNE = False  # True = HSV 트랙바 창
RECORD = True  # result.mp4 저장 (제출용)
SOURCE = 0  # 0 (카메라) / "demo" (합성 영상)
TARGET = "skyblue"

FRAME_W, FRAME_H = 640, 480
MIN_AREA = 500  # 이보다 작은 덩어리는 잡음
EDGE = 0.3  # 가장자리 30% 에 들어가면 이동 (가운데 40% 는 정지)
ROLL_POWER = 40  # int. 처음에는 20 정도로 낮춰서 방향부터 확인
THROTTLE_POWER = 40
SEND_INTERVAL = 0.1
LOST_HOLD = 0.7  # 놓쳐도 이 시간까지는 직전 명령 유지
TAKEOFF_SETTLE = 3.0  # 이륙 직후 조종 명령을 참는 시간
MIRROR = True  # 화면 오른쪽 = 내 오른쪽

COLOR_RANGES = {
    "skyblue": [((85, 60, 120), (105, 255, 255))],
    "blue": [((110, 100, 30), (130, 255, 255))],
    "yellow": [((20, 100, 100), (35, 255, 255))],
    "green": [((40, 80, 60), (80, 255, 255))],
    "red": [((0, 150, 80), (8, 255, 255)), ((170, 150, 80), (179, 255, 255))],
}

TUNER = "HSV Tuner"
BOX_COLOR = (255, 0, 255)
FONT = cv.FONT_HERSHEY_SIMPLEX
_last_printed = None


class FakeDrone:
    """DRY_RUN 용. 실제 Drone 과 같은 이름·반환값을 흉내 낸다."""

    def open(self, port=None):
        print(f"[DRY] open {port}")
        return True  # 진짜 open() 도 bool 을 돌려준다

    def sendTakeOff(self):
        print("[DRY] takeOff")

    def sendLanding(self):
        print("[DRY] landing")

    def sendStop(self):
        print("[DRY] stop")

    def sendControl(self, roll, pitch, yaw, throttle):
        pass

    def close(self):
        print("[DRY] close")


def connect():
    if DRY_RUN:
        drone = FakeDrone()
        drone.open()
        return drone

    from CodingDrone.drone import Drone

    from drone_util import find_port

    drone = Drone()
    if not drone.open(find_port()):  # False 를 돌려줄 뿐 예외가 아니다
        raise SystemExit("드론 연결에 실패했습니다. 동글과 전원을 확인하세요.")
    return drone


def setup_tuner(first_range):
    (h_lo, s_lo, v_lo), (h_hi, _, _) = first_range
    cv.namedWindow(TUNER)
    for name, val, mx in (("H low", h_lo, 179), ("H high", h_hi, 179),
                          ("S low", s_lo, 255), ("V low", v_lo, 255)):
        cv.createTrackbar(name, TUNER, val, mx, lambda _x: None)


def read_tuner():
    """트랙바 값을 읽고, 바뀌면 COLOR_RANGES 에 붙여 넣을 모양으로 찍어 준다."""
    global _last_printed
    ranges = [((cv.getTrackbarPos("H low", TUNER), cv.getTrackbarPos("S low", TUNER),
                cv.getTrackbarPos("V low", TUNER)),
               (cv.getTrackbarPos("H high", TUNER), 255, 255))]
    if ranges != _last_printed:
        print(f'    "{TARGET}": {ranges},')
        _last_printed = ranges
    return ranges


def make_demo_frames(n=150):
    ball = cv.cvtColor(np.uint8([[[95, 200, 230]]]), cv.COLOR_HSV2BGR)[0][0].tolist()
    path = [(320, 240), (320, 60), (60, 240), (580, 240), (320, 420), (320, 240), None]
    for i in range(n):
        frame = np.full((FRAME_H, FRAME_W, 3), 60, np.uint8)
        pos = path[min(i * len(path) // n, len(path) - 1)]
        if pos is not None:
            cv.circle(frame, pos, 45, ball, -1)
        yield frame


def make_mask(frame, ranges):
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    mask = None
    for lower, upper in ranges:
        part = cv.inRange(hsv, np.array(lower), np.array(upper))
        mask = part if mask is None else cv.bitwise_or(mask, part)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
    return cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)


def find_box(mask):
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    biggest = max(contours, key=cv.contourArea)
    if cv.contourArea(biggest) < MIN_AREA:
        return None
    return cv.boundingRect(biggest)


def decide(center):
    """중심 좌표 → (roll, throttle, 표시). y 는 위쪽이 0 이다."""
    if center is None:
        return 0, 0, "LOST - HOVER"
    cx, cy = center
    roll = throttle = 0
    labels = []
    if cy < FRAME_H * EDGE:
        throttle, labels = THROTTLE_POWER, labels + ["UP"]
    elif cy > FRAME_H * (1 - EDGE):
        throttle, labels = -THROTTLE_POWER, labels + ["DOWN"]
    if cx < FRAME_W * EDGE:
        roll, labels = -ROLL_POWER, labels + ["LEFT"]
    elif cx > FRAME_W * (1 - EDGE):
        roll, labels = ROLL_POWER, labels + ["RIGHT"]
    return roll, throttle, " + ".join(labels) if labels else "CENTER - HOVER"


def draw_overlay(frame, box, label, flying, fps):
    """정지 영역, 물체 박스, 지금 명령을 그린다 (제출 영상에서 보이게)."""
    cv.rectangle(frame, (int(FRAME_W * EDGE), int(FRAME_H * EDGE)),
                 (int(FRAME_W * (1 - EDGE)), int(FRAME_H * (1 - EDGE))), (200, 200, 200), 1)
    if box is not None:
        x, y, w, h = box
        cv.rectangle(frame, (x, y), (x + w, y + h), BOX_COLOR, 3)
        cv.circle(frame, (x + w // 2, y + h // 2), 5, BOX_COLOR, -1)
        cv.putText(frame, f"({x + w // 2}, {y + h // 2})", (x, max(y - 10, 20)),
                   FONT, 0.6, BOX_COLOR, 2)
    state = "FLYING" if flying else "LANDED"
    if DRY_RUN:
        state += " (DRY RUN)"
    cv.putText(frame, f"{TARGET.upper()} | {state} | {fps:.1f}fps", (10, 25),
               FONT, 0.7, (255, 255, 255), 2)
    cv.putText(frame, f"CMD: {label}", (10, FRAME_H - 15), FONT, 0.8, (0, 255, 255), 2)


def emergency_stop(drone):
    """모터를 즉시 끈다. 드론은 그 자리에서 떨어지므로 낮을 때만."""
    print("!!! EMERGENCY STOP !!!")
    drone.sendControl(0, 0, 0, 0)
    for _ in range(5):  # 한 번은 놓칠 수 있다
        drone.sendStop()
        sleep(0.05)


def main():
    ranges = COLOR_RANGES[TARGET]
    if TUNE:
        setup_tuner(ranges[0])

    frames = make_demo_frames() if SOURCE == "demo" else None
    cap = None if frames else cv.VideoCapture(SOURCE)
    if cap is not None:
        if not cap.isOpened():
            raise SystemExit("카메라를 열지 못했습니다. 카메라 권한을 확인하세요.")
        cap.set(cv.CAP_PROP_FRAME_WIDTH, FRAME_W)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, FRAME_H)

    drone = connect()
    writer = None
    flying = False
    takeoff_at = last_sent = last_seen = 0.0
    last_cmd = None
    held = (0, 0, "LOST - HOVER")
    fps_now = 0.0
    prev = time()
    frame_count = 0

    try:
        while True:
            if frames is not None:
                frame = next(frames, None)
                if frame is None:
                    break
            else:
                ok, frame = cap.read()
                if not ok:
                    print("카메라 프레임을 읽지 못했습니다.")
                    break
                frame = cv.resize(frame, (FRAME_W, FRAME_H))
            if MIRROR:
                frame = cv.flip(frame, 1)
            frame_count += 1

            if TUNE:
                ranges = read_tuner()
            mask = make_mask(frame, ranges)
            box = find_box(mask)
            center = None if box is None else (box[0] + box[2] // 2, box[1] + box[3] // 2)

            roll, throttle, label = decide(center)
            now = time()
            if center is not None:
                last_seen, held = now, (roll, throttle, label)
            elif now - last_seen < LOST_HOLD:
                roll, throttle, label = held[0], held[1], held[2] + " (hold)"
            if not flying:
                label = "LANDED (press t)"

            if flying and now - takeoff_at >= TAKEOFF_SETTLE and now - last_sent >= SEND_INTERVAL:
                drone.sendControl(roll, 0, 0, throttle)  # 네 값 모두 int
                last_sent = now
                if (roll, throttle) != last_cmd:
                    print(f"{label:20s} roll={roll:4d} throttle={throttle:4d} center={center}")
                    last_cmd = (roll, throttle)

            fps_now = 0.9 * fps_now + 0.1 * (1.0 / max(now - prev, 1e-6))
            prev = now

            draw_overlay(frame, box, label, flying, fps_now)
            view = np.hstack([frame, cv.cvtColor(mask, cv.COLOR_GRAY2BGR)])  # 왼쪽 영상 / 오른쪽 마스크
            cv.imshow("Color Drone Control", view)

            if RECORD:
                if writer is None and frame_count > 20:  # 처리 속도가 안정된 뒤에 연다
                    rec_fps = max(round(fps_now), 1)
                    writer = cv.VideoWriter("result.mp4", cv.VideoWriter_fourcc(*"mp4v"),
                                            rec_fps, (FRAME_W * 2, FRAME_H))  # 크기는 view 와 같게
                    if not writer.isOpened():
                        print("result.mp4 를 열지 못했습니다 — 녹화 없이 계속합니다.")
                        writer = None
                    else:
                        print(f"녹화 시작: result.mp4 ({FRAME_W * 2}x{FRAME_H}, {rec_fps}fps)")
                elif writer is not None:
                    writer.write(view)

            key = cv.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
            if key == ord("t") and not flying:
                drone.sendTakeOff()
                flying, takeoff_at = True, now
            elif key == ord("l") and flying:
                drone.sendControl(0, 0, 0, 0)
                drone.sendLanding()
                flying = False
            elif key == ord(" "):
                emergency_stop(drone)
                flying = False
    except KeyboardInterrupt:
        print("Ctrl+C")
    finally:
        # 어떻게 끝나든 착륙 → 해제. 녹화 파일도 닫아야 재생된다(47).
        if flying:
            drone.sendControl(0, 0, 0, 0)
            drone.sendLanding()
            for i in range(3, 0, -1):
                print("Landing", i)
                sleep(1)
        sleep(0.1)
        drone.close()
        if cap is not None:
            cap.release()
        if writer is not None:
            writer.release()
            print("녹화 저장: result.mp4")
        cv.destroyAllWindows()
        cv.waitKey(1)


if __name__ == "__main__":
    main()
