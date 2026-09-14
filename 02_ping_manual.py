"""02. Ping / Ack — 수동 수신 방식 (Drone(False))

Drone(flagCheckBackground=False) 로 만들면 수신 파싱을 직접 check() 로 돌려야 한다.
강의 예제가 이 형태다.

[핵심 학습 내용]
루프 안에 sleep(0.01) 을 넣으면 실패한다.
조종기는 연결되어 있는 동안 조이스틱 데이터(DataType.Joystick, 0x71)를
초당 수백 프레임 계속 송신한다. check() 는 한 번에 아주 적은 양만 처리하므로
sleep(0.01) 이면 1초에 100번밖에 돌지 못하고, 들어오는 양이 처리량의 수십 배가 되어
버퍼가 계속 밀린다. Ack 은 그 뒤에 쌓인 채 타임아웃을 맞는다.
=> sleep 을 빼고 최대한 빠르게 돌린다.

[실제로 오간 프레임]
  송신 Ping   : 0A 55 | 01 08 70 20 | 00 00 00 00 00 00 00 00 | 86 D9
  수신 Ack    : 0A 55 | 02 0B 20 70 | 01 44 1C 00 ...          | 1B BF
  수신 조이스틱: 0A 55 | 71 08 20 70 | 00 00 22 02 00 00 22 02  | 90 0D

  구조: [0A 55 시작] [dataType 길이 from to] [data...] [crc16]
  0x70 = Base(내 PC), 0x20 = Controller(조종기), 0x10 = Drone(드론 본체)
"""

import time

from CodingDrone.drone import Drone
from CodingDrone.protocol import DataType, DeviceType

from drone_util import find_port

TIMEOUT_SEC = 1.0


def main():
    dron = Drone(False)  # 백그라운드 수신 OFF -> check() 를 직접 돌린다
    dron.open(find_port())

    try:
        dron.sendPing(DeviceType.Controller)
        started = time.time()

        while time.time() < started + TIMEOUT_SEC:
            # sleep 없음: 조이스틱 프레임 홍수를 따라잡아야 한다
            if dron.check() == DataType.Ack:
                ack = dron.getData(DataType.Ack)
                print(f"{ack.dataType.name} / {ack.systemTime} / {ack.crc16:04X}")
                print(f"T: {time.time() - started:.3f}s")
                break
        else:
            print("Time Over")
    finally:
        # 수신 스레드가 read() 중일 때 닫으면 [Errno 6] Device not configured 가 뜬다.
        # 무해하지만, 잠깐 쉬었다 닫으면 대부분 사라진다.
        time.sleep(0.1)
        dron.close()


if __name__ == "__main__":
    main()
