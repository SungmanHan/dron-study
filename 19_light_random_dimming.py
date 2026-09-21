"""19. 랜덤 색 디밍 — 조종기 RGB / 조종기 Colors / 드론 RGB

강의 예제 7, 8, 9 를 한 파일로 합쳤다. 셋 다 구조가 같고 바뀌는 건
"색을 어떻게 뽑느냐(RGB vs Colors)" 와 "어디로 보내느냐(모드 enum)" 뿐이다.

[핵심 학습 내용 1 — 반환값은 응답이 아니라 송신 프레임]
sendLightModeColor(...) 의 반환값을 받아 찍는 예제가 나오는데, 이건 드론이 보낸 답이 아니다.
transfer() 가 **방금 시리얼로 써 보낸 바이트열을 그대로 돌려주는 것**이다.
(포트가 안 열려 있으면 None, 인자 타입이 틀려도 None)
드론의 응답을 보려면 03번처럼 setEventHandler 로 받아야 한다.
그러니 로그 컬럼 이름을 response 라고 붙이면 오해하기 쉽다 — sent 가 맞다.

[핵심 학습 내용 2 — convertByteArrayToString 은 이미 있다]
바이트열을 16진수 문자열로 바꿔 주는 이 헬퍼는 CodingDrone 라이브러리에 들어 있다
(`CodingDrone/drone.py`). 직접 만들 필요가 없고, 아래처럼 import 해서 쓴다.
강의 예제가 `from CodingDrone.drone import *` 를 쓰니 따로 안 보였을 뿐이다.

[핵심 학습 내용 3 — Colors.EndOfType 은 색이 아니다]
    colors = Colors(random.randint(0, Colors.EndOfType.value))   # 강의 예제
randint 는 **상한을 포함**하므로 EndOfType(141) 이 뽑힐 수 있다. 이건 목록의 끝을
표시하는 경계값이지 색이 아니다. 실제 색은 0 ~ 140.
    colors = Colors(random.randint(0, Colors.EndOfType.value - 1))   # 이렇게
"""

import random
from time import sleep

from CodingDrone.drone import Drone, convertByteArrayToString
from CodingDrone.protocol import (
    Colors,
    DeviceType,
    LightModeController,
    LightModeDrone,
)

from drone_util import find_port

REPEAT = 10
DELAY = 0.6
LAST_COLOR = Colors.EndOfType.value - 1  # 140. EndOfType 은 경계값이라 제외


def random_rgb():
    return (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )


def main():
    dron = Drone()
    try:
        dron.open(find_port())

        # 예제7 — 조종기, RGB 랜덤
        print("[조종기 / RGB 랜덤]")
        for i in range(REPEAT):
            r, g, b = random_rgb()
            sent = dron.sendLightModeColor(LightModeController.BodyDimming, 1, r, g, b)
            print(f"{i:2} / r={r:3} g={g:3} b={b:3} / sent: {convertByteArrayToString(sent)}")
            sleep(DELAY)

        # 예제8 — 조종기, Colors 팔레트 랜덤
        print("[조종기 / Colors 랜덤]")
        for i in range(REPEAT):
            color = Colors(random.randint(0, LAST_COLOR))
            sent = dron.sendLightModeColors(LightModeController.BodyDimming, 1, color)
            print(f"{i:2} / {color.name:<16} / sent: {convertByteArrayToString(sent)}")
            sleep(DELAY)

        # 예제9 — 드론, RGB 랜덤 (모드 enum 만 바뀐다)
        print("[드론 / RGB 랜덤]")
        for i in range(REPEAT):
            r, g, b = random_rgb()
            sent = dron.sendLightModeColor(LightModeDrone.BodyDimming, 1, r, g, b)
            print(f"{i:2} / r={r:3} g={g:3} b={b:3} / sent: {convertByteArrayToString(sent)}")
            sleep(DELAY)
    finally:
        dron.sendLightManual(DeviceType.Controller, 0xFF, 0)
        dron.sendLightManual(DeviceType.Drone, 0xFF, 0)
        sleep(0.1)
        dron.close()


if __name__ == "__main__":
    main()
