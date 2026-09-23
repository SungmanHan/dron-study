"""25. [과제] 하방센서 / 전방센서 값을 창 두 개로 출력 (Tkinter)

요구사항: 하방센서 출력창과 전방센서 출력창을 만들고, 0.5초 간격으로 두 센서값을
요청해 실시간 표시한다. 15회 반복 후 자동 종료.

    하방 : DataType.Altitude -> altitude.rangeHeight  (m)
    전방 : DataType.Range    -> range.front           (mm)

※ 이륙하지 않는다. 드론을 손에 들고 바닥·앞쪽 거리를 바꿔 가며 값 변화를 확인한다.

[핵심 학습 내용 — 화면은 메인 스레드에서만]
센서 핸들러는 드론 라이브러리의 **백그라운드 수신 스레드**에서 호출되는데
Tkinter 위젯은 메인 스레드에서만 건드려야 한다.
그래서 핸들러는 값만 전역에 저장하고, 화면 갱신은 `root.after()` 로 메인 스레드에서 한다.
07_button_turtle.py 에서 turtle 을 메인 스레드로 옮긴 것과 같은 구조다
(거기서는 queue, 여기서는 "마지막 값만 필요하니" 전역 변수 하나로 충분하다).

[open() 은 예외를 던지지 않는다]
연결에 실패해도 False 를 반환하고 끝난다. 그대로 두면 창은 멀쩡히 뜨고
"측정 중..." 만 계속 찍히며 값이 영영 안 들어온다. 반환값을 확인해서 바로 알려 준다.

[sleep 을 쓰지 않는다]
요청 두 개 사이의 간격도 `after` 로 준다. 메인 스레드에서 sleep 을 걸면
그동안 창이 멈추고(버튼·이동 반응 없음) 로그도 늦게 그려진다.
"""

import tkinter as tk
from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import DataType, DeviceType

from drone_util import find_port

REPEAT = 15  # 측정 횟수
INTERVAL_MS = 500  # 회차 간격
WAIT_MS = 300  # 요청 후 응답을 기다리는 시간
GAP_MS = 50  # 두 요청 사이 간격

dron = Drone()  # 백그라운드 수신 ON — 핸들러 동작 조건
bottom_value = None  # 하방 최신값 (m)  — 수신 스레드가 갱신
front_value = None  # 전방 최신값 (mm) — 수신 스레드가 갱신
count = 0
running = True


# ── 핸들러 (수신 스레드) — 값만 저장한다 ─────────────────────
def event_altitude(altitude):
    global bottom_value
    bottom_value = altitude.rangeHeight


def event_range(range_data):
    global front_value
    front_value = range_data.front


# ── 측정 루프 (메인 스레드) ──────────────────────────────────
def request_sensors():
    global count
    if not running:
        return

    count += 1
    status_label.config(text=f"측정 중... {count} / {REPEAT}")

    dron.sendRequest(DeviceType.Drone, DataType.Altitude)
    root.after(GAP_MS, lambda: dron.sendRequest(DeviceType.Drone, DataType.Range))
    root.after(WAIT_MS, update_screen)


def update_screen():
    if not running:
        return

    if bottom_value is not None:
        bottom_now.config(text=f"{bottom_value:.3f} m  ({bottom_value * 100:.1f} cm)")
        bottom_log.insert(tk.END, f"{count:2d}회 : {bottom_value:.3f} m")
    else:
        bottom_log.insert(tk.END, f"{count:2d}회 : 수신 대기")
    bottom_log.see(tk.END)

    if front_value is not None:
        front_now.config(text=f"{front_value} mm  ({front_value / 10:.1f} cm)")
        front_log.insert(tk.END, f"{count:2d}회 : {front_value} mm")
    else:
        front_log.insert(tk.END, f"{count:2d}회 : 수신 대기")
    front_log.see(tk.END)

    print(f"[{count:2d}/{REPEAT}] 하방: {bottom_value}  전방: {front_value}")

    if count < REPEAT:
        root.after(INTERVAL_MS - WAIT_MS, request_sensors)
    else:
        status_label.config(text=f"{REPEAT}회 측정 완료 — 3초 뒤 종료합니다")
        root.after(3000, close_window)


def close_window():
    global running
    running = False  # 예약된 after 콜백이 위젯을 건드리지 않게
    root.destroy()


# ── 화면 구성 ────────────────────────────────────────────────
def make_panel(parent, title, color):
    frame = tk.LabelFrame(parent, text=title, font=("Arial", 14, "bold"),
                          fg=color, padx=10, pady=10)
    now = tk.Label(frame, text="-", font=("Arial", 22, "bold"), fg=color, width=18)
    now.pack(pady=(0, 10))
    log = tk.Listbox(frame, height=REPEAT, width=26, font=("Courier", 12))
    log.pack()
    return frame, now, log


root = tk.Tk()
root.title("드론 하방센서 / 전방센서 데이터")
root.protocol("WM_DELETE_WINDOW", close_window)

tk.Label(root, text="드론 센서 실시간 출력", font=("Arial", 18, "bold")).pack(pady=10)

panels = tk.Frame(root)
panels.pack(padx=15)

bottom_frame, bottom_now, bottom_log = make_panel(panels, "하방센서 (고도)", "#1f6feb")
bottom_frame.grid(row=0, column=0, padx=10)

front_frame, front_now, front_log = make_panel(panels, "전방센서 (장애물 거리)", "#d1242f")
front_frame.grid(row=0, column=1, padx=10)

status_label = tk.Label(root, text="드론 연결 중...", font=("Arial", 12))
status_label.pack(pady=10)


def main():
    try:
        if not dron.open(find_port()):  # open() 은 실패해도 예외가 아니라 False
            status_label.config(text="드론 연결 실패 — USB 연결을 확인하세요")
            root.mainloop()
            return

        dron.setEventHandler(DataType.Altitude, event_altitude)
        dron.setEventHandler(DataType.Range, event_range)

        root.after(500, request_sensors)  # 창이 뜨고 0.5초 뒤 첫 측정
        root.mainloop()  # 창이 닫힐 때까지 여기서 대기
    finally:
        sleep(0.1)
        dron.close()
        print("종료")


if __name__ == "__main__":
    main()
