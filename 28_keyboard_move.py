"""28. 키보드로 전후좌우·상하·회전 이동 — ⚠️ 실제로 이륙한다

    space  비상 정지        esc  착륙 후 종료
    1 / 0  이륙 / 착륙
    w / s  상승 / 하강      throttle
    ↑ / ↓  전진 / 후진      pitch
    ← / →  좌 / 우 이동     roll
    a / d  좌회전 / 우회전   yaw   (강의 예제에 빠져 있어 추가)

실행:  sudo .venv/bin/python 28_keyboard_move.py

[sendControl(roll, pitch, yaw, throttle)]
각 축 -100 ~ 100. **+ 방향 = 우 / 전진 / 우회전 / 상승**.
한 번 보내고 끝나는 명령이라, 누르고 있는 동안 움직이게 하려면 루프에서 계속 보내야 한다.

[`else: sendControl(0, 0, 0, 0)` 이 이 예제의 핵심]
드론은 마지막으로 받은 명령을 계속 유지한다. 키를 떼도 아무것도 안 보내면 그대로 날아간다.
아무 키도 안 눌렸을 때 매 루프 0 을 보내는 이 한 줄이 "누르는 동안만 이동" 을 만든다.

[네 값은 반드시 int]
    sendControl(0, 0, 0, POWER / 3)   # ← float. 조용히 무시된다
라이브러리가 `isinstance(int)` 를 검사해서 아니면 **예외 없이 `None` 을 반환**하고 끝난다.
부저(10)·LED(17) 에서 겪은 것과 같은 함정이다. 나눗셈 `/` 는 항상 float 이므로
세기를 계산해서 넣을 때는 `int()` 로 감쌀 것.
반대로 범위를 벗어난 값(예: 200)은 조용하지 않다 — 내부가 `pack('<bbbb')`,
즉 signed 1바이트라 `struct.error` 로 터진다.

[elif 체인이라 대각선 이동이 안 된다]
위에서부터 처음 걸린 키 하나만 처리하므로 `↑` + `→` 를 같이 눌러도 전진만 한다.
동시 입력을 하려면 축별로 값을 모아 한 번에 `sendControl` 해야 한다 → 29 번 과제 파일.

[키 이름은 소문자로]
`"W"` 같은 대문자는 환경에 따라 `shift+w` 로 해석될 수 있다.
방향키 `"up"`/`"left"` 는 라이브러리가 정규화하므로 대소문자 상관없다.
"""

from time import sleep

from CodingDrone.drone import Drone

from drone_util import find_port

POWER = 30  # 이동 세기 (0~100). int 여야 한다
HOVER_MS = 4000

try:
    import keyboard
except ImportError:
    raise SystemExit("keyboard 모듈이 없습니다.  pip install keyboard  (26 번 파일 설명 참고)")


dron = Drone()

if not dron.open(find_port()):
    raise SystemExit("드론 연결 실패 — USB 연결을 확인하세요")

print("1 이륙 / 0 착륙 / wsad / 방향키 / space 비상정지 / esc 종료")

try:
    while True:
        # ── 단발 명령 — 비상 키가 맨 위 ──────────────────────
        if keyboard.is_pressed("space"):
            print("Stop")
            dron.sendStop()

        elif keyboard.is_pressed("esc"):
            break

        elif keyboard.is_pressed("1"):
            print("TakeOff")
            dron.sendTakeOff()
            sleep(0.01)
            dron.sendControlWhile(0, 0, 0, 0, HOVER_MS)  # 이 4초 동안은 키를 안 읽는다

        elif keyboard.is_pressed("0"):
            print("Landing")
            dron.sendLanding()

        # ── 이동 명령 — roll, pitch, yaw, throttle ───────────
        elif keyboard.is_pressed("w"):
            print("Up")
            dron.sendControl(0, 0, 0, POWER)
        elif keyboard.is_pressed("s"):
            print("Down")
            dron.sendControl(0, 0, 0, -POWER)

        elif keyboard.is_pressed("up"):
            print("Forward")
            dron.sendControl(0, POWER, 0, 0)
        elif keyboard.is_pressed("down"):
            print("Backward")
            dron.sendControl(0, -POWER, 0, 0)

        elif keyboard.is_pressed("left"):
            print("Left")
            dron.sendControl(-POWER, 0, 0, 0)
        elif keyboard.is_pressed("right"):
            print("Right")
            dron.sendControl(POWER, 0, 0, 0)

        elif keyboard.is_pressed("a"):
            print("Turn Left")
            dron.sendControl(0, 0, -POWER, 0)
        elif keyboard.is_pressed("d"):
            print("Turn Right")
            dron.sendControl(0, 0, POWER, 0)

        else:
            dron.sendControl(0, 0, 0, 0)  # ★ 키를 떼면 제자리 호버링

        sleep(0.01)  # 강의 코드에는 없다 — 없으면 else 가 초당 수천 번 전송해 시리얼을 꽉 채운다

finally:
    dron.sendLanding()
    sleep(0.1)
    dron.close()
    print("포트 닫음")
