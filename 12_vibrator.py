"""12. 진동 — sendVibrator / Header+Vibrator 직접 전송

진동도 조종기가 낸다.

  on    (ms) 진동하는 시간
  off   (ms) 쉬는 시간
  total (ms) 이 on/off 패턴을 반복할 전체 시간

  on=100, off=200, total=900  ->  "부-웅 (쉼) 부-웅 (쉼) 부-웅" 3회

[핵심 학습 내용 — 래퍼가 이미 있다]
수업에서는 Header + Vibrator 를 직접 만들어 drone.transfer(header, data) 로
보냈지만, CodingDrone 1.0.4 에는 부저와 마찬가지로 래퍼 메서드가 있다.

  dron.sendVibrator(on, off, total)         # mode = VibratorMode.Instantly
  dron.sendVibratorReserve(on, off, total)  # mode = VibratorMode.Continually (예약)

라이브러리 소스를 열어 보면 sendVibrator() 의 본문이 아래 send_raw() 와 같다.
실습에서는 래퍼를 쓰고, 저수준 형태는 "전송 계층이 이렇게 생겼다" 를 보는 용도로 남긴다.
mode 를 직접 바꾸고 싶을 때만 저수준이 필요하다.

[from_ 는 Base(0x70)]
수업 코드는 header.from_ 에 DeviceType.Tester(0xA0) 를 넣었다. 동작은 하지만,
라이브러리 래퍼는 전부 DeviceType.Base(0x70) 를 쓴다 — 0x70 = 내 PC.
저수준으로 보낼 때도 Base 로 맞추는 편이 프레임 로그가 일관된다.

[transfer(header, data)]
수업 노트의 drone.transfer(hasattr, data) 는 오타다. hasattr 은 파이썬 내장 함수라
NameError 조차 나지 않고 "함수 객체" 가 그대로 전달돼, 엉뚱한 곳에서 터진다.
"""

from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import (
    DataType,
    DeviceType,
    Header,
    Vibrator,
    VibratorMode,
)

from drone_util import find_port


def send_raw(dron, on, off, total, mode=VibratorMode.Instantly):
    """래퍼를 쓰지 않고 프레임을 직접 만들어 보낸다 (학습용)."""
    header = Header()
    header.dataType = DataType.Vibrator
    header.length = Vibrator.getSize()
    header.from_ = DeviceType.Base  # 0x70 = 내 PC
    header.to_ = DeviceType.Controller  # 0x20 = 조종기

    data = Vibrator()
    data.mode = mode
    data.on = on
    data.off = off
    data.total = total

    return dron.transfer(header, data)  # transfer(header, data) — 오타 주의


def main():
    dron = Drone()
    try:
        dron.open(find_port())
        dron.sendPing(DeviceType.Controller)

        print("짧게 1회")
        dron.sendVibrator(100, 200, 300)
        sleep(0.6)

        print("3회 반복")
        dron.sendVibrator(100, 200, 900)
        sleep(1.2)

        print("저수준 전송으로 같은 진동")
        send_raw(dron, 100, 200, 300)
        sleep(0.6)
    finally:
        sleep(0.1)
        dron.close()


if __name__ == "__main__":
    main()
