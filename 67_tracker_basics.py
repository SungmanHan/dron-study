r"""67. 추적의 원리를 손으로 — IoU 매칭 · ID 발급 · 소멸

32 강 이론. 드론·카메라·모델 없이 **숫자만으로** 돌린다.

[탐지와 추적의 차이는 한 줄이다]
    탐지  이 프레임에 무엇이 어디 있는가
    추적  + **이전 프레임의 그 물체와 같은 물체인가** (같으면 같은 ID)

매 프레임 탐지하고 그 결과를 이전 것과 짝지어 ID 를 잇는 방식을 **Tracking-by-Detection** 이라고 한다.
짝짓는 절차는 네 단계다.

    1) 예측   이전 물체가 이번엔 어디쯤 있을지 (칼만 필터)
    2) 매칭   예측 위치와 새 박스의 겹침(IoU)이 가장 큰 쌍을 연결 (헝가리안 알고리즘)
    3) 발급   매칭 안 된 새 박스에는 새 ID
    4) 소멸   몇 프레임 이상 안 보이면 목록에서 지운다

이 파일은 1)을 생략하고(직전 위치를 그대로 예측으로 쓴다) 2)를 **탐욕적 매칭**으로 단순화한
30 줄짜리 트래커를 만든다. BoT-SORT·ByteTrack 이 하는 일의 뼈대가 이것이다.
IoU 는 58 에서 쓴 그 함수 그대로다 — NMS 는 **한 프레임 안에서** 겹친 박스를 지웠고,
추적은 **프레임 사이에서** 겹친 박스를 잇는다. 같은 도구, 다른 축.

[실험 셋 — 아래에서 직접 돌려 본다]
    A 그냥 이동       한 물체가 오른쪽으로     -> ID 가 유지된다
    B 잠깐 사라짐     두 프레임 탐지가 끊긴다   -> MAX_AGE=2 면 ID 유지, **MAX_AGE=0 이면 새 ID**
    C 두 물체가 교차  서로 지나쳐 간다         -> 스치는 frame 7 에서 **ID 가 뒤바뀐다** (ID Switch)

C 가 추적기의 고질병이다. 위치(IoU)만 보고 이으면, 두 박스가 겹치는 순간 어느 쪽이 어느 쪽인지
구분할 근거가 없다. 그래서 진짜 트래커는 **속도(어디로 가던 중이었나)** 를 함께 본다 — 칼만 필터의 역할.
B 는 강의의 경고와 같다: `conf` 를 0.7 로 높이면 탐지가 자주 끊겨 ID 가 더 자주 바뀐다.

[이 트래커의 한계 — 일부러 남겨 둔 것]
예측을 "직전 위치 그대로" 로 대신했으므로, 안 보이는 동안 물체가 움직이면 따라가지 못한다.
IoU 로만 잇기 때문에 빠르게 움직이는 물체(한 프레임에 박스 폭만큼 이동)도 놓친다 —
폭 60 짜리 박스가 40 픽셀씩 움직이면 IoU 가 0.2 라 기본 임계값 0.3 에서 매번 새 ID 가 발급된다.
"""

IOU_THRESHOLD = 0.3  # 이보다 많이 겹치면 같은 물체로 본다
MAX_AGE = 2  # 몇 프레임까지 안 보여도 기다려 줄지 (0 = 바로 지운다)


def iou(a, b):
    """두 박스 (x1, y1, x2, y2) 의 겹침 비율. 58 의 그 계산."""
    left, top = max(a[0], b[0]), max(a[1], b[1])
    right, bottom = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, right - left) * max(0, bottom - top)
    if inter == 0:
        return 0.0
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return inter / float(area_a + area_b - inter)


class SimpleTracker:
    """IoU 로 잇는 최소 트래커. 예측은 '직전 위치 그대로'로 대신한다."""

    def __init__(self, iou_threshold=IOU_THRESHOLD, max_age=MAX_AGE):
        self.iou_threshold = iou_threshold
        self.max_age = max_age
        self.tracks = {}  # {id: {"box": ..., "age": 몇 프레임째 안 보이는가}}
        self._next_id = 1

    def update(self, detections):
        """이번 프레임의 박스 목록 -> [(id, box)]. 순서는 탐지 순서 그대로."""
        matched = {}
        used = set()
        for det in detections:
            # 2) 매칭 — 남은 트랙 중 가장 많이 겹치는 것 하나 (탐욕적)
            best_id, best_iou = None, self.iou_threshold
            for track_id, track in self.tracks.items():
                if track_id in used:
                    continue
                score = iou(track["box"], det)
                if score >= best_iou:
                    best_id, best_iou = track_id, score
            if best_id is None:
                best_id = self._next_id  # 3) 발급 — 짝이 없으면 새 ID
                self._next_id += 1
            used.add(best_id)
            matched[best_id] = det

        # 4) 소멸 — 이번에 못 본 트랙은 나이를 먹고, 너무 오래되면 지운다
        for track_id, track in list(self.tracks.items()):
            if track_id in matched:
                continue
            track["age"] += 1
            if track["age"] > self.max_age:
                del self.tracks[track_id]

        for track_id, box in matched.items():
            self.tracks[track_id] = {"box": box, "age": 0}
        return [(track_id, box) for track_id, box in matched.items()]


def run(title, frames, max_age=MAX_AGE):
    """프레임별 탐지 목록을 넣고 ID 가 어떻게 붙는지 찍는다."""
    tracker = SimpleTracker(max_age=max_age)
    print(f"\n[{title}]  (IoU>={IOU_THRESHOLD}, MAX_AGE={max_age})")
    for i, detections in enumerate(frames):
        result = tracker.update(detections)
        shown = "  ".join(f"ID{tid}@x={box[0]}" for tid, box in sorted(result))
        print(f"  frame {i}: 탐지 {len(detections)}개 -> {shown if shown else '(없음)'}")
    return tracker


def box_at(x, y=100, w=60, h=120):
    return (x, y, x + w, y + h)


def main():
    step = 8  # 한 프레임에 움직이는 픽셀. 폭 60 짜리 박스라 IoU 0.76 — 넉넉히 이어진다

    # A) 한 물체가 오른쪽으로 이동 — 매 프레임 많이 겹치므로 ID 가 이어진다
    run("A. 그냥 이동", [[box_at(100 + i * step)] for i in range(5)])

    # B) 중간 두 프레임에서 탐지가 끊긴다 (가림) — 기다려 주면 같은 ID, 아니면 새 ID
    blinking = [[box_at(100)], [box_at(108)], [], [], [box_at(132)]]
    run("B. 잠깐 사라짐 — 기다려 준다 (MAX_AGE=2)", blinking, max_age=2)
    run("B'. 잠깐 사라짐 — 안 기다린다 (MAX_AGE=0)", blinking, max_age=0)

    # C) 두 물체가 서로를 지나친다 — 겹치는 순간 ID 가 뒤바뀐다
    crossing = [[box_at(100 + i * step), box_at(200 - i * step)] for i in range(14)]
    run("C. 두 물체가 교차 (ID Switch)", crossing)

    print("\n[정리]")
    print("  · 같은 IoU 계산이 한 프레임 안에서는 NMS, 프레임 사이에서는 추적에 쓰인다.")
    print("  · B: 탐지가 끊기면 ID 가 바뀐다 -> conf 를 너무 높이면 추적이 더 불안정해진다.")
    print("  · C: 두 물체가 스쳐 지나가는 frame 7 에서 ID1 이 **왼쪽으로 가던 물체**로 옮겨 붙는다.")
    print("       위치만 보고 이었기 때문이다. 실제 트래커는 칼만 필터로 '어디로 가던 중이었는지'")
    print("       를 함께 보고, 헝가리안 알고리즘으로 전체 조합 중 최적을 고른다.")


if __name__ == "__main__":
    main()
