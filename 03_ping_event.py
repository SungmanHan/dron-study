"""03. Ping / Ack — 이벤트 핸들러 방식 (Drone())

Drone() 은 flagCheckBackground=True 가 기본값이라, 백그라운드 스레드가
check() 를 계속 돌린다. 그래서 check() 루프를 직접 관리할 필요가 없고
setEventHandler() 로 등록한 콜백이 알아서 호출된다.

[핵심 학습 내용]
이벤트 핸들러는 백그라운드 수신이 켜져 있어야 동작한다.
Drone(False) 로 만든 객체에 setEventHandler() 를 걸면 check() 를
아무도 돌리지 않으므로 콜백이 영원히 호출되지 않는다.

실습에는 이 방식이 편하다. State / Attitude / Range 등도 핸들러만
하나씩 더 등록하면 되고, 이후 비행 명령 실습에서도 그대로 쓴다.
"""

from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import DataType, DeviceType

from drone_util import find_port


def event_ack(ack):
    print(f"{ack.dataType.name} / {ack.systemTime} / {ack.crc16:04X}")


def event_state(state):
    # State 객체의 필드명은 라이브러리 버전에 따라 다르므로 통째로 찍어서 확인한다
    print("[State]", vars(state))


def main():
    dron = Drone()  # 백그라운드 수신 ON
    dron.open(find_port())

    try:
        dron.setEventHandler(DataType.Ack, event_ack)
        dron.setEventHandler(DataType.State, event_state)

        dron.sendPing(DeviceType.Controller)
        sleep(0.5)  # 핸들러가 호출될 시간. 0.1 은 짧다.
    finally:
        dron.close()


if __name__ == "__main__":
    main()
