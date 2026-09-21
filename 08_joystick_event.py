"""08. 조종기 조이스틱 입력 — DataType.Joystick

조이스틱 상태는 Joystick 프레임(0x71)으로 올라온다.
왼쪽/오른쪽 스틱이 각각 x, y 와 direction, event 를 가진다.

  joystick.left.x / .y          -100 ~ +100
  joystick.left.direction       JoystickDirection (TL TM TR / ML CN MR / BL BM BR)
  joystick.left.event           JoystickEvent (In: 영역 진입 / Stay: 유지 / Out: 벗어남)

[핵심 학습 내용]
조종기가 연결돼 있으면 조이스틱 프레임이 초당 수백 개 들어온다.
그대로 print 하면 콘솔이 폭주하고, 콜백에서 무거운 일을 하면 수신이 밀린다.
=> 이 파일은 강의 예제대로 전부 찍는 RAW 모드와,
   값이 바뀔 때만 찍는 모드를 토글로 둔다. 실습은 두 번째가 훨씬 볼 만하다.
"""

from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import DataType, DeviceType

from drone_util import find_port

PRINT_ALL = False  # True 면 강의 예제처럼 들어오는 프레임을 전부 찍는다
WAIT_SEC = 10

_last = None


def format_joystick(joystick):
    return (
        "L: ({0:4}, {1:4}), {2:5}, {3:5} / ".format(
            joystick.left.x,
            joystick.left.y,
            joystick.left.direction.name,
            joystick.left.event.name,
        )
        + "R: ({0:4}, {1:4}), {2:5}, {3:5}".format(
            joystick.right.x,
            joystick.right.y,
            joystick.right.direction.name,
            joystick.right.event.name,
        )
    )


def event_joystick(joystick):
    global _last

    if PRINT_ALL:
        print("eventJoystick() /", format_joystick(joystick))
        return

    # 값이 바뀐 프레임만 출력 — 초당 수백 줄이 수십 줄로 줄어든다
    current = (
        joystick.left.x,
        joystick.left.y,
        joystick.right.x,
        joystick.right.y,
    )
    if current != _last:
        _last = current
        print("eventJoystick() /", format_joystick(joystick))


def main():
    dron = Drone()
    try:
        dron.open(find_port())
        dron.setEventHandler(DataType.Joystick, event_joystick)
        dron.sendPing(DeviceType.Controller)

        print(f"{WAIT_SEC}초 동안 조이스틱을 움직여 보세요.")
        for i in range(WAIT_SEC, 0, -1):
            print(i)
            sleep(1)
    finally:
        sleep(0.1)
        dron.close()


if __name__ == "__main__":
    main()
