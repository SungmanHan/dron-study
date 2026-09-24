r"""68. 사물 추적 — ID 를 붙이고 궤적을 그린다 📷

32 강 실습. 65(탐지)에 **ID 와 궤적**이 붙는다.

    DETECTOR = "yolo"   model.track(persist=True) 로 실제 추적 (설치 + 가중치 필요)
    DETECTOR = "demo"   합성 영상 + 색 검출 + 67 의 IoU 트래커 — **설치 없이 돌아간다** (기본값)
    SOURCE   = 0        카메라 / "demo" 합성 영상 / "경로" 동영상

[탐지에서 추적으로 — 함수 하나가 바뀐다]
    model(frame, ...)                         탐지만. 매 프레임 남남
    model.track(frame, persist=True, ...)     ID 까지. **persist 를 빼면 매 프레임 ID 가 초기화된다**

`persist=True` 가 이 강의의 핵심 옵션이다. 트래커가 이전 프레임의 상태를 들고 있어야
"같은 물체" 판정이 가능하다.

    tracker="botsort.yaml"    기본값. 카메라 움직임 보정까지 — 정확도 쪽
    tracker="bytetrack.yaml"  신뢰도 낮은 박스까지 활용 — 가볍고 빠른 쪽 (CPU 노트북에 유리)

[박스에 id 가 없을 수도 있다]
추적이 확정되기 전이면 `box.id` 가 `None` 이다. 그대로 `int(box.id)` 하면 터진다.

    track_id = int(box.id[0]) if box.id is not None else -1

강의 원본은 `int(box.id)` 로 쓰는데, 원소 하나짜리 텐서라 우연히 동작할 뿐이다.
변수 이름도 `id` 대신 `track_id` 로 — `id()` 는 파이썬 내장 함수다.

[궤적은 ID 별 중심점을 모아 선으로 잇는다]
    track_history = defaultdict(lambda: deque(maxlen=30))   # 오래된 점은 알아서 밀려난다
    track_history[track_id].append((cx, cy))
    pygame.draw.lines(screen, 색, False, 목록, 2)            # 점이 2개 이상일 때만

`deque(maxlen=30)` 은 31 번째를 넣으면 가장 오래된 것을 버린다(확인: maxlen=3 에 0~4 를 넣으면 `[2, 3, 4]`).
ID 가 바뀌면 궤적도 새로 시작된다 — 그래서 **궤적이 끊기는 지점이 곧 ID 가 바뀐 지점**이다.

[거울 모드는 탐지 전에]
`cv.flip` 을 화면에 그리기 직전에 하면, 추론은 뒤집기 전 그림으로 돌아 **박스 좌표가 좌우로 어긋난다.**
프레임을 먼저 뒤집고, 그 뒤집힌 프레임으로 추론·표시 둘 다 한다.

[강의 코드의 라벨 버그]
    conf = int(box.conf[0] * 100)        # 이미 정수 (예: 87)
    label = f"...{conf:.2f}..."          # -> "87.00" 으로 찍힌다
정수에 소수점 둘째 자리를 붙인 것이다. `f"{0.87:.0%}"` -> `"87%"` 가 의도한 모양이다.

[demo 모드로 무엇을 보나]
합성 영상에서 두 물체가 **서로를 지나친다.** 스치는 순간 ID 가 뒤바뀌고 궤적이 꺾이는 것을
눈으로 볼 수 있다 — 67 의 실험 C 와 같은 현상이다. 가려짐·교차는 트래커의 고질병이라
YOLO 를 붙여도 같은 일이 일어난다.
"""

from collections import defaultdict, deque

import cv2 as cv
import numpy as np
import pygame

DETECTOR = "demo"  # "yolo" / "demo"
SOURCE = "demo"  # 0 (카메라) / "demo" / "파일경로"
MODEL_FILE = "yolo11n.pt"
CONF = 0.5  # 강의는 0.7 — 너무 높이면 탐지가 끊겨 ID 가 자주 바뀐다
TRACKER_YAML = "bytetrack.yaml"  # "botsort.yaml" 이 기본값
TRACK_CLASSES = None  # 예: [0] 이면 사람만
TRAIL_LEN = 30  # 궤적으로 남길 중심점 개수
WIDTH, HEIGHT = 640, 480
FPS = 30
MIRROR = False  # 카메라일 때만 의미가 있다. 탐지 전에 뒤집는다
MAX_SECONDS = 0  # 0 = 무제한
IOU_THRESHOLD = 0.3  # demo 트래커용 (67 참고)
MAX_AGE = 2

BOX_COLOR = (0, 255, 0)
LABEL_COLOR = (255, 0, 0)
TRAIL_COLOR = (255, 255, 0)
DEMO_HSV = ((95, 80, 80), (115, 255, 255))


def iou(a, b):
    left, top = max(a[0], b[0]), max(a[1], b[1])
    right, bottom = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, right - left) * max(0, bottom - top)
    if inter == 0:
        return 0.0
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return inter / float(area_a + area_b - inter)


class SimpleTracker:
    """67 의 트래커를 그대로 가져왔다 (파일 이름이 숫자로 시작해 import 할 수 없다)."""

    def __init__(self, iou_threshold=IOU_THRESHOLD, max_age=MAX_AGE):
        self.iou_threshold, self.max_age = iou_threshold, max_age
        self.tracks, self._next_id = {}, 1

    def update(self, detections):
        matched, used = {}, set()
        for det in detections:
            best_id, best_iou = None, self.iou_threshold
            for track_id, track in self.tracks.items():
                if track_id in used:
                    continue
                score = iou(track["box"], det)
                if score >= best_iou:
                    best_id, best_iou = track_id, score
            if best_id is None:
                best_id, self._next_id = self._next_id, self._next_id + 1
            used.add(best_id)
            matched[best_id] = det
        for track_id, track in list(self.tracks.items()):
            if track_id not in matched:
                track["age"] += 1
                if track["age"] > self.max_age:
                    del self.tracks[track_id]
        for track_id, box in matched.items():
            self.tracks[track_id] = {"box": box, "age": 0}
        return [(tid, box) for tid, box in matched.items()]


def demo_frames():
    """두 물체가 서로를 지나치는 영상 — 스치는 순간 ID 가 뒤바뀌는 걸 보려고 만든 장면."""
    i = 0
    while True:
        frame = np.full((HEIGHT, WIDTH, 3), 70, np.uint8)
        # 사인 곡선으로 부드럽게 좌우로 — 두 물체가 반대 위상이라 한가운데서 스친다
        swing = (WIDTH / 2 - 90) * np.sin(i / 25.0)
        for x in (int(WIDTH / 2 + swing), int(WIDTH / 2 - swing)):
            cv.rectangle(frame, (x - 35, 180), (x + 35, 330), (200, 120, 40), cv.FILLED)
        i += 1
        yield True, frame


def detect_demo(frame):
    """색으로 찾는 자리끼움 탐지기(65 와 같다). 돌려주는 값에는 ID 가 없다."""
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    mask = cv.inRange(hsv, np.array(DEMO_HSV[0]), np.array(DEMO_HSV[1]))
    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    boxes = []
    for contour in contours:
        if cv.contourArea(contour) < 1500:
            continue
        x, y, w, h = cv.boundingRect(contour)
        boxes.append((x, y, x + w, y + h))
    return boxes


def track_yolo(frame, model):
    """model.track 결과를 (track_id, box, conf, name) 목록으로."""
    out = []
    results = model.track(frame, conf=CONF, persist=True, classes=TRACK_CLASSES,
                          tracker=TRACKER_YAML, verbose=False)
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            track_id = int(box.id[0]) if box.id is not None else -1  # 확정 전이면 None
            out.append((track_id, (x1, y1, x2, y2), float(box.conf[0]),
                        model.names[int(box.cls[0])]))
    return out


def main():
    model = None
    if DETECTOR == "yolo":
        try:
            from ultralytics import YOLO
        except ImportError:
            raise SystemExit("ultralytics 가 없습니다.  pip install ultralytics  (63 참고)\n"
                             '  설치 없이 보려면 DETECTOR = "demo"')
        model = YOLO(MODEL_FILE)

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption("68 object tracking")
    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()

    frames = demo_frames() if SOURCE == "demo" else None
    cap = None if frames else cv.VideoCapture(SOURCE)
    if cap is not None:
        cap.set(cv.CAP_PROP_FRAME_WIDTH, WIDTH)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        if not cap.isOpened():
            pygame.quit()
            raise SystemExit("카메라를 열지 못했습니다. (시스템 환경설정 > 보안 > 카메라 권한)")

    tracker = SimpleTracker()
    history = defaultdict(lambda: deque(maxlen=TRAIL_LEN))  # ID 별 중심점
    seen_ids = set()
    running, count = True, 0
    started = pygame.time.get_ticks()
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            ok, frame = next(frames) if frames else cap.read()
            if not ok:
                print("프레임을 읽지 못했습니다.")
                break
            if frame.shape[1] != WIDTH or frame.shape[0] != HEIGHT:
                frame = cv.resize(frame, (WIDTH, HEIGHT))
            if MIRROR:
                frame = cv.flip(frame, 1)  # 탐지 전에 뒤집어야 좌표가 화면과 맞는다
            count += 1

            rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            screen.blit(pygame.image.frombuffer(rgb.tobytes(), (WIDTH, HEIGHT), "RGB"), (0, 0))

            if DETECTOR == "demo":
                tracked = [(tid, box, 0.9, "object")
                           for tid, box in tracker.update(detect_demo(frame))]
            else:
                tracked = track_yolo(frame, model)

            for track_id, (x1, y1, x2, y2), conf, name in tracked:
                seen_ids.add(track_id)
                pygame.draw.rect(screen, BOX_COLOR, (x1, y1, x2 - x1, y2 - y1), 2)
                label = f"{name} {conf:.0%} ID:{track_id}"  # 정수에 :.2f 를 쓰면 "87.00"
                text = font.render(label, True, LABEL_COLOR)
                screen.blit(text, (x1, max(y1 - text.get_height(), 0)))

                if track_id != -1:  # 궤적 — 중심점을 모아 선으로 잇는다
                    history[track_id].append(((x1 + x2) // 2, (y1 + y2) // 2))
                    if len(history[track_id]) > 1:
                        pygame.draw.lines(screen, TRAIL_COLOR, False,
                                          list(history[track_id]), 2)

            info = (f"FPS: {clock.get_fps():5.2f}  tracks: {len(tracked)}  "
                    f"ids so far: {len(seen_ids)}{'  (DEMO)' if DETECTOR == 'demo' else ''}")
            screen.blit(font.render(info, True, (0, 0, 255)), (10, 10))

            pygame.display.flip()
            clock.tick(FPS)
            if MAX_SECONDS and pygame.time.get_ticks() - started > MAX_SECONDS * 1000:
                running = False
    finally:
        if cap is not None:
            cap.release()
        pygame.quit()
        # 발급된 ID 수가 물체 수보다 훨씬 많다면 ID 가 계속 갈아 끼워졌다는 뜻이다
        print(f"{count} 프레임 / 발급된 ID {len(seen_ids)}개 {sorted(seen_ids)}")


if __name__ == "__main__":
    main()
