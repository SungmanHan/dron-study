"""31. 정지는 착륙이 아니다 — `sendStop` vs `sendLanding`   ⚠️ 실제로 이륙한다

    MODE = 1   이륙 → 5초 → sendStop()                     (강의 예제2)
               ⚠️ 뜬 상태에서 모터를 끈다 = 그 자리에서 **떨어진다**
    MODE = 2   이륙 → 6.4초 호버링 → 3.6초 하강 → sendStop()  (강의 예제3-A)
               충분히 낮춘 뒤 끄므로 훨씬 안전하다. 기본값.

두 함수는 이름만 비슷하고 하는 일이 다르다.

    sendLanding()   CommandType.FlightEvent + FlightEvent.Landing(0x12)
                    → 고도를 천천히 낮춰 착지한 뒤 모터를 끈다. **정상 종료용**
    sendStop()      CommandType.Stop (0x01)  ← FlightEvent 가 아니다
                    → 모터를 즉시 끈다. 공중이면 추락. **비상용**

"비상 상황 = 무조건 Stop" 으로 외우면 위험하다. 대부분의 상황에서 필요한 건
`sendLanding()` 쪽이고, `sendStop()` 은 드론이 벽이나 사람 쪽으로 돌진해서
**떨어뜨리는 편이 나은** 순간에만 쓴다.

[MODE 2 가 하는 일 — throttle 로 미리 내려놓기]
    dron.sendControlWhile(0, 0, 0, -25, 3600)
네 번째 값이 throttle 이다. 음수 = 하강, 양수 = 상승 (28 참고).
-25 로 3.6초면 바닥 가까이 내려온다. 이 상태에서 Stop 하면 떨어져도 충격이 작다.
`sendControlWhile` 은 지정한 시간 동안 블로킹이므로 뒤에 sleep 이 필요 없다.

[하강 시간은 고도에 따라 다르다]
-25 / 3.6초는 강의 기준 값일 뿐 정해진 답이 아니다. 천장이 낮은 방에서 이륙했다면
그 전에 바닥에 닿고, `sendControlWhile` 은 남은 시간 동안 계속 하강 명령을 보낸다.
바닥에 눌린 채로 모터가 도는 상태가 되므로 낮은 고도에서는 시간을 줄일 것.
23/24 처럼 하방 센서(`DataType.Range`) 를 읽어 높이로 판단하는 편이 정확하다.

[실습 전]
매트·이불 같은 부드러운 바닥 위에서, 프로펠러 가드를 끼우고 할 것.
MODE 1 은 "이렇게 떨어진다" 를 한 번 보는 용도이고, 평소 쓸 코드가 아니다.

실행:  .venv/bin/python 31_flight_stop.py
"""

from time import sleep

from CodingDrone.drone import Drone

from drone_util import countdown, find_port

MODE = 2  # 1 = 공중에서 바로 정지(위험) / 2 = 하강 후 정지

TAKEOFF_WAIT = 5
HOVER_MS = 6400  # MODE 2 호버링 (6.4초)
DESCEND_MS = 3600  # MODE 2 하강 (3.6초)
DESCEND_THROTTLE = -25  # 음수 = 하강

dron = Drone()

if not dron.open(find_port()):
    raise SystemExit("드론 연결 실패 — USB 연결을 확인하세요")

try:
    print("TakeOff")
    dron.sendTakeOff()

    if MODE == 1:
        # ── 강의 예제2 — 뜬 상태 그대로 모터 정지 ─────────────────
        countdown(TAKEOFF_WAIT, "이륙 안정화")

        print("Stop  — 모터 즉시 정지 (떨어집니다)")
        dron.sendStop()
        countdown(5, "정리")

    else:
        # ── 강의 예제3-A — 내려놓고 나서 정지 ──────────────────────
        # 이륙 직후 기다리지 않는다. 바로 뒤의 호버링 명령이 6.4초간
        # 블로킹되므로 이륙 안정화 시간은 그 안에서 확보된다.
        print("Hovering")
        dron.sendControlWhile(0, 0, 0, 0, HOVER_MS)

        print("Throttle down")
        dron.sendControlWhile(0, 0, 0, DESCEND_THROTTLE, DESCEND_MS)

        print("Stop  — 낮은 고도에서 모터 정지")
        dron.sendStop()
        countdown(3, "정리")

finally:
    # Stop 으로 끝나는 예제지만, 중간에 Ctrl+C 로 빠져나왔다면 아직 떠 있다.
    # 그 경우를 위해 착륙을 보낸다. 이미 멈춘 드론에는 아무 영향이 없다.
    dron.sendLanding()
    sleep(0.1)
    dron.close()
    print("포트 닫음")
