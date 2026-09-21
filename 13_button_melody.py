"""13. [과제] 조종기 버튼으로 "비행기" 멜로디 연주 + 진동

요구사항
  - 조종기 버튼을 누르면 "비행기" 멜로디를 연주한다
  - 버튼을 누르면 진동이 울린다
  - 계이름: 미 레 도 레 미 미 미 / 레 레 레 / 미 미 미

  FrontLeftTop(1)     -> 비행기 연주
  FrontLeftBottom(2)  -> 연주 중단
  아무 버튼           -> 진동 1회

[핵심 학습 내용 — 콜백에서 멜로디를 재생하면 안 된다]
콜백은 백그라운드 수신 스레드에서 불린다. 그 안에서 멜로디를 끝까지 재생하면
약 6초 동안 수신 스레드가 sleep 에 붙잡혀, 그 사이 들어온 버튼·조이스틱 프레임이
전부 밀린다. 연주 중에 누른 버튼이 연주가 끝난 뒤에야 처리되는 식이다.

  콜백 -> queue 에 요청만 넣고 즉시 반환
  메인 루프 -> queue 에서 꺼내 재생

07_button_turtle.py 에서 turtle 을 메인 스레드로 옮긴 것과 같은 이유, 같은 해법이다.
진동은 프레임 한 개를 보내고 끝나므로 콜백에서 바로 보내도 된다.

[Press 필터]
버튼을 누르고 있으면 Press 가 계속 들어와 멜로디가 겹쳐서 재생된다.
ButtonEvent.Down 만 처리한다.

[time 은 int]
sendBuzzerScale(scale, time) 은 time 이 int 가 아니면 조용히 아무것도 하지 않는다.
박자를 나눠 쓸 때 float 이 되기 쉬우므로 int() 로 감싼다.
"""

import queue
from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import BuzzerScale, ButtonEvent, DataType, DeviceType

from drone_util import find_port

FRONT_LEFT_TOP = 0x0001  # 연주
FRONT_LEFT_BOTTOM = 0x0002  # 중단

# 비행기 — 미 레 도 레 미 미 미 / 레 레 레 / 미 미 미
MELODY = [
    BuzzerScale.E4, BuzzerScale.D4, BuzzerScale.C4, BuzzerScale.D4,
    BuzzerScale.E4, BuzzerScale.E4, BuzzerScale.E4,
    BuzzerScale.D4, BuzzerScale.D4, BuzzerScale.D4,
    BuzzerScale.E4, BuzzerScale.E4, BuzzerScale.E4,
]

NOTE_MS = 400  # 한 음의 길이
GAP_MS = 60  # 음 사이 틈. 없으면 "미미미" 가 한 음처럼 들린다

# 콜백(수신 스레드)과 메인 루프가 함께 쓰므로 모듈 수준에 둔다
dron = Drone()
requests = queue.Queue()
stop_flag = False


def event_button(button):
    """수신 스레드에서 호출된다. 진동만 보내고 연주는 큐에 맡긴다."""
    global stop_flag

    if button.event != ButtonEvent.Down:  # Press / Up 무시
        return

    print("button :", button.button)
    dron.sendVibrator(100, 200, 300)  # 프레임 1개 — 콜백에서 보내도 된다

    if button.button == FRONT_LEFT_TOP:
        stop_flag = False
        requests.put("play")
    elif button.button == FRONT_LEFT_BOTTOM:
        stop_flag = True  # 재생 루프가 다음 음에서 빠져나온다


def play_melody():
    print("비행기 ♪")
    for scale in MELODY:
        if stop_flag:
            print("중단")
            break
        dron.sendBuzzerScale(scale, int(NOTE_MS))
        sleep((NOTE_MS + GAP_MS) / 1000)
    dron.sendBuzzerMute(10)


def main():
    dron.open(find_port())
    dron.setEventHandler(DataType.Button, event_button)
    dron.sendPing(DeviceType.Controller)

    print("조종기 1번 버튼: 연주 / 2번 버튼: 중단  (Ctrl+C 로 종료)")
    try:
        while True:
            try:
                requests.get(timeout=0.2)
            except queue.Empty:
                continue
            play_melody()
    except KeyboardInterrupt:
        pass
    finally:
        sleep(0.1)
        dron.close()


if __name__ == "__main__":
    main()
