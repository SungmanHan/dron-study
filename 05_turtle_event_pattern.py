"""05. 사전 개념 — 이벤트 콜백 패턴 (turtle)

드론 코드를 보기 전에 turtle 로 같은 구조를 먼저 확인한다.
turtle 의 onscreenclick() + mainloop() 는 CodingDrone 의
setEventHandler() + 백그라운드 수신 스레드와 정확히 같은 그림이다.

    turtle                              CodingDrone
    ---------------------------------   ------------------------------------------
    turtle.onscreenclick(draw_circle)   drone.setEventHandler(DataType.Button, cb)
    turtle.mainloop()                   Drone() 이 띄운 백그라운드 스레드가 check() 를 계속 돈다
    클릭 -> 콜백에 (x, y) 전달          프레임 수신 -> 콜백에 Button/Joystick 객체 전달

[핵심 학습 내용]
- 콜백은 "이벤트 루프가 돌고 있을 때만" 불린다.
  turtle 은 mainloop(), 드론은 Drone() 의 백그라운드 수신 스레드가 그 역할이다.
  Drone(False) 로 열면 check() 를 아무도 돌리지 않아 핸들러가 영영 호출되지 않는다.
- 콜백 안에서 난 예외는 바깥 try/except 로 안 잡힌다.
  실습 중 penup() 을 penpu() 로 잘못 쳤더니, 클릭할 때마다 콜백 안에서 예외가 나고
  화면에는 아무것도 안 그려지는데 프로그램은 멀쩡히 돌았다.
  => "아무 반응이 없다" 는 증상은 콜백 내부 예외를 먼저 의심한다.
"""

import turtle


def draw_circle(x, y):
    turtle.penup()  # penpu() 오타 주의 — 콜백 안에서 조용히 터진다
    turtle.goto(x, y)
    turtle.pendown()
    turtle.circle(50)


def main():
    turtle.onscreenclick(draw_circle)
    turtle.mainloop()  # 이벤트 루프. 이게 없으면 콜백이 불릴 기회 자체가 없다


if __name__ == "__main__":
    main()
