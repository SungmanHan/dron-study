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
| `14_display_shape.py` | 조종기 LCD — 지우기 / 반전 / 점 · 선 · 사각형 · 원 |
| `15_display_string.py` | 조종기 LCD — 문자열 / 정렬 문자열 |
| `16_display_random_initials.py` | [과제] 이니셜 + 원을 랜덤 위치로 10회 출력 |
| `17_light_manual.py` | LED 수동 제어 — `sendLightManual` (조종기 / 드론) |
| `18_light_mode.py` | LED 모드 제어 — `sendLightMode*` / `sendLightEvent*` |
| `19_light_random_dimming.py` | 랜덤 색 디밍 — RGB / `Colors` 팔레트 / 드론 |
| `20_drone_light_random_dimming_20.py` | [과제] 드론 LED 랜덤 디밍 20회 + 실행 로그 |
| `21_sensor_altitude.py` | 센서 읽기 — 고도 `Altitude` |
| `22_sensor_motion_attitude.py` | 센서 읽기 — 모션 `Motion` / 자세 `Attitude` |
| `23_sensor_bottom_landing.py` | 센서로 제어 — 하방 거리로 자동 착륙 ⚠️이륙 |
| `24_sensor_front_landing.py` | 센서로 제어 — 전방 거리로 자동 착륙 ⚠️이륙 |
| `25_sensor_gui.py` | [과제] 하방/전방 센서값 Tkinter 실시간 출력 |
| `26_keyboard_input.py` | 키보드 입력 — `keyboard` 모듈 네 가지 방식 |
| `27_keyboard_takeoff_landing.py` | 키보드로 이륙 / 착륙 / 비상 정지 ⚠️이륙 |
| `28_keyboard_move.py` | 키보드로 전후좌우·상하·회전 이동 ⚠️이륙 |
| `29_keyboard_drone_gui.py` | [과제] 키보드 조종 + 상태·조종값 GUI ⚠️이륙 |

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

## 조종기 LCD — Display

조종기에는 **128 x 64 흑백 LCD** 가 있다. 좌표는 `x 0~127`, `y 0~63` 이고 **원점은 좌상단**.
부저·진동과 마찬가지로 목적지가 조종기라 드론 본체 없이 실습할 수 있다.

```python
dron.sendDisplayClearAll(pixel)                          # 전체를 pixel 색으로 채움
dron.sendDisplayClear(x, y, w, h, pixel)                 # 일부만
dron.sendDisplayInvert(x, y, w, h)                       # 일부 반전
dron.sendDisplayDrawPoint(x, y, pixel)
dron.sendDisplayDrawLine(x1, y1, x2, y2, pixel, line)
dron.sendDisplayDrawRect(x, y, w, h, pixel, fill, line)
dron.sendDisplayDrawCircle(x, y, radius, pixel, fill)
dron.sendDisplayDrawString(x, y, message, font, pixel)
dron.sendDisplayDrawStringAlign(x_start, x_end, y, message, align, font, pixel)
```

**"Clear" 는 지운다기보다 그 영역을 지정한 색으로 칠한다.**
`ClearAll(Black)` 뒤에 `Clear(..., White)` 를 하면 그 자리가 흰 사각형이 된다.

| enum | 값 |
|---|---|
| `DisplayPixel` | `Black`(0) `White`(1) `Inverse`(2) `Outline`(3) — **4개다** |
| `DisplayLine` | `Solid`(0) `Dotted`(1) `Dashed`(2) |
| `DisplayFont` | `LiberationMono5x8`(0) `LiberationMono10x16`(1) |
| `DisplayAlign` | `Left`(0) `Center`(1) `Right`(2) |

인자 타입을 틀리면 **조용히 무시된다.** `pixel` / `line` / `font` / `align` 은 enum 이어야 한다.
`sendDisplayDrawPoint(64, 32, 1)` 은 아무 일도 일어나지 않고, 에러도 안 난다 → `DisplayPixel(1)`.

### 문자열 — 래퍼가 이미 있다

수업에서는 `Header` + `DisplayDrawString` 을 직접 만들고
`header.length = getSize() + len(message)` 로 다시 계산한 뒤 `transfer()` 로 보냈는데,
**`sendDisplayDrawString()` / `sendDisplayDrawStringAlign()` 래퍼의 본문이 바로 그 코드다.**
길이 재계산도 래퍼가 해 준다 (진동의 `sendVibrator` 와 같은 상황).

문자열 프레임만 길이를 다시 계산하는 이유는, 다른 데이터는 크기가 고정이지만
문자열은 뒤에 `message` 가 그대로 붙는 **가변 길이 프레임**이기 때문이다.

래퍼는 **`message` 가 세 번째 인자**다. 데이터 객체의 필드 순서(x, y, font, pixel, message)와
달라서 저수준 코드를 래퍼로 옮길 때 헷갈리기 쉽다.

**⚠️ 한글은 조용히 사라진다.** `toArray()` 가 `message.encode('ascii', 'ignore')` 라
ASCII 가 아닌 글자는 에러 없이 버려진다. 게다가 `length` 는 **문자 수**로 계산되어
헤더 길이와 실제 바이트 수가 어긋난다. 실측:

```
message = "한글"  ->  header.length = 6 + 2 = 8  인데 실제 데이터는 6바이트
message = "HAN"   ->  header.length = 6 + 3 = 9,  실제 데이터도 9바이트
```

화면에 아무것도 안 나오거나 깨지는 이유가 이것이다. **영문/숫자만 쓴다.**

### 랜덤 좌표는 화면 밖으로 나간다

좌표가 좌상단 기준이라 `x`, `y` 는 글자·도형의 **왼쪽 위**다.
`randint(0, 127)` / `randint(0, 63)` 으로 뽑으면 오른쪽·아래가 잘린다.
글꼴 크기 x 글자 수만큼 여유를 빼고 뽑는다 (`16_display_random_initials.py`).
10x16 글꼴로 3글자면 `x ≤ 98`, `y ≤ 48`.

## LED — 수동 제어 vs 모드 제어

LED 함수는 두 계열이다.

| 계열 | 함수 | 목적지 지정 방법 |
|---|---|---|
| **수동** | `sendLightManual(deviceType, flags, brightness)` | `deviceType` **인자로** 지정 |
| **모드** | `sendLightModeColor` / `sendLightModeColors` / `sendLightEventColor` / `sendLightEventColors` | `lightMode` **enum 타입으로** 결정 |

깜빡임·디밍 같은 패턴은 **펌웨어가 만든다.** 모드와 색만 주면 되고,
`Dimming`(천천히 밝아졌다 어두워짐) 을 코드로 구현할 필요가 없다.
`Event` 계열은 여기에 `repeat`(반복 횟수)이 붙은 것뿐이다.

```python
dron.sendLightManual(DeviceType.Controller, LightFlagsController.BodyRed.value, 10)
dron.sendLightModeColor(LightModeController.BodyDimming, 3, 200, 0, 200)   # interval, r, g, b
dron.sendLightModeColors(LightModeDrone.BodyDimming, 3, Colors.Cyan)
dron.sendLightEventColor(LightModeDrone.BodyDimming, 3, 5, 200, 200, 200)  # interval, repeat, rgb
```

### 목적지는 `lightMode` 의 타입이 정한다

`sendLightMode*` / `sendLightEvent*` 에는 `deviceType` 인자가 **없다.**
라이브러리가 넘어온 `lightMode` 가 어느 enum 인지 보고 목적지를 정한다.

```
LightModeController.BodyDimming  ->  header.to_ = Controller
LightModeDrone.BodyDimming       ->  header.to_ = Drone
int 를 그냥 넘기면                ->  Drone
```

"드론도 조종기와 사용법이 같고 첫 인자만 바꾸면 된다" 는 말의 실제 내용이 이것이다.

### flags 값은 조종기와 드론이 다르다

```
LightFlagsController : BodyRed 0x01  BodyGreen 0x02  BodyBlue 0x04
LightFlagsDrone      : Rear    0x01  BodyRed   0x02  BodyGreen 0x04  BodyBlue 0x08  A 0x10  B 0x20
```

`flags` 는 enum 이 아니라 **int** 라서 `.value` 를 붙여야 한다. 안 붙이면 타입 검사에 걸려
조용히 무시된다. OR 로 합칠 수 있고(`BodyRed.value | BodyBlue.value`),
`0xFF` + brightness 0 이면 전부 끄기다.

모드 목록은 `LightModeController` 가 Body 계열만, `LightModeDrone` 은 `Rear` / `Body` / `A` / `B`
네 그룹에 같은 패턴(`Hold` `Flicker` `FlickerDouble` `Dimming` `Sunrise` `Sunset`)이 반복된다.
무지개(`BodyRainbow`, `BodyRainbow2`)는 양쪽 다 있다.

### 반환값은 응답이 아니라 송신 프레임

`sendLight*` 의 반환값을 찍는 예제가 나오는데, 드론이 보낸 답이 아니라
`transfer()` 가 **방금 시리얼에 써 보낸 바이트열**을 그대로 돌려준 것이다.
(포트가 닫혀 있으면 `None`, 인자 타입이 틀려도 `None`)
드론의 응답을 보려면 `03_ping_event.py` 처럼 `setEventHandler` 로 받아야 한다.

바이트열을 16진수로 찍는 `convertByteArrayToString()` 은 **라이브러리에 이미 있다**
(`CodingDrone/drone.py`). 직접 만들 필요 없이 `from CodingDrone.drone import convertByteArrayToString`.

### `Colors.EndOfType` 은 색이 아니다

```python
Colors(random.randint(0, Colors.EndOfType.value))       # EndOfType(141) 이 뽑힐 수 있다
Colors(random.randint(0, Colors.EndOfType.value - 1))   # 실제 색은 0 ~ 140
```

`randint` 는 **상한을 포함**한다. `EndOfType` 은 목록의 끝을 표시하는 경계값이다.

### 모드는 끌 때까지 유지된다

스크립트가 끝나도 드론·조종기는 마지막 패턴을 계속 유지한다.
`finally` 에서 `sendLightManual(deviceType, 0xFF, 0)` 으로 소등한다.

## 센서 — 요청하고, 응답은 핸들러로 받는다

지금까지(부저·LED·LCD)는 **보내기만** 했다. 센서는 처음으로 **받는** 쪽이다.

```python
dron.setEventHandler(DataType.Altitude, event_altitude)   # ① 등록 (1회면 충분)
dron.sendRequest(DeviceType.Drone, DataType.Altitude)     # ② 요청 (반복)
def event_altitude(altitude): ...                         # ③ 응답이 오면 자동 호출
```

`sendRequest()` 의 반환값은 센서값이 아니다. LED 때와 같이 **방금 보낸 프레임**이고,
드론의 응답은 백그라운드 수신 스레드가 받아 핸들러로 넘긴다.
그래서 `Drone()` 이어야 한다 — `Drone(False)` 면 요청은 나가지만 핸들러가 영영 안 불린다.

| DataType | 클래스 | 필드 | 형식 |
|---|---|---|---|
| `Altitude`(0x43) | Altitude | `temperature` `pressure` `altitude` `rangeHeight` | **Float32** |
| `Motion`(0x44) | Motion | `accelX/Y/Z` `gyroRoll/Pitch/Yaw` `angleRoll/Pitch/Yaw` | Int16 |
| `Attitude`(0x41) | Attitude | `roll` `pitch` `yaw` | Int16 |
| `Range`(0x45) | Range | `left` `front` `right` `rear` `top` `bottom` | Int16, **mm** |

### 헷갈리는 짝들

- **`Altitude`(고도) ≠ `Attitude`(자세)** — 철자 한 글자 차이. 강의 자료에서도 주석이 섞여 있었다.
- **`altitude` ≠ `rangeHeight`** — 같은 Altitude 안의 다른 값이다.
  `altitude` 는 기압 기반 **해발고도**라 실내에서도 수십 m 로 나오고 흔들린다.
  "바닥에서 얼마나 떠 있나" 는 하방 거리센서값인 `rangeHeight`.
- **`gyro*` ≠ `angle*`** — `gyro` 는 **각속도**(도는 동안만 튀고 멈추면 0),
  `angle` 은 **각도**(기울인 채 멈춰도 그 값을 유지). 이 차이를 눈으로 보는 게 모션 예제의 목적이다.
- **`accel*` 은 ×10 된 정수** — 수평으로 두면 `accelZ` 가 약 98(= 9.8m/s², 중력).
- **단위가 예제마다 다르다** — 하방 `rangeHeight` 는 **m**(0.3 = 30cm),
  전방 `front` 는 **mm**(200~400 = 20~40cm). 숫자 크기가 1000배 차이 나는 이유.
  같은 하방 거리를 `Range.bottom`(mm) 으로도 볼 수 있다.
- `Attitude`/`Range` 는 Int16 이라 `{:.3f}` 로 찍으면 항상 `.000`. Float32 인 `Altitude` 만 소수가 보인다.

### 핸들러에서 전역 변수를 바꾸려면 `global`

"센서값으로 판단해서 명령" 을 하려면 핸들러가 바깥 상태를 바꿔야 하는데, 여기서 걸린다.

```python
def event_altitude(altitude):
    if altitude.rangeHeight < 0.3:
        isDetected = True      # ← 대입이 있으면 파이썬은 이 이름을 지역 변수로 본다
    if isDetected:             # ← 평상시(대입이 안 된 경로)엔 여기서 터진다
        ...
# UnboundLocalError: cannot access local variable 'isDetected' ...
```

조건이 맞을 때는 대입이 먼저 일어나 **우연히 동작하므로**, "착륙은 되는데 평소엔 계속 에러가
찍히는" 상태가 된다. 전역 플래그는 끝까지 False 다. 해결은 함수 첫 줄 `global isDetected`.

### 그 밖에 정리한 것

- **핸들러 등록은 루프 밖 1회** — 강의 예제는 `while` 안에서 매번 재등록한다(무해하지만 의미 없다).
- **감지되면 `break`** — 안 그러면 착륙한 뒤에도 요청과 착륙 명령을 계속 보낸다.
- **`Ctrl+C` 에도 착륙** — 강의 화면 버전 하나는 착륙 없이 "측정 종료" 만 찍고 **호버링을 계속**한다.
- **`close()`** — 강의 예제에 없어서 다음 실행 때 포트가 물린다.
- **핸들러 매개변수 이름 `range`** — 내장 함수 `range()` 를 가린다. `range_data` 로.
- **`open()` 은 실패해도 예외를 던지지 않고 `False` 를 반환한다.** GUI 처럼 창만 먼저 뜨는 구조에서는
  "측정 중..." 만 계속 찍히고 값이 안 들어오는 상태가 된다 → 반환값을 확인할 것.

## 비행 명령 — 키보드로 조종

센서(21~25)까지는 드론이 **가만히 있었다.** 여기서부터 실제로 난다.

### 명령은 네 개뿐이다

| 함수 | 내부 | 동작 |
|---|---|---|
| `sendTakeOff()` | `CommandType.FlightEvent` + `FlightEvent.TakeOff` | 이륙 |
| `sendLanding()` | `CommandType.FlightEvent` + `FlightEvent.Landing` | 착륙 (천천히 내려온다) |
| `sendStop()` | `CommandType.Stop` | **모터 즉시 정지** — 공중이면 추락 |
| `sendControl(roll, pitch, yaw, throttle)` | `DataType.Control` | 4축 이동, 1회 전송 |

`sendStop` 만 FlightEvent 가 아니라 별도 커맨드다. "비상 = Stop" 으로 외우면 위험하다 —
공중에서 필요한 건 보통 `sendLanding()` 쪽이다.
`sendFlightEvent(FlightEvent.X)` 를 쓰면 `FlipFront/Rear/Left/Right`, `Return`, `ResetHeading`
같은 나머지 이벤트도 보낼 수 있다.

### 축과 부호

| 축 | − | + |
|---|---|---|
| `roll` | 좌이동 | 우이동 |
| `pitch` | 후진 | 전진 |
| `yaw` | 좌회전 | 우회전 |
| `throttle` | 하강 | 상승 |

**+ 방향 = 우 / 전진 / 우회전 / 상승.** 범위는 -100 ~ 100.

### 네 값은 반드시 int

```python
dron.sendControl(0, 0, 0, POWER / 3)   # float → 조용히 무시된다
```

`isinstance(int)` 검사에 걸려 **예외 없이 `None` 을 반환**하고 끝난다(부저·LED 와 같은 함정).
나눗셈 `/` 는 항상 float 이므로 `int()` 로 감쌀 것.
반대로 범위를 벗어난 값은 조용하지 않다 — 내부가 `pack('<bbbb')` 라
`struct.error: 'b' format requires -128 <= number <= 127` 로 터진다.

### `sendControl` 은 1회, `sendControlWhile` 은 블로킹

```python
dron.sendControlWhile(0, 0, 0, 0, 4000)   # 4초간 제자리
```

라이브러리 내부는 그냥 `while` 루프다 — 4초 동안 `sendControl` 을 20ms 간격(초당 50회)으로
반복 전송한다. **그동안 함수에서 못 빠져나온다.** 이륙 직후 자세를 잡는 데는 맞지만,
이 4초 안에 누른 키는 전부 무시되고 GUI 라면 창까지 같이 멈춘다.
그래서 29 에서는 이 함수를 쓰지 않고 "이륙 후 4초 동안 매 주기 `(0,0,0,0)` 을 보내는 상태" 로 바꿨다.

### 키를 떼면 0 을 보내야 한다

드론은 **마지막으로 받은 명령을 계속 유지한다.** 파이썬이 죽어도, 셀을 멈춰도 그대로 난다.

```python
else:
    dron.sendControl(0, 0, 0, 0)   # 이 한 줄이 "누르는 동안만 이동" 을 만든다
```

같은 이유로 조종 루프는 `try/finally` 로 감싸고 `finally` 에서 `sendLanding()` → `close()` 를 한다.

### 키 입력 세 가지 방식

| 방식 | 함수 | 블로킹 | 드론 조종에서 |
|---|---|---|---|
| 폴링 | `is_pressed("w")` | X | **기본.** 루프에서 여러 키를 동시에 확인 |
| 대기 | `read_key()` | O | 키 이름 확인용. 루프가 멈춰서 조종에는 못 쓴다 |
| 이벤트 | `on_press` / `on_release` | X | 누를 때 시작 / 뗄 때 정지, 이륙·착륙 같은 단발 명령 |

`read_key()` 는 누를 때와 뗄 때 각각 이벤트가 생겨 **한 번 눌러도 두 번** 반환된다.
`on_press` 의 콜백이 받는 건 문자열이 아니라 `KeyboardEvent` 객체다 (`event.name` / `event.event_type`).

### macOS 에서 `keyboard` 는 sudo 가 필요하다

이 모듈은 터미널이 포커스가 아니어도 키를 읽는다 = **전역 키 후킹**이라 권한이 필요하다.

```bash
pip install keyboard
sudo .venv/bin/python 28_keyboard_move.py
```

`sudo python` 이 아니라 **venv 안의 파이썬을 경로로 직접** 지정해야 한다. `sudo` 가 환경변수를
갈아엎어 venv 활성화가 풀리고, 시스템 파이썬에는 keyboard 가 없어 `ModuleNotFoundError` 가 난다.
시스템 설정 → 개인정보 보호 및 보안 → **입력 모니터링** 에 터미널 허용도 필요하다.

과제(29)가 Tkinter 키 이벤트(`<KeyPress>` / `<KeyRelease>`)를 기본으로 쓰는 이유가 이것이다.
창이 포커스인 동안의 키만 받으면 충분하고, 그건 전역 후킹이 아니라 권한이 필요 없다.
대신 **창이 포커스를 잃으면 `KeyRelease` 를 못 받아** 키가 눌린 채로 남는다 →
`<FocusOut>` 에서 눌린 키 집합을 비워야 한다.

### GUI 조종 — `while True` 를 버린다

Tkinter 는 `mainloop()` 이 돌아야 화면이 갱신된다. 28 처럼 무한 루프를 돌리면 창이 얼어붙는다.

```python
def tick(self):
    now_keys = self.keys.get_pressed()
    new_keys = now_keys - self.prev_keys   # 이번 주기에 새로 눌린 키만
    self.prev_keys = now_keys
    ...
    self.root.after(TICK_MS, self.tick)    # 20ms 뒤 다시
```

- **단발 명령은 `new_keys` 로** — 이륙·착륙·비상정지를 매 주기 보내면 20ms 마다 명령이 쏟아진다.
- **20ms 는 임의의 수가 아니다** — 라이브러리의 `sendControlWhile` 이 쓰는 간격과 같다(초당 50회).
- **동시 입력** — `elif` 체인(28) 은 키 하나만 처리해서 대각선이 안 된다.
  축별로 값을 모아 `sendControl` 을 **한 번** 호출하면 `↑`+`→` 가 같이 나간다.

### 멈추는 방법은 세 단계다

1. **비상 키** — `space` 를 **가장 먼저** 검사한다. `if/elif` 체인은 위에서 처음 걸린 것만
   처리하므로, 비상 키가 아래에 있으면 다른 키가 눌린 동안 영영 검사되지 않는다.
2. **조종기 모드 전환** — 조종기 전원 버튼을 한 번 눌러 조종기로 직접 착륙시킨다.
3. **뒤집기** — 드론은 뒤집히면 모터가 꺼진다. 프로펠러 말고 몸체를 잡을 것.

호버링이 안 되고 한쪽으로 흐른다면 바닥 탓이다. 하단 옵티컬 플로우 센서가
바닥 무늬의 움직임을 보고 위치를 유지하므로, 단색·유광·어두운 바닥에서는 못 읽는다.
**무늬 있는 바닥, 넓은 곳.**

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
| LCD 에 문자열이 안 나옴 | 한글 — `encode('ascii', 'ignore')` 로 버려지고 헤더 길이까지 어긋남 | 영문/숫자만 사용 |
| 그리기 명령이 아무 반응 없음 | `pixel`/`font` 등을 int 로 넘김 — 라이브러리가 isinstance 검사 후 조용히 `None` 반환 | `DisplayPixel(1)` 처럼 enum 으로 |
| 랜덤 출력이 화면 밖으로 잘림 | 좌표가 좌상단 기준인데 0~127 / 0~63 전 범위에서 뽑음 | 글꼴 크기 x 글자 수만큼 빼고 뽑는다 |
| `import random` 없이 `random` 이 동작함 | `from CodingDrone.drone import *` 가 drone.py 의 `import random` 까지 끌고 옴 | 우연히 되는 것이므로 직접 import |
| LED 가 안 켜짐 | `flags` 에 `.value` 를 안 붙여 enum 을 넘김 — isinstance(int) 검사에 걸려 조용히 무시 | `LightFlagsController.BodyRed.value` |
| 반환값을 드론 응답으로 오해 | `transfer()` 는 **보낸 바이트열**을 돌려준다 | 응답은 `setEventHandler` 로 받는다 |
| 랜덤 색에 이상한 값이 섞임 | `randint(0, Colors.EndOfType.value)` — 상한 포함이라 경계값이 뽑힘 | `- 1` 을 해서 0~140 |
| 스크립트가 끝나도 LED 가 계속 켜져 있음 | Mode 계열은 끌 때까지 유지 | `finally` 에서 `sendLightManual(..., 0xFF, 0)` |
| `open()` 을 인자 없이 호출 | 포트 목록의 **마지막 것**을 고른다 — 드론 동글이라는 보장이 없다 | `drone_util.find_port()` |
| `UnboundLocalError: isDetected` | 핸들러에서 전역에 대입 — `global` 누락. 조건이 맞는 경로만 우연히 동작 | 함수 첫 줄에 `global` |
| 센서 핸들러가 안 불림 | `Drone(False)` — 요청은 나가지만 수신 스레드가 없다 | `Drone()` |
| 창은 뜨는데 센서값이 안 들어옴 | `open()` 이 실패해도 예외 없이 `False` 를 반환 | 반환값 확인 후 안내 |
| Tkinter 창이 멈추거나 이상하게 갱신됨 | 핸들러(수신 스레드)에서 위젯을 직접 건드림 / 메인 스레드 `sleep` | 값만 저장하고 `root.after` 로 갱신 |
| 값이 안 잡히거나 즉시 착륙 | 단위 혼동 — 하방 `rangeHeight` 는 m, 전방 `front` 는 mm | 1000배 차이를 확인 |
| `sendControl` 이 아무 반응 없음 | 네 값 중 하나가 float — `isinstance(int)` 검사 후 조용히 `None` 반환 | `int()` 로 감싼다 |
| `struct.error: 'b' format requires -128 <= number <= 127` | 세기를 100 넘게 줌 — 내부가 signed 1바이트 | -100 ~ 100 |
| 키를 뗐는데 계속 날아감 | 드론은 마지막 명령을 유지한다 | `else: sendControl(0,0,0,0)` |
| 이륙 후 4초간 키가 안 먹음 | `sendControlWhile` 이 그 시간 동안 블로킹 | 상태로 바꿔 매 주기 0 전송 |
| 키를 안 눌러도 CPU 100% | 폴링 루프에 쉼이 없음 | `sleep(0.01)` |
| Tk 창이 얼어붙음 | `while True` 로 조종 루프를 돌림 | `root.after(20, tick)` |
| 이륙 명령이 20ms 마다 반복 전송됨 | 눌린 키 전체를 매 주기 처리 | `new_keys = now_keys - prev_keys` |
| 창을 벗어났더니 드론이 계속 이동 | 포커스를 잃으면 `KeyRelease` 를 못 받아 키가 눌린 채로 남음 | `<FocusOut>` 에서 집합 비우기 |
| `sudo python` 이 `ModuleNotFoundError` | sudo 가 환경변수를 갈아엎어 venv 가 풀림 | `sudo .venv/bin/python ...` |
| 대각선 이동이 안 됨 | `elif` 체인은 키 하나만 처리 | 축별로 모아 `sendControl` 한 번 |

## 주요 상수

`04_api_explorer.py` 로 전체를 뽑을 수 있다. 실습에 쓰는 것만 추리면,

- **`FlightEvent`** — `TakeOff` `Landing` `Stop` `Reverse` `Return` `FlipFront/Rear/Left/Right` `ResetHeading`
  (`sendTakeOff`/`sendLanding` 은 이 중 둘을 감싼 래퍼다. 나머지는 `sendFlightEvent()` 로)
- **`ModeControlFlight`** — 보통 `Attitude`(자세 제어). `Position` 은 위치 센서 필요
- **`DataType`** — `State`(0x40) 배터리·비행상태, `Attitude`(0x41) 기울기,
  `Altitude`(0x43) 고도, `Motion`(0x44) 가속도·자이로·각도, `Range`(0x45) 거리센서
- **`DeviceType`** — `Drone`(0x10) `Controller`(0x20) `Base`(0x70)
- **`BuzzerMode`** — `Mute` `Scale` `Hz` + 각각의 `Reserve`, `Stop`
- **`BuzzerScale`** — `C1`~`B8`, 샵은 `CS4` 형태. `Mute`(0xEE) `Fin`(0xFF) 은 특수값
- **`VibratorMode`** — `Instantly`(즉시) `Continually`(예약) `Stop`
- **`DisplayPixel`** — `Black` `White` `Inverse` `Outline` / **`DisplayLine`** — `Solid` `Dotted` `Dashed`
- **`DisplayFont`** — `LiberationMono5x8` `LiberationMono10x16` / **`DisplayAlign`** — `Left` `Center` `Right`
- **`LightFlagsController` / `LightFlagsDrone`** — 켤 LED 비트. **값이 서로 다르다**
- **`LightModeController` / `LightModeDrone`** — `Hold` `Flicker` `FlickerDouble` `Dimming` `Sunrise` `Sunset` `Rainbow`
- **`Colors`** — 색 이름 팔레트 0~140 (`EndOfType`=141 은 경계값)

각 enum 의 `None_` 과 `EndOfType` 은 실제 명령이 아니라 경계값이므로 무시한다.

## 비행 실습 시 주의

노트북은 셀 실행을 중단해도 드론이 마지막 명령을 계속 유지한다.
비상 정지 셀을 미리 만들어 두고 실행 대기 상태로 둘 것.

```python
dron.sendStop()
```

넓은 실내 공간, 프로펠러 가드 장착은 기본.

**실제로 이륙하는 파일은 `23` `24` `27` `28` `29` 다섯 개다.**
(`21_sensor_altitude.py` 는 `TAKEOFF = True` 로 바꿨을 때만.) 나머지는 전부 책상 위에서 돌아간다.
`23`/`24` 는 이륙 전 3초 카운트다운을 찍고, `27`~`29` 는 `1` 키를 눌러야 뜬다.
다섯 개 모두 `Ctrl+C` 나 창 닫기로 중단해도 착륙 명령이 나간다.
`29` 는 `SIMULATION = True` 로 두면 드론 없이 화면·키 동작만 확인할 수 있다.
손은 프로펠러에 닿지 않게 **아래쪽 / 정면에서 천천히** 넣을 것.
