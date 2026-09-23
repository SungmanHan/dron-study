r"""50. 색으로 물체 추적하기 — 마스크 → 윤곽선 → 위치

24 강 예제1. 드론은 아직 쓰지 않는다. `SOURCE` 를 바꿔 실행한다.

    SOURCE = 0        카메라 (강의 방식)
    SOURCE = "demo"   색 공이 움직이는 합성 영상을 만들어 쓴다 — **카메라 없이 확인용** (기본값)
    SOURCE = "경로"   동영상 파일

22 강에서 만든 마스크(`inRange`)에 **"그래서 그게 어디 있는데"** 를 붙이는 단계다.

    HSV 변환 -> inRange 로 마스크 -> 잡음 정리 -> findContours -> 가장 큰 것 -> boundingRect

[findContours 반환값이 버전마다 다르다]
    contours, hierarchy = cv.findContours(...)      # OpenCV 4.x (지금)
    _, contours, hierarchy = cv.findContours(...)   # OpenCV 3.x
인터넷 예제를 붙여 넣었을 때 `too many values to unpack` 이 나면 이 차이다.
`RETR_EXTERNAL` 은 바깥 윤곽선만, `CHAIN_APPROX_SIMPLE` 은 꼭짓점 위주로 압축해서 돌려준다.

[강의 코드의 `for` 루프는 "마지막" 물체를 남긴다]
    for c in contours:
        if cv.contourArea(c) > 500:
            x, y, w, h = cv.boundingRect(c)
            height = y          # ← 돌 때마다 덮어쓴다
같은 색 물체가 둘 이상이면 **마지막으로 훑은 것**이 드론 명령의 기준이 된다. 어느 게 마지막인지는
윤곽선 순서에 달렸다. `max(contours, key=cv.contourArea)` 로 **가장 큰 것 하나**만 쓰는 편이 예측 가능하다.

[`boundingRect` 의 (x, y) 는 왼쪽 위다]
공의 위치로 쓰려면 중심이 맞다. `cx = x + w // 2`, `cy = y + h // 2`.
강의 코드는 왼쪽 위 좌표를 그대로 써서, 공이 커질수록 기준점이 왼쪽 위로 치우친다.

[강의 예제1(트랙바)의 계산에는 버그가 있다]
예제1 은 고른 색을 HSV 로 바꾼 뒤 `H ± 10` 을 범위로 쓴다.

    ch_hsv = [hsv[0], s, v]                      # hsv[0] 은 numpy uint8
    lower = np.array([ch_hsv[0] - 10, ...])      # H=0(빨강) 이면 -10 이 아니라 **246**

`uint8` 은 음수가 없어 아래로 넘친다(43 참고). 직접 돌려 보면 빨강을 골랐을 때
`lower=[246 120 177]`, `upper=[10 255 255]` 가 되어 **하한이 상한보다 커지고 마스크가 전부 검게 나온다.**
"빨강은 잘 안 잡힌다" 로 넘어가기 쉬운데 원인은 색이 아니라 이 뺄셈이다.
→ `int()` 로 바꿔 계산하고, 빨강은 22 강처럼 두 구간으로 잡는다(`COLOR_RANGES["red"]`).

[잡음 정리 — 열기(OPEN) 다음 닫기(CLOSE)]
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)    # 점 잡음 제거
    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)   # 물체 안의 구멍 메우기
없어도 돌아가지만, 이게 없으면 형광등 반사 하나에 `findContours` 가 수십 개를 돌려준다.

[색 범위는 실습 장소에서 다시 잡는다]
`TUNE = True` 로 두면 트랙바가 뜬다. 물체만 하얗게 남도록 맞춘 뒤 콘솔에 찍힌 값을
`COLOR_RANGES` 에 옮겨 적는다. 창가와 실내등 아래의 값이 다르다.
"""

import cv2 as cv
import numpy as np

SOURCE = "demo"  # 0 (카메라) / "demo" (합성 영상) / "파일경로"
TARGET = "skyblue"  # COLOR_RANGES 의 키
TUNE = False  # True = HSV 트랙바 창 (값을 찾은 뒤 False)
SHOW = "window"  # "window" = 영상+마스크 / "none" = 좌표만
MIN_AREA = 500  # 이보다 작은 덩어리는 잡음으로 버린다
FRAME_W, FRAME_H = 640, 480

# OpenCV 기준 H 0~179 / S·V 0~255. 빨강만 구간이 둘이다(22 참고).
COLOR_RANGES = {
    "skyblue": [((85, 60, 120), (105, 255, 255))],
    "blue": [((110, 100, 30), (130, 255, 255))],  # 강의가 쓰는 파랑 (H 120 ± 10)
    "yellow": [((20, 100, 100), (35, 255, 255))],
    "green": [((40, 80, 60), (80, 255, 255))],
    "red": [((0, 150, 80), (8, 255, 255)),
            ((170, 150, 80), (179, 255, 255))],
}

TUNER = "HSV Tuner"


def make_demo_frames(n=120):
    """색 공이 가운데 → 위 → 아래 → 왼쪽 → 오른쪽으로 움직이다 사라지는 영상."""
    ball_bgr = cv.cvtColor(np.uint8([[[95, 200, 230]]]), cv.COLOR_HSV2BGR)[0][0].tolist()
    path = [(320, 240), (320, 60), (320, 420), (60, 240), (580, 240), None]
    for i in range(n):
        frame = np.full((FRAME_H, FRAME_W, 3), 60, np.uint8)
        cv.putText(frame, "demo", (10, FRAME_H - 12), cv.FONT_HERSHEY_SIMPLEX, 0.6, (90, 90, 90), 1)
        pos = path[min(i * len(path) // n, len(path) - 1)]
        if pos is not None:
            cv.circle(frame, pos, 45, ball_bgr, -1)
        yield frame


def setup_tuner(first_range):
    """H 하한/상한, S 하한, V 하한 트랙바. 초기값은 지금 프리셋."""
    (h_lo, s_lo, v_lo), (h_hi, _, _) = first_range
    cv.namedWindow(TUNER)
    for name, val, mx in (("H low", h_lo, 179), ("H high", h_hi, 179),
                          ("S low", s_lo, 255), ("V low", v_lo, 255)):
        cv.createTrackbar(name, TUNER, val, mx, lambda _x: None)


def read_tuner():
    """트랙바 값을 COLOR_RANGES 에 그대로 붙여 넣을 수 있는 모양으로 읽는다."""
    lo = (cv.getTrackbarPos("H low", TUNER), cv.getTrackbarPos("S low", TUNER),
          cv.getTrackbarPos("V low", TUNER))
    hi = (cv.getTrackbarPos("H high", TUNER), 255, 255)
    return [(lo, hi)]


def make_mask(frame, ranges):
    """지정한 색 범위만 흰색인 마스크. 구간이 여러 개면 OR 로 합친다."""
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    mask = None
    for lower, upper in ranges:
        part = cv.inRange(hsv, np.array(lower), np.array(upper))
        mask = part if mask is None else cv.bitwise_or(mask, part)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)  # 점 잡음 제거
    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)  # 구멍 메우기
    return mask


def find_target(mask):
    """가장 큰 덩어리 하나를 (x, y, w, h) 로. 없으면 None."""
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)  # 4.x 는 2개
    if not contours:
        return None
    biggest = max(contours, key=cv.contourArea)  # 마지막 것이 아니라 가장 큰 것
    if cv.contourArea(biggest) < MIN_AREA:
        return None
    return cv.boundingRect(biggest)


def center_of(box):
    """박스의 중심. boundingRect 가 주는 (x, y) 는 왼쪽 위다."""
    if box is None:
        return None
    x, y, w, h = box
    return x + w // 2, y + h // 2


def main():
    ranges = COLOR_RANGES[TARGET]
    if TUNE:
        setup_tuner(ranges[0])

    frames = make_demo_frames() if SOURCE == "demo" else None
    cap = None if frames else cv.VideoCapture(SOURCE)
    if cap is not None and not cap.isOpened():
        raise SystemExit("영상을 열지 못했습니다. 카메라 권한 또는 경로 확인")

    seen = 0
    try:
        while True:
            if frames is not None:
                frame = next(frames, None)
                if frame is None:
                    break
            else:
                ok, frame = cap.read()
                if not ok:
                    break
                frame = cv.resize(frame, (FRAME_W, FRAME_H))
                frame = cv.flip(frame, 1)  # 거울 모드 — 내 오른쪽이 화면 오른쪽

            if TUNE:
                ranges = read_tuner()
            mask = make_mask(frame, ranges)
            box = find_target(mask)
            center = center_of(box)
            if center is not None:
                seen += 1

            if box is not None:
                x, y, w, h = box
                cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), 3)
                cv.circle(frame, center, 5, (255, 0, 255), -1)
                cv.putText(frame, f"{center}", (x, max(y - 10, 20)),
                           cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

            if SHOW != "window":
                print(f"  center={center}")
                continue

            # 왼쪽 = 카메라 / 오른쪽 = 마스크. 마스크는 1채널이라 3채널로 바꿔야 붙는다
            view = np.hstack([frame, cv.cvtColor(mask, cv.COLOR_GRAY2BGR)])
            cv.imshow("Color Tracker", view)
            if (cv.waitKey(30) & 0xFF) in (27, ord("q")):
                break
    finally:
        if cap is not None:
            cap.release()
        cv.destroyAllWindows()
        cv.waitKey(1)
        print(f"  물체를 찾은 프레임 {seen}개")


if __name__ == "__main__":
    main()
