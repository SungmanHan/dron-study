# 코딩드론 학습 기록

CodingDrone(파이썬) 으로 드론 제어를 실습하면서 정리한 내용.
환경은 macOS 12 (Intel) / Homebrew Python 3.14 / CodingDrone 1.0.4.

## 파일

| 파일 | 내용 |
|---|---|
| `drone_util.py` | 동글 포트 자동 탐색(`find_port` / 군집용 `find_ports`) + 명령 완료 대기(`countdown`) |
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
| `30_flight_takeoff_hover_landing.py` | 자율 비행 기본형 — 이륙 / 호버링 / 착륙 ⚠️이륙 |
| `31_flight_stop.py` | `sendLanding` vs `sendStop` — 하강 후 정지 ⚠️이륙 |
| `32_position_move.py` | 거리 이동 — `sendControlPosition` / `16` ("ㄱ"자) ⚠️이륙 |
| `33_position_return_home.py` | 리턴홈 — `sendFlightEvent(FlightEvent.Return)` ⚠️이륙 |
| `34_pattern_square.py` | 패턴 비행 — 정사각형 (방향 이동 / heading 회전) ⚠️이륙 |
| `35_mission_goal_circle.py` | [미션1·2·3] 상승·전진·옆 이동으로 목적지 원 착륙 ⚠️이륙 |
| `36_mission_obstacle_stop.py` | [미션4·5] 전방 센서 감지 → 착륙 / 회피 후 착륙 ⚠️이륙 |
| `37_mission_land_on_target.py` | [미션6] 하방 센서로 높은 목적지 감지 → 그 위에 착륙 ⚠️이륙 |
| `38_assignment_route_obstacle.py` | [과제] 버튼 출발 + 경로 비행 + 장애물 회피 + LED ⚠️이륙 |
| `39_opencv_check.py` | OpenCV 설치 확인 — 버전 / 중복 설치 / GUI 백엔드 |
| `40_opencv_image_read.py` | OpenCV 이미지 읽기 — `imread` / `imshow` (+ matplotlib) |
| `41_opencv_gray.py` | 흑백처리 — `imread(경로, 0)` vs `cvtColor(BGR2GRAY)` |
| `42_opencv_template_match.py` | 템플릿 매칭 — 여러 사진 중 원하는 것 찾기 |
| `43_opencv_hsv.py` | HSV 색공간 — 색을 H 하나로 고르기 (숫자만) |
| `44_assignment_color_extract.py` | [과제] 색상표에서 특정 색 추출 — `inRange` + `bitwise_and` |
| `45_video_source.py` | 영상 입력 — `VideoCapture` (카메라 / 동영상 / 합성 영상) 📷 |
| `46_draw_shapes_text.py` | 도형·텍스트 그리기 — 선 · 원 · 사각형 · 글꼴 5종 |
| `47_video_record.py` | 영상 저장 — `VideoWriter` 와 조용히 실패하는 세 자리 |
| `48_face_detect.py` | 얼굴 인식 — Haar Cascade (`CascadeClassifier`) 📷 |
| `49_assignment_face_eye_lip.py` | [과제] 얼굴·눈·입 인식 + 이름표 + `r` 녹화 📷 |
| `50_color_tracker.py` | 색으로 물체 추적 — 마스크 → 윤곽선 → 중심 좌표 📷 |
| `51_color_drone_control.py` | 색으로 드론 제어 — 이착륙 / 상하좌우 ⚠️이륙 📷 |
| `52_assignment_color_drone.py` | [과제] 색 추적으로 드론 상하좌우 + 녹화 ⚠️이륙 📷 |
| `53_swarm_two_drones.py` | 군집비행 — 2대 이륙·앞뒤·LED·좌우·착륙 ⚠️이륙 |
| `54_swarm_four_drones.py` | 군집비행 — 4대 높이 교차 ⚠️이륙 |
| `55_swarm_patterns.py` | 군집 패턴 — 순차 이륙 · 웨이브 · 확장/축소 · 사각 회전 ⚠️이륙 |
| `56_feature_fragility.py` | 수동 특징이 언제 무너지는가 — 조명·각도·크기 실측 |
| `57_conv_filter_basics.py` | 합성곱 — 커널 · 특징맵 · 풀링 · 파라미터 수 |
| `58_detection_postprocess.py` | 탐지 결과 정리 — 신뢰도 · IoU · NMS (`cv.dnn.NMSBoxes`) |
| `59_pygame_window.py` | Pygame 기본 창 — 렌더링 루프 · 더블 버퍼링 |
| `60_pygame_camera.py` | 카메라 영상을 Pygame 창에 + 덧그리기(AR) 📷 |
| `61_assignment_hello_drone.py` | [과제] 영상 위에 "Hello Drone" 띄우기 📷 |
| `62_image_to_pygame.py` | 사진을 비율 유지해 Pygame 창에 (레터박스) |
| `63_yolo_check.py` | YOLO 준비 확인 — 설치·모델 파일·라인업·결과 구조 |
| `64_yolo_image_inference.py` | 이미지 추론 — 박스·라벨을 화면에 얹기 (설치 없이도 확인) |
| `65_yolo_camera_realtime.py` | 실시간 추론 — 매 프레임 탐지 + FPS 표시 📷 |
| `66_assignment_person_blind.py` | [과제] 사람만 찾아 가리기 (채우기 / 반투명 / 모자이크) 📷 |
| `67_tracker_basics.py` | 추적의 원리를 손으로 — IoU 매칭·ID 발급·소멸 (숫자만) |
| `68_object_tracking_camera.py` | 사물 추적 — ID + 궤적 (`model.track`) 📷 |

⚠️이륙 = 드론이 실제로 뜬다 / 📷 = 카메라를 쓴다(`45` 는 `SOURCE = "demo"` 로 카메라 없이도 돌아간다)

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

## 자율 비행 — 거리와 패턴

27~29 는 **사람이 키를 누르는 만큼** 움직였다. 30~34 는 명령을 코드에 순서대로 적어 두고
손을 뗀다. 사람이 개입하지 않으니, 명령이 끝날 때까지 기다리는 일을 코드가 대신해야 한다.

### 기다리는 방식이 명령마다 다르다

| 함수 | 대기 | 비고 |
|---|---|---|
| `sendTakeOff()` / `sendLanding()` | 비블로킹 → 약 5초 | 보내고 바로 리턴한다 |
| `sendStop()` | — | 모터 즉시 정지 |
| `sendControlWhile(r, p, y, t, ms)` | **블로킹** | 내부가 `while` — 그 ms 동안 못 빠져나온다 |
| `sendControlPosition(...)` / `16` | 비블로킹 → 이동 시간만큼 | 안 기다리면 다음 명령이 덮어쓴다 |
| `sendFlightEvent(FlightEvent.Return)` | 비블로킹 → 복귀 시간만큼 | |

    이동 대기 = 거리 ÷ 속도 + 여유 2~3초       1 m ÷ 0.5 m/s = 2초
    회전 대기 = 회전각 ÷ 회전속도 + 여유        90° ÷ 45°/s   = 2초

블로킹인 건 `sendControlWhile` 하나뿐이다. 강의 코드가 이 함수 뒤에 붙이는 `sleep(0.01)` 은
없어도 그만이라 뺐다. 반대로 위치 명령 뒤의 대기는 **빠뜨리면 동작이 깨진다.**

### 위치 명령 — "얼마나 갈지" 를 직접 쓴다

```python
sendControlPosition(positionX, positionY, positionZ, velocity, heading, rotationalVelocity)
```

| 인자 | 단위 | 범위(펌웨어) | 부호 |
|---|---|---|---|
| `positionX` | m | -10.0 ~ 10.0 | 앞 **+** / 뒤 **−** |
| `positionY` | m | -10.0 ~ 10.0 | 좌 **+** / 우 **−** |
| `positionZ` | m | -10.0 ~ 10.0 | 위 **+** / 아래 **−** |
| `velocity` | m/s | 0.5 ~ 2.0 | |
| `heading` | ° | -360 ~ 360 | 좌회전 **+** / 우회전 **−** |
| `rotationalVelocity` | °/s | 10 ~ 360 | |

**오른쪽과 우회전이 음수다.** 가장 많이 틀리는 부분이고, 틀려도 에러가 안 나서 그냥 반대로 간다.

`sendControlPosition16` 은 같은 명령을 **×10 한 정수**로 보낸다 — `1 m = 10`, `0.5 m/s = 5`.
20바이트(`<ffffhh`) 와 12바이트(`<hhhhhh`) 로 길이만 다르고 둘 다 `DataType.Control` 이다.
(슬라이드의 "거리 100 이 1미터" 는 오탈자다. 실습 코드의 `sendControlPosition16(10, …)` = 1 m 가 맞다.)

### int 규칙이 한 호출 안에서 갈린다

| 함수 | float 허용 | int 전용 |
|---|---|---|
| `sendControl` | 없음 | 네 값 전부 |
| `sendControlPosition` | `x` `y` `z` `velocity` | **`heading` `rotationalVelocity`** |
| `sendControlPosition16` | 없음 | **여섯 개 전부** |

```python
dron.sendControlPosition(1.0, 0, 0, 0.5, -90.0, 45)   # heading 이 float → 조용히 무시
dron.sendControlPosition16(10, 0, 0, 0.5, 0, 0)       # velocity 가 float → 조용히 무시
```

부저·LED·`sendControl` 과 같은 함정이다. `isinstance` 검사에 걸리면 **예외 없이 `None` 을
반환하고 끝난다.** 드론은 가만히 있고 에러도 없으니 "명령이 안 먹네" 로만 보인다.

### 범위를 넘겨도 에러가 안 난다

`sendControl` 은 내부가 `pack('<bbbb')` 라 100 을 넘기면 `struct.error` 로 **터져서** 알려줬다.
위치 명령은 int16(±32767) / float 이라 웬만한 값이 다 통과하고, 라이브러리에 범위 검사도 없다.
위 표의 "-10.0 ~ 10.0" 은 펌웨어 쪽 제한이지 파이썬이 막아 주는 값이 아니다.

> **단위를 잘못 쓰면 에러 대신 드론이 날아간다.** 위치 명령에서만큼은 "에러가 안 났으니
> 맞게 보냈다" 가 성립하지 않는다. 값을 바꿀 때는 낮은 값부터 올려 가며 확인할 것.

### 리턴홈 — `sendFlightEvent`

```python
from CodingDrone.protocol import FlightEvent
dron.sendFlightEvent(FlightEvent.Return)   # 이륙 지점으로 복귀
```

사실 계속 쓰고 있던 함수다 — `sendTakeOff()` / `sendLanding()` 이 `FlightEvent.TakeOff`(0x11) /
`Landing`(0x12) 을 감싼 래퍼이고, 래퍼가 없는 `Return`(0x18) · `Reverse` · `Flip*` · `ResetHeading`
은 이 함수로 직접 보낸다. 인자는 **반드시 `FlightEvent` enum** 이다 — `0x18` 처럼 int 를 넣으면
`isinstance` 검사에 걸려 조용히 무시된다.

돌아오는 위치는 드론이 **스스로 추정한** 값이다. 하방 옵티컬 플로우가 바닥 무늬로 이동량을
누적하므로 단색·유광 바닥에서는 수십 cm 어긋난다.

### 패턴 비행 두 가지

| | 방향 이동 (34 MODE 1) | heading 회전 (34 MODE 2) |
|---|---|---|
| 명령 | 전진·우·후진·좌 4가지 | **전진 + 우회전 2가지** |
| 드론 앞쪽 | 계속 처음 방향 | 모서리마다 바뀜 |
| 모습 | 옆·뒤로 미끄러진다 | 자동차처럼 코너링 |
| 확장 | 임의의 경로 | 정다각형 — **회전각 = 360 ÷ 변의 수** |

두 번째가 성립하는 이유는 **위치 이동이 바디 기준**이기 때문이다. "앞" 은 방의 고정된 방향이
아니라 드론이 지금 바라보는 쪽이라, 회전한 뒤의 전진은 새 방향으로 나아간다.
그래서 같은 명령 두 개만 반복해도 도형이 된다.

방향 이동 쪽은 네 변의 합이 0 이라 리턴홈 없이도 출발점으로 돌아온다 — 이론상. 실제로는
이동 오차가 누적되어 조금씩 어긋난다.

### 중단하는 방법

자율 비행은 시작하면 사람이 낄 자리가 없다. 빠져나오는 길은 하나뿐이다.

- **대기 중 Ctrl+C** → `KeyboardInterrupt` → `finally` 의 `sendLanding()` 이 나간다.
- **터미널 창을 그냥 닫으면 안 된다.** 파이썬만 죽고 드론은 마지막 명령을 유지한 채 계속 난다.
- 그래도 안 되면 조종기 전원 버튼으로 직접 착륙시키거나, 몸체를 잡아 뒤집는다(뒤집히면 모터가 꺼진다).

## 미션 비행 — 센서로 판단하고 반응한다

30~34 는 **얼마나 갈지 아는** 비행이었다. 35~38 은 두 가지를 섞는다.

| | 아는 거리 | 모르는 거리 |
|---|---|---|
| 명령 | `sendControlPosition(거리, 속도)` | `sendControl(0, 세기, 0, 0)` 반복 |
| 멈추는 조건 | 목표 도착 시 자동 | **센서가 정한다** |
| 간 거리 | 안다 | 모른다 |
| 쓰는 곳 | 경로·회피 이동 | "장애물 만날 때까지" 전진 |

둘 다 `DataType.Control` 이라 **나중에 보낸 쪽이 이긴다.** 세기로 전진하다 거리 이동으로
넘어갈 때는 `sendControl(0, 0, 0, 0)` 으로 먼저 끊고, 관성이 죽도록 0.5초 쉰다.

### 센서에 따라 바뀌는 건 네 줄뿐이다

| | 전방 (36, 38) | 하방 (37) |
|---|---|---|
| 요청 | `DataType.Range` | `DataType.Altitude` |
| 콜백 | `event_range(range_data)` | `event_altitude(altitude)` |
| 값 | `range_data.front` | `altitude.rangeHeight` |
| 단위 | **mm** (400 = 40 cm) | **m** (0.4 = 40 cm) |

1000배 차이다. 헷갈리면 영영 감지가 안 되거나 이륙하자마자 착륙한다.
`altitude.altitude` 는 기압 기반이라 상자 위를 지나도 안 변한다 — 쓰지 않는다.

하방 감지 기준값은 고정된 수가 아니다. **호버링 높이 − 상자 높이 + 여유**이고,
호버링 높이는 기체·바닥·배터리마다 다르다. 21 번으로 먼저 찍어 보고 정한다.

### 콜백은 플래그만 세운다

강의 원본은 콜백 안에서 정지·이동·착륙까지 한다. 세 가지가 한꺼번에 깨진다.

| 원본 | 결과 |
|---|---|
| `global` 누락 (미션 4·5·6) | 대입한 값이 지역 변수에 갇혀 **메인 루프가 영영 안 끝난다.** 콜백이 착륙시켜 놓고도 전진 명령이 계속 나간다 |
| `if value == False` (미션 6) | `value` 는 정의된 적이 없다 → `NameError` → `except KeyboardInterrupt` 에 안 잡히고 `finally` 의 `close()` 만 실행 → **드론이 전진 명령을 받은 채 공중에 남고 연결만 끊긴다** |
| 콜백 안의 `sleep(2)` (미션 5) | 콜백은 **백그라운드 수신 스레드**가 부른다. 2초를 멈추면 그동안 수신이 밀리고, 값이 올 때마다 불리므로 이동·착륙 명령이 중복된다 |

정리하면 **콜백은 값 저장 + 플래그, 명령은 메인 루프에서 한 번.** 핸들러 등록도 루프 밖 1회다.
감지 구간 `300 < front < 400` 도 좁다 — 빠르게 지나가면 그 창을 건너뛴다 → `0 < front < 400`
(0 은 측정 실패라 제외).

### 간 거리를 세면 착륙 지점이 고정된다

과제(38)의 핵심이다. `sendControl` 로 계속 전진하면 **몇 m 왔는지 알 수가 없어서**,
장애물이 어디서 나오느냐에 따라 착륙 지점이 매번 달라진다.
그래서 감시 구간만 0.1 m 씩 위치 명령으로 끊어 가며 `traveled` 를 센다.

회피는 "오른쪽 → 전진 → 왼쪽" 이라 옆으로 나간 만큼은 돌아오지만 **앞으로 간 거리는 남는다.**

    ① 회피 전진분을 traveled 에 더한다        → 남은 구간만 더 간다
    ② 그래도 목표를 넘겼으면(overshoot)        → 마지막 후진 구간에서 그만큼 더 물러난다

②를 넘어간 자리에서 바로 하면 **방금 피한 장애물에 다시 부딪힌다.** 옆으로 빠진 뒤에 보정한다.

경로 전체에서 `heading` 을 0 으로 두는 것도 같은 이유다. 회전하면 전방 센서가 다른 쪽을
보게 되므로, 기체는 앞을 본 채 게걸음으로만 움직인다.

### 버튼으로 출발 / LED 로 상태 표시

```python
dron.setEventHandler(DataType.Button, event_button)
dron.sendLightModeColor(LightModeDrone.BodyHold, 200, 0, 255, 0)   # 초록 점등
```

- 버튼은 **`ButtonEvent.Down` 만** 본다(누르고 있으면 `Press` 가 계속 들어온다).
  전원 버튼 `ButtonFlagController.TopRight`(0x0020)는 제외해야 한다.
- `sendLightModeColor(lightMode, interval, r, g, b)` 의 `interval` 은 모드마다 뜻이 다르다 —
  `Hold` 는 **밝기**, `Flicker` 는 **점멸 주기(ms)**, `Dimming` 은 디밍 속도.
- `interval`·`r`·`g`·`b` 는 **int 전용**이고, `lightMode` 는 enum 이어야 한다. 아니면 조용히 무시.
- 모드는 끌 때까지 유지되므로 `finally` 에서 `sendLightManual(DeviceType.Drone, 0xFF, 0)` 로 끈다.

### 좁은 방에서 거리를 줄일 때 — 속도까지 줄이면 안 된다

거리를 1/3 로 줄이면 속도도 1/3 로 줄이고 싶어지는데, 위치 명령의 권장 속도는 **0.5~2.0 m/s**
다. 0.17 m/s 나 0.1 m/s 는 그 아래고, 0.05 m 짜리 조각도 너무 짧다.
라이브러리는 막지 않지만(위치 명령에는 범위 검사가 없다) 기체가 굼뜨거나 한 조각을 제자리에서
흘려보낼 수 있다. 38 의 `ROOM = "NARROW"` 는 그걸 감수한 타협이다 — 넓은 곳에서는 `"WIDE"`.

## 영상인식 OpenCV — 드론에서 잠깐 내려온다

21 강은 드론을 날리지 않는다. 인공지능 이론과 OpenCV 설치까지다. (`39`, `40`)

### 인공지능 ⊃ 머신러닝 ⊃ 딥러닝

| | 머신러닝 | 딥러닝 |
|---|---|---|
| 지능의 원천 | 통계학습 | 자가학습 |
| 특징 파악 | **사람이** 데이터 정보를 준다 | **스스로** 특징을 찾아 분류한다 |
| 관계 | 상위 개념 | 머신러닝의 하위 분야 |
| 예 | 추천 서비스 | 알파고 |

- **머신러닝 학습 종류** — 지도학습(분류 / 회귀), 비지도학습(군집 / 차원 축소),
  강화학습(완전한 답 대신 **보상**을 준다. 게임·로봇 학습에 주로 쓴다)
- **딥러닝 대표 모델** — CNN(시신경 구조 모방, 얼굴인식·문장분류) /
  RNN(순차 데이터 반복 학습, 음성인식·번역) / GAN(두 모델이 대결하며 학습, 창작물)
- **연표** — 1943 인공신경망 연구 시작(맥클록·피츠) → 1950 튜링 테스트(앨런 튜링)
  → 1956 다트머스 회의에서 'AI' 라는 말이 처음 쓰임

| | OpenCV | TensorFlow |
|---|---|---|
| 성격 | 실시간 컴퓨터 비전 라이브러리 | 머신러닝 엔진 |
| 만든 곳 | 인텔 | 구글 (2015 오픈소스 전환) |
| 작성 언어 | C/C++ | C++ |
| 파이썬 | 바인딩 제공 (자바·매트랩도) | API 제공 |

### 설치 — 강의대로 하면 안 되는 한 가지

슬라이드는 `opencv-python` 과 `opencv-contrib-python` 을 **둘 다** 깔라고 하는데,
두 패키지는 같은 `cv2/` 디렉터리를 설치한다(설치된 `opencv-python` 의 dist-info RECORD 는
실제로 전부 `cv2/...` 였다. contrib 도 같은 자리를 쓴다).
pip 는 합쳐 주지 않고 덮어쓰므로 섞이면 버전 불일치·기능 누락이 난다. **하나만** 고른다.
contrib 쪽이 메인 모듈을 포함하니 contrib 하나면 충분하다.

맥에는 "cmd 관리자 권한 실행" 이 없다. 드론 실습용 venv 를 그대로 쓰면 되고 `sudo` 도 필요 없다.

```bash
source .venv/bin/activate
pip install opencv-contrib-python matplotlib
python -c "import cv2; print(cv2.__version__)"
```

- `numpy` 는 CodingDrone 이 의존성으로 이미 깔아 둔다. 영상이 곧 숫자 행렬이라 필요한 것.
- **설치 이름은 `opencv-python`, import 이름은 `cv2`** 다. `import opencv` 는 없다.
- 버전은 달라도 정상이다(슬라이드는 촬영 당시의 `4.4.0`). 이 저장소는 21~22 강을 **5.0.0** 으로 확인했고,
  **23 강부터는 4.10.0.84 로 내렸다** — 얼굴 인식(`CascadeClassifier`)이 5.0 에서 빠졌기 때문이다(아래 23 강 절).
- `opencv-python-headless` 가 깔리면 `imshow` 가 안 된다. `39` 가 GUI 백엔드를 찍어 준다
  (맥은 `COCOA`, headless 는 `NONE`).

### 읽는 두 줄, 보여주는 세 줄

| 코드 | 뜻 |
|---|---|
| `cv.imread(경로)` | 컬러로 읽기 (`IMREAD_COLOR` = 1) |
| `cv.imread(경로, 0)` | 흑백으로 읽기 (`0` 은 `IMREAD_GRAYSCALE` 의 값. `-1` 은 알파까지) |
| `cv.imshow(제목, img)` | 창에 올리기 — **이것만으로는 안 그려진다** |
| `cv.waitKey(0)` | 키 대기. **창은 이 안에서 그려진다.** 밀리초를 주면 시간 초과 시 `-1` |
| `cv.destroyAllWindows()` | 창 닫기 |

슬라이드 코드를 그대로 치면 창이 안 뜨거나 회색으로 멈추는 이유가 이것이다.
창의 X 버튼으로 닫으려 하지 말고 **창에 포커스를 준 채 키를 누른다.**

읽은 결과는 numpy 배열이다 — 컬러 `(높이, 너비, 3)`, 흑백 `(높이, 너비)`, 값은 0~255.

### 여기도 조용히 실패한다

`imread` 는 경로가 틀려도 **예외를 던지지 않고 `None` 을 돌려준다.**

```
[ WARN:0@0.06] global loadsave.cpp:278 findDecoder imread_('/nope/none.jpg'): can't open/read file
```

경고 한 줄은 찍히지만 프로그램은 그대로 진행되고, 진짜 에러는 한참 뒤 `imshow` 나
`shape` 에서 엉뚱한 모습으로 터진다. 드론 라이브러리가 인자 타입이 틀리면
조용히 `None` 을 돌려주던 것과 같은 종류다. **읽은 직후 `is None` 검사가 정석.**

### 색 순서가 BGR 이다

OpenCV 는 파랑-초록-빨강 순으로 저장한다. 파란 픽셀을 찍으면 `[255 0 0]` 이 나온다.
cv 끼리 주고받을 땐 상관없지만 matplotlib 으로 그릴 때는 바꿔야 색이 맞는다.

```python
plt.imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB))   # 안 바꾸면 파랑↔빨강이 뒤집힌다
plt.imshow(gray, cmap="gray")                    # 흑백은 cmap 을 줘야 회색으로 나온다
```

맥 주피터에서는 `cv.imshow` 창이 커널을 먹통으로 만드는 일이 잦으니 이 방식이 안전하다.
`40` 의 `SHOW` 를 `"plot"` 으로 바꾸면 같은 그림을 matplotlib 으로 그린다.

## 이미지 인식과 색 검출 — 찾고, 지우고, 고른다

22 강. 역시 드론은 쓰지 않는다. (`41`~`44`)

### 흑백처리 — 두 방법은 같지 않다

| 방법 | 코드 | 특징 |
|---|---|---|
| ① 읽을 때 | `cv.imread(경로, 0)` | 1채널. 원본 컬러는 남지 않는다 |
| ② 읽고 변환 | `cv.cvtColor(img, cv.COLOR_BGR2GRAY)` | 컬러 원본을 두고 흑백본을 따로 만든다 |

색상 인식이 목적이면 ②. **한 번 흑백이 된 이미지는 색을 되돌릴 수 없다** —
`COLOR_GRAY2BGR` 은 3채널로 늘려 줄 뿐 세 채널 값이 같아 여전히 회색이다.

강의는 두 방법을 같은 것으로 소개하는데, 같은 사진을 두 방법으로 읽어 빼 보면 다르다.

| 파일 | 최대 차이 | 다른 픽셀 |
|---|---|---|
| PNG | 1 | 44만 중 9만 (반올림) |
| JPEG | **12** | 76만 중 3만 |

JPEG 은 압축할 때 색을 밝기와 색차로 나눠 저장한다. `imread(경로, 0)` 은 그 밝기 성분을
바로 꺼내 오고 `cvtColor` 는 컬러로 펼친 뒤 다시 계산하는 것으로 보인다(경로가 다르다는 뜻).
실습 결과가 눈에 띄게 달라지진 않지만 "둘은 같다" 고 말할 수는 없다.

흑백 변환은 평균이 아니라 사람 눈을 반영한 가중합이다 — `0.299R + 0.587G + 0.114B`.
직접 계산한 값과 `cvtColor` 결과의 차이는 최대 1(반올림)이었다.
같은 255 라도 초록은 150, 빨강은 76, 파랑은 29 로 변환된다.

### 템플릿 매칭 — 항상 무언가를 찾아낸다

```
cv.matchTemplate(장면, 템플릿, 방법)  ->  점수 배열
cv.minMaxLoc(배열)                    ->  (최솟값, 최댓값, 최솟값 위치, 최댓값 위치)
```

| 방법 | 점수 | 정답 위치 |
|---|---|---|
| `TM_SQDIFF` (강의) | 차이의 제곱합 — 작을수록 비슷 | `minLoc` |
| `TM_CCOEFF_NORMED` | 상관계수 −1~1 — 클수록 비슷 | `maxLoc` |

방법을 바꾸면 `minLoc`/`maxLoc` 도 같이 바꿔야 한다. 그리고 **대상이 장면에 없어도
가장 덜 다른 자리를 돌려주므로 사각형은 언제나 그려진다.** 강의의 `TM_SQDIFF` 는
점수가 몇십억짜리 절대값이라 성공·실패를 가릴 수 없다 — `TM_CCOEFF_NORMED` 로 바꾸고
`maxVal > 0.8` 같은 기준을 걸어야 "못 찾았다" 를 알 수 있다.
직접 그린 장면으로 확인한 값:

| 상황 | 점수 | 결과 |
|---|---|---|
| 장면에서 잘라낸 템플릿 | 1.000 | 오차 0 픽셀 |
| 0.6 배로 줄인 템플릿 | 0.555 | 엉뚱한 자리 |
| 위 + 크기 탐색 | 0.988 (배율 1.65) | 오차 (1, 2) 픽셀 |
| 장면에 없는 대상 | 0.328 | **좌표는 나온다** |

### 학습자료실 이미지로는 강의대로 안 된다

22 차시 이미지 5장(드론 4대가 든 전체 사진 + 드론 1~4 개별 png)으로 강의 코드를 돌리면
찾지 못한다. 개별 png 가 전체 사진에서 **잘라낸 조각이 아니라 따로 찍은 사진**이라
크기도 각도도 다르기 때문이다. 전체 사진은 773x987 인데 개별 파일은
638x698 / 366x510 / 767x767 / 615x895 로 장면 속 드론보다 오히려 크다.

| 템플릿 | 원래 크기 그대로 | 크기를 바꿔 가며 |
|---|---|---|
| 분홍 드론 | 0.03 | **0.96** (0.56 배) |
| 하늘색 드론 | 0.22 | 0.61 (0.88 배) |
| 빨강 프로펠러 드론 | 0.13 | 0.23 |
| 볼 가드 드론 | −0.06 | 0.44 (0.42 배) |

크기를 맞춰도 빨강 프로펠러 드론은 0.23 이다. **각도가 다르기 때문**이다.
템플릿 매칭은 크기·각도가 같을 때만 쓸 수 있다는 한계가 그대로 나온다.
그래서 `42` 는 기본값으로 장면을 직접 그려서 쓴다.

### HSV — 색의 종류는 H 하나로 결정된다

BGR 은 조명이 어두워지면 세 값이 전부 내려가 색 범위를 잡기 어렵다. HSV 는 밝기 변화가
주로 V 에만 반영되므로 "파란색 찾기" 가 `H 가 110~130` 으로 끝난다.

| | 이론 (슬라이드) | **OpenCV** | 환산 |
|---|---|---|---|
| H 색상 | 0~360° | **0~179** | ÷2 (8비트 한 칸에 담으려고) |
| S 채도 | 0~100 | **0~255** | ×2.55 |
| V 명도 | 0~100 | **0~255** | ×2.55 |

빨강 0 / 노랑 30 / 초록 60 / 하늘 90 / 파랑 120 / 보라 150. 슬라이드의 "파랑 220~260°" 가
OpenCV 로 110~130 이다. 색 하나를 변환할 때는 1x1 이미지로 만들어 넘긴다 —
`cv.cvtColor(np.uint8([[[0, 0, 255]]]), cv.COLOR_BGR2HSV)`. `np.uint8` 을 빼면 int64 라 에러다.

함정 셋:

- **빨강은 두 구간이다.** H=0 이 색상환의 시작이자 끝이라 0 과 179 양쪽에 걸친다.
- **`uint8` 로 빼면 음수가 없다.** `H(0) − 10` 은 −10 이 아니라 **246**. `int()` 로 바꿔 계산한다.
  (numpy 2.x 는 `overflow encountered` 경고라도 띄워 준다. 값은 그대로 246)
- **흰색·회색·검정도 H 가 0 이다.** 빨강과 구분되지 않으므로 **S·V 최솟값을 함께 건다**
  (강의의 "적당한 값 30"). 실제 사진은 50~100 까지 올린다.

### 색 검출 세 단계 — 과제

```
원본(BGR) ──cvtColor──▶ HSV ──inRange(범위)──▶ 마스크(흰/검)
    │                                              │
    └──────────────── bitwise_and(mask=) ◀─────────┘
```

`cv.bitwise_and(img, img, mask=마스크)` 에 같은 원본을 두 번 넣는 게 이상해 보이지만,
마스크가 흰 곳만 계산하므로 결과가 "그 색만 원본 그대로" 가 된다.

과제의 핵심은 **빨강을 한 구간으로 잡으면 안 된다**는 것. 강의의 `(0-10) ~ (0+10)` 은
H 에 음수가 없어 사실상 `0~10` 만 검출하고, 반대쪽 끝 `170~179` 가 통째로 빠진다.
색상환을 만들어 세어 보면 한 구간 4.3% / 두 구간 8.2% 로 **1.91 배** 차이가 난다.

```python
mask1 = cv.inRange(hsv, (0, 30, 30),   (10, 255, 255))
mask2 = cv.inRange(hsv, (170, 30, 30), (179, 255, 255))
mask  = cv.bitwise_or(mask1, mask2)
```

`44` 는 색상환이 없어도 되도록 직접 그린다 — 각도를 그대로 H 로, 중심에서의 거리를 S 로
넣으면 색상환이 된다. "H 는 각도" 가 그림으로 확인되는 부분이다.

> 슬라이드 주석 오류: `height, width = img_color.shape[:2]` 옆의 `가로 [0], 세로[1]` 은 반대다.
> `shape[0]` 이 높이(세로), `shape[1]` 이 너비(가로)다. 변수 이름 순서가 맞다.

## 영상과 얼굴 인식 — 카메라가 붙는다

23 강. 드론은 아직 안 쓰지만 카메라가 등장한다. (`45`~`49`)
맥은 **시스템 환경설정 → 보안 및 개인 정보 보호 → 카메라** 에서 터미널(또는 VS Code)을 허용해야 한다.
허용 전에는 `isOpened()` 가 False 이거나 검은 화면만 나온다.

### ⚠️ 얼굴 인식은 OpenCV 4.x 에서만 된다

`cv.CascadeClassifier` 와 학습된 xml 이 **5.0 에서 통째로 빠졌다.** 캐시에 남아 있던
5.0.0.93 휠을 직접 열어 확인한 결과:

| | OpenCV 5.0.0.93 | OpenCV 4.10.0.84 |
|---|---|---|
| `cv2/data/` 안의 xml | **0개** (`__init__.py` 하나뿐) | **17개** |
| `.so` 안의 `CascadeClassifier` | **0건** | 있음 |

```bash
pip install --only-binary=:all: "opencv-python<5"
```

`--only-binary=:all:` 은 소스 컴파일로 새는 것을 막는다. 이 맥(macOS 12 Intel / Python 3.12)에
pip 가 주는 최신 바이너리는 **4.10.0.84** 이고, 그냥 `pip install opencv-python` 하면
5.0 을 소스에서 빌드하려 든다.

### 영상 한 프레임을 다루는 골격

```python
cap = cv.VideoCapture(0)          # 정수 = 카메라, 문자열 = 동영상 파일
while True:
    ret, frame = cap.read()
    if not ret:                   # 강의 예제1 에 빠져 있는 줄
        break                     # 카메라가 끊겼거나 파일이 끝났다. frame 은 None
    ...
    cv.imshow("frame", frame)
    if cv.waitKey(30) & 0xFF == 27:   # ESC
        break
cap.release()                     # 안 하면 카메라가 잡힌 채로 남는다
```

- **`set()` 은 요청일 뿐이다.** 적용된 값은 `get()` 으로 확인한다. 동영상 파일에 쓰면 아예 무시된다 —
  320x240 파일에 640x480 을 요청해도 그대로 320x240 이었다. `cap.set(3, …)` 의 3·4·5 는
  `FRAME_WIDTH`·`FRAME_HEIGHT`·`FPS`.
- **슬라이드 주석 오류**: `cv.flip(frame, 1)` 옆이 "상하반전" 인데 **좌우 반전**이다(상하는 `0`).
- `45` 는 `SOURCE = "demo"` 로 두면 합성 영상을 만들어 읽으므로 **카메라 없이** 전 과정을 확인할 수 있다.

### 좌표 순서가 두 가지다

| | 순서 | 예 |
|---|---|---|
| numpy 슬라이싱 | **세로, 가로** | `img[100:200, 200:300]` |
| 그리기 함수 | **가로, 세로** | `cv.rectangle(img, (x, y), …)` |
| 배열 만들기 | 높이, 너비, 채널 | `np.zeros((480, 640, 3), np.uint8)` |
| 카메라 설정 | 너비, 높이 | `cap.set(…WIDTH, 640)` |

두께에 `-1`(`cv.FILLED`)을 주면 속이 찬다. 사각형의 두 점은 마주보는 꼭짓점이기만 하면 되고,
`putText` 의 좌표는 글자의 **왼쪽 아래**다. `FONT_ITALIC` 은 단독 글꼴이 아니라 `|` 로 조합한다.
**Hershey 글꼴에는 한글이 없다** — `???` 로 나온다.
그리기 함수는 새 이미지를 주는 게 아니라 넘긴 배열을 직접 고친다.

### 영상 저장 — 조용히 실패하는 세 자리

| 실수 | 증상 (직접 확인한 값) |
|---|---|
| `fps` 에 0 을 넘김 (맥 카메라가 0 을 돌려줌) | `isOpened()` **False**, 이후 `write()` 는 무반응 |
| 저장 크기 ≠ 프레임 크기 | 에러 없이 **257 바이트 / 0 프레임** |
| `release()` 누락 | **44 바이트**, 다시 열면 `moov atom not found` |

정상 저장본은 27KB / 30 프레임 / fps 20 / 320x240 으로 읽혔다. 강의 예제4 슬라이드에는
`out.release()` 가 아예 빠져 있다. 크기는 카메라에서 읽은 값을 그대로 쓰고, `try/finally` 로 닫는다.
코덱은 이 맥에서 `mp4v` `DIVX` `XVID` `avc1` `MJPG` 다섯 다 열렸다 —
QuickTime 이 avi 를 못 여니 `mp4v` + `.mp4` 가 편하다.

### 얼굴 인식 — 분류기도 조용히 실패한다

```python
face = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')
if face.empty():      # 경로가 틀려도 예외가 안 난다. imread 가 None 을 주던 것과 같은 종류
    ...
faces = face.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
```

입력은 **흑백**이다(밝기 차이로 특징을 찾는다). xml 파일만 바꾸면 눈·상체·고양이 얼굴이 된다.

**파라미터는 `minSize` 가 더 결정적이다.** 얼굴 두 개(47x47, 58x58)가 있는 사진으로 재 보면:

| 조건 | 결과 |
|---|---|
| `minNeighbors` 3 / 5 / 6 | 전부 2개 (차이 없음) |
| `minSize` (30,30) / (50,50) | 2개 |
| `minSize` (80,80) | **0개** |

과제 코드의 `minSize=(80, 80)` 은 웹캠 앞 얼굴(150~250 픽셀) 기준이라, 조금만 멀어지면 통째로 놓친다.

눈은 **얼굴을 먼저 찾고 그 안에서만** 찾는다. 화면 전체에서 찾으면 콧구멍·입꼬리까지 눈으로 잡는다.
잘라낸 영역(ROI)은 원본 배열의 창문이라 `roi_color` 에 그리면 `frame` 에도 그려진다 —
좌표를 더할 필요가 없다. 단 얼굴이 충분히 커야 한다. 위 사진의 47~58 픽셀 얼굴에서는
눈도 입도 하나도 잡히지 않았다(선글라스 탓도 있다).

**박스가 그려졌다고 거기에 얼굴이 있는 건 아니다.** 같은 사진에 `haarcascade_profileface` 를
돌렸더니 사람이 아닌 바닥 쪽에 하나가 잡혔고, 2배로 확대하니 같은 얼굴에 박스가 겹쳐 잡혔다.

### 과제에서 손본 것

- **`eyes[:2]` 는 "가장 그럴듯한 둘" 이 아니다.** `detectMultiScale` 결과는 신뢰도 순이 아니라
  훑은 순서(위→아래, 왼→오)다. 앞의 둘이 눈썹일 수 있다 → 넓이 순으로 큰 둘.
- 창의 **X 버튼으로 닫으면 루프가 안 끝난다**(키만 보고 있어서) → `getWindowProperty` 도 함께 본다.
- 녹화 fps 를 **시작 직후의 측정값**으로 잡으면 이동평균이 덜 올라와 영상이 느리게 재생된다
  → 몇 프레임 지난 뒤의 값만 쓰고, 아니면 카메라 fps 로.
- `● REC` 표시는 `write()` 뒤에 그리므로 **녹화본에는 안 남는다**(화면에만). 과제 주석은 반대로 읽힌다.
- 분류기 로드를 `main()` 안으로 옮겼다. 최상단에 두면 **import 만 해도** 죽는다.

## 색으로 드론을 움직인다 — 눈과 손이 이어진다

24 강. 22~23 강의 색 검출에 드론 명령을 붙인다. (`50`~`52`)
**`DRY_RUN = True` 로 두면 드론 없이** 인식과 판단만 확인할 수 있고,
`SOURCE = "demo"` 면 카메라도 없이 합성 영상으로 돌아간다. 이 순서로 확인하고 띄운다.

### 마스크에 "어디 있는지" 를 붙인다

```
HSV 변환 -> inRange 마스크 -> 잡음 정리 -> findContours -> 가장 큰 것 -> boundingRect -> 중심
```

- `findContours` 는 **4.x 에서 반환값이 2개**(3.x 는 3개)다. 붙여 넣은 예제가
  `too many values to unpack` 을 내면 이 차이다.
- 강의 코드는 `for` 로 돌며 `height = y` 를 덮어써서 **마지막으로 훑은 물체**가 기준이 된다.
  `max(contours, key=cv.contourArea)` 로 가장 큰 것 하나만 쓰는 편이 예측 가능하다.
- `boundingRect` 의 `(x, y)` 는 **왼쪽 위**다. 공의 위치로 쓰려면 `x + w//2`, `y + h//2`.
- 열기(OPEN) → 닫기(CLOSE) 로 잡음을 정리하지 않으면 형광등 반사 하나에 윤곽선이 수십 개 나온다.

### 강의 예제1(트랙바)의 `H ± 10` 은 빨강에서 깨진다

```python
ch_hsv = [hsv[0], s, v]                   # hsv[0] 은 numpy uint8
lower = np.array([ch_hsv[0] - 10, ...])   # H=0 이면 -10 이 아니라 246
```

직접 돌려 보면 빨강을 고른 순간 `lower=[246 120 177]`, `upper=[10 255 255]` 가 되어
**하한이 상한보다 커지고 마스크가 전부 검게** 나온다. "빨강은 원래 잘 안 잡힌다" 로 넘어가기 쉬운데
원인은 색이 아니라 이 뺄셈이다(43 의 `uint8` 함정). `int()` 로 계산하고, 빨강은 22 강처럼 두 구간으로 잡는다.

### 강의 예제2 — 시작하자마자 이륙한다

| 문제 | 왜 | 고친 방법 |
|---|---|---|
| 첫 프레임부터 이륙 | `height = 0` 으로 시작하는데 판단이 `height < 300` | `t` 키로만 이륙 |
| 초당 수십 번 이착륙 명령 | 매 프레임 `sendTakeOff()`/`sendLanding()` | 상태가 바뀔 때만 전송 |
| 공을 치워도 계속 이륙 상태 | `height` 가 마지막 값을 유지 | 놓치면 잠깐 뒤 정지로 |
| 끝나도 드론은 그대로 | ESC 로 루프만 빠져나옴, 착륙·`close()` 없음 | `try/finally` 로 착륙 보장 |

### 강의 예제3 — 슬라이드 코드와 영상 코드의 축이 다르다

| | 슬라이드 | 영상(최종) |
|---|---|---|
| 상승·하강 판단 | `width`(x) | **`height`(y)** |
| 좌·우 판단 | `height`(y) | **`width`(x)** |
| 오른쪽 조건 | `500 < height < 600` | `500 < width < 600` |

슬라이드대로 치면 **오른쪽 이동이 영원히 일어나지 않는다.** 화면 높이가 480 이라 `height` 가
500 을 넘을 수 없기 때문이다. 슬라이드에는 매 루프 `sendControl(0,0,0,0)` + `sleep(0.1)` 도 있는데,
이동 명령이 바로 정지 명령으로 덮여 거의 움직이지 않는다.

**가운데에서는 "아무 명령 없음" 이 아니라 "정지 명령" 을 보내야 한다.** 드론은 마지막 명령을
유지하므로, 가운데 영역에서 아무것도 안 보내면 하던 이동을 계속한다
(28 강의 `else: sendControl(0,0,0,0)` 과 같은 이야기).

**roll 부호는 거울 여부에 달렸다.** 웹캠 원본은 거울이 아니라서 내가 공을 오른쪽으로 옮기면
화면에서는 왼쪽으로 간다. 강의 영상이 화면 왼쪽에 `roll +50` 을 준 이유다.
`50`~`52` 는 `MIRROR = True` 로 먼저 좌우를 뒤집고 화면 오른쪽에 `roll +` 를 준다.
드론이 나를 마주 보고 있으면 또 반대가 되니 **낮은 세기로 방향부터 확인**할 것.

### 과제 코드에서 고친 것

- **포트 하드코딩**(`/dev/cu.usbmodem31A9388730351`) → `find_port()`. USB 포트를 바꿔 꽂으면 숫자가 달라진다.
- **`open()` 의 반환값을 본다.** 실패해도 예외가 아니라 `False` 다 — 확인하지 않으면
  연결도 안 된 채 이륙 명령을 보내며 계속 돈다.
- **녹화 fps 를 20 으로 고정하지 않는다.** 색 추적이 무거우면 실제로는 그보다 느려서
  저장본이 빨리 감기처럼 재생된다(47) → 측정한 처리 속도로 연다.
- 녹화 크기는 화면과 같아야 한다. 원본+마스크를 가로로 붙이므로 **`(FRAME_W * 2, FRAME_H)`** —
  안 맞으면 에러 없이 빈 파일이 된다(47).

## 군집비행 — 새 함수는 하나도 없다

25 강. (`53`~`55`) 여러 대를 날리는 일의 전부는 **객체를 여러 개 만드는 것**이다.

    드론 N 대 = 조종기 N 대 = 시리얼 포트 N 개 = `Drone` 객체 N 개

라이브러리 쪽 상태가 전부 인스턴스 변수(`self._serialport`, `self._receiver`, `self._eventHandler` …)라
객체끼리 섞이지 않는다. 대신 `open()` 마다 **수신 스레드가 하나씩 더 생긴다**(4 대면 4 개).
세 파일 모두 `DRY_RUN = True` 면 드론 없이 순서와 값만 확인할 수 있다.

### ⚠️ `open()` 을 인자 없이 부르면 안 된다

```python
drone.open()          # 포트를 안 주면 comports() 의 마지막 장치를 잡는다
drone.open(포트)       # 반환값 False = 실패. 예외가 아니다
```

한 대일 때도 위험하지만 군집에서는 **두 객체가 같은 포트를 잡거나 엉뚱한 장치를 잡는다.**
포트 이름의 숫자는 꽂는 자리에 따라 바뀌어서 **이름만 보고 몇 번 드론인지 알 수 없으므로**,
`53`~`55` 는 이륙 전에 드론마다 LED 를 순서대로 켜서 짝을 확인한다(`LED_CHECK`).
포트를 한꺼번에 찾는 `find_ports(개수)` 를 `drone_util` 에 추가했다 — 개수가 안 맞으면 바로 알려 준다.

### `sendControlWhile` 은 블로킹이다 — 군집에서 이게 함정

라이브러리를 열어 보면 `timeMs` 동안 **20 ms 간격으로 `sendControl` 을 반복**하고
그 시간이 다 지나야 반환한다. 한 대에 보내는 동안 나머지는 마지막 명령을 유지할 뿐이다.

| | "3 초 호버링" 루프의 실제 시간 |
|---|---|
| 2 대 | 2 × 1 초 × 3 회 = 약 **6 초** |
| 4 대 | 4 × 1 초 × 3 회 = 약 **12 초** |

제자리(0,0,0,0)라 호버링에서는 티가 안 나지만, **이동을 이 함수로 주면 대수만큼 시차가 생긴다.**
동시에 움직이려면 논블로킹인 `sendControlPosition` 을 연달아 보내고 `sleep` 으로 기다린다.
(하네스로 세어 보면 2 대 코드가 실제로 564 프레임, 4 대 코드가 1,662 프레임을 보낸다 —
대부분이 이 호버링 루프다.)

### 좌우 이동은 배치에 따라 충돌이 된다

코딩드론은 **y+ 가 왼쪽**이다. 2 대 예제 6 단계에서 drone1 은 +y, drone2 는 −y 로 1 m 씩 간다.

| 배치 | 결과 |
|---|---|
| drone1 왼쪽 / drone2 오른쪽 | 2 m → 4 m 로 벌어진다 ✅ |
| 반대로 두면 | 서로를 향해 1 m 씩 — **충돌** ❌ |

4 대 예제는 5 단계에서 두 조가 높이를 맞바꾸며 스쳐 지나가므로, 1/2 조와 3/4 조를
**대각선으로 엇갈리게** 놓는다. 간격은 2 m 이상 — 더 가까우면 서로의 프로펠러 바람에 자세가 흔들린다.
최고 높이가 이륙 높이 + 1.4 m 이니 **천장을 먼저 확인**할 것.

### 패턴은 "드론마다 다른 값" 일 뿐이다

| 패턴 | 만드는 법 |
|---|---|
| 동시 / 순차 이륙 | `sendTakeOff()` 를 한꺼번에 / 사이에 `sleep()` |
| 대칭 이륙 · 대형 변경 · 웨이브 | 이륙 후 드론마다 `sendControlPosition(0, 0, **z**, …)` 의 z 를 다르게 |
| 군집 이동 | 전원에게 같은 `(x, y)` |
| 확장 / 축소 | 대형 중심에서 자기 자리로 향하는 부호로 `(x, y)` |
| 사각 회전 | "다음 꼭짓점 − 지금 꼭짓점". 반시계면 d1 앞 / d2 왼쪽 / d3 뒤 / d4 오른쪽 |

`55` 는 대형 좌표표에서 이 값들을 **계산해서** 만든다. 패턴을 수행한 뒤에는 부호를 뒤집어
원위치시킨다 — 위치 명령은 절대 좌표가 아니라 "지금 위치에서 얼마" 라서, 안 돌아오면 대형이 계속 밀린다.
옵티컬센서가 바닥 무늬로 이동량을 재므로 **무늬 없는 바닥·반사·어두운 곳에서는 위치가 흐르고**,
반복할수록 오차가 쌓인다.

### 슬라이드 오탈자

- 2 대 코드 4 단계 `print('Step.4| Drone1/2 Backward")` — 따옴표 짝이 안 맞아 **SyntaxError**. 실행 자체가 안 된다.
- 6·7 단계의 출력이 `[Step.3]`, `[Step.2]` 로 적혀 있다.
- 8·9 단계 주석·출력이 `drone3/4` — 4 대 코드에서 복사한 흔적.
- 두 예제 모두 **예외 처리가 없다.** 중간에 멈추면 드론은 마지막 명령을 유지한 채 떠 있고 포트도 안 닫힌다.

## OpenCV 를 넘어 CNN 으로 — 무엇이 다른가

26 강. 이론 강의라 코드가 없다. 대신 **말로 된 주장을 숫자로 확인하는** 파일 셋을 뒀다. (`56`~`58`)

### 수동 특징 vs 학습된 특징

| | OpenCV 전통 방식 | CNN (예: YOLO) |
|---|---|---|
| 특징 추출 | 사람이 규칙을 만든다 (색 범위, 엣지, Haar, HOG) | 데이터에서 배운다 |
| 정확도·강인성 | 가정한 조건 밖에서 급격히 나빠짐 | 환경 변화에 강함 |
| 다중 객체 | 제한적 | 동시에 여러 개·여러 종류 |
| 실시간성 | Haar 는 빠름 | YOLO 계열은 매우 빠름 |
| 데이터 | 거의 없어도 됨 | 대량 필요 (전이학습으로 완화) |
| 자원 | 가볍다 | GPU 급 연산 |

22~24 강에서 쓴 "H 85~105, S≥60, V≥120" 같은 숫자가 바로 **사람이 만든 규칙**이다.

### 그 규칙은 얼마나 쉽게 깨지는가 — 직접 재 본 값 (`56`)

색 임계값은 **조명이 절반이 되는 것만으로** 마스크가 0 픽셀이 된다.

| 조건 | 공의 HSV | 검출 |
|---|---|---|
| 기준 | H95 S200 V230 | O |
| 밝기 x0.6 | H95 S200 V138 | O |
| **밝기 x0.5** | H95 S200 **V115** | **X** (V 하한 120) |
| 붉은 조명 | H89 S172 V200 | O |
| **더 붉은 조명** | **H81** S159 V200 | **X** (H 하한 85) |

흐릿하게 잡히는 게 아니라 **"아무것도 없음" 과 구분되지 않는다.**
실습에서 "아까는 됐는데 지금은 안 된다" 의 정체가 대개 이것이다.

Haar Cascade(23 강)도 같은 식으로 흔들어 봤다. 얼굴 두 개짜리 사진 기준:

| 축 | 결과 |
|---|---|
| 회전 | 0도 2개 / 10~15도 1개 / **20도 이상 0개** |
| 밝기 | x0.3 ~ x1.6 전부 2개 — **밝기에는 강하다** |
| 크기 | x1.5 3개 / x1.0 2개 / **x0.75 이하 0개** |
| 흐림 | blur 9~15 에서 3개 (오검출 증가) |

고개를 **20도만 기울여도** 얼굴이 사라진다. Haar 특징이 "정면 얼굴의 명암 패턴" 을 가정하기 때문이다.
반대로 밝기에는 강한데 명암의 **차이**를 보기 때문이다 — "조명·각도에 약하다" 는 축마다 정도가 다르다.

### 합성곱이 실제로 하는 계산 (`57`)

3x3 숫자판(커널)을 이미지에 밀면서 곱해 더한 결과가 **특징맵**이고, 값이 큰 자리 = 그 무늬가 강한 자리다.
커널마다 반응하는 것이 다르다 — 직접 그린 그림에서 영역별 평균 반응:

| 커널 | 세로 막대 | 가로 막대 | 원 |
|---|---|---|---|
| 세로 엣지 | **14.4** | 4.2 | 43.6 |
| 가로 엣지 | 5.1 | **21.3** | 49.9 |

`cv.filter2D(img, -1, kernel)` 한 줄이다. **CNN 이 다른 점은 이 아홉 개 숫자를 사람이 안 정한다**는 것뿐이다.
층을 쌓으면 엣지 → 엣지의 조합 → 부품 → 물체로 보는 단위가 커지고,
풀링(2x2 최댓값)은 크기를 절반으로 줄여 계산을 아끼고 위치 변화에 덜 민감하게 만든다.

대신 학습할 숫자가 많다. 작은 CNN 세 층만 세어도 **93,248 개**(3→32, 32→64, 64→128 채널)다.
손으로 고른 커널 네 개가 36 개였던 것과 비교하면, "대량의 데이터가 필요하다" 는 말의 크기가 보인다.

### 탐지기의 출력은 정답이 아니다 (`58`)

1 단계 검출기(YOLO·SSD)는 한 번의 순전파로 **후보 박스 수천 개**를 뱉는다. 쓸 수 있게 만들려면
① 신뢰도 임계값으로 거르고 ② **NMS** 로 겹친 박스를 정리한다. 둘 다 모델이 아니라 후처리라
모델 파일 없이도 그대로 해 볼 수 있다.

    IoU = 교집합 / 합집합      NMS = 점수 최고 박스를 남기고, 그것과 IoU 가 기준 이상인 것을 버린다

`58` 은 손으로 짠 NMS 와 `cv.dnn.NMSBoxes` 의 결과가 같은지 맞춰 본다(일치한다).
임계값을 바꾸면 결과가 이렇게 움직인다 — 후보 6 개(물체 3 개) 기준:

| score / nms | 0.1 | 0.4 | 0.9 |
|---|---|---|---|
| 0.3 | 3개 | 3개 | 6개 |
| 0.5 | 2개 | 2개 | 5개 |
| 0.9 | 1개 | 1개 | 1개 |

`cv.dnn` 모듈은 설치된 OpenCV 에 이미 있다. 없는 것은 **학습된 가중치 파일**뿐이고,
구하면 `readNet` → `blobFromImage` → `forward` → 위 후처리 네 단계로 붙는다.

### 모델 계보 (슬라이드 정리)

| 모델 | 시기 | 핵심 | ILSVRC Top-5 오류 |
|---|---|---|---|
| LeNet | 1998 | 합성곱+풀링+FC 구조를 정립 (손글씨) | — |
| AlexNet | 2012 | ReLU · Dropout · GPU 학습 | 약 15~16% |
| VGGNet | 2014 | 3x3 만 균일하게 깊게 | 약 7.3% |
| GoogLeNet | 2014 | Inception (여러 크기 병렬) + 1x1 | 약 6.7% |
| ResNet | 2015 | 잔차 연결로 100층 이상 | 약 3.57% |

(오류율은 자료마다 조금씩 다르게 적힌다 — 앙상블 등 측정 조건 차이다.)
탐지 쪽은 **2 단계**(R-CNN → Fast → Faster: 후보 영역 생성 후 분류, 정확하지만 느림)와
**1 단계**(YOLO·SSD: 한 번에 박스+클래스, 빠름)로 갈린다. 드론처럼 실시간 영상을 다루면 1 단계다.

## Pygame — 출력과 입력을 나눈다 (AR 의 뼈대)

28 강. (`59`~`61`) OpenCV 는 **입력**(카메라·분석), Pygame 은 **출력**(그리기·이벤트)을 맡는다.
영상 위에 도형과 글자를 얹으면 그게 곧 간단한 AR 화면이다.
세 파일 모두 `SOURCE = "demo"` / `MAX_SECONDS` 로 카메라 없이도 돌려 볼 수 있다.

```bash
pip install pygame       # venv 안에서. 확인한 버전 2.6.1 (SDL 2.28.4)
```

### 렌더링 루프는 네 줄이다

```python
for event in pygame.event.get():   # 1) 이벤트 — 안 꺼내면 창이 '응답 없음' 이 된다
    ...
screen.fill((0, 0, 0))             # 2) 뒤 버퍼에 그리기
pygame.display.flip()              # 3) 앞뒤 버퍼 교체 (더블 버퍼링)
clock.tick(30)                     # 4) 속도 제한
```

**더블 버퍼링** — 보이는 버퍼와 그리는 버퍼를 따로 두고 다 그린 뒤 통째로 바꾸므로
중간 과정이 보이지 않는다(깜빡임·찢어짐 없음). 일부만 바뀌면 `display.update(rect)` 가 싸지만
카메라 영상처럼 전체가 바뀌면 `flip()` 이 맞다.
`pygame.event.get()` 은 OS 이벤트 큐를 비우는 일도 한다 — 23 강의 `cv.waitKey()` 와 같은 자리다.

**`clock.tick()` 을 빼면 같은 그림을 미친 듯이 다시 그린다.** headless 로 재 보면
tick 없이 **1 초에 8,884 회**, `tick(30)` 이면 **29 회**. 보이는 결과는 같고 CPU 만 태운다.
강의 예제1 이 `clock` 을 만들어 놓고 `tick()` 을 안 부른다.

### 카메라 프레임 → Surface: 색과 축을 맞춘다

| 단계 | 하는 일 |
|---|---|
| `cap.read()` | `(높이, 너비, 3)` BGR 배열 |
| `cvtColor(..., BGR2RGB)` | Pygame 은 RGB 로 읽는다 |
| `make_surface(rgb.swapaxes(0, 1))` | `surfarray` 는 `(너비, 높이, 3)` = `[x][y]` 로 해석한다 |

축을 안 맞추면 **전치된다.** 가로로 긴 띠를 넣고 확인해 보면:

| | Surface 크기 | (x=100, y=10) | (x=10, y=100) |
|---|---|---|---|
| `swapaxes` 없이 | (480, 640) | 검정 | **빨강** (띠가 세로로 섰다) |
| `swapaxes(0, 1)` | (640, 480) | **빨강** | 검정 |
| `image.frombuffer` | (640, 480) | **빨강** | 검정 |

### 전치는 공짜가 아니다 — `frombuffer` 가 39배 빠르다

640x480 프레임 200 장 기준(변환 함수만):

| 방법 | 프레임당 | 초당 한계 |
|---|---|---|
| `make_surface` + `swapaxes` | 4.72 ms | 212 장 |
| `image.frombuffer` | **0.12 ms** | 8,177 장 |

BGR→RGB 까지 포함해 `60` 이 직접 찍은 값은 `frombuffer` 0.6 ms / `make_surface` 4.0 ms 였다.
30 fps 면 한 프레임에 33 ms 가 있으니 강의 방식으로도 충분하지만, 얼굴 인식(48)이나
색 추적(50)을 함께 돌리면 이 4 ms 가 아깝다. `60` 의 `SURFACE_MODE` 로 바꿔 가며 볼 수 있다.

### 강의 코드에서 고친 것

- **`import sys` 없이 `exit()` 호출.** `exit()` 는 대화형 셸용 헬퍼라 스크립트·주피터에서 불안정하다 → `sys.exit()`.
- **`clock.tick()` 누락** (위 참고). 순서도 "그리기 → flip → 이벤트" 대신 **이벤트 → 그리기 → flip → tick**.
- **종료 경로가 세 군데**(QUIT / ESC / break)라 `cap.release()` 를 빠뜨리기 쉽다 →
  `try/finally` 한 곳으로. 안 하면 **카메라 LED 가 켜진 채 남는다.**
- **과제 코드는 카메라 열기에 실패하면 창을 남긴다** — `pygame.init()` 으로 창을 띄운 뒤
  `pygame.quit()` 없이 `sys.exit()` 만 부른다. 먼저 닫고 끝내도록 고쳤다.
- 고정 문구는 루프 밖에서 한 번만 `render` 해 두고 `blit` 만 한다.
- **기본 폰트로 한글은 안 나온다.** `SysFont(None, 48)` 에는 한글 글리프가 없다 —
  macOS 는 `"applegothic"` 같은 시스템 폰트 이름을 주거나 `pygame.font.Font(경로, 크기)`.

## 객체 탐지 준비 — 사진을 창에 띄우고, YOLO 를 확인한다

29 강. (`62`, `63`) 이번 차시는 **모델을 로드만 하고 추론은 하지 않는다** —
다음 강의에서 이 화면 위에 탐지 결과를 그리기 위한 준비다.

### 레터박스 — 두 비율 중 작은 쪽

28 강은 프레임을 창 크기로 그냥 늘렸다. 사진은 비율을 지켜야 하므로:

```python
scale = min(창너비 / 원본너비, 창높이 / 원본높이)   # 큰 쪽을 쓰면 잘린다
```

810x1080 사진을 640x480 창에 넣으면 `min(0.790, 0.444) = 0.444` → **360x480**,
좌우로 140 픽셀씩 검은 여백이 남는다. 강의 코드는 `(0, 0)` 에 붙여 여백이 한쪽으로 몰리는데,
`((창너비 − 새너비) // 2, …)` 로 붙이면 가운데에 온다(`62` 의 `CENTER`).

**축 순서는 세 군데가 다 다르다** — 이미지가 눕거나 찌그러지는 원인의 대부분이다.

| | 순서 |
|---|---|
| `frame.shape` | (높이, 너비, 채널) |
| `cv.resize(…, (w, h))` | (너비, 높이) |
| `pygame.surfarray` | (너비, 높이, 채널) |

줄일 때 보간법은 `INTER_AREA` 가 깨끗하다(기본값은 `INTER_LINEAR`).
그리고 **정지 이미지는 루프 밖에서 한 번만** 그린다 — 루프는 이벤트만 받으면 된다(단 `clock.tick()` 은 넣는다).

### YOLO 를 붙이기 전에 알아 둘 것 (`63`)

```bash
pip install ultralytics      # torch 가 함께 딸려 온다 — 수백 MB 급
```

```python
model = YOLO("yolo11n.pt")   # 파일이 없으면 첫 실행 때 자동으로 내려받는다 (인터넷 필요)
results = model.predict(source="사진.jpg", save=True)
r = results[0]
for box in r.boxes:
    name = r.names[int(box.cls[0])]        # COCO 80종
    conf = float(box.conf[0])              # 신뢰도
    x1, y1, x2, y2 = box.xyxy[0].tolist()  # 좌상단·우하단
annotated = r.plot()                       # 박스가 그려진 **BGR** 배열 → 62 의 변환으로 그대로 띄운다
```

- ⚠️ **강의 자료 안에서 파일명이 갈린다** — 설명은 `yolov11n.pt`, 예제 코드는 `yolo11n.pt`.
  공식 표기는 **v 가 없는** `yolo11n.pt` 이고 예제 코드 쪽이 맞다.
- 크기는 `n`(nano) · `s` · `m` · `l` · `x` 순으로 정확해지고 느려진다. 노트북·드론 영상에는 **nano**.
- 작업은 파일명으로 고른다 — `-seg`(분할) `-pose`(자세) `-cls`(분류) `-obb`(회전 박스).
- **신뢰도 임계값과 NMS 는 여기서도 그대로다.** 58 에서 손으로 짠 후처리를 ultralytics 가
  내부에서 해 줄 뿐이다(`conf=`, `iou=` 인자).
- 설치 없이 가려면 ONNX 모델 + `cv.dnn`(58) — 전처리·후처리를 직접 짜야 한다.
- 받은 가중치(`*.pt`)와 결과 폴더(`runs/`)는 `.gitignore` 에 넣었다.

## 탐지 결과를 화면에 얹기 — 좌표는 어딘가에 매여 있다

30 강. (`64`) 62 가 띄운 그림 위에 박스와 라벨을 그린다.

```
imread -> 리사이즈 -> BGR2RGB -> Surface -> blit -> 추론 -> 박스·라벨 -> flip
```

### `box.xyxy` 는 "추론에 넣은 그림" 기준이다

원본(810x1080)으로 추론하고 화면에는 줄인 그림(360x480)을 띄우면 **박스만 2.25 배**가 되어
엉뚱한 자리에 간다. `64` 는 두 방식을 모두 넣고 화면 좌표가 같은지 확인한다.

| `INFER_ON` | 추론 입력 | 화면에 그릴 때 |
|---|---|---|
| `"resized"` (강의 방식, 권장) | 줄인 그림 | 그대로 |
| `"original"` | 원본 | **좌표 × scale** 을 해야 맞는다 |

직접 돌려 보면 두 방식의 화면 좌표가 같게 나온다(`bus 91% (166, 53)-(473, 391)`).
원본으로 추론하면 작은 물체를 더 잘 잡는 대신 느리다 — 어느 쪽이든 **좌표 변환을 빼먹지 않는 것**이 요점이다.
레터박스로 여백을 줬다면 `offset` 도 함께 더해야 한다.

### 라벨은 잘리고 묻힌다

- 객체가 맨 위에 있으면 `y1 - 20` 이 음수라 글자가 화면 밖으로 나간다 → `max(y1 - 글자높이, 0)`.
- 밝은 그림 위의 흰 글씨는 안 보인다 → `font.render(label, True, 글자색, **배경색**)` 로 칸을 깔아 준다.
- 박스는 `pygame.draw.rect(surface, 색, (x, y, **너비**, **높이**), 두께)` — `xyxy` 를 그대로 넣으면 안 되고
  `x2 - x1`, `y2 - y1` 로 바꿔야 한다.

### 강의 자료 사이에서 모델이 다르다

29 강은 `yolo11n.pt`(YOLO11), 30 강은 `yolov8n.pt`(YOLOv8) 를 쓴다. API 가 같아 둘 다 돌아가지만
**가중치를 두 번 받게 된다** — 하나로 맞추는 편이 낫다.
`conf=` 는 신뢰도 임계값, `iou=` 는 NMS 임계값이다. 58 에서 손으로 짠 후처리를 인자로 여는 것뿐이다.

### 설치 없이 확인하기

`DETECTOR = "demo"` 면 고정 박스로 **좌표 변환·그리기·라벨 처리만** 확인할 수 있다
(ultralytics 는 torch 까지 딸려 와 무겁다 — 63 참고). demo 박스는 인식 결과가 아니라
화면에 제대로 얹히는지 보는 용도다.

## 실시간 추론과 가리기 — 매 프레임 도는 루프

31 강. (`65`, `66`) 64 는 사진 한 장이었고, 이제 **매 프레임** 추론한다.
구조는 60(영상 출력)과 같고 `blit` 과 `flip` 사이에 추론과 그리기가 들어갈 뿐이다.

```
read -> BGR2RGB -> Surface -> blit -> 추론 -> 박스·라벨 -> FPS -> flip -> tick
```

### ⚠️ 모델에는 RGB 가 아니라 원본 BGR 을 넘긴다

화면용으로 만든 `frame_rgb` 를 그대로 추론에 넣기 쉬운데, **ultralytics 는 numpy 입력을 BGR 로 간주한다.**
RGB 를 넣으면 색이 뒤집힌 그림으로 추론하는 셈이다. 화면 변환과 추론 입력을 분리해 둘 것.
(강의·ultralytics 문서 기준이고, 모델이 없어 직접 재 보지는 못했다.)

### FPS 가 30 에 못 미치면 추론이 병목이다

`clock.tick(30)` 으로 상한을 걸었으니 `clock.get_fps()` 가 곧 추론 속도의 지표가 된다.
GPU 없는 노트북에서 5~10 이 나오는 건 정상이다. 줄이는 수단:

| 방법 | 효과 |
|---|---|
| `classes=[0]` | 사람만 찾는다 — 가리는 게 목적이면 나머지 79종은 볼 이유가 없다 |
| `conf=0.5` | 임계값을 올려 후보를 줄인다 |
| `INFER_EVERY = 2` | 두 프레임에 한 번만 추론하고 결과를 재사용 |
| `imgsz=320` | 입력 해상도를 줄인다 (작은 물체는 놓친다) |

### 과제의 핵심은 `width` 인자 하나다

```python
pygame.draw.rect(surface, color, rect, width=0)   # width 는 테두리 두께, 0(기본) = 채우기
```

직접 재 보면 **두께를 생략하면 사각형 안쪽 픽셀이 `(0,0,0)`** 이 되고, `width=2` 면 안쪽은 원래 색 그대로다.
사람이면 두께를 빼고, 아니면 2 를 준다 — 그게 과제의 전부다.

가리는 방법 셋을 넣고 확인했다:

| 모드 | 방법 | 확인한 값 |
|---|---|---|
| `fill` | `draw.rect` 두께 없이 | 안쪽이 완전히 덮인다 |
| `alpha` | `Surface(..., pygame.SRCALPHA)` + `fill((0,0,0,180))` | 흰 배경 위에서 **75** = 255 × (1 − 180/255) — 뒤가 비친다 |
| `mosaic` | 그 영역만 8x8 로 줄였다가 `INTER_NEAREST` 로 확대 | 15x15 블록 안이 모두 같은 값 |

**`mosaic` 만 Surface 로 바꾸기 전에** 처리해야 한다 — pygame 으로 덮는 게 아니라 프레임 자체를 고치는 것이다.
박스가 사람에 딱 붙으면 머리카락·어깨가 삐져나오므로 `PAD` 만큼 넓혀 덮되, 화면 밖으로 나가지 않게 자른다.

### 강의 코드에서 고친 것

- **`cap.release()` 가 없다.** 안 하면 다음 실행에서 카메라가 "사용 중" 으로 안 열린다 → `try/finally`.
- 6 단계 슬라이드의 라벨이 `Conf: {model.names[cls]}%` 라 **`Conf: person%`** 가 찍힌다 →
  클래스 자리에 이름, Conf 자리에 신뢰도.
- 라벨이 화면 위로 잘린다(`y1 - 20` 이 음수) → `max(y1 - 글자높이, 0)`.
- 카메라가 640x480 을 못 주면 좌표가 어긋난다 → 받은 프레임 크기를 확인해 맞춘다.
- 같은 `(255, 0, 0)` 이 **pygame 에서는 빨강, OpenCV 에서는 파랑**이다. 섞어 쓰면 색이 뒤집힌다.
- 캡처 파일(`capture_*.png`)은 `.gitignore` 에 넣었다.

## 사물 추적 — 프레임 사이를 잇는다

32 강. (`67`, `68`) 탐지와 추적의 차이는 한 줄이다.

    탐지  이 프레임에 무엇이 어디 있는가
    추적  + **이전 프레임의 그 물체와 같은 물체인가** (같으면 같은 ID)

매 프레임 탐지하고 그 결과를 이전 것과 짝지어 ID 를 잇는 방식이 **Tracking-by-Detection** 이다.

| 단계 | 하는 일 |
|---|---|
| 예측 | 이전 물체가 이번엔 어디쯤 있을지 (칼만 필터) |
| 매칭 | 예측 위치와 새 박스의 IoU 가 가장 큰 쌍을 연결 (헝가리안 알고리즘) |
| 발급 | 짝이 없는 새 박스에는 새 ID |
| 소멸 | 몇 프레임 이상 안 보이면 목록에서 지운다 |

**같은 IoU 계산이 한 프레임 안에서는 NMS(58), 프레임 사이에서는 추적에 쓰인다.** 같은 도구, 다른 축.

### 30 줄짜리 트래커로 재현되는 두 가지 사고 (`67`)

예측을 "직전 위치 그대로" 로 대신하고 탐욕적으로 매칭하는 최소 트래커로도 교과서적 실패가 그대로 나온다.

| 실험 | 결과 |
|---|---|
| A. 한 물체가 이동 | ID 유지 |
| B. 두 프레임 탐지가 끊김 | `MAX_AGE=2` → ID 유지 / **`MAX_AGE=0` → 새 ID** |
| C. 두 물체가 교차 | 스치는 **frame 7 에서 ID 가 뒤바뀐다** (ID Switch) |

B 가 강의의 경고와 같다 — `conf` 를 0.7 로 높이면 탐지가 자주 끊겨 ID 가 더 자주 바뀐다.
C 는 위치(IoU)만 보고 이었기 때문이다. 겹치는 순간에는 어느 쪽이 어느 쪽인지 구분할 근거가 없다 →
진짜 트래커는 **속도(어디로 가던 중이었나)** 를 함께 본다. 그게 칼만 필터의 역할이다.
IoU 매칭은 빠른 물체에도 약하다 — 폭 60 박스가 한 프레임에 40 픽셀 움직이면 IoU 가 0.2 라 매번 새 ID 다.

### 실습 코드에서 바뀌는 건 함수 하나 (`68`)

```python
model(frame, ...)                       # 탐지만 — 매 프레임 남남
model.track(frame, persist=True, ...)   # ID 까지. persist 를 빼면 매 프레임 ID 가 초기화된다
```

| 옵션 | 뜻 |
|---|---|
| `persist=True` | 이전 프레임의 추적 상태를 유지 — **이 강의의 핵심 옵션** |
| `tracker="botsort.yaml"` | 기본값. 카메라 움직임 보정까지, 정확도 쪽 |
| `tracker="bytetrack.yaml"` | 신뢰도 낮은 박스까지 활용, 가볍고 빠른 쪽 |
| `classes=[0]` | 사람만 추적 (드론 Follow-me 응용) |

- **`box.id` 는 `None` 일 수 있다**(추적 확정 전) → `int(box.id[0]) if box.id is not None else -1`.
  변수 이름도 `id` 대신 `track_id` — `id()` 는 파이썬 내장 함수다.
- **거울 모드는 탐지 전에.** 그리기 직전에 뒤집으면 추론은 뒤집기 전 그림으로 돌아 박스가 좌우로 어긋난다.
- **라벨 버그**: `conf = int(box.conf[0] * 100)` 로 정수를 만든 뒤 `f"{conf:.2f}"` 를 쓰면 **`87.00`** 이 찍힌다.
  `f"{0.87:.0%}"` → `"87%"` 가 의도한 모양이다.
- 궤적은 ID 별 중심점을 `deque(maxlen=30)` 에 모아 `pygame.draw.lines` 로 잇는다
  (`maxlen=3` 에 0~4 를 넣으면 `[2, 3, 4]`). **궤적이 끊기는 지점이 곧 ID 가 바뀐 지점**이다.

`DETECTOR = "demo"` 면 설치 없이 돈다 — 합성 영상에서 두 물체가 서로를 지나가고, 색 검출 + 67 의
트래커로 ID 를 붙인다. 5 초(142 프레임)를 돌리면 물체는 둘인데 **발급된 ID 는 셋** —
가운데서 스치며 한 번 갈아 끼워졌다는 뜻이다. YOLO 를 붙여도 같은 일이 일어난다.

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
| `sendControlPosition` 이 아무 반응 없음 | `heading`/`rotationalVelocity` 에 float — 앞 네 개는 float 이 되는데 이 둘만 int 전용 | 정수로 (`-90.0` → `-90`) |
| `sendControlPosition16` 이 아무 반응 없음 | 여섯 값 중 하나가 float (`velocity=0.5` 등) | 전부 ×10 한 정수로 (`0.5 m/s` → `5`) |
| 1 m 만 가라고 했는데 10 m 를 감 | 슬라이드의 "거리 100 이 1미터" 오탈자 | `1 m = 10`. 위치 명령은 **범위 검사가 없어 에러도 안 난다** |
| 오른쪽으로 가라니 왼쪽으로 감 | `positionY` 는 좌 + / 우 − | 오른쪽은 음수. `heading` 도 우회전이 음수 |
| 이동 도중에 착륙해 버림 | 위치 명령은 비블로킹인데 대기를 안 줌 | 거리 ÷ 속도 + 여유 2~3초 |
| 두 이동이 겹쳐 대각선으로 감 | 앞 명령이 끝나기 전에 다음 명령이 덮어씀 | 위와 같음 |
| `sendFlightEvent(0x18)` 이 무반응 | int 를 넘김 — `isinstance(FlightEvent)` 검사에 걸림 | `FlightEvent.Return` |
| 사각형이 출발점에서 어긋남 | 네 변의 이동 오차가 누적 | 마지막에 리턴홈을 한 번 넣는다 |
| 바닥에 닿았는데 모터가 계속 돔 | `sendControlWhile` 하강이 남은 시간 동안 계속 전송 | 낮은 고도면 시간을 줄이거나 하방 센서로 판단(23) |
| Ctrl+C 대신 창을 닫았더니 계속 낢 | 파이썬만 죽고 드론은 마지막 명령을 유지 | Ctrl+C 로 빠져나와 `finally` 의 착륙을 태운다 |
| 장애물을 감지했는데 루프가 안 끝남 | 콜백에서 `global` 누락 — 대입이 지역 변수를 만든다. 에러도 안 난다 | 함수 첫 줄에 `global`. 착륙한 뒤에도 전진 명령이 계속 나가고 있었다 |
| `NameError: name 'value' is not defined` | 콜백은 `isDetected`, 메인 루프는 `value` 를 검사(복사 흔적) | 변수 통일. `except KeyboardInterrupt` 에 안 잡혀 **드론이 공중에 남고 연결만 끊긴다** → `finally` 에 착륙 |
| 장애물 앞을 그냥 지나침 | 감지 구간 `300 < front < 400` 이 좁아 빠르면 건너뛴다 | `0 < front < 400` (0 은 측정 실패라 제외) |
| 회피 중 센서값이 밀리고 명령이 겹침 | 콜백(수신 스레드) 안에서 `sleep(2)` + 이동·착륙까지 처리 | 콜백은 플래그만, 명령은 메인 루프에서 한 번 |
| 장애물 위치에 따라 착륙 지점이 매번 달라짐 | `sendControl` 로 전진하면 **간 거리를 모른다** | 감시 구간을 위치 명령으로 끊어 가며 `traveled` 를 센다 |
| 회피한 뒤 후진하다 그 장애물에 다시 부딪힘 | 넘어간 자리에서 바로 보정 | 옆으로 빠져나온 뒤의 구간에서 보정한다 |
| `TypeError: takes 7 positional arguments but 8 were given` | 슬라이드의 `sendControlPosition16(0, 0, 3, 0, 5, 0, 0)` — 인자가 7개 | `(0, 0, 3, 5, 0, 0)`. 위치 명령에서 **예외가 나는 드문 경우**다 |
| 세기 전진 뒤 거리 이동이 엉뚱하게 나감 | 앞의 `sendControl` 전진 명령이 아직 살아 있다 | `sendControl(0,0,0,0)` 으로 끊고 0.5초 (관성) |
| 거리를 줄였더니 드론이 제자리에 머묾 | 속도 0.1 m/s·조각 0.05 m — 위치 명령 권장 속도(0.5~2.0) 아래 | 거리만 줄이고 속도는 유지. 막아 주지 않으니 에러도 안 난다 |
| 전원 버튼을 눌렀는데 미션이 출발함 | 모든 버튼을 출발 신호로 봄 | `ButtonFlagController.TopRight`(0x0020) 제외 + `ButtonEvent.Down` 만 |
| 하방 감지가 안 되거나 이륙하자마자 착륙 | `rangeHeight` 는 m 인데 mm 기준값을 넣음 / 호버링 높이를 안 재고 예시값 0.3~0.4 를 그대로 씀 | 21 번으로 이륙 후 `rangeHeight` 를 먼저 찍고 **호버링 높이 − 상자 높이 + 여유** 로 정한다 |
| `ModuleNotFoundError: No module named 'opencv'` | 설치 이름(`opencv-python`)과 모듈 이름(`cv2`)이 다름 | `import cv2 as cv` |
| `imshow` 를 불렀는데 창이 안 뜨거나 회색으로 멈춤 | 창은 `waitKey()` 안에서 그려진다 | `imshow` + `waitKey(0)` + `destroyAllWindows()` 세 줄 묶음 |
| 경로를 고쳤는데도 뒤에서 엉뚱한 에러 | `imread` 는 실패해도 예외 없이 `None` 만 돌려준다 | 읽은 직후 `is None` 검사 |
| `cv.imread('C:\image\drone.jpg')` 가 없는 경로를 찾음 | `\i` 등이 이스케이프로 해석됨 | raw 문자열 `r'...'` 또는 `/` 사용 |
| matplotlib 으로 그렸더니 파랑↔빨강이 뒤바뀜 | OpenCV 는 BGR 순서로 저장한다 | `cv.cvtColor(img, cv.COLOR_BGR2RGB)` |
| 흑백 이미지가 알록달록하게 나옴 | matplotlib 기본 컬러맵이 적용됨 | `plt.imshow(gray, cmap='gray')` |
| OpenCV 를 깔았는데 버전이 슬라이드와 다름 | 슬라이드 `4.4.0` 은 촬영 당시 값 | 정상. `cv.__version__` 이 찍히면 설치 성공 |
| 빨간색을 찾았는데 절반만 검출됨 | H 에 음수가 없어 `0-10 ~ 0+10` 이 사실상 `0~10` 이다 | `0~10` + `170~179` 두 마스크를 `bitwise_or` (실측 1.91 배) |
| `H - 10` 을 했는데 246 이 나옴 | `uint8` 은 음수가 없어 아래로 넘친다 | `int(h) - 10` 으로 계산 |
| 흰 배경·회색까지 빨강으로 잡힘 | 무채색도 H 가 0 이다 | 하한에 `S>=30, V>=30` 을 함께 건다 |
| `cvtColor` 에서 에러 | 색 하나를 `[[[0,0,255]]]` 로 넘기며 `np.uint8` 을 빠뜨림 | `np.uint8([[bgr]])` — int64 는 못 받는다 |
| 템플릿 매칭이 엉뚱한 곳을 가리킴 | 대상이 없어도 가장 덜 다른 자리를 돌려준다 | `TM_CCOEFF_NORMED` + `maxVal > 0.8` 기준값 |
| 학습자료 이미지로 드론을 못 찾음 | 개별 png 가 전체 사진의 잘라낸 조각이 아니다(크기·각도가 다름) | 크기 탐색으로 일부만 찾힘. 각도가 다르면 그래도 실패 |
| `cv.error: ... template` | 템플릿이 장면보다 큼 | 점수 배열 크기가 `장면 - 템플릿 + 1` 이라 성립 불가. 템플릿을 줄인다 |
| 매칭 점수는 높은데 위치가 틀림 | 무늬 없는 단색 배경 — 어디에 대도 똑같이 맞는다 | 실제 사진처럼 무늬가 있어야 한다(`42` 가 얼룩을 입히는 이유) |
| `AttributeError: module 'cv2' has no attribute 'CascadeClassifier'` | OpenCV 5.0 에는 분류기도 xml 도 없다 | `pip install --only-binary=:all: "opencv-python<5"` |
| `imshow` 에서 이상한 에러 | 카메라 권한이 없어 `frame` 이 `None` | `ret` 을 먼저 확인 — `if not ret: break` |
| 다음 실행에서 카메라가 안 열림 | 앞 실행이 `release()` 없이 죽어 장치를 물고 있다 | `try/finally` 로 `cap.release()` |
| 저장한 영상이 재생이 안 됨 (44 바이트) | `writer.release()` 누락 — 파일 끝 정보가 안 써진다 | `finally` 에서 release |
| 저장 파일이 257 바이트에 0 프레임 | 저장 크기와 프레임 크기가 다름 | 크기는 카메라에서 읽은 값으로. 에러가 안 난다 |
| `VideoWriter` 가 안 열림 | 맥 카메라가 `CAP_PROP_FPS` 를 0 으로 돌려줌 | 0 이면 30 같은 기본값으로 대체 |
| 녹화 영상이 빨리 감기처럼 재생됨 | 실제 처리 속도보다 높은 fps 로 저장 | 측정한 FPS 를 저장 fps 로 |
| 해상도를 640x480 으로 바꿨는데 그대로 | `set()` 은 요청일 뿐, 파일 소스에는 무시된다 | `get()` 으로 실제 값 확인 |
| 얼굴이 하나도 안 잡힘 | `minSize` 가 화면 속 얼굴보다 큼 | 먼저 `minSize` 를 낮춘다(실측: 80→0개, 50→2개) |
| 눈이 엉뚱한 곳에 잡힘 | 화면 전체에서 눈을 찾음 | 얼굴을 먼저 찾고 그 안(위쪽 절반)에서만 |
| 창을 X 로 닫았는데 프로그램이 안 끝남 | 키 입력만 확인하는 루프 | `getWindowProperty(...) < 1` 도 같이 검사 |
| `q` 를 눌러도 종료가 안 됨 | 한글 입력 상태라 `ㅂ` 이 들어감 | 영문 상태에서, 영상 창에 포커스를 준 뒤 |
| 빨강을 골랐더니 마스크가 전부 검정 | `uint8` 뺄셈이 넘쳐 `H 하한`이 246 이 됨 | `int()` 로 계산 + 빨강은 두 구간 |
| 프로그램을 켜자마자 드론이 뜸 | `height = 0` 초기값이 이륙 조건(`< 300`)을 만족 | 키로만 이륙하게 하거나 초기값을 화면 아래로 |
| 공을 치웠는데 계속 그 방향으로 감 | 좌표 변수가 마지막 값을 유지 | 못 찾으면 잠깐 뒤 `sendControl(0,0,0,0)` |
| 가운데로 옮겨도 안 멈춤 | 가운데에서 아무 명령도 안 보냄 → 마지막 명령 유지 | 정지 영역에서 0 을 보낸다 |
| 오른쪽으로 옮겨도 반응이 없음 | 슬라이드의 `500 < height < 600` — 화면 높이가 480 | 축이 뒤바뀐 실수. `width` 로 판단 |
| 이동 명령이 먹지 않음 | 매 루프 `sendControl(0,0,0,0)` 이 바로 덮어씀 | 정지 명령은 가운데일 때만 |
| 좌우가 반대로 움직임 | 거울 반전 여부 + 드론이 향한 방향 | `MIRROR` 를 정하고 낮은 세기로 부호부터 확인 |
| `too many values to unpack` | `findContours` 반환값이 3.x 는 3개, 4.x 는 2개 | `contours, _ = ...` |
| 같은 색 물건이 둘인데 엉뚱한 걸 따라감 | `for` 루프가 마지막 윤곽선으로 덮어씀 | `max(contours, key=cv.contourArea)` |
| 군집인데 한 대만 움직임 | `open()` 을 인자 없이 불러 두 객체가 같은 포트를 잡음 | 포트를 명시하고 반환값 확인 |
| 코드의 drone1 이 엉뚱한 자리의 드론 | 포트 이름 숫자는 꽂는 자리에 따라 바뀐다 | 이륙 전에 LED 를 하나씩 켜서 짝 확인 |
| "3초 호버링" 인데 12초가 걸림 | `sendControlWhile` 이 블로킹 — 대수만큼 곱해진다 | 이동은 `sendControlPosition` 으로 |
| 좌우로 벌리랬더니 서로 부딪힘 | `y+` 가 왼쪽인데 배치가 반대 | 배치와 부호를 함께 확인 |
| 패턴을 반복할수록 대형이 밀림 | 위치 명령은 "지금 위치에서 얼마" 다 | 수행 뒤 부호를 뒤집어 원위치 |
| 조종기가 4대인데 포트가 3개만 보임 | 충전 전용 케이블 / 허브 인식 불량 | 데이터 케이블 + 전원 공급형 허브. `find_ports(4)` 가 개수를 확인해 준다 |
| 어제는 되던 색 인식이 오늘은 안 됨 | 조명이 바뀌어 S·V 하한에 걸림 (실측: 밝기 x0.5 면 0픽셀) | 그 자리에서 다시 튜닝. 근본 해결은 학습 기반 |
| 고개를 돌렸더니 얼굴이 안 잡힘 | Haar 는 정면 명암 패턴 가정 — 20도면 0개 | 각도 제한을 알고 쓰거나 CNN 검출기로 |
| 한 물체에 박스가 여러 개 | 탐지기 출력은 후보 박스 수천 개다 | 신뢰도 임계값 + `cv.dnn.NMSBoxes` |
| NMS 를 했는데 붙어 있는 두 물체가 하나로 | NMS 임계값이 너무 낮다 | 임계값을 올린다(장면마다 다르다) |
| Pygame 창이 '응답 없음' | 루프에서 `pygame.event.get()` 을 안 부름 | 매 프레임 이벤트를 꺼낸다 |
| 영상이 90도 돌아가고 찌그러짐 | `surfarray` 는 `[x][y]` 로 읽는다 | `rgb.swapaxes(0, 1)` 또는 `image.frombuffer` |
| 파랑과 빨강이 뒤바뀜 | OpenCV 는 BGR, Pygame 은 RGB | `cvtColor(..., COLOR_BGR2RGB)` |
| 아무것도 안 하는데 CPU 가 100% | `clock.tick()` 누락 — 초당 8,884회 루프 | `clock.tick(30)` |
| 종료했는데 카메라 LED 가 켜져 있음 | 종료 경로에서 `cap.release()` 누락 | `try/finally` 로 모은다 |
| 한글 메시지가 네모로 나옴 | 기본 폰트에 한글 글리프가 없다 | 시스템 폰트 지정(macOS `applegothic`) |
| 주피터에서 셀이 끝났는데 창이 남음 | `pygame.quit()` 미호출 | `finally` 에서 호출 |
| 사진이 창에서 잘림 | 두 비율 중 **큰** 쪽으로 줄였다 | `min(ratio_w, ratio_h)` |
| 여백이 한쪽으로 몰림 | `(0, 0)` 에 붙였다 | `((W-w)//2, (H-h)//2)` 로 가운데 정렬 |
| 줄인 사진이 지저분함 | 기본 보간 `INTER_LINEAR` | 축소는 `INTER_AREA` |
| `yolov11n.pt` 를 못 찾음 | 공식 표기는 `yolo11n.pt` (v 없음) | 강의 자료 안에서도 갈린다 — 예제 코드 쪽이 맞다 |
| 첫 실행이 오래 걸림 | 가중치를 자동으로 내려받는 중 | 인터넷 필요. 받은 `.pt` 는 실행 폴더에 생긴다 |
| 박스가 물체보다 크게·엉뚱한 곳에 그려짐 | 원본으로 추론하고 줄인 그림에 그렸다 | 줄인 그림으로 추론하거나 좌표에 scale·offset 적용 |
| 박스가 이상한 모양으로 그려짐 | `draw.rect` 는 `(x, y, 너비, 높이)` | `xyxy` 를 `x2-x1`, `y2-y1` 로 변환 |
| 라벨 글자가 화면 위로 잘림 | `y1 - 20` 이 음수 | `max(y1 - 글자높이, 0)` |
| 밝은 배경에서 라벨이 안 보임 | 흰 글자 + 밝은 그림 | `font.render(..., 글자색, 배경색)` |
| 가중치를 두 번 받음 | 29강 `yolo11n.pt` / 30강 `yolov8n.pt` | 한 파일로 맞춘다 |
| 다음 실행에서 카메라가 안 열림 | 종료 경로에서 `cap.release()` 누락 | `try/finally` 로 보장 |
| 라벨에 `Conf: person%` 가 찍힘 | 슬라이드가 클래스 이름을 Conf 자리에 넣었다 | 이름과 신뢰도 자리를 바로잡는다 |
| 사람을 가렸는데 가장자리가 보임 | 박스가 대상에 딱 붙어 나온다 | `PAD` 만큼 넓히고 화면 밖은 자른다 |
| 반투명이 안 되고 그냥 까맣게 덮임 | 알파를 쓰려면 `SRCALPHA` Surface 가 필요하다 | `pygame.Surface(크기, pygame.SRCALPHA)` |
| 모자이크가 화면에만 적용되고 저장본엔 없음 | 프레임이 아니라 화면에 그렸다 | 모자이크는 Surface 변환 **전에** 프레임을 고친다 |
| 추론을 켜니 FPS 가 뚝 떨어짐 | 매 프레임 전체 클래스 추론 | `classes=[0]` · `INFER_EVERY` · `imgsz` 조절 |
| ID 가 매 프레임 새로 매겨짐 | `model.track(...)` 에 `persist=True` 누락 | 추적의 핵심 옵션이다 |
| `int(box.id)` 에서 에러 | 추적 확정 전이면 `box.id` 가 `None` | `int(box.id[0]) if box.id is not None else -1` |
| 라벨에 `87.00` 이 찍힘 | 정수 `conf` 에 `:.2f` | float 로 두고 `:.0%` |
| 박스가 좌우로 어긋남 | 그리기 직전에 `flip` 해서 추론은 원본으로 돌았다 | 탐지 **전에** 뒤집는다 |
| 가려졌다 나타나면 ID 가 바뀜 | 탐지가 끊긴 사이 매칭이 끊긴다 | `conf` 를 낮추거나 트래커의 대기 프레임을 늘린다 |
| 두 사람이 스칠 때 ID 가 서로 바뀜 | 위치만으로는 구분 불가 (ID Switch) | 트래커의 고질병 — 칼만 필터가 속도를 함께 본다 |

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

**실제로 이륙하는 파일은 `23` `24` `27`~`38` `51`~`55` 열아홉 개다.**
(`21_sensor_altitude.py` 는 `TAKEOFF = True` 로 바꿨을 때만.) 나머지는 전부 책상 위에서 돌아간다.
`23`/`24` 는 이륙 전 3초 카운트다운을 찍고, `27`~`29` 는 `1` 키를 눌러야 뜨며,
`30`~`37` 은 **실행하는 순간 바로 이륙한다** — 자율 비행이라 시작 신호가 따로 없다.
`38` 만 예외로 조종기 버튼을 눌러야 출발한다(과제 조건).
`51`/`52` 는 `t` 키를 눌러야 뜨고, `space` 가 비상 정지(모터를 끄므로 **그 자리에서 떨어진다**)다.
`53`~`55` 는 드론 2~4 대를 동시에 띄운다 — 간격 2 m 이상, 천장 높이, 배터리 전량 확인.
열아홉 개 모두 `Ctrl+C` 로 중단하면 `finally` 의 착륙 명령이 나간다.
창을 그냥 닫으면 파이썬만 죽고 드론은 마지막 명령을 유지하므로 반드시 `Ctrl+C` 로 끝낼 것.
`29` 는 `SIMULATION = True`, `51`~`55` 는 `DRY_RUN = True` 로 두면 드론 없이 확인할 수 있다
(`SOURCE = "demo"` 까지 주면 카메라도 필요 없다).
`30`~`38` 은 이동 거리·속도를 상수로 빼 뒀다 — 좁은 곳에서는 `DIST_M`/`SIDE_M` 을 0.5 로 줄이고,
`38` 은 `ROOM = "NARROW"` 로 바꾼다(속도는 줄이지 말 것).
한 변 1 m 짜리 패턴 비행(`34`)은 최소 2 m × 2 m, 과제(`38`)는 앞뒤 약 3 m × 좌우 2 m 가 필요하다
(`NARROW` 는 앞뒤 1.5 m × 좌우 1 m).
`36`~`38` 은 센서를 보고 멈추므로 **경로에 장애물 말고 다른 물체가 없어야 한다** —
가방·의자 다리도 그대로 장애물·목적지로 인식된다.
손은 프로펠러에 닿지 않게 **아래쪽 / 정면에서 천천히** 넣을 것.
