"""14. 조종기 LCD — 지우기 / 반전 / 도형 그리기

조종기에는 128 x 64 흑백 LCD 가 있다. 좌표는 x 0~127, y 0~63 이고 원점은 좌상단이다.
부저·진동과 마찬가지로 목적지는 조종기(DeviceType.Controller) 라 드론 본체는 필요 없다.

  sendDisplayClearAll(pixel)                       화면 전체를 pixel 색으로 채운다
  sendDisplayClear(x, y, w, h, pixel)              일부 영역만 채운다
  sendDisplayInvert(x, y, w, h)                    일부 영역을 반전시킨다
  sendDisplayDrawPoint(x, y, pixel)                점
  sendDisplayDrawLine(x1, y1, x2, y2, pixel, line) 선
  sendDisplayDrawRect(x, y, w, h, pixel, fill, line)  사각형
  sendDisplayDrawCircle(x, y, radius, pixel, fill)    원

[핵심 학습 내용]
- "Clear" 는 지운다기보다 **그 영역을 지정한 색으로 칠한다**.
  ClearAll(Black) 뒤에 Clear(..., White) 를 하면 그 자리가 흰 사각형이 된다.
- 그리기 명령은 보내고 바로 반환한다. 화면이 갱신되는 걸 눈으로 보려면 sleep 을 넣는다.
- 인자 타입을 틀리면 조용히 무시된다. pixel/line 은 반드시 enum 이어야 한다.
    dron.sendDisplayDrawPoint(64, 32, 1)                 # 1 은 int -> 아무 일도 안 일어남
    dron.sendDisplayDrawPoint(64, 32, DisplayPixel(1))   # OK

[열거형]
  DisplayPixel : Black(0) White(1) Inverse(2) Outline(3)   <- 4개. 0/1 만 있는 게 아니다
  DisplayLine  : Solid(0) Dotted(1) Dashed(2)
  DisplayFont  : LiberationMono5x8(0) LiberationMono10x16(1)
  DisplayAlign : Left(0) Center(1) Right(2)

[강의 예제의 함정]
- 예제에서 random 을 import 하지 않고 썼는데 동작한다. `from CodingDrone.drone import *` 가
  drone.py 안의 `import random` 까지 끌고 들어오기 때문이다. **우연히 되는 것**이므로
  random 을 쓸 거면 직접 import 한다.
- 예제 6, 7 의 마지막 줄은 `drone.close` — 괄호가 없어 메서드 객체만 꺼내고 끝난다.
  포트가 안 닫히고 다음 실행에서 multiple access on port 가 난다.
"""

import random
from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import DeviceType, DisplayLine, DisplayPixel

from drone_util import find_port

DELAY = 0.5
WIDTH, HEIGHT = 128, 64


def main():
    dron = Drone()
    try:
        dron.open(find_port())
        dron.sendPing(DeviceType.Controller)

        # 1) 지우기 — 전체를 검게 칠하고, 일부만 희게 칠한다
        dron.sendDisplayClearAll(DisplayPixel.Black)
        sleep(DELAY)
        dron.sendDisplayClear(59, 27, 10, 10, DisplayPixel.White)
        sleep(DELAY)

        # 2) 반전
        dron.sendDisplayInvert(44, 12, 40, 40)
        sleep(DELAY)

        # 3) 점
        dron.sendDisplayClearAll(DisplayPixel.Black)
        dron.sendDisplayDrawPoint(64, 32, DisplayPixel.White)
        sleep(DELAY)

        # 4) 선
        dron.sendDisplayClearAll(DisplayPixel.Black)
        dron.sendDisplayDrawLine(10, 10, 118, 45, DisplayPixel.White)
        sleep(DELAY)

        # 5) 사각형 — flagFill=False 면 테두리만, line 으로 실선/점선 선택
        dron.sendDisplayClearAll(DisplayPixel.Black)
        dron.sendDisplayDrawRect(
            44, 12, 40, 40, DisplayPixel.White, False, DisplayLine.Dashed
        )
        sleep(DELAY)

        # 6) 원 — flagFill=True 면 채운 원
        dron.sendDisplayClearAll(DisplayPixel.Black)
        dron.sendDisplayDrawCircle(65, 32, 10, DisplayPixel.White, True)
        sleep(DELAY)

        # 7) 랜덤 선 — 강의 예제는 100회에 0.5초라 50초가 걸린다. 20회로 줄였다
        dron.sendDisplayClearAll(DisplayPixel.Black)
        for _ in range(20):
            dron.sendDisplayDrawLine(
                random.randint(0, WIDTH - 1),
                random.randint(0, HEIGHT - 1),
                random.randint(0, WIDTH - 1),
                random.randint(0, HEIGHT - 1),
                DisplayPixel(random.randint(0, 1)),  # Black / White
                DisplayLine(random.randint(0, 2)),  # Solid / Dotted / Dashed
            )
            sleep(0.2)

        # 8) 랜덤 원
        dron.sendDisplayClearAll(DisplayPixel.Black)
        for _ in range(20):
            dron.sendDisplayDrawCircle(
                random.randint(0, WIDTH - 1),
                random.randint(0, HEIGHT - 1),
                random.randint(5, 20),
                DisplayPixel.White,
                False,
            )
            sleep(0.2)
    finally:
        sleep(0.1)
        dron.close()  # 괄호 필수


if __name__ == "__main__":
    main()
