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
| `10_buzzer.py` | 부저 — `sendBuzzerScale` / `sendBuzzerHz` / Reserve |
| `11_buzzer_song.py` | 부저로 "학교종이 땡땡땡" 연주 |
| `12_vibrator.py` | 진동 — `sendVibrator` 와 저수준 `transfer` |
| `13_button_melody.py` | [과제] 버튼으로 "비행기" 연주 + 진동 |

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

## 부저 / 진동 — 소리는 조종기가 낸다

부저도 진동도 **조종기**가 낸다. 프레임의 목적지가 `DeviceType.Controller`(0x20) 다.
드론 본체는 관여하지 않으므로 프로펠러 없이도 실습할 수 있다.

### 부저

```python
dron.sendBuzzerScale(BuzzerScale.C4, 400)   # 음계로 (실습에서 가장 많이 쓴다)
dron.sendBuzzerHz(440, 500)                 # 주파수로
dron.sendBuzzerMute(10)                     # 묵음
dron.sendBuzzer(BuzzerMode.Scale, BuzzerScale.A4.value, 500)  # 저수준
```

`BuzzerMode` 는 `Mute` / `Scale` / `Hz` 와 각각의 `Reserve`(예약) 버전, 그리고 `Stop`.
**Reserve 계열은 바로 전에 호출한 소리가 끝난 뒤 이어서 재생되도록 예약**한다.
그래서 `sendBuzzerScale` + `sendBuzzerScaleReserve` 로 두 음을 sleep 없이 붙일 수 있다.

`BuzzerScale` 은 `C1`~`B8` 이고 샵은 `CS4` 처럼 `S` 를 붙인다.
실습에 쓰는 4옥타브대는 **도 `C4` / 레 `D4` / 미 `E4` / 파 `F4` / 솔 `G4` / 라 `A4` / 시 `B4`**.
`Mute`(0xEE) `Fin`(0xFF) `EndOfType` 은 음이 아니라 특수값이다.

**⚠️ `time` 이 `int` 가 아니면 조용히 무시된다.**
`sendBuzzerScale()` 은 내부에서 `isinstance(time, int)` 를 검사하고, 아니면
아무것도 보내지 않고 `None` 을 반환한다. **예외가 나지 않는다.**
파이썬의 `/` 는 항상 float 이라 박자를 계산해 넣을 때 자주 밟는다.
"소리가 안 나는데 에러도 없다" 면 `time` 부터 본다. → `int()` 로 감쌀 것.

**시간이 두 개다.** `sendBuzzerScale(scale, time)` 의 `time` 은 조종기가 소리를 내는 길이이고,
이 함수는 명령만 보내고 바로 반환한다. 파이썬 쪽에서 `sleep` 을 하지 않으면
다음 음 명령이 곧바로 날아가 앞 음을 덮어쓴다. 둘을 같이 맞춰야 한다.
음 사이를 조금(여기서는 60ms) 띄우지 않으면 "미미미" 가 늘어진 "미—" 하나로 들린다.

### 진동

```python
dron.sendVibrator(on, off, total)         # on: 진동 ms, off: 쉼 ms, total: 전체 ms
dron.sendVibratorReserve(on, off, total)  # mode = Continually (예약)
```

`on=100, off=200, total=900` 이면 "부웅 (쉼) 부웅 (쉼) 부웅" 3회.

수업에서는 `Header` + `Vibrator` 를 직접 만들어 `dron.transfer(header, data)` 로 보냈는데,
**CodingDrone 1.0.4 에는 부저와 마찬가지로 `sendVibrator()` 래퍼가 있다.**
라이브러리 소스를 열어 보면 래퍼 본문이 그 저수준 코드와 같다.
직접 조립하는 건 `mode` 를 손대야 할 때만 필요하다 (`12_vibrator.py` 에 둘 다 남겨 뒀다).

저수준으로 보낼 때 `header.from_` 은 **`DeviceType.Base`(0x70 = 내 PC)** 로 맞춘다.
`Tester`(0xA0) 도 존재하고 동작도 하지만, 라이브러리 래퍼는 전부 `Base` 를 쓴다.

### 콜백에서 멜로디를 재생하지 말 것

버튼 콜백은 백그라운드 수신 스레드에서 불린다. 그 안에서 멜로디를 끝까지 재생하면
수 초 동안 수신 스레드가 `sleep` 에 붙잡혀, 그 사이 들어온 버튼·조이스틱 프레임이 전부 밀린다.
콜백은 큐에 요청만 넣고 재생은 메인 루프에서 한다 — turtle 을 메인 스레드로 옮긴 것과 같은 해법.
진동은 프레임 한 개로 끝나므로 콜백에서 바로 보내도 된다.

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
| 부저가 소리를 안 내는데 에러도 없음 | `time` 인자가 float — 라이브러리가 `isinstance(int)` 검사 후 조용히 `None` 반환 | `int()` 로 감싼다 |
| 음이 이어져 한 음처럼 들림 | 같은 음을 틈 없이 연속 전송 | 음 사이 60ms 정도 띄운다 |
| 앞 음이 끊기고 다음 음이 나옴 | 명령 시간(ms)만 주고 파이썬은 안 쉼 | `sleep` 으로 같이 맞춘다 |
| 연주 중 누른 버튼이 늦게 처리됨 | 콜백 안에서 멜로디를 끝까지 재생 → 수신 스레드 블로킹 | 콜백은 큐에 넣고 메인 루프에서 재생 |
| `transfer(hasattr, data)` | `header` 오타. `hasattr` 은 내장 함수라 `NameError` 조차 안 난다 | `transfer(header, data)` |

## 주요 상수

`04_api_explorer.py` 로 전체를 뽑을 수 있다. 실습에 쓰는 것만 추리면,

- **`FlightEvent`** — `TakeOff` `Landing` `Stop` `FlipFront/Rear/Left/Right` `ResetHeading`
- **`ModeControlFlight`** — 보통 `Attitude`(자세 제어). `Position` 은 위치 센서 필요
- **`DataType`** — `State`(0x40) 배터리·비행상태, `Attitude`(0x41) 기울기,
  `Altitude`(0x43) 고도, `Range`(0x45) 거리센서
- **`DeviceType`** — `Drone`(0x10) `Controller`(0x20) `Base`(0x70)
- **`BuzzerMode`** — `Mute` `Scale` `Hz` + 각각의 `Reserve`, `Stop`
- **`BuzzerScale`** — `C1`~`B8`, 샵은 `CS4` 형태. `Mute`(0xEE) `Fin`(0xFF) 은 특수값
- **`VibratorMode`** — `Instantly`(즉시) `Continually`(예약) `Stop`

각 enum 의 `None_` 과 `EndOfType` 은 실제 명령이 아니라 경계값이므로 무시한다.

## 비행 실습 시 주의

노트북은 셀 실행을 중단해도 드론이 마지막 명령을 계속 유지한다.
비상 정지 셀을 미리 만들어 두고 실행 대기 상태로 둘 것.

```python
dron.sendStop()
```

넓은 실내 공간, 프로펠러 가드 장착은 기본.
