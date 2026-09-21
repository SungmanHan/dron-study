"""07. 버튼으로 turtle 도형 그리기

조종기 버튼 값에 따라 turtle 을 움직인다.
  FrontLeftTop(1)     -> 전진 100
  FrontLeftBottom(2)  -> 후진 100
  FrontRightTop(4)    -> 반지름 150 원

[핵심 학습 내용]
1) 그리기는 메인 스레드에서 한다.
   드론 콜백은 백그라운드 수신 스레드에서 불리는데, turtle(tkinter) 은
   스레드 안전하지 않다. 콜백에서 바로 forward() 를 부르면 잘 되는 것처럼
   보이다가 창이 멈추거나 이상하게 그려진다.
   => 콜백은 Queue 에 넣기만 하고, 실제 그리기는 turtle.ontimer 로
      메인 스레드에서 꺼내 처리한다.

2) Press 이벤트를 걸러야 한다.
   버튼을 누르고 있으면 Press 가 계속 들어와서 도형이 수십 개 그려진다.
   ButtonEvent.Down 만 처리한다.

3) 스크립트로 실행할 때는 mainloop() 가 필요하다.
   주피터는 셀이 끝나도 커널이 살아 있어서 없어도 되는 것처럼 보이지만,
   .py 로 돌리면 open/setEventHandler 만 하고 바로 프로세스가 끝나 버린다.
"""

import queue
import turtle
from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import ButtonEvent, DataType, DeviceType

from drone_util import find_port

FRONT_LEFT_TOP = 0x0001
FRONT_LEFT_BOTTOM = 0x0002
FRONT_RIGHT_TOP = 0x0004

POLL_MS = 50

commands = queue.Queue()


def event_button(button):
    """수신 스레드에서 호출된다. 큐에 넣기만 하고 즉시 반환한다."""
    if button.event != ButtonEvent.Down:  # 누르는 중(Press) / 뗌(Up) 은 무시
        return
    commands.put(button.button)


def draw(btn):
    """메인 스레드에서만 호출된다."""
    print("button :", btn)
    if btn == FRONT_LEFT_TOP:
        turtle.forward(100)
    elif btn == FRONT_LEFT_BOTTOM:
        turtle.backward(100)
    elif btn == FRONT_RIGHT_TOP:
        turtle.circle(150)


def poll():
    while True:
        try:
            draw(commands.get_nowait())
        except queue.Empty:
            break
    turtle.ontimer(poll, POLL_MS)


def main():
    dron = Drone()
    try:
        dron.open(find_port())
        dron.setEventHandler(DataType.Button, event_button)
        dron.sendPing(DeviceType.Controller)

        turtle.ontimer(poll, POLL_MS)
        turtle.mainloop()  # 창을 닫으면 빠져나온다
    finally:
        sleep(0.1)
        dron.close()


if __name__ == "__main__":
    main()
