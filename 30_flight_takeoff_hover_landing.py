"""30. 자율 비행의 기본형 — 이륙 → 호버링 → 착륙   ⚠️ 실제로 이륙한다

27~29 는 사람이 키를 누르는 만큼만 움직였다. 여기서부터는 **명령을 코드에 순서대로
나열해 두고 손을 떼는** 자율 비행이다. 사람이 개입할 수 없으니, 명령이 끝날 때까지
기다리는 일을 코드가 대신 해줘야 한다.

    이륙 → 5초 대기 → 3초 호버링 → 착륙 → 5초 대기 → 포트 닫기

이 틀이 19강 모든 예제의 뼈대다. 가운데 "호버링" 자리에 이동 명령을 끼워 넣으면
32(거리 이동) · 33(리턴홈) · 34(패턴 비행) 가 된다.

[왜 명령마다 기다리는가]
`sendTakeOff()` / `sendLanding()` 은 "이륙해라" 라는 말을 **보내고 바로 리턴**한다.
드론이 실제로 다 뜨는 데는 몇 초가 걸리므로, 기다리지 않고 다음 줄로 넘어가면
이륙 도중에 착륙 명령이 들어가 동작이 꼬인다. `countdown()` 이 그 대기다.

[딱 하나 블로킹인 함수 — sendControlWhile]
    dron.sendControlWhile(0, 0, 0, 0, 1000)
라이브러리 내부가 `while` 로 1초 동안 `sendControl(0,0,0,0)` 을 20ms 간격(초당 50회)으로
반복 전송한다. **그 1초 동안 다음 줄로 넘어가지 않는다.** 그래서 이 명령 뒤에는
따로 기다릴 필요가 없다 — 강의 코드의 `sleep(0.01)` 은 없어도 그만이라 뺐다.

[호버링 명령이 꼭 필요한 건 아니다]
네 값이 모두 0 = "스틱을 놓은 상태". 그런데 드론은 **마지막 명령을 계속 유지**하므로
이륙 후 아무 명령도 안 보내도 제자리에 떠 있다. 아래 호버링 구간은 "지금부터 3초는
제자리" 라는 것을 코드에 명시하는 의미이고, 실제로 필요해지는 건 이 자리에
`sendControl(0, 30, 0, 0)` 같은 이동 값을 넣을 때다.

[중단하는 방법]
대기 중 Ctrl+C → `KeyboardInterrupt` → `finally` 의 `sendLanding()` 이 나간다.
터미널 창을 그냥 닫으면 파이썬만 죽고 **드론은 마지막 명령을 유지한 채 계속 떠 있다.**
반드시 Ctrl+C 로 빠져나올 것.

실행:  .venv/bin/python 30_flight_takeoff_hover_landing.py
"""

from time import sleep

from CodingDrone.drone import Drone

from drone_util import countdown, find_port

TAKEOFF_WAIT = 5  # 이륙 후 자세가 안정될 때까지
HOVER_SEC = 3  # 호버링 시간 (1초짜리 sendControlWhile 을 이 횟수만큼)
LANDING_WAIT = 5  # 착지 완료까지

dron = Drone()  # 백그라운드 수신 ON

if not dron.open(find_port()):  # open() 은 실패해도 예외가 아니라 False 를 돌려준다
    raise SystemExit("드론 연결 실패 — USB 연결을 확인하세요")

try:
    # 1) 이륙 — 내부적으로 CommandType.FlightEvent + FlightEvent.TakeOff
    print("TakeOff")
    dron.sendTakeOff()
    countdown(TAKEOFF_WAIT, "이륙 안정화")

    # 2) 호버링 — 네 값 모두 0. 한 번 호출할 때마다 1초씩 블로킹된다.
    #    sendControlWhile(0, 0, 0, 0, 3000) 한 줄과 결과는 같고,
    #    이렇게 쪼개면 남은 시간을 찍을 수 있다.
    print("Hovering")
    for i in range(HOVER_SEC, 0, -1):
        print(f"  호버링 {i}")
        dron.sendControlWhile(0, 0, 0, 0, 1000)

    # 3) 착륙 — 천천히 내려와 모터를 끈다. sendStop() 과 다르다(31 참고).
    print("Landing")
    dron.sendLanding()
    countdown(LANDING_WAIT, "착지 대기")

finally:
    # 예외·Ctrl+C 로 빠져나와도 착륙은 보낸다.
    # 이미 착륙한 드론에 한 번 더 보내도 아무 일도 일어나지 않는다.
    dron.sendLanding()
    sleep(0.1)  # 수신 스레드가 read 중일 때 close 하면 Errno 6
    dron.close()
    print("포트 닫음")
