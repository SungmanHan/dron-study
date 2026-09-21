"""17. LED 수동 제어 — sendLightManual

  sendLightManual(deviceType, flags, brightness)
    deviceType : DeviceType.Controller(조종기) / DeviceType.Drone(드론)
    flags      : 켤 LED 비트 플래그 (OR 로 합칠 수 있다)
    brightness : 0 ~ 255

LED 계열은 크게 둘이다.
  - 수동 제어  : sendLightManual — 무엇을 어느 밝기로 켤지 직접 지정 (이 파일)
  - 모드 제어  : sendLightMode*/sendLightEvent* — 모드만 주면 깜빡임·디밍은 펌웨어가 만든다 (18번)

[⚠️ flags 값이 조종기와 드론이 다르다]
같은 BodyRed 라도 값이 다르므로 상수를 바꿔 쓰면 엉뚱한 LED 가 켜진다.

  LightFlagsController : BodyRed 0x01  BodyGreen 0x02  BodyBlue 0x04
  LightFlagsDrone      : Rear    0x01  BodyRed   0x02  BodyGreen 0x04  BodyBlue 0x08  A 0x10  B 0x20

flags 는 enum 이 아니라 **int** 를 받는다. 그래서 `.value` 를 붙여야 한다.
`0xFF` 처럼 전체 비트를 켜면 "모든 LED" 라는 뜻이고, brightness 0 과 같이 쓰면 전부 끄기가 된다.

[조용한 실패]
sendLightManual 은 deviceType 이 DeviceType, flags·brightness 가 int 가 아니면
아무것도 보내지 않고 None 을 반환한다. 예외가 나지 않는다.
`LightFlagsController.BodyRed` (.value 없이) 를 넘기면 이 경우에 걸려 조용히 무시된다.

[강의 예제 정리]
예제1·5(조종기/드론 기본)와 예제2(빨강-파랑-초록 반복)를 한 파일로 합쳤다.
예제2 원본은 `while True:` 무한 반복이라 실습 종료가 애매해서 횟수로 바꿨다.
(파이썬에는 `cnt--` 가 없다. `cnt -= 1`.)
"""

from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import DeviceType, LightFlagsController, LightFlagsDrone

from drone_util import find_port

DELAY = 0.5
REPEAT = 3
ALL_FLAGS = 0xFF  # 모든 LED


def blink(dron, device, flag, brightness=100):
    dron.sendLightManual(device, flag, brightness)
    sleep(DELAY)
    dron.sendLightManual(device, flag, 0)
    sleep(DELAY)


def main():
    dron = Drone()
    try:
        dron.open(find_port())

        # 1) 조종기 — 전부 끄고 빨강만 약하게
        dron.sendLightManual(DeviceType.Controller, ALL_FLAGS, 0)
        sleep(1)
        dron.sendLightManual(
            DeviceType.Controller, LightFlagsController.BodyRed.value, 10
        )
        sleep(1)

        # 2) 조종기 — 빨강 / 파랑 / 초록 반복
        for _ in range(REPEAT):
            blink(dron, DeviceType.Controller, LightFlagsController.BodyRed.value)
            blink(dron, DeviceType.Controller, LightFlagsController.BodyBlue.value)
            blink(dron, DeviceType.Controller, LightFlagsController.BodyGreen.value)

        # 3) 드론 — 같은 코드에서 DeviceType 과 LightFlags 만 바뀐다
        dron.sendLightManual(DeviceType.Drone, ALL_FLAGS, 0)
        sleep(1)
        dron.sendLightManual(DeviceType.Drone, LightFlagsDrone.BodyRed.value, 10)
        sleep(1)

        # 4) 플래그는 OR 로 합칠 수 있다 — 빨강+파랑 = 보라
        dron.sendLightManual(
            DeviceType.Drone,
            LightFlagsDrone.BodyRed.value | LightFlagsDrone.BodyBlue.value,
            100,
        )
        sleep(1)
    finally:
        # 실습 끝에는 꺼 둔다. 모드 명령은 끄지 않으면 계속 유지된다
        dron.sendLightManual(DeviceType.Controller, ALL_FLAGS, 0)
        dron.sendLightManual(DeviceType.Drone, ALL_FLAGS, 0)
        sleep(0.1)
        dron.close()


if __name__ == "__main__":
    main()
