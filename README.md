# 코딩드론 학습 기록

CodingDrone(파이썬) 으로 드론 제어를 실습하면서 정리한 내용.
환경은 macOS 12 (Intel) / Homebrew Python 3.14 / CodingDrone 1.0.4.

## 파일

| 파일 | 내용 |
|---|---|
| `drone_util.py` | 동글 포트 자동 탐색 |
| `01_list_ports.py` | 시리얼 포트 목록 확인 |
| `02_ping_manual.py` | Ping/Ack — `check()` 를 직접 돌리는 방식 |
| `03_ping_event.py` | Ping/Ack — 이벤트 핸들러 방식 (권장) |
| `04_api_explorer.py` | 사용 가능한 명령·상수 목록 뽑기 |
| `05_turtle_event_pattern.py` | 사전 개념 — turtle 로 보는 이벤트 콜백 패턴 |
| `06_button_event.py` | 조종기 버튼 입력 (`DataType.Button`) |
| `07_button_turtle.py` | 버튼으로 turtle 도형 그리기 |
| `08_joystick_event.py` | 조종기 조이스틱 입력 (`DataType.Joystick`) |
| `09_joystick_direction.py` | [과제] 조이스틱 방향 → TM/BM/ML/MR 출력 |

## 환경 구축

macOS 의 Homebrew Python 은 시스템 영역 보호(PEP 668) 때문에
`pip3 install` 이 `externally-managed-environment` 로 막힌다.
가상환경을 만들어 그 안에 설치한다.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

venv 를 활성화하면 `pip`, `pip3`, `python`, `python3` 가 모두 venv 안쪽을 가리키므로
강의 명령어를 그대로 따라가도 된다. 프롬프트가 `(.venv)` 로 바뀌었는지로 확인.

`--break-system-packages` 로 우회할 수도 있지만 Homebrew Python 이 깨질 수 있어 쓰지 않는다.

주피터로 실습할 경우, **같은 venv 안에** 설치하고 커널을 등록해야 한다.
다른 곳에 설치하면 커널이 CodingDrone 을 찾지 못한다.

```bash
pip install jupyter
python -m ipykernel install --user --name=dron --display-name "Python (dron)"
```

## 하드웨어 연결

동글은 STM32 Virtual ComPort(USB CDC) 로 잡힌다. **별도 드라이버 불필요.**

```
/dev/cu.usbmodem31A9388730351   STM32 Virtual ComPort in FS Mode
```

- macOS 에서는 `/dev/tty.*` 가 아니라 **`/dev/cu.*`** 를 쓴다. tty 쪽은 open 에서 블로킹된다.
- 포트 이름의 숫자는 USB 포트를 바꿔 꽂으면 달라진다. 하드코딩하지 말고 매번 탐색할 것.
- USB 허브나 C타입 젠더를 거치면 인식이 불안정하다. 본체 포트에 직접 연결한다.

## 통신 프로토콜

실제로 오간 바이트를 뜯어보면 구조가 보인다.
(`Drone(False, True, True, True, True)` 로 송수신 로그를 켜서 확인)

```
구조: [0A 55 시작] [dataType] [length] [from] [to] [data...] [crc16]

송신 Ping    : 0A 55 | 01 08 70 20 | 00 00 00 00 00 00 00 00 | 86 D9
수신 Ack     : 0A 55 | 02 0B 20 70 | 01 44 1C 00 ...          | 1B BF
수신 조이스틱 : 0A 55 | 71 08 20 70 | 00 00 22 02 00 00 22 02  | 90 0D
```

- `0x70` = Base(내 PC), `0x20` = Controller(조종기), `0x10` = Drone(드론 본체)
- `0x01` Ping, `0x02` Ack, `0x71` Joystick
- **조종기는 연결되어 있는 동안 조이스틱 데이터를 초당 수백 프레임 계속 송신한다.**
  이 사실이 아래 문제의 원인이 된다.

## 수신 방식 두 가지

### 수동 — `Drone(False)`

`check()` 를 직접 호출해야 파싱이 진행된다. 강의 예제가 이 형태.

```python
dron = Drone(False)
while time.time() < started + 1.0:
    if dron.check() == DataType.Ack:
        ...
```

루프에 `sleep(0.01)` 을 넣으면 실패한다. 1초에 100번밖에 못 도는데
조이스틱 프레임이 그보다 수십 배 빠르게 밀려들어 버퍼가 계속 쌓이고,
Ack 은 그 뒤에 묻힌 채 타임아웃된다. **sleep 없이 최대한 빠르게 돌린다.**

### 이벤트 핸들러 — `Drone()`

`flagCheckBackground=True` 가 기본값이라 백그라운드 스레드가 `check()` 를 돌린다.
콜백만 등록하면 되므로 실습에는 이쪽이 훨씬 편하다.

```python
dron = Drone()
dron.setEventHandler(DataType.Ack, event_ack)
dron.sendPing(DeviceType.Controller)
sleep(0.5)
```

**핸들러는 백그라운드 수신이 켜져 있어야 동작한다.**
`Drone(False)` 객체에 핸들러를 걸면 `check()` 를 아무도 돌리지 않아 영영 호출되지 않는다.

## 콘트롤러 입력 — 버튼 / 조이스틱

### 이벤트 콜백 패턴은 turtle 과 같은 그림이다

| turtle | CodingDrone |
|---|---|
| `turtle.onscreenclick(draw_circle)` | `drone.setEventHandler(DataType.Button, event_button)` |
| `turtle.mainloop()` | `Drone()` 이 띄운 백그라운드 스레드가 `check()` 를 계속 돌린다 |
| 클릭 → 콜백에 `(x, y)` 전달 | 프레임 수신 → 콜백에 `Button` / `Joystick` 객체 전달 |

콜백은 이벤트 루프가 돌고 있을 때만 불린다. `Drone(False)` 로 열면
`check()` 를 아무도 돌리지 않으므로 핸들러를 걸어도 영영 호출되지 않는다.
**버튼·조이스틱 실습은 반드시 `Drone()`.**

### 버튼 — `DataType.Button` (0x70)

`button.button` 은 enum 이 아니라 **비트마스크(정수)** 다. 동시에 누르면 OR 로 합쳐지므로
`bin(button.button)[2:].zfill(16)` 으로 16비트를 그대로 찍어 보는 게 이해가 빠르다.

| 값 | 이름 | | 값 | 이름 |
|---|---|---|---|---|
| `0x0001` | FrontLeftTop | | `0x0040` | MidUp |
| `0x0002` | FrontLeftBottom | | `0x0080` | MidLeft |
| `0x0004` | FrontRightTop | | `0x0100` | MidRight |
| `0x0008` | FrontRightBottom | | `0x0200` | MidDown |
| `0x0010` | TopLeft | | `0x0400` | BottomLeft |
| `0x0020` | TopRight (POWER) | | `0x0800` | BottomRight |

`button.event` 는 `Down`(누름) / `Press`(누르는 중, **반복**) / `Up`(뗌) / `EndContinuePress`.
버튼을 누르고 있으면 `Press` 가 계속 들어오므로,
"한 번 눌렀을 때 한 번만" 반응하려면 **`ButtonEvent.Down` 만 골라야 한다.**

### 조이스틱 — `DataType.Joystick` (0x71)

```
joystick.left.x / .y        -100 ~ +100
joystick.left.direction     JoystickDirection
joystick.left.event         JoystickEvent (In / Stay / Out)
```

`JoystickDirection` 은 3x3 격자다. **가운데는 `CENTER` 가 아니라 `CN`.**

```
TL  TM  TR        TM = 위     BM = 아래
ML  CN  MR        ML = 왼쪽   MR = 오른쪽
BL  BM  BR        None_ = 정의하지 않은 영역(무시)
```

**출력 폭주 주의.** 조종기가 연결돼 있으면 조이스틱 프레임이 초당 수백 개 들어온다.
같은 영역에 머무는 동안 `Stay` 가 계속 오므로 그대로 찍으면 같은 줄이 폭포처럼 쏟아진다.
영역에 새로 들어간 순간인 **`JoystickEvent.In` 만** 출력하면 "움직인 방향" 이 한 줄씩 깔끔하게 찍힌다
(`09_joystick_direction.py`). 값 변화만 찍는 방법도 있다 (`08_joystick_event.py`).

콜백 안에서 무거운 처리를 하면 수신이 밀린다. 콜백은 짧게 유지한다.

### turtle 을 콜백에서 직접 그리지 말 것

드론 콜백은 **백그라운드 수신 스레드**에서 불리는데 turtle(tkinter) 은 스레드 안전하지 않다.
콜백에서 바로 `forward()` 를 부르면 되는 것처럼 보이다가 창이 멈추거나 이상하게 그려진다.
콜백은 `queue.Queue` 에 넣기만 하고, 실제 그리기는 `turtle.ontimer` 로
메인 스레드에서 꺼내 처리한다 (`07_button_turtle.py`).

주피터는 셀이 끝나도 커널이 살아 있어 `mainloop()` 없이도 되는 것처럼 보이지만,
`.py` 로 돌리면 핸들러만 걸고 프로세스가 바로 끝나 버린다. 스크립트에는 대기 루프나 `mainloop()` 가 필요하다.

## 삽질 기록

| 증상 | 원인 | 해결 |
|---|---|---|
| `externally-managed-environment` | Homebrew Python 의 PEP 668 보호 | venv 안에서 설치 |
| `device reports readiness to read but returned no data (multiple access on port?)` | 앞 셀에서 만든 Drone 객체가 포트를 물고 있는 상태에서 또 열었음 | 커널 재시작, 변수명 통일, `try/finally` 로 확실히 close |
| 계속 `Time Over` (1) | ping 은 `dron` 으로 보내고 확인은 `drone.check()` — 이미 닫힌 다른 객체를 보고 있었음 | 변수명 하나로 통일 |
| 계속 `Time Over` (2) | `sleep(0.01)` 때문에 조이스틱 프레임에 Ack 이 묻힘 | 루프에서 sleep 제거 |
| 이벤트 핸들러가 호출 안 됨 | `Drone(False)` 라 `check()` 가 안 돌아감 | `Drone()` 으로 생성 |
| `NameError: name 'crc16' is not defined` | `ack,crc16` 오타 | `ack.crc16` |
| `[Errno 6] Device not configured` | 수신 스레드가 read 중일 때 close | 무해. close 직전 `sleep(0.1)` |
| `dron.close` 해도 포트가 안 닫힘 | 괄호 누락 — 메서드 객체만 꺼냄 | `dron.close()` |
| `AttributeError: sandPing` | `sendPing` 오타 | 오타 수정 |
| 오타 하나로 포트가 물린 채 남음 | 예외가 나면서 `drone.close()` 까지 도달하지 못함 | `try/finally` 로 close 보장. 이미 물렸으면 **커널 재시작** (셀 재실행으로는 안 풀림), 필요하면 `lsof \| grep usbmodem` 으로 점유 프로세스 확인 후 종료 |
| 콜백 안의 예외가 `try/except` 에 안 잡힘 | 백그라운드 수신 스레드(`_receiving`)에서 불리므로 메인 스레드 예외 처리와 무관 | 콜백 내부에서 직접 처리. "아무 반응이 없다" 면 콜백 안 예외를 먼저 의심 |
| turtle 이 클릭해도 안 그려짐 | `penup()` 을 `penpu()` 로 오타 — 콜백 안에서 조용히 터짐 | 위와 같음 |
| 버튼 한 번 눌렀는데 도형이 여러 개 | `Press` 이벤트가 누르는 동안 반복 수신 | `ButtonEvent.Down` 만 처리 |
| 조이스틱 출력이 폭포처럼 쏟아짐 | `Stay` 이벤트가 초당 수백 번 | `JoystickEvent.In` 만 출력하거나 값 변화 시에만 출력 |

## 주요 상수

`04_api_explorer.py` 로 전체를 뽑을 수 있다. 실습에 쓰는 것만 추리면,

- **`FlightEvent`** — `TakeOff` `Landing` `Stop` `FlipFront/Rear/Left/Right` `ResetHeading`
- **`ModeControlFlight`** — 보통 `Attitude`(자세 제어). `Position` 은 위치 센서 필요
- **`DataType`** — `State`(0x40) 배터리·비행상태, `Attitude`(0x41) 기울기,
  `Altitude`(0x43) 고도, `Range`(0x45) 거리센서
- **`DeviceType`** — `Drone`(0x10) `Controller`(0x20) `Base`(0x70)

각 enum 의 `None_` 과 `EndOfType` 은 실제 명령이 아니라 경계값이므로 무시한다.

## 비행 실습 시 주의

노트북은 셀 실행을 중단해도 드론이 마지막 명령을 계속 유지한다.
비상 정지 셀을 미리 만들어 두고 실행 대기 상태로 둘 것.

```python
dron.sendStop()
```

넓은 실내 공간, 프로펠러 가드 장착은 기본.
