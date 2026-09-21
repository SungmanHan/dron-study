"""20. [과제] 드론 LED 를 랜덤 색으로 20회 디밍

요구사항: 조종기와 드론을 페어링한 상태에서 드론 LED 가 랜덤 색상으로 20회 디밍되게 한다.
제출자료: 코딩 원본파일(.py) + 실행데이터 → 실행하면 log_drone_light_dimming.txt 가 생긴다.

19번(예제9)과 같은 패턴이고 횟수만 20회다.
  - 디밍 효과는 LightModeDrone.BodyDimming 모드가 만든다. 코드는 색만 뽑아 보낸다
  - 목적지가 드론인 이유는 모드 enum 이 LightModeDrone 이기 때문이다 (18번 참고)

[로그 컬럼 이름 주의]
sendLightModeColor() 의 반환값은 드론의 **응답이 아니라 방금 보낸 프레임**이다.
(transfer() 가 시리얼에 쓴 바이트열을 그대로 돌려준다. 포트가 닫혀 있으면 None)
그래서 로그 컬럼을 response 가 아니라 sent 로 적는다.

[끝나면 꺼 준다]
Mode 계열은 명령을 멈춰도 드론이 그 패턴을 계속 유지한다.
finally 에서 sendLightManual(..., 0xFF, 0) 으로 소등한다.
"""

import random
from datetime import datetime
from time import sleep

from CodingDrone.drone import Drone, convertByteArrayToString
from CodingDrone.protocol import DeviceType, LightModeDrone

from drone_util import find_port

LOG_FILE = "log_drone_light_dimming.txt"
REPEAT = 20
DELAY = 0.6
ALL_FLAGS = 0xFF


def main():
    dron = Drone()
    try:
        dron.open(find_port())

        with open(LOG_FILE, "w", encoding="utf-8") as log:
            log.write(f"실행 시작: {datetime.now().isoformat()}\n")
            log.write("i, r, g, b, sent\n")

            for i in range(1, REPEAT + 1):
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)

                sent = dron.sendLightModeColor(LightModeDrone.BodyDimming, 1, r, g, b)

                line = (
                    f"{i:2}/{REPEAT} / r={r:3} g={g:3} b={b:3}"
                    f" / sent: {convertByteArrayToString(sent)}"
                )
                print(line)
                log.write(line + "\n")

                sleep(DELAY)

            log.write(f"실행 종료: {datetime.now().isoformat()}\n")

        print(f"실행 로그: {LOG_FILE}")
    finally:
        dron.sendLightManual(DeviceType.Drone, ALL_FLAGS, 0)
        sleep(0.1)
        dron.close()


if __name__ == "__main__":
    main()
