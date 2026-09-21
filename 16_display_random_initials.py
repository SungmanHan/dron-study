"""16. [과제] 조종기 LCD 에 이니셜 + 원을 랜덤 위치로 10회 출력

요구사항: 디스플레이에 본인 이니셜 문자와 원 도형이 랜덤으로 10번 출력되게 한다.

[핵심 학습 내용]
1) 래퍼를 쓴다.
   수업 예제는 Header + DisplayDrawString 을 직접 조립했지만
   sendDisplayDrawString(x, y, message, font, pixel) 이 같은 일을 한다.
   가변 길이(getSize() + len(message)) 계산도 래퍼가 해 준다.

2) 이니셜은 ASCII 로.
   내부에서 encode('ascii', 'ignore') 를 하기 때문에 한글은 에러 없이 사라진다.
   아래에서 미리 검사해서 "조용히 안 나오는" 상황을 막는다.

3) 랜덤 좌표를 화면 밖으로 보내지 않는다.
   좌표는 좌상단 기준이라 x, y 는 글자의 **왼쪽 위**다. 0~127 / 0~63 으로 뽑으면
   오른쪽·아래가 잘린다. 글꼴 크기 x 글자 수만큼 여유를 빼고 뽑는다.
   (5x8 글꼴 = 글자당 5px, 높이 8px / 10x16 글꼴 = 글자당 10px, 높이 16px)
"""

import random
from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import DeviceType, DisplayFont, DisplayPixel

from drone_util import find_port

INITIALS = "HAN"  # 본인 이니셜로 바꿀 것. 영문/숫자만 (한글은 표시되지 않는다)
FONT = DisplayFont.LiberationMono10x16

WIDTH, HEIGHT = 128, 64
FONT_SIZE = {  # (글자 폭, 높이)
    DisplayFont.LiberationMono5x8: (5, 8),
    DisplayFont.LiberationMono10x16: (10, 16),
}
REPEAT = 10
DELAY = 0.5


def random_text_position(message, font):
    """문자열이 화면 안에 다 들어오는 좌상단 좌표를 뽑는다."""
    char_w, char_h = FONT_SIZE[font]
    max_x = max(0, WIDTH - char_w * len(message))
    max_y = max(0, HEIGHT - char_h)
    return random.randint(0, max_x), random.randint(0, max_y)


def main():
    if not INITIALS.isascii():
        raise SystemExit("INITIALS 는 영문/숫자만 가능합니다 (한글은 화면에 나오지 않습니다)")

    dron = Drone()
    try:
        dron.open(find_port())
        dron.sendPing(DeviceType.Controller)

        dron.sendDisplayClearAll(DisplayPixel.Black)
        sleep(DELAY)

        for i in range(1, REPEAT + 1):
            # 매번 새 화면에서 시작해야 이전 것과 겹치지 않는다
            dron.sendDisplayClearAll(DisplayPixel.Black)

            x, y = random_text_position(INITIALS, FONT)
            dron.sendDisplayDrawString(x, y, INITIALS, FONT, DisplayPixel.White)

            cx = random.randint(0, WIDTH - 1)
            cy = random.randint(0, HEIGHT - 1)
            radius = random.randint(5, 20)
            dron.sendDisplayDrawCircle(cx, cy, radius, DisplayPixel.White, False)

            print(f"[{i:2}/{REPEAT}] {INITIALS} ({x},{y}) / 원 ({cx},{cy}) r={radius}")
            sleep(DELAY)
    finally:
        sleep(0.1)
        dron.close()


if __name__ == "__main__":
    main()
