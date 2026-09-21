"""06. 조종기 버튼 입력 — DataType.Button

조종기의 버튼 상태는 Button 프레임(0x70)으로 올라온다.
setEventHandler(DataType.Button, ...) 로 콜백만 걸면 된다.

[핵심 학습 내용]
- button.button 은 enum 이 아니라 비트마스크(정수)다. 동시에 누르면 OR 로 합쳐진다.
  그래서 bin() + zfill(16) 으로 16비트를 그대로 찍어 보는 게 이해가 빠르다.
- button.event 는 Down(누름) / Press(누르는 중, 반복) / Up(뗌) 이다.
  Press 는 누르고 있는 동안 계속 들어오므로, "한 번 눌렀을 때 한 번만" 반응하게 하려면
  ButtonEvent.Down 만 골라야 한다. (07 번 예제에서 이걸 쓴다)
- 대기 시간(여기서는 10초) 안에 실제로 버튼을 눌러야 콜백이 찍힌다.
  아무것도 안 찍히면 "연결 문제" 보다 "그 사이에 안 눌렀음" 을 먼저 의심할 것.

[ButtonFlagController — 실측값]
  0x0001 FrontLeftTop      0x0002 FrontLeftBottom
  0x0004 FrontRightTop     0x0008 FrontRightBottom
  0x0010 TopLeft           0x0020 TopRight (POWER ON/OFF)
  0x0040 MidUp   0x0080 MidLeft   0x0100 MidRight   0x0200 MidDown
  0x0400 BottomLeft        0x0800 BottomRight
"""

from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import ButtonFlagController, DataType, DeviceType

from drone_util import find_port

WAIT_SEC = 10


def button_names(value):
    """비트마스크를 눌린 버튼 이름들로 푼다. 동시 입력도 그대로 보인다."""
    names = [
        flag.name
        for flag in ButtonFlagController
        if flag.value and (value & flag.value) == flag.value
    ]
    return ", ".join(names) if names else "-"


def event_button(button):
    print(
        "eventButton() / Button: 0b{0}, Event: {1:6} / {2}".format(
            bin(button.button)[2:].zfill(16),
            button.event.name,
            button_names(button.button),
        )
    )


def main():
    dron = Drone()  # 백그라운드 수신 ON. Drone(False) 면 콜백이 안 불린다
    try:
        dron.open(find_port())
        dron.setEventHandler(DataType.Button, event_button)
        dron.sendPing(DeviceType.Controller)

        print(f"{WAIT_SEC}초 동안 조종기 버튼을 눌러 보세요.")
        for i in range(WAIT_SEC, 0, -1):
            print(i)
            sleep(1)
    finally:
        # 예외가 나도 여기로 온다. close() 를 못 하고 죽으면 포트가 물린 채 남아
        # 다음 실행에서 multiple access on port 가 뜬다.
        sleep(0.1)
        dron.close()


if __name__ == "__main__":
    main()
