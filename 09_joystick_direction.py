"""09. [과제] 조이스틱으로 방향 출력 프로그램 만들기

요구사항: 조이스틱 방향(상, 하, 좌, 우)에 따라 방향 메시지(TM, BM, ML, MR)를 출력한다.

[방향 enum — 라이브러리 소스에서 확인]
CodingDrone/protocol.py 의 JoystickDirection 은 3x3 격자다.

        TL   TM   TR        TM = 위,   BM = 아래
        ML   CN   MR        ML = 왼쪽, MR = 오른쪽
        BL   CN(가운데) 은 CENTER 가 아니라 CN 이다
        BL   BM   BR

  None_ = 0 은 "정의하지 않은 영역" 이므로 무시한다.
  대각선(TL TR BL BR)은 과제 요구사항 밖이라 여기서도 무시한다.

[핵심 학습 내용]
event 를 걸러야 한다. 조이스틱은 같은 영역에 머물러 있는 동안
Stay 이벤트를 초당 수백 번 보내므로, 그대로 출력하면 같은 줄이 폭포처럼 쏟아진다.
영역에 새로 들어간 순간인 JoystickEvent.In 만 출력하면
"움직인 방향" 이 한 줄씩 깔끔하게 찍힌다.
"""

from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import DataType, DeviceType, JoystickDirection, JoystickEvent

from drone_util import find_port

WAIT_SEC = 10

MESSAGES = {
    JoystickDirection.TM: "위쪽 (TM)",
    JoystickDirection.BM: "아래쪽 (BM)",
    JoystickDirection.ML: "왼쪽 (ML)",
    JoystickDirection.MR: "오른쪽 (MR)",
}


def print_direction(side, block):
    if block.event != JoystickEvent.In:  # 영역에 진입한 순간만
        return
    message = MESSAGES.get(block.direction)
    if message:  # CN(중앙), 대각선, None_ 은 무시
        print(f"{side} 방향 : {message}")


def event_joystick(joystick):
    print_direction("L", joystick.left)
    print_direction("R", joystick.right)


def main():
    dron = Drone()
    try:
        dron.open(find_port())
        dron.setEventHandler(DataType.Joystick, event_joystick)
        dron.sendPing(DeviceType.Controller)

        print(f"{WAIT_SEC}초 동안 조이스틱을 상/하/좌/우로 움직여 보세요.")
        for i in range(WAIT_SEC, 0, -1):
            print(i)
            sleep(1)
    finally:
        sleep(0.1)
        dron.close()


if __name__ == "__main__":
    main()
