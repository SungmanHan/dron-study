"""11. 부저로 연주 — "학교종이 땡땡땡"

sendBuzzerScale() 을 순서대로 호출하고 sleep 으로 박자를 맞춘다.

[핵심 학습 내용 — 두 개의 시간]
sendBuzzerScale(scale, time) 의 time(ms)은 **조종기가 소리를 내는 길이**다.
이 함수는 명령만 보내고 바로 반환하므로, 파이썬 쪽에서 sleep 을 하지 않으면
다음 음 명령이 곧바로 날아가 앞 음을 덮어쓴다. 두 시간을 같이 맞춰야 한다.

  드론이 내는 시간 : sendBuzzerScale(..., 400)
  파이썬이 쉬는 시간: sleep(0.4 + 약간)

음 사이를 조금 띄워야(GAP) 같은 음이 연속될 때 두 번으로 들린다.
안 띄우면 "미미미" 가 길게 늘어진 "미—" 하나로 들린다.

Reserve 로 예약해서 붙이는 방법도 있지만(10번 참고), 악보처럼 음 길이가
제각각인 곡은 sleep 으로 맞추는 쪽이 눈에 보이고 고치기 쉽다.
"""

from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import BuzzerScale, DeviceType

from drone_util import find_port

# 학교종이 땡땡땡 / 어서 모이자 / 선생님이 우리를 / 기다리신다
# 솔솔라라 솔솔미  솔솔미미 레     솔솔라라 솔솔미    솔미레미 도
NOTE = 400  # ms, 4분음표
SONG = [
    (BuzzerScale.G4, NOTE), (BuzzerScale.G4, NOTE),
    (BuzzerScale.A4, NOTE), (BuzzerScale.A4, NOTE),
    (BuzzerScale.G4, NOTE), (BuzzerScale.G4, NOTE),
    (BuzzerScale.E4, NOTE * 2),
    (BuzzerScale.G4, NOTE), (BuzzerScale.G4, NOTE),
    (BuzzerScale.E4, NOTE), (BuzzerScale.E4, NOTE),
    (BuzzerScale.D4, NOTE * 2),
    (BuzzerScale.G4, NOTE), (BuzzerScale.G4, NOTE),
    (BuzzerScale.A4, NOTE), (BuzzerScale.A4, NOTE),
    (BuzzerScale.G4, NOTE), (BuzzerScale.G4, NOTE),
    (BuzzerScale.E4, NOTE * 2),
    (BuzzerScale.G4, NOTE), (BuzzerScale.E4, NOTE),
    (BuzzerScale.D4, NOTE), (BuzzerScale.E4, NOTE),
    (BuzzerScale.C4, NOTE * 2),
]

GAP_MS = 60  # 음 사이 틈. 없으면 같은 음이 이어져 한 음처럼 들린다


def play(dron, song):
    for scale, duration in song:
        # duration 은 반드시 int. float 이면 라이브러리가 조용히 무시한다
        dron.sendBuzzerScale(scale, int(duration))
        sleep((duration + GAP_MS) / 1000)


def main():
    dron = Drone()
    try:
        dron.open(find_port())
        dron.sendPing(DeviceType.Controller)

        print("학교종이 땡땡땡")
        play(dron, SONG)

        dron.sendBuzzerMute(10)
    finally:
        sleep(0.1)
        dron.close()


if __name__ == "__main__":
    main()
