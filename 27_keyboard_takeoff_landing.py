"""27. 키보드로 이륙 / 착륙 — ⚠️ 실제로 이륙한다

    1      이륙 + 4초 호버링
    0      착륙
    space  비상 정지 (sendStop) — 모터가 즉시 꺼진다. 공중이면 그대로 떨어진다
    esc    착륙 후 종료

실행:  sudo .venv/bin/python 27_keyboard_takeoff_landing.py   (keyboard 모듈 권한)

[비행 명령 세 가지]
    sendTakeOff()   이륙        CommandType.FlightEvent + FlightEvent.TakeOff
    sendLanding()   착륙        CommandType.FlightEvent + FlightEvent.Landing
    sendStop()      강제 정지   CommandType.Stop
`sendStop` 만 FlightEvent 가 아니라 별도 커맨드다. 착륙(`sendLanding`)은 천천히
내려오고, 정지(`sendStop`)는 모터를 즉시 끈다 — 공중에서 쓰면 추락이다.
용도가 다르니 "비상 = 무조건 Stop" 으로 외우지 말 것.

[비상 키는 가장 먼저 검사한다]
if/elif 체인은 위에서부터 처음 걸린 것 하나만 처리한다. 비상 키가 아래에 있으면
다른 키가 눌려 있는 동안 영영 검사되지 않는다. 그래서 맨 위에 둔다.

[sendControlWhile 은 그 시간 동안 멈춰 있다]
    sendControlWhile(0, 0, 0, 0, 4000)
라이브러리 내부는 `while` 로 4초 동안 `sendControl` 을 20ms 간격(초당 50회)으로
반복 전송한다. 그동안 함수에서 못 빠져나오므로 **4초간 키 입력을 읽지 않는다.**
이륙 직후 자세를 안정시키는 용도로는 맞지만, 이 4초 안에 `0` 을 눌러도 착륙하지 않는다.
(GUI 라면 창까지 4초간 멈춘다 → 29 에서는 이 함수를 쓰지 않는다.)

[원본 강의 코드에 없던 것]
루프를 빠져나갈 방법, `close()`, 비상 정지 키가 전부 없다.
파이썬이 죽어도 드론은 **마지막 명령을 계속 유지**하므로, 예외·Ctrl+C 로 끝나도
착륙이 나가도록 `try/finally` 로 감쌌다.
"""

from time import sleep

from CodingDrone.drone import Drone

from drone_util import find_port

HOVER_MS = 4000  # 이륙 후 호버링 시간

try:
    import keyboard
except ImportError:
    raise SystemExit("keyboard 모듈이 없습니다.  pip install keyboard  (26 번 파일 설명 참고)")


dron = Drone()  # 백그라운드 수신 ON

if not dron.open(find_port()):  # open() 은 실패해도 예외가 아니라 False 를 돌려준다
    raise SystemExit("드론 연결 실패 — USB 연결을 확인하세요")

print("1 이륙 / 0 착륙 / space 비상정지 / esc 종료")

try:
    while True:
        if keyboard.is_pressed("space"):  # ★ 비상 키를 맨 위에
            print("Stop  — 모터 즉시 정지")
            dron.sendStop()

        elif keyboard.is_pressed("esc"):
            print("종료")
            break

        elif keyboard.is_pressed("1"):
            print("TakeOff")
            dron.sendTakeOff()
            sleep(0.01)
            dron.sendControlWhile(0, 0, 0, 0, HOVER_MS)  # 4초 제자리 (이 동안 키 안 읽힘)

        elif keyboard.is_pressed("0"):
            print("Landing")
            dron.sendLanding()

        sleep(0.01)  # 루프에 쉼이 없으면 CPU 를 100% 쓴다

finally:
    dron.sendLanding()  # 예외로 빠져나와도 착륙은 보낸다
    sleep(0.1)  # 수신 스레드가 read 중일 때 close 하면 Errno 6
    dron.close()
    print("포트 닫음")
