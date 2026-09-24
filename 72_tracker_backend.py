r"""72. 추적기 고르기 — CSRT 는 어디에 있나, 그리고 무엇을 믿을 수 있나

35 강. 강의는 "**CSRT** 추적기로 박스를 따라간다" 로 시작한다.
그런데 **일반 `opencv-python` 에는 CSRT 가 없다.** 이 파일은 ① 지금 환경에서 실제로 쓸 수 있는
추적기를 조사하고 ② 추적이 무엇을 잘하고 무엇을 못하는지 합성 영상으로 **직접 재 본다**.
카메라도 드론도 필요 없다. (실행할 때마다 현재 환경 기준으로 다시 찍힌다.)

[1) CSRT 는 contrib 에만 있다 — 두 패키지의 차이]

    opencv-python 4.10.0.84          TrackerCSRT_create  **없음** (바이너리 심볼 0 개)
                                     cv2.legacy          **없음** -> AttributeError
    opencv-contrib-python 4.10.0.84  TrackerCSRT / KCF / legacy  전부 있음

강의가 적어 둔 대비책 `cv2.legacy.TrackerCSRT_create()` 는 일반 패키지에서 **대비가 되지 않는다** —
`legacy` 모듈 자체가 contrib 쪽이라 `AttributeError: module 'cv2' has no attribute 'legacy'` 가 난다.
그래서 `create_tracker()` 는 **CSRT → KCF → MIL** 순으로 있는 것을 고르고, 하나도 없으면
무엇을 설치해야 하는지 말해 준다. 가중치 파일이 필요한 GOTURN·Vit·Nano·DaSiamRPN 은 건너뛴다.

    pip uninstall -y opencv-python              # 같은 cv2 폴더를 써서 함께 두면 충돌한다
    pip install "opencv-contrib-python==4.10.0.84"

아래 수치는 **contrib 로 교체한 환경**에서 잰 값이다(36 강 과제 준비가 이 교체를 요구한다).

[2) 세 추적기 — 같은 영상 120 프레임]

    가림 없음      속도                IoU 평균   update()=False
      CSRT     47.9 ms ( 21 fps)     0.933         0 회
      KCF       7.0 ms (144 fps)     0.822         0 회
      MIL      56.9 ms ( 18 fps)     0.773         0 회
      HSV 재검출 1.2 ms (861 fps)     0.951          -

속도만 보면 **KCF 가 7 배 빠르고**, 정확도는 CSRT 가 낫다. 그런데 셋 다
**HSV 재검출(1.2 ms)보다 느리다.** 강의의 "검출은 무겁고 추적은 가볍다" 는 비교 대상이
SAM 이라서 맞는 말이었을 뿐이다(이 기계에서 grabCut 분할 **758 ms**, floodFill 1.0 ms).
가벼운 검출기가 있으면 추적기를 끼워 넣을 이유가 없다. 추적은 속도 수단이 아니라
**비싼 검출기를 덜 부르는** 수단이다.

[3) 추적이 진짜 못하는 것 — 가림 뒤 복귀]

    가림 있음      IoU 평균   최종     update()=False
      CSRT        0.396    0.000      69 회
      KCF         0.346    0.000      69 회
      MIL         0.428    0.000       0 회   <- ⚠️
      HSV 재검출   0.817    0.967        -

추적기는 상태를 이어 가는 대신 **한 번 놓치면 셋 다 스스로 못 돌아온다**(최종 IoU 0.000).
검출은 매 프레임 처음부터 찾으므로 기둥을 지나자마자 복귀했다.

[4) ⚠️ MIL 은 놓친 것을 알려주지 않는다]

CSRT·KCF 는 놓친 뒤 `success = False` 를 69 회 돌려줬다. **MIL 은 0 회다.**
박스가 멈춘 채 계속 "성공" 을 돌려주므로, `success` 만 보고 해제를 판단하는 코드는
contrib 가 없는 환경(= MIL 폴백)에서 **엉뚱한 좌표를 계속 흘려보낸다.**

그래서 이 파일은 추적기와 무관한 외부 확인을 하나 붙였다 — 첫 박스의 **색 히스토그램**과
현재 박스를 비교해 유사도가 `LOST_TH` 아래로 `LOST_K` 프레임 연속이면 놓친 것으로 본다.

    가드 선언 55 프레임   /   IoU 붕괴 CSRT·KCF 51, MIL 59 프레임   /   가림 없을 때 선언 없음

추적기가 무엇이든 같은 자리에서 잡아낸다. 한 프레임만 보면 0.819 처럼 튀는 값이 나오므로
**연속 K 회** 조건이 필요하다.

⚠️ MIL 은 내부에 무작위 표본을 쓰므로 실행할 때마다 수치가 조금씩 달라진다.
"""

import time

import cv2 as cv
import numpy as np

W, H = 640, 480
N_FRAMES = 120
SIZE = 60  # 물체 한 변
LOST_TH = 0.5  # 히스토그램 유사도 임계
LOST_K = 5  # 연속 몇 프레임 미달이면 놓침으로 선언

# 후보 추적기 — 앞에 있는 것부터 시도한다 (CSRT 는 contrib 에만 있다)
TRACKER_ORDER = ["TrackerCSRT_create", "TrackerKCF_create", "TrackerMIL_create"]


def create_tracker(verbose=True):
    """이 환경에서 만들 수 있는 추적기를 돌려준다. 없으면 None."""
    for name in TRACKER_ORDER:
        factory = getattr(cv, name, None)
        if factory is None:
            continue
        try:
            tracker = factory()
        except cv.error:  # 가중치 파일이 필요한 종류
            continue
        if verbose:
            print(f"  추적기: cv.{name}()")
        return tracker
    if verbose:
        print("  ⚠️ 쓸 수 있는 추적기가 없다 -> pip install opencv-contrib-python")
    return None


# ---------------------------------------------------------------- 합성 영상
def make_background(seed=7):
    """저해상도 노이즈를 키워 질감을 만든다 (평면 배경은 추적이 너무 쉬워진다)"""
    rng = np.random.default_rng(seed)
    small = rng.integers(40, 120, (H // 16, W // 16, 3), dtype=np.int16).astype(np.uint8)
    return cv.resize(small, (W, H), interpolation=cv.INTER_CUBIC)


BG = make_background()


def gt_box(i):
    """i 번째 프레임의 정답 박스 — 가로로 지나가며 위아래로 흔들린다"""
    x = int(60 + (W - 180) * i / (N_FRAMES - 1))
    y = int(H / 2 - 60 + 70 * np.sin(i / N_FRAMES * 2 * np.pi))
    return (x, y, SIZE, SIZE)


def make_frame(i, occlusion=False):
    frame = BG.copy()
    x, y, w, h = gt_box(i)
    cv.rectangle(frame, (x, y), (x + w, y + h), (40, 90, 230), -1)  # 주황 물체(BGR)
    cv.circle(frame, (x + w // 2, y + h // 2), 12, (30, 60, 180), -1)
    if occlusion and 0.42 < i / N_FRAMES < 0.58:
        cv.rectangle(frame, (W // 2 - 45, 0), (W // 2 + 45, H), (70, 70, 70), -1)
    return frame


# ---------------------------------------------------------------- 도구
def iou(a, b):
    """두 박스의 겹침 비율 — 추적이 맞는지 채점하는 자"""
    if a is None or b is None:
        return 0.0
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    x1, y1 = max(ax, bx), max(ay, by)
    x2, y2 = min(ax + aw, bx + bw), min(ay + ah, by + bh)
    iw, ih = max(0, x2 - x1), max(0, y2 - y1)
    inter = iw * ih
    return inter / (aw * ah + bw * bh - inter) if inter else 0.0


def patch_hist(frame, box):
    """박스 안쪽의 색 분포 — 추적기가 딴 데를 잡았는지 보는 외부 확인용"""
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


def detect_hsv(frame):
    """매 프레임 처음부터 찾는 '검출' 쪽 — 주황색 덩어리 하나"""
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    mask = cv.inRange(hsv, (5, 120, 120), (25, 255, 255))
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    largest = max(contours, key=cv.contourArea)
    if cv.contourArea(largest) < 100:
        return None
    return cv.boundingRect(largest)


# ---------------------------------------------------------------- 실험
def probe():
    print(f"[1] OpenCV {cv.__version__} 에서 만들 수 있는 추적기")
    names = sorted(n for n in dir(cv) if n.startswith("Tracker") and n.endswith("_create"))
    for name in names:
        try:
            getattr(cv, name)()
            print(f"    {name:26s} OK")
        except cv.error as e:
            reason = "onnx 모델 필요" if "onnx" in str(e) else "모델 파일 필요"
            print(f"    {name:26s} 실패 ({reason})")
    print(f"    {'TrackerCSRT_create':26s} {'있음' if hasattr(cv, 'TrackerCSRT_create') else '**없음** (contrib 전용)'}")
    try:
        cv.legacy.TrackerCSRT_create()
        print("    cv.legacy 대비책            동작")
    except AttributeError as e:
        print(f"    cv.legacy 대비책            AttributeError: {e}")
    print()


def available_trackers():
    """가중치 파일 없이 바로 만들어지는 추적기 이름들"""
    names = []
    for name in ("TrackerCSRT_create", "TrackerKCF_create", "TrackerMIL_create"):
        factory = getattr(cv, name, None)
        if factory is None:
            continue
        try:
            factory()
        except cv.error:
            continue
        names.append(name)
    return names


def compare(occlusion):
    """있는 추적기 전부 vs 매 프레임 재검출 — 속도와 정확도를 같은 영상으로 잰다"""
    frames = [make_frame(i, occlusion) for i in range(N_FRAMES)]
    tag = "가림 있음" if occlusion else "가림 없음"
    print(f"    [{tag}]")

    for name in available_trackers():
        tracker = getattr(cv, name)()
        tracker.init(frames[0], gt_box(0))
        ref = patch_hist(frames[0], gt_box(0))

        t_ms, t_iou, miss, declared, false_count = [], [], 0, None, 0
        for i in range(1, N_FRAMES):
            t0 = time.perf_counter()
            ok, box = tracker.update(frames[i])
            t_ms.append((time.perf_counter() - t0) * 1000)
            if not ok:
                false_count += 1
            t_iou.append(iou(gt_box(i), tuple(map(int, box))))
            miss = miss + 1 if similarity(ref, frames[i], box) < LOST_TH else 0
            if declared is None and miss >= LOST_K:
                declared = i
        broken = next((i for i, v in enumerate(t_iou, start=1) if v < 0.3), None)
        short = name.replace("Tracker", "").replace("_create", "")
        print(f"      추적 {short:4s} {np.mean(t_ms):6.2f} ms/frame ({1000 / np.mean(t_ms):5.1f} fps)"
              f"  IoU 평균 {np.mean(t_iou):.3f} 최종 {t_iou[-1]:.3f}"
              f"  update()=False {false_count:3d}회  IoU붕괴 {str(broken):>4s}  가드 {str(declared):>4s}")

    d_ms, d_iou = [], []
    for i in range(1, N_FRAMES):
        t0 = time.perf_counter()
        box = detect_hsv(frames[i])
        d_ms.append((time.perf_counter() - t0) * 1000)
        d_iou.append(iou(gt_box(i), box))
    print(f"      재검출 HSV  {np.mean(d_ms):6.2f} ms/frame ({1000 / np.mean(d_ms):5.1f} fps)"
          f"  IoU 평균 {np.mean(d_iou):.3f} 최종 {d_iou[-1]:.3f}")


def main():
    probe()
    print(f"[2] 추적 vs 재검출 — 같은 합성 영상 {N_FRAMES} 프레임")
    print(f"    (IoU붕괴 = IoU 가 0.3 아래로 내려간 프레임, 가드 = 유사도 {LOST_TH} 미만 {LOST_K} 연속)")
    compare(occlusion=False)
    compare(occlusion=True)
    print()
    print("[3] 정리")
    print("    - 추적은 검출보다 빠른 게 아니라, **비싼 검출기를 덜 부르는** 수단이다.")
    print("    - 한 번 놓치면 스스로 복귀하지 못한다 -> 다시 클릭하거나 재검출이 필요하다.")
    print("    - update() 의 success 만 믿으면 안 된다 -> 외부 확인(유사도)을 함께 본다.")


if __name__ == "__main__":
    main()
