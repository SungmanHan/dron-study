"""29. [과제] 키보드로 드론을 조종하고 상태를 창에 표시 — ⚠️ 실제로 이륙한다

요구사항: 키보드로 이착륙과 전후좌우상하 이동을 제어하고, 드론 상태(이륙/착륙/이동방향)와
전송 중인 조종값을 화면에 실시간으로 표시한다.

    1 / 0   이륙 / 착륙          w / s   상승 / 하강
    ↑ / ↓   전진 / 후진          ← / →   좌 / 우 이동
    a / d   좌회전 / 우회전       space   비상 정지 (sendStop)
    esc 또는 창 닫기              착륙 후 종료

화면: 상태 배지 / 이동 방향 / roll·pitch·yaw·throttle 막대 / 명령 로그
실행 기록은 콘솔과 log_drone_keyboard_gui.txt 에 함께 남는다.

설정
    INPUT_MODE = "tk"        Tk 창의 키 이벤트 — sudo 불필요, macOS 권장 (창이 포커스여야 한다)
    INPUT_MODE = "keyboard"  강의의 keyboard 모듈 — macOS 는 sudo 필요 (26 번 파일 참고)
    SIMULATION = True        드론 없이 화면·키 동작만 확인

[while True 대신 root.after]
Tkinter 는 `mainloop()` 가 돌아야 화면이 갱신된다. 28 번처럼 무한 루프를 돌리면
창이 그대로 얼어붙는다. 20ms 마다 `tick()` 을 예약해 키 확인 → 명령 전송 → 화면 갱신을 한다.
20ms 는 임의의 수가 아니라 라이브러리의 `sendControlWhile` 이 내부에서 쓰는 간격과 같다
(초당 50회 전송).

[sendControlWhile(...,4000) 도 쓰지 않는다]
4초 동안 함수에서 안 빠져나오므로 창이 4초 멈춘다. 대신 "이륙 후 4초 동안은
매 주기 (0,0,0,0) 을 보내는 상태" 로 바꿨다. 결과는 같고 화면은 살아 있다.

[단발 명령은 "새로 눌린 순간" 만]
    new_keys = now_keys - prev_keys
이륙·착륙·비상정지를 매 주기 보내면 20ms 마다 명령이 쏟아진다.
직전 주기에 없던 키만 뽑아서 한 번씩 처리한다.

[동시 입력 — elif 체인을 버린다]
28 번은 키 하나만 처리해서 대각선 이동이 안 됐다. 여기서는 축별로 값을 모은 뒤
`sendControl` 을 **한 번** 호출한다. `↑`+`→` 면 전진 + 우이동이 같이 나간다.
같은 축의 반대 키를 동시에 누르면 먼저 정의된 쪽이 이긴다(dict 순서).

[Ctrl+C 로도, 창을 닫아도 착륙]
`WM_DELETE_WINDOW` 를 가로채고 `mainloop()` 바깥도 `finally` 로 감쌌다.
드론은 마지막 명령을 유지하므로 착륙을 보내지 않고 끝내면 계속 떠 있다.
"""

import datetime
import time
import tkinter as tk

INPUT_MODE = "tk"  # "tk" 또는 "keyboard"
SIMULATION = False  # True 면 드론 없이 화면만
POWER = 30  # 이동 세기 0~100 — int 여야 한다 (float 이면 조용히 무시된다)
TICK_MS = 20  # 제어 주기
TAKEOFF_HOLD_SEC = 4.0  # 이륙 후 안정화 시간
LOG_FILE = "log_drone_keyboard_gui.txt"

# 키 → (표시 이름, 축, 부호)    축: 0 roll, 1 pitch, 2 yaw, 3 throttle
MOVE_KEYS = {
    "w": ("상승", 3, +1),
    "s": ("하강", 3, -1),
    "up": ("전진", 1, +1),
    "down": ("후진", 1, -1),
    "left": ("좌이동", 0, -1),
    "right": ("우이동", 0, +1),
    "a": ("좌회전", 2, -1),
    "d": ("우회전", 2, +1),
}
ACTION_KEYS = ["1", "0", "space", "escape"]
ALL_KEYS = list(MOVE_KEYS) + ACTION_KEYS
KEYBOARD_NAME = {"escape": "esc"}  # keyboard 모듈과 Tk keysym 이 다른 것만

STATUS_COLOR = {
    "대기": "#6b7280",
    "연결 실패": "#dc2626",
    "이륙": "#2563eb",
    "비행 중": "#16a34a",
    "착륙": "#d97706",
    "비상 정지": "#dc2626",
}


def log(msg):
    stamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]  # 밀리초까지
    line = f"[{stamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


class FakeDrone:
    """SIMULATION 용 — 호출만 받고 아무것도 보내지 않는다."""

    def open(self, *args):
        log("[SIM] open")
        return True

    def close(self):
        log("[SIM] close")

    def sendTakeOff(self):
        pass

    def sendLanding(self):
        pass

    def sendStop(self):
        pass

    def sendControl(self, roll, pitch, yaw, throttle):
        pass


class KeyInput:
    """지금 눌려 있는 키 집합을 돌려준다. Tk 이벤트 / keyboard 모듈 두 방식."""

    def __init__(self, root, mode):
        self.mode = mode
        self.pressed = set()
        if mode == "keyboard":
            import keyboard  # 26 번에서 본 그 모듈 (macOS 는 sudo 필요)

            self.kb = keyboard
        else:
            root.bind("<KeyPress>", lambda e: self.pressed.add(e.keysym.lower()))
            root.bind("<KeyRelease>", lambda e: self.pressed.discard(e.keysym.lower()))
            # 창이 포커스를 잃으면 뗀 키의 KeyRelease 를 못 받는다 → 눌린 채로 남아 계속 이동한다
            root.bind("<FocusOut>", lambda e: self.pressed.clear())

    def get_pressed(self):
        if self.mode == "keyboard":
            return {k for k in ALL_KEYS if self.kb.is_pressed(KEYBOARD_NAME.get(k, k))}
        return {k for k in self.pressed if k in ALL_KEYS}


class DroneKeyboardApp:
    def __init__(self, root):
        self.root = root
        self.dron = None
        self.status = "대기"
        self.direction = "-"
        self.control = [0, 0, 0, 0]  # roll, pitch, yaw, throttle
        self.takeoff_time = 0.0
        self.prev_keys = set()
        self.running = True

        self.build_gui()  # ★ 연결보다 화면을 먼저 — 실패해도 이유를 화면에 띄운다
        root.protocol("WM_DELETE_WINDOW", self.shutdown)

        if not self.connect():
            return

        self.keys = KeyInput(root, INPUT_MODE)
        log(f"시작 (INPUT_MODE={INPUT_MODE}, SIMULATION={SIMULATION}, POWER={POWER})")
        self.root.after(TICK_MS, self.tick)

    # ── 연결 ─────────────────────────────────────────────────
    def connect(self):
        if SIMULATION:
            self.dron = FakeDrone()
            self.dron.open()
            return True

        from CodingDrone.drone import Drone

        from drone_util import find_port

        try:
            port = find_port()
        except RuntimeError as e:
            self.fail(str(e).splitlines()[0])
            return False

        self.dron = Drone()
        if not self.dron.open(port):  # open() 은 실패해도 예외가 아니라 False
            self.fail("드론 연결 실패 — USB 연결을 확인하세요")
            return False

        self.gui_log(f"드론 연결 완료 ({port})")
        return True

    def fail(self, msg):
        self.dron = None
        self.set_status("연결 실패")
        self.gui_log(msg)
        self.refresh_gui()  # tick 이 안 돌므로 여기서 직접 한 번 그린다

    # ── 화면 ─────────────────────────────────────────────────
    def build_gui(self):
        r = self.root
        r.title("CodingDrone 키보드 조종")
        r.geometry("460x600")
        r.configure(padx=16, pady=12)

        tk.Label(r, text="드론 상태", font=("Helvetica", 13)).pack(anchor="w")
        self.lbl_status = tk.Label(
            r, text="대기", font=("Helvetica", 30, "bold"),
            fg="white", bg=STATUS_COLOR["대기"], width=14, pady=6,
        )
        self.lbl_status.pack(fill="x", pady=(2, 10))

        tk.Label(r, text="이동 방향", font=("Helvetica", 13)).pack(anchor="w")
        self.lbl_dir = tk.Label(r, text="-", font=("Helvetica", 22, "bold"))
        self.lbl_dir.pack(anchor="w", pady=(0, 10))

        tk.Label(
            r, text="전송 조종값  sendControl(roll, pitch, yaw, throttle)",
            font=("Helvetica", 12),
        ).pack(anchor="w")

        self.bars = []
        frame = tk.Frame(r)
        frame.pack(fill="x", pady=(4, 10))
        for i, name in enumerate(["roll", "pitch", "yaw", "throttle"]):
            tk.Label(frame, text=name, width=8, anchor="w").grid(row=i, column=0)
            cv = tk.Canvas(frame, width=260, height=16, bg="#e5e7eb", highlightthickness=0)
            cv.grid(row=i, column=1, pady=2)
            cv.create_line(130, 0, 130, 16, fill="#9ca3af")  # 0 기준선
            bar = cv.create_rectangle(130, 2, 130, 14, fill="#2563eb", width=0)
            val = tk.Label(frame, text="0", width=5, anchor="e")
            val.grid(row=i, column=2)
            self.bars.append((cv, bar, val))

        tk.Label(
            r, justify="left", fg="#374151",
            text=("1 이륙   0 착륙   space 비상정지   esc 종료\n"
                  "w/s 상승·하강   ↑↓ 전진·후진   ←→ 좌·우   a/d 회전"),
        ).pack(anchor="w", pady=(0, 8))

        tk.Label(r, text="명령 로그", font=("Helvetica", 12)).pack(anchor="w")
        self.txt_log = tk.Text(r, height=10, font=("Menlo", 10), state="disabled")
        self.txt_log.pack(fill="both", expand=True)

    def gui_log(self, msg):
        log(msg)
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", f"{datetime.datetime.now():%H:%M:%S}  {msg}\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")

    def refresh_gui(self):
        self.lbl_status.config(text=self.status, bg=STATUS_COLOR[self.status])
        self.lbl_dir.config(text=self.direction)
        for (cv, bar, val), v in zip(self.bars, self.control):
            x = 130 + v * 130 / 100  # -100~100 → 0~260 px
            cv.coords(bar, min(130, x), 2, max(130, x), 14)
            val.config(text=f"{v:+d}" if v else "0")

    def set_status(self, status):
        if status != self.status:
            self.status = status
            self.gui_log(f"상태: {status}")

    def set_direction(self, direction):
        if direction != self.direction:
            self.direction = direction
            self.gui_log(f"이동: {direction}  control={self.control}")

    # ── 제어 루프 (TICK_MS 마다) ─────────────────────────────
    def tick(self):
        if not self.running:
            return

        now_keys = self.keys.get_pressed()
        new_keys = now_keys - self.prev_keys  # 이번 주기에 새로 눌린 키만
        self.prev_keys = now_keys

        # 1) 단발 명령 — 비상 정지를 가장 먼저
        if "space" in new_keys:
            self.dron.sendStop()
            self.control = [0, 0, 0, 0]
            self.set_status("비상 정지")
            self.set_direction("-")
        elif "escape" in new_keys:
            self.shutdown()
            return
        elif "1" in new_keys and self.status in ("대기", "착륙", "비상 정지"):
            self.dron.sendTakeOff()
            self.takeoff_time = time.time()
            self.set_status("이륙")
        elif "0" in new_keys and self.status in ("이륙", "비행 중"):
            self.dron.sendLanding()
            self.control = [0, 0, 0, 0]
            self.set_status("착륙")
            self.set_direction("-")

        # 2) 이동 명령 — 떠 있을 때만
        if self.status == "이륙" and time.time() - self.takeoff_time < TAKEOFF_HOLD_SEC:
            self.control = [0, 0, 0, 0]  # sendControlWhile(0,0,0,0,4000) 을 블로킹 없이
            self.dron.sendControl(*self.control)
            self.set_direction("안정화 (호버링)")

        elif self.status in ("이륙", "비행 중"):
            self.set_status("비행 중")
            control = [0, 0, 0, 0]
            names = []
            for key, (name, axis, sign) in MOVE_KEYS.items():
                if key in now_keys and control[axis] == 0:  # 같은 축 반대키는 먼저 것만
                    control[axis] = sign * POWER
                    names.append(name)
            self.control = control
            self.dron.sendControl(*control)  # 아무 키도 없으면 (0,0,0,0) → 제자리 호버링
            self.set_direction(" + ".join(names) if names else "호버링")

        self.refresh_gui()
        self.root.after(TICK_MS, self.tick)

    # ── 종료 ─────────────────────────────────────────────────
    def shutdown(self):
        if not self.running:
            return
        self.running = False

        if self.dron is not None:
            log("종료 — 착륙 명령 전송 후 포트 닫기")
            try:
                self.dron.sendLanding()
                time.sleep(0.1)  # 수신 스레드가 read 중일 때 close 하면 Errno 6
            finally:
                self.dron.close()

        try:
            self.root.destroy()
        except tk.TclError:
            pass  # 이미 닫힌 창


if __name__ == "__main__":
    root = tk.Tk()
    app = DroneKeyboardApp(root)
    try:
        root.mainloop()
    finally:
        app.shutdown()  # Ctrl+C 로 mainloop 가 끊겨도 착륙 + close
