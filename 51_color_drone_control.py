r"""51. 색으로 드론 제어 — 이착륙 / 상하좌우 ⚠️ 실제로 이륙한다

24 강 예제2·3. 두 예제는 같은 골격에 **판단 규칙만 다르다.**

    MODE = 1   공이 화면 위쪽이면 이륙, 아래쪽이면 착륙   (예제2)
    MODE = 2   공 위치에 따라 상승·하강·좌·우 이동        (예제3)

    DRY_RUN = True   드론 없이 인식과 판단만 확인 (명령은 콘솔에만) ← 먼저 이걸로
    SOURCE = "demo"  카메라도 없이 확인 (50 의 합성 영상)

키:  `t` 이륙   `l` 착륙   `space` 비상 정지   `ESC` 착륙 후 종료

[sendControl(roll, pitch, yaw, throttle)]
각 값 -100~100 의 **int**. `roll` 우 +, `pitch` 전진 +, `yaw` 우회전 +, `throttle` 상승 +.
float 을 넣으면 라이브러리가 조용히 무시하고(28 참고), 범위를 넘으면 `struct.error` 로 터진다.

[강의 예제2 에서 고친 것]

1. **시작하자마자 이륙한다.** `height = 0` 으로 시작하는데 판단이 `if height < 300: sendTakeOff()`
   라서, 공을 들기도 전에 첫 프레임부터 이륙 명령이 나간다. → 이 파일은 `t` 키로만 이륙한다.
2. **매 프레임 명령을 보낸다.** 초당 수십 번 `sendTakeOff()`/`sendLanding()` 이 나가 통신이 밀린다.
   → 상태가 바뀔 때만 보낸다.
3. **공이 사라져도 마지막 값이 남는다.** 위에서 공을 치우면 계속 이륙 상태다.
   → 못 찾으면 잠깐(`LOST_HOLD`)만 유지하고 그다음엔 정지로 돌린다.
4. **끝나도 드론은 그대로 난다.** ESC 로 루프만 빠져나오고 착륙·`close()` 가 없다.
   → `try/finally` 로 착륙까지 보장한다.

예제3 은 아예 **연결하자마자 이륙**하고 5 초를 기다린다(`sendTakeOff()` + `sleep(5)`).
손 뗄 틈이 없어서 기본값은 `t` 키로 바꿨다. 강의대로 보려면 `AUTO_TAKEOFF = True`.

[강의 예제3 — 슬라이드 코드와 영상 코드가 다르다]

| | 슬라이드 | 영상(최종) |
|---|---|---|
| 상승·하강 판단 | `width`(x) | **`height`(y)** |
| 좌·우 판단 | `height`(y) | **`width`(x)** |
| 오른쪽 조건 | `500 < height < 600` | `500 < width < 600` |

슬라이드대로 치면 오른쪽 이동이 **영원히 일어나지 않는다.** 화면 높이가 480 이라
`height` 가 500 을 넘을 수 없기 때문이다. 축이 뒤바뀐 실수다.
슬라이드에는 매 루프 `sendControl(0, 0, 0, 0)` + `sleep(0.1)` 도 들어 있는데,
이동 명령이 바로 정지 명령으로 덮여서 거의 움직이지 않는다.

[roll 부호는 "거울이냐"에 달렸다]
웹캠 원본은 거울 반전이 아니라서, 내가 공을 오른쪽으로 옮기면 화면에서는 왼쪽으로 간다.
강의 영상이 화면 왼쪽에 `roll +50` 을 준 이유가 이것이다.
이 파일은 `MIRROR = True` 로 **먼저 좌우를 뒤집어** 화면 오른쪽 = 내 오른쪽으로 맞추고,
그래서 화면 오른쪽에 `roll +` 를 준다. 드론이 나를 보고 있으면 또 반대가 되니
**낮은 세기로 방향부터 확인**할 것.

[가운데는 "아무 명령 없음" 이 아니라 "정지 명령"]
드론은 마지막 명령을 유지한다. 가운데 영역에서 아무것도 안 보내면 하던 이동을 계속한다.
`sendControl(0, 0, 0, 0)` 을 보내야 멈춘다 — 28 강의 `else: sendControl(0,0,0,0)` 과 같은 이야기.
"""

from time import sleep, time

import cv2 as cv
import numpy as np

MODE = 1  # 1 = 이착륙(예제2) / 2 = 상하좌우(예제3)
DRY_RUN = True  # True = 드론 없이 판단만. 확인 뒤 False
SOURCE = 0  # 0 (카메라) / "demo" (합성 영상)
TARGET = "skyblue"
AUTO_TAKEOFF = False  # 강의 예제3 처럼 시작하자마자 이륙. ⚠️ 손 뗄 틈이 없다 — 기본은 t 키

FRAME_W, FRAME_H = 640, 480
MIN_AREA = 500
MIRROR = True  # 좌우 반전 — 화면 오른쪽 = 내 오른쪽

TAKEOFF_LINE = FRAME_H * 0.4  # MODE 1 — 이 선보다 위면 이륙
EDGE = 0.3  # MODE 2 — 가장자리 30% 에 들어가면 이동 (가운데 40% 는 정지)
ROLL_POWER = 40  # int 여야 한다
THROTTLE_POWER = 40
SEND_INTERVAL = 0.1  # 명령 전송 간격(초). 매 프레임 보내면 통신이 밀린다
LOST_HOLD = 0.7  # 공을 놓쳐도 이 시간까지는 직전 명령 유지
TAKEOFF_SETTLE = 3.0  # 이륙 직후 이 시간 동안은 조종 명령을 보내지 않는다

COLOR_RANGES = {
    "skyblue": [((85, 60, 120), (105, 255, 255))],
    "blue": [((110, 100, 30), (130, 255, 255))],
    "yellow": [((20, 100, 100), (35, 255, 255))],
    "red": [((0, 150, 80), (8, 255, 255)), ((170, 150, 80), (179, 255, 255))],
}


class FakeDrone:
    """DRY_RUN 용. 명령을 화면에 찍기만 한다."""

    def open(self, port=None):
        print(f"[DRY] open {port}")
        return True

    def sendTakeOff(self):
        print("[DRY] takeOff")

    def sendLanding(self):
        print("[DRY] landing")

    def sendStop(self):
        print("[DRY] stop")

    def sendControl(self, roll, pitch, yaw, throttle):
        pass  # 너무 자주 불려서 찍지 않는다. 바뀔 때만 main 에서 찍는다

    def close(self):
        print("[DRY] close")


def connect():
    if DRY_RUN:
        drone = FakeDrone()
        drone.open()
        return drone

    from CodingDrone.drone import Drone  # 드론을 쓸 때만 import

    from drone_util import find_port

    drone = Drone()
    if not drone.open(find_port()):  # 실패해도 예외가 아니라 False 다
        raise SystemExit("드론 연결에 실패했습니다.")
    return drone


def make_demo_frames(n=150):
    """카메라 대신 쓸 영상 — 공이 가운데/위/아래/왼쪽/오른쪽으로 옮겨 다닌다."""
    ball = cv.cvtColor(np.uint8([[[95, 200, 230]]]), cv.COLOR_HSV2BGR)[0][0].tolist()
    path = [(320, 240), (320, 60), (320, 420), (60, 240), (580, 240), (320, 240), None]
    for i in range(n):
        frame = np.full((FRAME_H, FRAME_W, 3), 60, np.uint8)
        pos = path[min(i * len(path) // n, len(path) - 1)]
        if pos is not None:
            cv.circle(frame, pos, 45, ball, -1)
        yield frame


def find_center(frame, ranges):
    """색 마스크 → 가장 큰 덩어리 → 중심 좌표. 못 찾으면 (None, None)."""
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    mask = None
    for lower, upper in ranges:
        part = cv.inRange(hsv, np.array(lower), np.array(upper))
        mask = part if mask is None else cv.bitwise_or(mask, part)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)

    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, mask
    biggest = max(contours, key=cv.contourArea)
    if cv.contourArea(biggest) < MIN_AREA:
        return None, mask
    x, y, w, h = cv.boundingRect(biggest)
    return (x + w // 2, y + h // 2), mask


def decide_takeoff(center, flying):
    """MODE 1 — 공이 윗부분이면 이륙, 아랫부분이면 착륙. 상태가 바뀔 때만 True 를 돌려준다."""
    if center is None:
        return None, "LOST"
    want_fly = center[1] < TAKEOFF_LINE  # y 는 위가 0
    if want_fly == flying:
        return None, "HOLD"  # 이미 그 상태다 — 다시 보내지 않는다
    return want_fly, "TAKEOFF" if want_fly else "LANDING"


def decide_move(center):
    """MODE 2 — 가장자리에 들어간 만큼 roll / throttle 을 정한다."""
    if center is None:
        return 0, 0, "LOST"
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
    return roll, throttle, " + ".join(labels) if labels else "CENTER"


def main():
    ranges = COLOR_RANGES[TARGET]
    frames = make_demo_frames() if SOURCE == "demo" else None
    cap = None if frames else cv.VideoCapture(SOURCE)
    if cap is not None:
        if not cap.isOpened():
            raise SystemExit("카메라를 열지 못했습니다. 카메라 권한을 확인하세요.")
        cap.set(cv.CAP_PROP_FRAME_WIDTH, FRAME_W)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, FRAME_H)

    drone = connect()
    flying = False
    takeoff_at = last_sent = last_seen = 0.0
    if AUTO_TAKEOFF:  # 강의 예제3 의 sendTakeOff() + sleep(5)
        print("AUTO TAKEOFF")
        drone.sendTakeOff()
        flying, takeoff_at = True, time()
        sleep(0 if DRY_RUN else 5)
    last_cmd = None
    held = (0, 0, "LOST")

    try:
        while True:
            if frames is not None:
                frame = next(frames, None)
                if frame is None:
                    break
            else:
                ok, frame = cap.read()
                if not ok:
                    print("프레임을 읽지 못했습니다.")
                    break
                frame = cv.resize(frame, (FRAME_W, FRAME_H))
            if MIRROR:
                frame = cv.flip(frame, 1)

            center, mask = find_center(frame, ranges)
            now = time()

            if MODE == 1:
                want, label = decide_takeoff(center, flying)
                if want is True:
                    drone.sendTakeOff()  # 상태가 바뀔 때만 — 매 프레임이 아니다
                    flying, takeoff_at = True, now
                    print("TAKEOFF")
                elif want is False:
                    drone.sendControl(0, 0, 0, 0)
                    drone.sendLanding()
                    flying = False
                    print("LANDING")
            else:
                roll, throttle, label = decide_move(center)
                if center is not None:
                    last_seen, held = now, (roll, throttle, label)
                elif now - last_seen < LOST_HOLD:  # 잠깐 놓친 것뿐이면 직전 명령 유지
                    roll, throttle, label = held[0], held[1], held[2] + " (hold)"
                # 그 시간이 지나면 roll/throttle 은 0 — 가운데와 같은 "정지 명령" 이다

                if flying and now - takeoff_at >= TAKEOFF_SETTLE and now - last_sent >= SEND_INTERVAL:
                    drone.sendControl(roll, 0, 0, throttle)  # 네 값 모두 int
                    last_sent = now
                    if (roll, throttle) != last_cmd:
                        print(f"{label:16s} roll={roll:4d} throttle={throttle:4d} center={center}")
                        last_cmd = (roll, throttle)

            # 화면 — 왼쪽 카메라 / 오른쪽 마스크
            if center is not None:
                cv.circle(frame, center, 8, (255, 0, 255), -1)
            if MODE == 2:
                cv.rectangle(frame, (int(FRAME_W * EDGE), int(FRAME_H * EDGE)),
                             (int(FRAME_W * (1 - EDGE)), int(FRAME_H * (1 - EDGE))),
                             (200, 200, 200), 1)
            else:
                cv.line(frame, (0, int(TAKEOFF_LINE)), (FRAME_W, int(TAKEOFF_LINE)),
                        (200, 200, 200), 1)
            cv.putText(frame, f"MODE {MODE} | {'FLYING' if flying else 'LANDED'}"
                              f"{' (DRY)' if DRY_RUN else ''} | {label}",
                       (10, 25), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv.imshow("Color Drone Control", np.hstack([frame, cv.cvtColor(mask, cv.COLOR_GRAY2BGR)]))

            key = cv.waitKey(1) & 0xFF
            if key == 27:  # ESC — finally 에서 착륙한다
                break
            if key == ord("t") and not flying:
                drone.sendTakeOff()
                flying, takeoff_at = True, now
            elif key == ord("l") and flying:
                drone.sendControl(0, 0, 0, 0)
                drone.sendLanding()
                flying = False
            elif key == ord(" "):  # 비상 정지 — 모터를 즉시 끈다. 그대로 떨어진다
                print("!!! STOP !!!")
                drone.sendControl(0, 0, 0, 0)
                for _ in range(5):
                    drone.sendStop()
                    sleep(0.05)
                flying = False
    except KeyboardInterrupt:
        print("Ctrl+C")
    finally:
        if flying:
            drone.sendControl(0, 0, 0, 0)
            drone.sendLanding()
            sleep(5)
        sleep(0.1)
        drone.close()
        if cap is not None:
            cap.release()
        cv.destroyAllWindows()
        cv.waitKey(1)


if __name__ == "__main__":
    main()
