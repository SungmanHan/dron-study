"""26. 키보드 입력 — `keyboard` 모듈의 네 가지 방식

드론을 붙이기 전에 키 입력만 먼저 익힌다. `MODE` 를 1~4 로 바꿔 가며 실행한다.

    1  is_pressed()  — 지금 눌려 있는지 물어본다 (폴링, 논블로킹)
    2  read_key()    — 키가 눌릴 때까지 기다렸다가 이름을 돌려준다 (블로킹)
    3  on_press()    — 누를 때마다 콜백
    4  on_release()  — 뗄 때마다 콜백

[결론부터 — 드론 조종에는 1번]
드론은 "누르고 있는 동안 계속 이동" 이어야 하는데, `sendControl()` 은 1회 전송이라
루프에서 반복 호출해야 한다. 그러려면 루프가 멈추면 안 되므로 논블로킹인
`is_pressed()` 가 맞는다. 게다가 `↑`+`→` 같은 동시 입력도 `if` 를 여러 번 쓰면 된다.
`read_key()` 는 키를 기다리는 동안 루프가 멈춰서 조종에 쓸 수 없다.
`on_press`/`on_release` 는 "누를 때 시작 / 뗄 때 정지" 나 이륙·착륙 같은 단발 명령에 어울린다.

[keyboard 는 이 저장소 venv 에 깔려 있지 않다]
    pip install keyboard
이 모듈은 OS 의 키 입력을 전역으로 가로채기 때문에(터미널이 포커스가 아니어도 읽힌다)
macOS 에서는 관리자 권한이 필요하다.

    sudo .venv/bin/python 26_keyboard_input.py

`sudo python` 이 아니라 **venv 안의 파이썬을 경로로 직접** 지정해야 한다.
`sudo` 는 환경변수를 갈아엎어서 venv 활성화가 풀리고, 시스템 파이썬에는
keyboard 가 없어 `ModuleNotFoundError` 가 난다.
추가로 시스템 설정 → 개인정보 보호 및 보안 → **입력 모니터링** 에 터미널을 허용해야 한다.

[그래서 과제(29)는 Tkinter 키 이벤트를 쓴다]
Tk 창이 포커스를 가진 동안의 키만 받으면 충분하고, 그건 전역 후킹이 아니라서
sudo 도 권한 설정도 필요 없다. 강의 방식(`keyboard`)도 29 에서 토글로 남겨 뒀다.

[슬라이드 오탈자 두 개]
- `keyboard.on_press("키이름")` — 인자는 키 이름이 아니라 **콜백 함수**다.
  특정 키 하나만 잡으려면 `on_press_key("a", 콜백)` 이 따로 있다.
- `on_ release` — 밑줄 뒤 공백. 그대로 치면 SyntaxError.
"""

import time

MODE = 1  # 1 ~ 4

try:
    import keyboard
except ImportError:
    raise SystemExit(
        "keyboard 모듈이 없습니다.  pip install keyboard\n"
        "macOS 는 실행에도 권한이 필요합니다.  sudo .venv/bin/python 26_keyboard_input.py"
    )


# ── 1. is_pressed — 폴링 ─────────────────────────────────────
def demo_is_pressed():
    """루프를 돌면서 '지금 눌려 있나' 를 계속 확인한다."""
    print("↑ 를 누르면 종료합니다. (조합키 예: 'ctrl+c')")
    while True:
        if keyboard.is_pressed("up"):  # 대문자 'UP' 도 동작 — 내부에서 소문자로 정규화한다
            print("UP 키가 눌렸습니다.")
            break
        time.sleep(0.01)  # 없으면 이 루프 하나가 CPU 코어를 100% 먹는다


# ── 2. read_key — 블로킹 ─────────────────────────────────────
def demo_read_key():
    """키 이벤트가 올 때까지 기다렸다가 키 이름을 돌려준다."""
    print("아무 키나 누르면 이름을 출력합니다. q 로 종료.")
    while True:
        key = keyboard.read_key()  # 여기서 멈춰 있다
        if key == "q":
            break
        print(key)
    # 강의 코드는 `if is_pressed('q'): break / else: print(read_key())` 였는데,
    # read_key() 안에서 멈춰 있는 동안에는 is_pressed('q') 검사가 아예 돌지 않는다.
    # q 를 짧게 눌렀다 떼면 이름만 찍히고 종료되지 않는다 → 반환값으로 비교하는 쪽이 확실하다.
    # 또 키는 누를 때와 뗄 때 각각 이벤트가 생기므로 한 번 눌러도 두 번 찍히는 게 정상이다.


# ── 3. on_press / 4. on_release — 이벤트 콜백 ────────────────
def demo_on_press():
    """누를 때마다 콜백이 불린다. 05_turtle_event_pattern.py 와 같은 그림이다."""

    def handle_press(event):
        # event 는 문자열이 아니라 KeyboardEvent 객체다.
        # 그냥 출력하면 'KeyboardEvent(a down)' 처럼 나온다 → .name 을 쓴다.
        print(f"키 {event.name} 가 눌렸습니다.  (event_type={event.event_type})")

    keyboard.on_press(handle_press)
    keyboard.wait("esc")  # 등록만 하고 끝나면 아무 일도 안 일어난다. esc 까지 붙잡아 둔다


def demo_on_release():
    def handle_release(event):
        print(f"키 {event.name} 가 놓였습니다.")

    keyboard.on_release(handle_release)
    keyboard.wait("esc")  # 인자 없는 wait() 는 영원히 안 끝난다 → 종료 키를 준다


DEMOS = {1: demo_is_pressed, 2: demo_read_key, 3: demo_on_press, 4: demo_on_release}

if __name__ == "__main__":
    try:
        DEMOS[MODE]()
    except KeyboardInterrupt:
        # 터미널의 Ctrl+C 는 keyboard 가 보기 전에 파이썬이 먼저 가로챈다
        pass
    print("종료")
