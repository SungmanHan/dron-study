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
