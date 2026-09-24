r"""75. [과제] Drone AR Game — 미사일 피하기 📷

36 강 과제. 웹캠에 비친 드론을 **클릭(SAM)** 하거나 **드래그**해서 고르면 추적기가 따라가고,
화면 가장자리에서 유도 미사일이 날아온다. **충돌하지 않고 버틴 시간이 곧 점수**다.

    SOURCE  = "demo"  카메라 없이 움직이는 합성 드론으로 게임이 돈다 (기본값)
    SOURCE  = 0       웹캠
    USE_SAM = False   SAM 없이 드래그로만 선택 (느린 PC / 미설치 환경)
    클릭·드래그 = 대상 선택 / SPACE = 시작·재개 / R = 재시작 / ESC = 종료

[상태]
    SELECT ──(선택)──> READY ──SPACE──> PLAY ──(피격)──> OVER ──R──> READY
                                          │ ▲
                                 (추적 놓침) ▼ │ (재선택 후 SPACE)
                                        PAUSED

[점수 — 과제의 핵심]
    delta_tick = clock.tick(fps)   # 직전 프레임 이후 실제로 흐른 ms
    dt = min(delta_tick / 1000, MAX_DT)
    if state == "PLAY": elapsed_ms += dt * 1000

⚠️ 원본은 점수에 `delta_tick`(자르지 않은 값), 물리에 `dt`(0.1 초에서 자른 값)를 썼다.
10 fps 밑에서는 **세계가 느려지는데 점수는 그대로 올라** 느린 PC 가 유리해진다
(8 fps 에서 세계 진행 80%, 5 fps 에서 50% — 74 에서 잰 값).
여기서는 **둘 다 `dt`** 로 맞췄다. 점수 의미는 그대로 "버틴 초" 다.

[⛔ 추적 실패를 감지해야 게임이 성립한다]
이 환경의 추적기는 `TrackerMIL` 인데(CSRT 는 contrib 전용 — 72 참고),
**물체를 완전히 놓친 뒤에도 `update()` 가 계속 `True` 를 돌려준다**(72 에서 119/119 프레임 실측).
그러면 드론 박스가 허공에 멈춘 채 미사일이 그리로 모여들어, 플레이어는 조종간을 쥐고도
아무것도 못 하면서 점수만 쌓인다. 그래서 73 과 같은 **색 히스토그램 가드**로 놓침을 판정하고
`PAUSED` 로 넘어간다 — 점수도 함께 멈춘다.

[게임 균형 — 74 에서 잰 것]
- `MISSILE_TURN_RATE`(100°/s)는 **무제한 선회와 결과가 같다.** 회피를 가르는 건 속도비다.
  어렵게/쉽게 하려면 `MISSILE_SPEED_*` 를 만지는 편이 직접적이다(30°/s 부근부터 선회 제한이 일한다).
- 속도가 `90 + 4t` 로 올라 220 에서 멈추므로 **32.5 초부터는 속도로 피할 수 없다.**
- `HITBOX_SCALE = 0.7` 은 한 변 70% = **면적 49%**. 박스에 섞인 배경을 보정하는 값이다.

[원본에서 고친 것]
1. 점수/물리 `dt` 통일 (위)
2. 추적 놓침 판정 — `update()` 의 `success` 만으로는 영영 안 걸린다
3. `create_tracker()` 가 CSRT → KCF → MIL 순으로 **있는 것**을 고른다
4. `DroneLed` — `drone.open(None)` 은 **자동 탐색이 아니다.** 라이브러리 기본값이 문자열
   `"None"` 이라 파이썬 `None` 은 그 분기를 타지 않는다. 예외도 안 나고 `False` 만 돌아와
   원본은 연결이 안 된 채 "드론 LED 연결 OK" 를 찍는다 → `drone_util.find_port()` + 반환값 확인
5. `make_surface(swapaxes)` → `image.frombuffer` (28 강에서 4.72 ms vs 0.12 ms)
6. SAM 마스크는 여러 후보 중 **클릭한 점을 포함하는 것**을 고르고 해상도를 맞춘다(71)
7. 카메라 없이도 돌도록 `SOURCE = "demo"`
"""

import math
import random
import sys
import time

import cv2 as cv
import numpy as np
import pygame

SOURCE = "demo"  # "demo" / 0 (카메라) / "파일경로"
USE_SAM = False  # True: 클릭 -> SAM 분할 (ultralytics 필요)
SAM_MODEL = "sam2_t.pt"
USE_DRONE_LED = False  # True: 게임 상태를 드론 LED 로 (조종기 USB 연결 필요)
DRONE_PORT = None  # None 이면 drone_util.find_port() 로 찾는다

WIDTH, HEIGHT = 640, 480
FPS = 30
MAX_DT = 0.1  # 한 프레임 순간이동 방지
MIN_BOX = 10  # 이보다 작은 박스로는 추적기를 초기화하지 않는다

MISSILE_RADIUS = 7
MISSILE_SPEED_START = 90.0  # px/s
MISSILE_SPEED_MAX = 220.0
MISSILE_SPEED_UP = 4.0  # 1 초마다 빨라지는 양
MISSILE_TURN_RATE = math.radians(100)  # 초당 최대 선회각 (74: 사실상 무제한과 같다)
MISSILE_LIFETIME = 7.0  # 초
SPAWN_INTERVAL_START = 2.5  # 생성 간격(초)
SPAWN_INTERVAL_MIN = 0.7
HITBOX_SCALE = 0.7  # 한 변 70% = 면적 49%

LOST_TH = 0.5  # 히스토그램 유사도 임계 (73 과 같다)
LOST_K = 5  # 연속 몇 프레임 미달이면 놓침
MAX_SECONDS = 0  # 0 = 무제한

TRACKER_ORDER = ["TrackerCSRT_create", "TrackerKCF_create", "TrackerMIL_create"]


# ---------------------------------------------------------------- 추적
def create_tracker():
    """이 환경에서 만들 수 있는 추적기. CSRT 는 contrib 에만 있다 (72 참고)."""
    for name in TRACKER_ORDER:
        factory = getattr(cv, name, None)
        if factory is None:
            continue
        try:
            return factory(), name
        except cv.error:  # 가중치 파일이 필요한 종류
            continue
    return None, None


def patch_hist(frame, box):
    """박스 안쪽 색 분포 — 추적기가 딴 데를 잡았는지 보는 외부 확인용"""
    x, y, w, h = (int(v) for v in box)
    x, y = max(0, x), max(0, y)
    patch = frame[y:y + h, x:x + w]
    if patch.size == 0:
        return None
    hist = cv.calcHist([cv.cvtColor(patch, cv.COLOR_BGR2HSV)], [0, 1], None,
                       [16, 16], [0, 180, 0, 256])
    cv.normalize(hist, hist, 0, 1, cv.NORM_MINMAX)
    return hist


def similarity(ref, frame, box):
    cur = patch_hist(frame, box)
    if ref is None or cur is None:
        return 0.0
    return cv.compareHist(ref, cur, cv.HISTCMP_CORREL)


def get_bbox(mask):
    """bool 마스크 -> 가장 큰 윤곽선의 (x, y, w, h). 없으면 None. (71 과 같다)"""
    if mask is None or not np.any(mask):
        return None
    contours, _ = cv.findContours(mask.astype(np.uint8) * 255,
                                  cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    return cv.boundingRect(max(contours, key=cv.contourArea))


def sam_bbox(model, frame, point):
    """클릭 좌표 하나로 SAM 분할 -> bbox. 여러 후보면 클릭 점을 포함하는 것."""
    try:
        results = model(frame, points=[list(point)], labels=[1], verbose=False)
    except Exception as exc:  # 추론이 실패해도 게임은 계속 돈다
        print(f"SAM error: {exc}")
        return None
    if not results or results[0].masks is None:
        return None
    h, w = frame.shape[:2]
    chosen = None
    for mask in results[0].masks.data.cpu().numpy():
        mask = np.asarray(mask).astype(bool)
        if mask.shape != (h, w):  # 마스크 해상도가 다르면 맞춘다 (0/1 이라 INTER_NEAREST)
            mask = cv.resize(mask.astype(np.uint8), (w, h),
                             interpolation=cv.INTER_NEAREST).astype(bool)
        if chosen is None:
            chosen = mask
        if mask[point[1], point[0]]:
            chosen = mask
            break
    return get_bbox(chosen)


# ---------------------------------------------------------------- 미사일
def spawn_missile(target, rng):
    """화면 네 변 중 한 곳에서 드론을 향해 생성"""
    edge = rng.choice(("top", "bottom", "left", "right"))
    if edge == "top":
        pos = [rng.uniform(0, WIDTH), -10.0]
    elif edge == "bottom":
        pos = [rng.uniform(0, WIDTH), HEIGHT + 10.0]
    elif edge == "left":
        pos = [-10.0, rng.uniform(0, HEIGHT)]
    else:
        pos = [WIDTH + 10.0, rng.uniform(0, HEIGHT)]
    return {"pos": pos,
            "angle": math.atan2(target[1] - pos[1], target[0] - pos[0]),
            "age": 0.0}


def update_missile(missile, target, speed, dt):
    """선회각을 제한한 유도 — 가까운 쪽으로 돌되 한 번에 turn_rate*dt 까지만"""
    desired = math.atan2(target[1] - missile["pos"][1], target[0] - missile["pos"][0])
    diff = (desired - missile["angle"] + math.pi) % (2 * math.pi) - math.pi  # -π ~ π
    max_turn = MISSILE_TURN_RATE * dt
    missile["angle"] += max(-max_turn, min(max_turn, diff))
    missile["pos"][0] += math.cos(missile["angle"]) * speed * dt
    missile["pos"][1] += math.sin(missile["angle"]) * speed * dt
    missile["age"] += dt


def hitbox(box):
    """박스를 중심 기준으로 줄인다 — 박스에는 드론 주변 배경이 섞여 있다"""
    x, y, w, h = box
    sw, sh = w * HITBOX_SCALE, h * HITBOX_SCALE
    return (x + (w - sw) / 2, y + (h - sh) / 2, sw, sh)


def circle_rect_hit(center, radius, rect):
    """사각형 위에서 원 중심과 가장 가까운 점까지의 거리로 판정 (74 에서 검증)"""
    x, y, w, h = rect
    nx = min(max(center[0], x), x + w)
    ny = min(max(center[1], y), y + h)
    return (center[0] - nx) ** 2 + (center[1] - ny) ** 2 < radius ** 2


# ---------------------------------------------------------------- 드론 LED (선택)
class DroneLed:
    """USE_DRONE_LED=True 일 때만 연결한다. 실패하면 LED 없이 진행."""

    def __init__(self):
        self.drone = None
        if not USE_DRONE_LED:
            return
        try:
            from CodingDrone.drone import Drone
            from CodingDrone.protocol import LightModeDrone
            import drone_util

            self.mode = LightModeDrone
            port = DRONE_PORT or drone_util.find_port()
            drone = Drone()
            # ⚠️ open(None) 은 자동 탐색이 아니다 — 기본값이 문자열 "None" 이라 분기를 타지 않고
            #    예외 없이 False 만 돌아온다. 반환값을 반드시 확인할 것.
            if not drone.open(port):
                print(f"드론 연결 실패({port}) - LED 없이 진행")
                return
            self.drone = drone
            print(f"드론 LED 연결 OK ({port})")
        except Exception as exc:
            print(f"드론 연결 실패 - LED 없이 진행: {exc}")

    def hold(self, r, g, b):
        if self.drone:  # 인자는 전부 int 여야 한다 (아니면 조용히 None)
            self.drone.sendLightModeColor(self.mode.BodyHold, 100, r, g, b)

    def dimming(self, r, g, b):
        if self.drone:
            self.drone.sendLightModeColor(self.mode.BodyDimming, 1, r, g, b)

    def close(self):
        if self.drone:
            time.sleep(0.1)  # 수신 스레드 정리 대기 (Errno 6 방지)
            self.drone.close()


# ---------------------------------------------------------------- 영상 소스
def demo_frames():
    """카메라 대신 쓰는 합성 '드론' — 좌우로 떠다닌다"""
    rng = np.random.default_rng(7)
    small = rng.integers(40, 110, (HEIGHT // 16, WIDTH // 16, 3), dtype=np.int16).astype(np.uint8)
    background = cv.resize(small, (WIDTH, HEIGHT), interpolation=cv.INTER_CUBIC)
    i = 0
    while True:
        phase = (i % 480) / 480  # 너무 빠르면 추적기가 놓친다 (실측 후 480 프레임 주기)
        frame = background.copy()
        x = int(WIDTH / 2 - 30 + 160 * math.sin(phase * 2 * math.pi))
        y = int(HEIGHT / 2 - 30 + 90 * math.sin(phase * 4 * math.pi))
        # 단색 사각형은 추적기가 크기를 못 잡고 쪼그라든다 -> 프로펠러로 무늬를 준다
        cv.rectangle(frame, (x + 15, y + 15), (x + 45, y + 45), (40, 90, 230), cv.FILLED)
        for ox, oy in ((0, 0), (45, 0), (0, 45), (45, 45)):
            cv.circle(frame, (x + ox + 7, y + oy + 7), 11, (30, 200, 240), cv.FILLED)
            cv.circle(frame, (x + ox + 7, y + oy + 7), 11, (20, 40, 60), 2)
        i += 1
        yield True, frame


# ---------------------------------------------------------------- 메인
def main():
    probe, tracker_name = create_tracker()
    if probe is None:
        raise SystemExit("쓸 수 있는 추적기가 없습니다.  pip install opencv-contrib-python  (72 참고)")
    print(f"추적기: cv.{tracker_name}()")

    model = None
    if USE_SAM:
        try:
            from ultralytics import SAM
            model = SAM(SAM_MODEL)
            print(f"{SAM_MODEL} loaded")
        except Exception as exc:
            print(f"SAM 로드 실패 -> 드래그 선택만 사용: {exc}")

    frames = demo_frames() if SOURCE == "demo" else None
    cap = None if frames else cv.VideoCapture(SOURCE)
    if cap is not None:
        cap.set(cv.CAP_PROP_FRAME_WIDTH, WIDTH)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        if not cap.isOpened():
            raise SystemExit("카메라를 열지 못했습니다. (시스템 환경설정 > 보안 > 카메라 권한)")

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption("75 Drone AR Game - Dodge the Missiles")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 26)
    big_font = pygame.font.SysFont(None, 60)
    rng = random.Random()
    led = DroneLed()

    def draw_text(text, pos, color=(255, 255, 255), f=None):
        f = f or font
        screen.blit(f.render(text, True, (0, 0, 0)), (pos[0] + 2, pos[1] + 2))  # 그림자
        screen.blit(f.render(text, True, color), pos)

    state = "SELECT"  # SELECT / READY / PLAY / PAUSED / OVER
    tracker = None
    current_box = None
    ref_hist = None
    miss = 0
    pending_point = pending_box = None
    drag_start = drag_now = None

    missiles = []
    elapsed_ms = best_ms = 0.0
    spawn_timer = 0.0
    hit_pos = None
    delta_tick = 0
    skip_tick = False  # SAM 추론으로 멈춘 시간은 버린다
    started = pygame.time.get_ticks()

    try:
        running = True
        while running:
            ok, frame = next(frames) if frames else cap.read()
            if not ok:
                print("프레임을 읽지 못했습니다.")
                break
            if frame.shape[1] != WIDTH or frame.shape[0] != HEIGHT:
                frame = cv.resize(frame, (WIDTH, HEIGHT))

            # ---------- 1) 대상 선택 ----------
            if pending_point is not None or pending_box is not None:
                box = pending_box
                if box is None:
                    if model is not None:
                        draw_text("SAM processing...", (WIDTH // 2 - 80, HEIGHT // 2), (255, 255, 0))
                        pygame.display.flip()  # 멈추기 전에 안내를 먼저 보여 준다
                        box = sam_bbox(model, frame, pending_point)
                        skip_tick = True
                    else:
                        print("SAM 미사용 - 드론 위를 드래그해서 선택하세요.")

                if box and box[2] >= MIN_BOX and box[3] >= MIN_BOX:
                    tracker, _ = create_tracker()
                    tracker.init(frame, tuple(int(v) for v in box))
                    current_box = tuple(int(v) for v in box)
                    ref_hist = patch_hist(frame, current_box)  # 놓침 판정 기준
                    miss = 0
                    print(f"대상 선택 OK {current_box}")
                    if state == "SELECT":
                        state = "READY"
                elif box is not None or model is not None:
                    print("선택 실패 - 다시 클릭하거나 드래그하세요.")
                pending_point = pending_box = None

            # ---------- 2) 추적 ----------
            if tracker is not None:
                ok_track, box = tracker.update(frame)
                box = tuple(int(v) for v in box)
                score = similarity(ref_hist, frame, box) if ok_track else 0.0
                miss = miss + 1 if score < LOST_TH else 0
                if not ok_track or miss >= LOST_K:
                    # success 만 보면 영영 안 걸린다 (72) — 유사도 가드가 실제로 잡는 쪽
                    why = "update()=False" if not ok_track else f"유사도 {score:.2f} x{miss}"
                    print(f"추적 실패({why}) - 대상을 다시 선택하세요.")
                    tracker, current_box, ref_hist, miss = None, None, None, 0
                    if state == "PLAY":
                        state = "PAUSED"
                        led.hold(255, 200, 0)
                    elif state == "READY":
                        state = "SELECT"
                else:
                    current_box = box

            dt = min(delta_tick / 1000, MAX_DT)

            # ---------- 3) 게임 진행 ----------
            if state == "PLAY" and current_box:
                elapsed_ms += dt * 1000  # 점수도 물리와 같은 dt 로 (원본은 delta_tick)
                t = elapsed_ms / 1000
                speed = min(MISSILE_SPEED_START + MISSILE_SPEED_UP * t, MISSILE_SPEED_MAX)
                interval = max(SPAWN_INTERVAL_START - 0.05 * t, SPAWN_INTERVAL_MIN)

                x, y, w, h = current_box
                target = (x + w / 2, y + h / 2)

                spawn_timer += dt
                if spawn_timer >= interval:
                    spawn_timer = 0.0
                    missiles.append(spawn_missile(target, rng))

                hb = hitbox(current_box)
                for missile in missiles:
                    update_missile(missile, target, speed, dt)
                    if circle_rect_hit(missile["pos"], MISSILE_RADIUS, hb):
                        state = "OVER"
                        hit_pos = (int(missile["pos"][0]), int(missile["pos"][1]))
                        best_ms = max(best_ms, elapsed_ms)
                        print(f"GAME OVER - SCORE {elapsed_ms / 1000:.2f}")
                        led.dimming(255, 0, 0)
                        break
                missiles = [m for m in missiles if m["age"] < MISSILE_LIFETIME]

            # ---------- 4) 그리기 ----------
            rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            screen.blit(pygame.image.frombuffer(rgb.tobytes(), (WIDTH, HEIGHT), "RGB"), (0, 0))

            if current_box:
                color = (255, 0, 0) if state == "OVER" else (0, 255, 0)
                pygame.draw.rect(screen, color, current_box, 2)
                pygame.draw.rect(screen, (0, 150, 0), [int(v) for v in hitbox(current_box)], 1)

            for missile in missiles:
                px, py = missile["pos"]
                tail = (px - math.cos(missile["angle"]) * 14, py - math.sin(missile["angle"]) * 14)
                pygame.draw.line(screen, (255, 200, 0),
                                 (int(tail[0]), int(tail[1])), (int(px), int(py)), 3)
                pygame.draw.circle(screen, (255, 0, 0), (int(px), int(py)), MISSILE_RADIUS)

            if drag_start and drag_now:
                x0, y0 = drag_start
                x1, y1 = drag_now
                pygame.draw.rect(screen, (255, 255, 0),
                                 (min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0)), 1)

            if state == "OVER" and hit_pos:
                pygame.draw.circle(screen, (255, 120, 0), hit_pos, 28, 4)
                draw_text("GAME OVER", (WIDTH // 2 - 125, HEIGHT // 2 - 40), (255, 60, 60), big_font)
                draw_text(f"SCORE {elapsed_ms / 1000:.2f}", (WIDTH // 2 - 60, HEIGHT // 2 + 15))

            draw_text(f"SCORE {elapsed_ms / 1000:6.2f}", (10, 10), (255, 255, 0))
            draw_text(f"BEST  {best_ms / 1000:6.2f}", (10, 34))
            draw_text(f"missiles {len(missiles)}", (WIDTH - 130, 10))
            draw_text({
                "SELECT": "Click(SAM) or drag a box on the drone" if model
                          else "Drag a box on the drone",
                "READY": "SPACE: start   (click/drag: reselect)",
                "PLAY": "Dodge the missiles!",
                "PAUSED": "TARGET LOST - reselect, SPACE: resume",
                "OVER": "R: retry   ESC: quit",
            }[state], (10, HEIGHT - 28), (200, 230, 255))

            pygame.display.flip()

            delta_tick = clock.tick(FPS)  # 직전 프레임 이후 실제 경과 ms (74 참고)
            if skip_tick:  # SAM 추론으로 멈춘 시간은 점수에서 뺀다
                delta_tick = 0
                skip_tick = False

            # ---------- 5) 입력 ----------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        if state == "READY":  # 새 판
                            missiles, elapsed_ms, spawn_timer, hit_pos = [], 0.0, 0.0, None
                            state = "PLAY"
                            led.hold(0, 255, 0)
                        elif state == "PAUSED" and current_box:  # 재개
                            state = "PLAY"
                            led.hold(0, 255, 0)
                    elif event.key == pygame.K_r and state == "OVER":
                        missiles, hit_pos = [], None
                        state = "READY" if current_box else "SELECT"
                        led.hold(0, 0, 255)
                # 게임 중에는 대상을 바꾸지 않는다
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and state != "PLAY":
                    drag_start = drag_now = event.pos
                elif event.type == pygame.MOUSEMOTION and drag_start:
                    drag_now = event.pos
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and drag_start:
                    x0, y0 = drag_start
                    x1, y1 = event.pos
                    if abs(x1 - x0) > 10 and abs(y1 - y0) > 10:
                        pending_box = (min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0))
                    else:
                        pending_point = [x0, y0]
                    drag_start = drag_now = None

            if MAX_SECONDS and pygame.time.get_ticks() - started > MAX_SECONDS * 1000:
                running = False
    finally:
        # 예외가 나도 카메라·창·드론을 정리한다
        if cap is not None:
            cap.release()
        pygame.quit()
        led.close()
        print(f"종료 - BEST {best_ms / 1000:.2f}")


if __name__ == "__main__":
    main()
    sys.exit()
