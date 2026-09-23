r"""43. HSV 색공간 — 색을 H 하나로 고르기

22 강 내용. 이미지도 드론도 필요 없다. 숫자만 찍어 보는 파일이다.

[왜 BGR 이 아니라 HSV 인가]
BGR 은 조명이 어두워지면 세 값이 전부 내려간다. "빨강" 을 B·G·R 범위로 잡으려면
밝기마다 다른 조건을 써야 한다. HSV 는 밝기 변화가 주로 V 에만 반영되므로
**색의 종류는 H 하나로 거의 결정된다.** 그래서 "파란색 찾기" 가 `H 가 110~130` 이 된다.

    H (Hue, 색상)        색의 종류. 빛의 파장
    S (Saturation, 채도) 얼마나 선명한가. 0 에 가까우면 무채색(흰·회)
    V (Value, 명도)      얼마나 밝은가. 0 이면 검정

[슬라이드의 0~360 / 0~100 은 이론값이다]
OpenCV 는 한 칸이 8비트(0~255)라 그대로 담지 못한다.

    H  0~360°  ->  **0~179**   (÷2)
    S  0~100   ->  **0~255**   (×2.55)
    V  0~100   ->  **0~255**   (×2.55)

슬라이드의 "파랑 220~260°" 는 OpenCV 로 **110~130** 이다. 검출 코드의 그 숫자가 이것이다.

[함정 셋 — 아래에서 직접 확인한다]
1. **빨강은 두 구간이다.** H=0 이 색상환의 시작이자 끝이라 빨강이 0 과 179 양쪽에 걸친다.
   `0-10 ~ 0+10` 한 구간만 잡으면 **절반만 검출된다.**
2. **`uint8` 로 빼면 음수가 안 나온다.** `H(0) - 10` 은 `-10` 이 아니라 **246** 이다.
   numpy 2.x 는 경고라도 띄워 주지만(`overflow encountered`) 값은 그대로 246 이다.
   범위를 계산할 때는 `int()` 로 바꿔서 한다.
3. **흰색·회색·검정도 H 가 0 이다.** 빨강과 구분이 안 된다. 그래서 색 검출에서는
   H 만 보지 않고 **S·V 의 최솟값을 함께 건다**(강의의 "적당한 값 30").

[한 픽셀짜리 이미지]
`cvtColor` 는 이미지를 받는 함수라 색 하나를 변환하려면 1x1 이미지로 만들어 넘긴다.

    pixel = np.uint8([[[0, 0, 255]]])   # shape (1, 1, 3), BGR 순서
    cv.cvtColor(pixel, cv.COLOR_BGR2HSV)[0][0]

`np.uint8` 을 빼먹으면 int64 배열이 되어 `cvtColor` 에서 에러가 난다.
"""

import cv2 as cv
import numpy as np

H_RANGE = 10  # 기준 색에서 ±얼마까지 같은 색으로 볼 것인가 (강의의 '+_ 10')
S_MIN, V_MIN = 30, 30  # 무채색·어두운 픽셀 제외 (사진이면 50~100 까지 올린다)

# BGR 순서다. [255, 0, 0] 은 빨강이 아니라 파랑.
COLORS_BGR = {
    "빨강": (0, 0, 255),
    "노랑": (0, 255, 255),
    "초록": (0, 255, 0),
    "하늘": (255, 255, 0),
    "파랑": (255, 0, 0),
    "보라": (255, 0, 255),
    "흰색": (255, 255, 255),
    "회색": (128, 128, 128),
    "검정": (0, 0, 0),
}


def bgr_to_hsv(bgr):
    """BGR 색 하나를 HSV 로 바꾼다. 1x1 이미지로 만들어 cvtColor 에 넘긴다."""
    pixel = np.uint8([[bgr]])  # shape (1, 1, 3)
    return cv.cvtColor(pixel, cv.COLOR_BGR2HSV)[0][0]


def detect_range(h):
    """H 기준값에서 검출 범위를 만든다. 빨강이면 구간이 두 개가 된다."""
    h = int(h)  # uint8 그대로 빼면 음수가 246 으로 넘어간다
    low, high = h - H_RANGE, h + H_RANGE
    if low < 0:  # 빨강 쪽 — 0 아래로 내려간 만큼은 179 쪽에서 가져온다
        return [((0, S_MIN, V_MIN), (high, 255, 255)),
                ((180 + low, S_MIN, V_MIN), (179, 255, 255))]
    if high > 179:  # 179 를 넘어간 경우도 마찬가지로 0 쪽으로 돈다
        return [((low, S_MIN, V_MIN), (179, 255, 255)),
                ((0, S_MIN, V_MIN), (high - 180, 255, 255))]
    return [((low, S_MIN, V_MIN), (high, 255, 255))]


def main():
    print("[BGR -> HSV]  이론 H 는 OpenCV H 의 2배다")
    print(f"  {'색':4s} {'BGR':18s} {'H':>4s} {'S':>4s} {'V':>4s}   이론 H")
    for name, bgr in COLORS_BGR.items():
        h, s, v = bgr_to_hsv(bgr)
        print(f"  {name:4s} {str(bgr):18s} {h:4d} {s:4d} {v:4d}   {int(h) * 2}°")

    print("\n[무채색은 H 를 믿으면 안 된다]")
    for name in ("흰색", "회색", "검정"):
        h, s, v = bgr_to_hsv(COLORS_BGR[name])
        print(f"  {name} H={h} — 빨강과 같은 0 이다. 구분되는 건 S={s}, V={v}")
    print(f"  → 그래서 하한에 S>={S_MIN}, V>={V_MIN} 를 같이 건다")

    print("\n[uint8 로 빼면 음수가 안 나온다]")
    h_red = bgr_to_hsv(COLORS_BGR["빨강"])[0]
    with np.errstate(over="ignore"):  # numpy 2.x 는 경고를 띄운다. 값은 그대로 246
        wrong = h_red - np.uint8(H_RANGE)
    print(f"  uint8: {h_red} - {H_RANGE} = {wrong}   (기대한 값은 -10)")
    print(f"  int  : {int(h_red)} - {H_RANGE} = {int(h_red) - H_RANGE}")

    print(f"\n[검출 범위 (H ±{H_RANGE}, S·V 최솟값 {S_MIN})]")
    for name in ("파랑", "초록", "빨강"):
        h = bgr_to_hsv(COLORS_BGR[name])[0]
        ranges = detect_range(h)
        tail = "  <- 구간이 두 개다" if len(ranges) > 1 else ""
        print(f"  {name} H={h}")
        for lower, upper in ranges:
            print(f"      {lower} ~ {upper}{tail}")
            tail = ""


if __name__ == "__main__":
    main()
