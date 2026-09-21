"""18. LED 모드 제어 — sendLightMode* / sendLightEvent*

  sendLightModeColor(lightMode, interval, r, g, b)        지정 모드로 RGB
  sendLightModeColors(lightMode, interval, colors)        지정 모드로 Colors 팔레트
  sendLightEventColor(lightEvent, interval, repeat, r, g, b)   + 반복 횟수
  sendLightEventColors(lightEvent, interval, repeat, colors)

  interval : 내부 밝기 제어 주기 0~65535 (작을수록 빠르다)
  repeat   : 반복 횟수 0~255
  colors   : Colors enum (색 이름 팔레트)

깜빡임·디밍 같은 패턴은 **펌웨어가 만든다.** 우리는 모드와 색만 준다.
Dimming = 색이 점점 밝아졌다 어두워지는 효과이므로, 코드에서 밝기를 조절할 필요가 없다.

[핵심 학습 내용 — 목적지는 lightMode 의 타입이 정한다]
sendLightMode*/sendLightEvent* 에는 deviceType 인자가 없다. 라이브러리가
lightMode 가 어느 enum 인지 보고 목적지를 정한다.

  LightModeController.BodyDimming  ->  header.to_ = Controller
  LightModeDrone.BodyDimming       ->  header.to_ = Drone
  (int 를 그냥 넘기면 Drone 으로 간다)

"드론도 조종기와 사용법이 같고 첫 인자만 바꾸면 된다" 는 말의 실제 내용이 이것이다.
반면 17번의 sendLightManual 은 deviceType 을 인자로 직접 받는다. 두 계열이 다르다.

[모드 목록]
  LightModeController : Body 계열만 — BodyNone/Manual/Hold/Flicker/FlickerDouble/
                        Dimming/Sunrise/Sunset/Rainbow/Rainbow2
  LightModeDrone      : Rear / Body / A / B 네 그룹에 같은 패턴이 반복
  공통 : Hold(계속 켬) Flicker(깜빡임) FlickerDouble(두 번 깜빡) Dimming(천천히 깜빡)

[강의 예제 정리]
예제3·4(조종기)와 예제6(드론)을 한 파일로 합쳤다. 예제4는 예제3에 이벤트 계열 두 개를
덧붙인 것이라 내용이 겹친다.
"""

from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import (
    Colors,
    DeviceType,
    LightModeController,
    LightModeDrone,
)

from drone_util import find_port


def main():
    dron = Drone()
    try:
        dron.open(find_port())

        # ── 조종기 ──────────────────────────────────────────────
        print("Controller BodyHold")
        dron.sendLightModeColor(LightModeController.BodyHold, 200, 200, 200, 0)
        sleep(2)

        print("Controller BodyDimming (RGB)")
        dron.sendLightModeColor(LightModeController.BodyDimming, 3, 200, 0, 200)
        sleep(3)

        print("Controller BodyDimming (Colors.Cyan)")
        dron.sendLightModeColors(LightModeController.BodyDimming, 3, Colors.Cyan)
        sleep(3)

        # Event 계열 — repeat 만큼만 하고 멈춘다
        print("Controller BodyDimming x3 (event, RGB)")
        dron.sendLightEventColor(LightModeController.BodyDimming, 3, 3, 200, 200, 200)
        sleep(3)

        print("Controller BodyDimming x3 (event, Colors.Magenta)")
        dron.sendLightEventColors(LightModeController.BodyDimming, 3, 3, Colors.Magenta)
        sleep(3)

        # ── 드론 — 함수는 그대로, 모드 enum 만 바뀐다 ────────────
        print("Drone BodyHold")
        dron.sendLightModeColor(LightModeDrone.BodyHold, 200, 0, 200, 200)
        sleep(2)

        print("Drone BodyDimming (RGB)")
        dron.sendLightModeColor(LightModeDrone.BodyDimming, 3, 0, 0, 200)
        sleep(3)

        print("Drone BodyDimming x5 (event)")
        dron.sendLightEventColor(LightModeDrone.BodyDimming, 3, 5, 200, 200, 200)
        sleep(3)

        # 드론에만 있는 모드 — 무지개
        print("Drone BodyRainbow")
        dron.sendLightModeColor(LightModeDrone.BodyRainbow, 5, 0, 0, 0)
        sleep(3)
    finally:
        # Mode 계열은 끄기 전까지 계속 유지된다
        dron.sendLightManual(DeviceType.Controller, 0xFF, 0)
        dron.sendLightManual(DeviceType.Drone, 0xFF, 0)
        sleep(0.1)
        dron.close()


if __name__ == "__main__":
    main()
