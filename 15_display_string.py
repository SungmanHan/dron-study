"""15. 조종기 LCD — 문자열 / 정렬 문자열

  sendDisplayDrawString(x, y, message, font, pixel)
  sendDisplayDrawStringAlign(x_start, x_end, y, message, align, font, pixel)

[핵심 학습 내용 — 래퍼가 이미 있다]
수업에서는 Header + DisplayDrawString 을 직접 만들어
header.length = getSize() + len(message) 로 다시 계산한 뒤 transfer() 로 보냈다.
그런데 CodingDrone 1.0.4 에는 위 두 래퍼가 있고, **본문이 바로 그 코드다.**
길이 재계산도 래퍼가 해 준다. 그러니 실습은 래퍼로 하고,
저수준은 "문자열 프레임은 길이가 가변" 이라는 걸 보는 용도로만 남긴다.

문자열 프레임만 length 를 다시 계산하는 이유:
다른 데이터는 크기가 고정이라 getSize() 로 끝나지만, 문자열은 뒤에 message 가
그대로 붙는 가변 길이 프레임이라 getSize() + len(message) 가 실제 길이다.

[⚠️ 한글은 조용히 사라진다]
DisplayDrawString.toArray() 는 message.encode('ascii', 'ignore') 로 인코딩한다.
'ignore' 라서 ASCII 가 아닌 글자는 **에러 없이 버려진다.** 게다가 length 는
문자 수로 계산되므로 헤더 길이와 실제 바이트 수가 어긋난다. 실측:

    message = "한글"  ->  header.length = 6 + 2 = 8 인데 실제 데이터는 6바이트
    message = "HAN"   ->  header.length = 6 + 3 = 9,  실제 데이터도 9바이트

화면에 아무것도 안 나오거나 깨지는 이유가 이것이다. **영문/숫자만 쓴다.**

[인자 순서 주의]
래퍼는 message 가 세 번째 인자다. 데이터 객체의 필드 순서(x, y, font, pixel, message)와
다르므로, 저수준 코드를 래퍼로 옮길 때 헷갈리기 쉽다.
font, pixel 을 enum 이 아닌 int 로 넘기면 조용히 None 을 반환한다(아무 것도 안 보냄).
"""

import random
from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import (
    DataType,
    DeviceType,
    DisplayAlign,
    DisplayDrawString,
    DisplayFont,
    DisplayPixel,
    Header,
)

from drone_util import find_port

DELAY = 0.5


def send_string_raw(dron, x, y, message, font, pixel):
    """래퍼를 쓰지 않고 프레임을 직접 만들어 보낸다 (학습용)."""
    header = Header()
    header.dataType = DataType.DisplayDrawString
    header.from_ = DeviceType.Base  # 라이브러리 래퍼도 Base(0x70) 를 쓴다
    header.to_ = DeviceType.Controller
    # 가변 길이: 고정 필드(6) + 문자열 길이
    header.length = DisplayDrawString.getSize() + len(message)

    data = DisplayDrawString()
    data.x = x
    data.y = y
    data.font = font
    data.pixel = pixel
    data.message = message

    return dron.transfer(header, data)


def main():
    dron = Drone()
    try:
        dron.open(find_port())
        dron.sendPing(DeviceType.Controller)

        # 1) 래퍼로 문자열 — 큰 글꼴
        dron.sendDisplayClearAll(DisplayPixel.Black)
        dron.sendDisplayDrawString(
            40, 24, "HELLO", DisplayFont.LiberationMono10x16, DisplayPixel.White
        )
        sleep(DELAY * 2)

        # 2) 저수준으로 같은 출력
        dron.sendDisplayClearAll(DisplayPixel.Black)
        send_string_raw(
            dron, 40, 24, "HELLO", DisplayFont.LiberationMono10x16, DisplayPixel.White
        )
        sleep(DELAY * 2)

        # 3) 정렬 — x_start ~ x_end 구간 안에서 Left / Center / Right
        dron.sendDisplayClearAll(DisplayPixel.Black)
        for y, align in ((0, DisplayAlign.Left), (24, DisplayAlign.Center), (48, DisplayAlign.Right)):
            dron.sendDisplayDrawStringAlign(
                0, 127, y, align.name.upper(), align,
                DisplayFont.LiberationMono5x8, DisplayPixel.White,
            )
            sleep(DELAY)

        # 4) 랜덤 정렬 출력 (강의 예제 9)
        dron.sendDisplayClearAll(DisplayPixel.Black)
        for _ in range(10):
            dron.sendDisplayDrawStringAlign(
                0,
                127,
                random.randint(0, 63),
                "LOVE",
                DisplayAlign(random.randint(0, 2)),
                DisplayFont(random.randint(0, 1)),
                DisplayPixel(random.randint(0, 1)),
            )
            sleep(DELAY)
    finally:
        sleep(0.1)
        dron.close()


if __name__ == "__main__":
    main()
