"""22. 센서 읽기 — 모션 Motion / 자세 Attitude (17강 예제2, 3)

둘 다 자이로(IMU)에서 나오는 값이고 구조는 21번과 같다. **이륙하지 않는다** —
드론을 손에 들고 기울이거나 돌리면서 값이 어떻게 변하는지 보는 실습이다.

[Motion — Int16 9개]
    accelX/Y/Z              가속도. **m/s² 를 10배 한 정수** (98 ≈ 9.8m/s² = 중력)
    gyroRoll/Pitch/Yaw      각속도(degree/s) — "지금 얼마나 빨리 돌고 있나"
    angleRoll/Pitch/Yaw     각도(degree)     — "지금 얼마나 기울어 있나"

[Attitude — Int16 3개]
    roll / pitch / yaw      각도(degree). Motion 의 angle* 과 같은 성격이다.

[핵심 학습 내용 1 — gyro 와 angle 은 다르다]
기울이는 **동안** gyro 가 튀고, 멈추면 gyro 는 0 으로 돌아온다.
angle 은 기울인 채 멈춰 있으면 그 값을 유지한다. 이 차이를 눈으로 확인하는 게 예제2의 목적이다.

[핵심 학습 내용 2 — Altitude(고도) ≠ Attitude(자세)]
철자가 한 글자 차이다. Alti**t**ude = 높이, Atti**t**ude = 기울기.
강의 자료에서도 주석이 섞여 있었다("# Altitude 정보 요청" 인데 실제로는 Motion/Attitude 요청).

[핵심 학습 내용 3 — 자세만 필요하면 Attitude 가 가볍다]
같은 각도 정보를 Motion 은 9개 값과 함께, Attitude 는 3개만 받는다.
Attitude 는 Int16 이라 `{:.3f}` 로 찍으면 항상 .000 으로 나온다 (Altitude 는 Float32 라 소수가 보인다).
"""

from time import sleep

from CodingDrone.drone import Drone
from CodingDrone.protocol import DataType, DeviceType

from drone_util import find_port

REPEAT = 10
INTERVAL = 0.5


def event_motion(motion):
    print("eventMotion()")
    # {0:5} = 폭 5칸 정렬. 정수라 소수점 지정이 없다
    print("- Accel: {0:5}, {1:5}, {2:5}".format(motion.accelX, motion.accelY, motion.accelZ))
    print("-  Gyro: {0:5}, {1:5}, {2:5}".format(motion.gyroRoll, motion.gyroPitch, motion.gyroYaw))
    print("- Angle: {0:5}, {1:5}, {2:5}".format(motion.angleRoll, motion.anglePitch, motion.angleYaw))


def event_attitude(attitude):
    print("eventAttitude() / roll {0:5}, pitch {1:5}, yaw {2:5}".format(
        attitude.roll, attitude.pitch, attitude.yaw))


def request_loop(dron, data_type, label):
    print(f"── {label} — 드론을 기울이거나 돌려 보세요")
    for i in range(REPEAT, 0, -1):
        print(i)
        dron.sendRequest(DeviceType.Drone, data_type)
        sleep(INTERVAL)


def main():
    dron = Drone()
    try:
        dron.open(find_port())

        # 핸들러 등록은 한 번이면 된다 (강의 예제는 루프 안에서 매번 등록했다)
        dron.setEventHandler(DataType.Motion, event_motion)
        dron.setEventHandler(DataType.Attitude, event_attitude)

        request_loop(dron, DataType.Motion, "Motion")
        request_loop(dron, DataType.Attitude, "Attitude")
    finally:
        sleep(0.1)
        dron.close()


if __name__ == "__main__":
    main()
