"""10. 부저 — sendBuzzer / sendBuzzerScale / Reserve

소리는 드론이 아니라 **조종기**가 낸다. (header.to_ = DeviceType.Controller)

  sendBuzzer(mode, value, time)   저수준. mode 에 따라 value 의 의미가 달라진다
  sendBuzzerScale(scale, time)    음계로 바로 재생 — 실습에서 가장 많이 쓴다
  sendBuzzerHz(hz, time)          주파수(Hz)로 재생
  sendBuzzerMute(time)            묵음

BuzzerMode = Mute / Scale / Hz + 각각의 Reserve(예약) 버전 + Stop.
Reserve 계열은 "바로 전에 호출한 소리가 끝난 뒤" 이어서 재생되도록 예약한다.
그래서 sendBuzzerScale + sendBuzzerScaleReserve 로 두 음을 sleep 없이 붙일 수 있다.

[핵심 학습 내용 — 조용한 실패]
sendBuzzerScale() 은 내부에서 isinstance(time, int) 를 검사하고,
아니면 **아무 것도 보내지 않고 None 을 반환한다.** 예외가 나지 않는다.

    dron.sendBuzzerScale(BuzzerScale.C4, 400)      # 소리 남
    dron.sendBuzzerScale(BuzzerScale.C4, 400 / 2)  # 200.0 은 float -> 조용히 무시

파이썬에서 `/` 는 항상 float 이다. 박자를 계산해서 넣을 때 자주 밟는다.
"소리가 안 나는데 에러도 없다" 면 time 이 float 인지부터 본다. => int() 로 감쌀 것.

[음계 이름]
BuzzerScale 은 C1~B8 (C, CS=샵, D, DS ... B). 실습은 4옥타브대가 듣기 좋다.
  도 C4 / 레 D4 / 미 E4 / 파 F4 / 솔 G4 / 라 A4 / 시 B4
Mute(0xEE), Fin(0xFF), EndOfType 은 음이 아니라 특수값이다.
"""

from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import BuzzerMode, BuzzerScale, DeviceType

from drone_util import find_port


def main():
    dron = Drone()
    try:
        dron.open(find_port())
        dron.sendPing(DeviceType.Controller)

        # 1) 음계로 재생 — 도레미
        print("도레미")
        for scale in (BuzzerScale.C4, BuzzerScale.D4, BuzzerScale.E4):
            dron.sendBuzzerScale(scale, 300)
            sleep(0.4)  # time 은 조종기가 내는 길이일 뿐, 파이썬은 기다려 주지 않는다

        # 2) Reserve — 예약으로 두 음 잇기 (사이에 sleep 이 필요 없다)
        print("예약 재생 (솔 -> 도)")
        dron.sendBuzzerScale(BuzzerScale.G4, 300)
        dron.sendBuzzerScaleReserve(BuzzerScale.C5, 300)
        sleep(0.8)

        # 3) 주파수로 재생
        print("440Hz (라)")
        dron.sendBuzzerHz(440, 500)
        sleep(0.6)

        # 4) 저수준 — sendBuzzer 로 같은 것을 직접
        print("sendBuzzer(Scale, ...) 로 같은 소리")
        dron.sendBuzzer(BuzzerMode.Scale, BuzzerScale.A4.value, 500)
        sleep(0.6)

        dron.sendBuzzerMute(10)
    finally:
        sleep(0.1)
        dron.close()


if __name__ == "__main__":
    main()
