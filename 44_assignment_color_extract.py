r"""44. [과제] 색상표에서 특정 색 추출하기 — `inRange` + `bitwise_and`

22 강 과제. 드론은 쓰지 않는다. `COLOR` 를 바꿔 가며 실행한다.

    COLOR = "blue"    강의 예제 (H 120)
    COLOR = "red"     **과제** (H 0 — 구간이 두 개)
    COLOR = "green"   H 60

[세 단계]
    ① BGR -> HSV          cv.cvtColor(img, cv.COLOR_BGR2HSV)
    ② 마스크 만들기        cv.inRange(hsv, 하한, 상한)
                          범위 안이면 255(흰), 밖이면 0(검) 인 **1채널 바이너리 이미지**
    ③ 마스크로 잘라내기    cv.bitwise_and(img, img, mask=마스크)
                          마스크가 흰 곳만 원본을 남기고 나머지는 검정

같은 원본을 `src1`, `src2` 에 두 번 넣는 게 이상해 보이지만, `bitwise_and` 는
`mask` 가 흰 곳만 계산하므로 결과가 "마스크 부분만 원본 그대로" 가 된다.

[과제의 핵심 — 빨강은 한 구간으로 안 된다]
강의는 `(0-10, 30, 30) ~ (0+10, 255, 255)` 로 쓴다. H 에 음수가 없으니 실제로는
**0~10 만** 검출되고 반대쪽 끝(170~179, 분홍 쪽 빨강)이 통째로 빠진다.
강의 화면에서 빨간 부채꼴이 반쪽만 나오는 게 이 때문이다. 두 구간을 따로 잡아 합쳐야 한다.

    mask1 = cv.inRange(hsv, (0, 30, 30),   (10, 255, 255))
    mask2 = cv.inRange(hsv, (170, 30, 30), (179, 255, 255))
    mask  = cv.bitwise_or(mask1, mask2)      # 둘 중 하나라도 흰색이면 흰색

색상환을 만들어 세어 본 결과 — 한 구간 4.3% / 두 구간 8.2% 로 **정확히 1.9 배** 차이가 났다.
(비교는 실행할 때마다 출력된다. 강의 방식이 얼마나 빠뜨리는지 숫자로 보라는 뜻)

[S·V 하한을 왜 거는가]
흰색·회색·검정도 H 는 0 이다(43 참고). S·V 최솟값을 안 걸면 색상환 한가운데의
흰 부분까지 빨강으로 잡힌다. 강의의 "적당한 값 30" 이 그 역할이고,
실제 사진에서는 조명 때문에 50~100 까지 올리는 경우가 많다.

[슬라이드 주석 오류]
`height, width = img_color.shape[:2]` 옆의 `가로 [0], 세로[1]` 은 반대다.
`shape[0]` 이 **높이(세로)**, `shape[1]` 이 **너비(가로)** 다. 변수 이름 순서가 맞다.

[색상환 이미지가 없어도 된다]
학습자료의 `color.png` 대신 색상환을 직접 그려서 쓴다(`make_color_wheel`).
각도를 그대로 H 로 넣고 중심에서 멀어질수록 S 를 올리면 색상환이 된다 —
43 에서 본 "H 는 각도" 가 그림으로 확인되는 부분이다.
쓸 이미지가 있으면 `IMAGE_PATH` 에 경로를 넣는다.
"""

import os
import tempfile

import cv2 as cv
import numpy as np

COLOR = "red"  # "red" (과제) / "blue" (강의) / "green"
SHOW = "none"  # "window" = 창 3개 / "plot" = matplotlib / "none" = 숫자만
SAVE = False  # True 면 마스크·결과 이미지를 파일로 저장

IMAGE_PATH = ""  # 비워 두면 색상환을 그려서 쓴다
WHEEL_SIZE = 400

H_RANGE = 10
S_MIN, V_MIN = 30, 30
BASE_H = {"red": 0, "green": 60, "blue": 120}


def make_color_wheel(size=WHEEL_SIZE):
    """H = 각도, S = 중심에서의 거리 인 색상환을 그린다."""
    center = (size - 1) / 2.0
    radius = size / 2.0 - 10
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    dx, dy = x - center, y - center
    dist = np.sqrt(dx * dx + dy * dy)

    angle = np.degrees(np.arctan2(-dy, dx)) % 360.0  # 0도 = 오른쪽 = 빨강
    h = (angle / 2.0).astype(np.uint8)  # OpenCV H 는 각도의 절반
    s = np.clip(dist / radius * 255, 0, 255).astype(np.uint8)  # 중심이 무채색
    v = np.full((size, size), 255, np.uint8)

    wheel = cv.cvtColor(cv.merge([h, s, v]), cv.COLOR_HSV2BGR)
    wheel[dist > radius] = (255, 255, 255)  # 원 바깥은 흰색
    return wheel


def ranges_for(color):
    """검출 범위를 만든다. 빨강만 구간이 두 개가 된다."""
    h = BASE_H[color]
    low, high = h - H_RANGE, h + H_RANGE
    if low < 0:
        return [((0, S_MIN, V_MIN), (high, 255, 255)),
                ((180 + low, S_MIN, V_MIN), (179, 255, 255))]
    return [((low, S_MIN, V_MIN), (high, 255, 255))]


def make_mask(hsv, ranges):
    """구간이 여러 개면 각각 마스크를 만들어 OR 로 합친다."""
    mask = None
    for lower, upper in ranges:
        part = cv.inRange(hsv, np.array(lower), np.array(upper))
        mask = part if mask is None else cv.bitwise_or(mask, part)
    return mask


def main():
    if IMAGE_PATH:
        img_color = cv.imread(IMAGE_PATH)
        if img_color is None:
            raise SystemExit(f"이미지를 읽지 못했습니다: {IMAGE_PATH}")
    else:
        img_color = make_color_wheel()

    # shape[0] = 높이(세로), shape[1] = 너비(가로). 슬라이드 주석과 반대가 맞다.
    height, width = img_color.shape[:2]
    total = height * width
    print(f"[원본] shape {img_color.shape}  (높이 {height}, 너비 {width})")

    img_hsv = cv.cvtColor(img_color, cv.COLOR_BGR2HSV)  # ① HSV 변환

    ranges = ranges_for(COLOR)
    print(f"[{COLOR}] 기준 H={BASE_H[COLOR]}  구간 {len(ranges)}개")
    for lower, upper in ranges:
        print(f"   {lower} ~ {upper}")

    img_mask = make_mask(img_hsv, ranges)  # ② 마스크
    img_result = cv.bitwise_and(img_color, img_color, mask=img_mask)  # ③ 잘라내기

    found = cv.countNonZero(img_mask)
    print(f"[검출] {found:,} / {total:,} 픽셀 ({found / total * 100:.1f}%)")

    # 빨강일 때만 — 강의 방식(한 구간)과 비교해서 얼마나 빠뜨리는지 본다.
    if len(ranges) > 1:
        half = cv.countNonZero(make_mask(img_hsv, ranges[:1]))
        print(f"   강의 방식(0~{H_RANGE} 한 구간)만 쓰면 {half:,} 픽셀 "
              f"({half / total * 100:.1f}%) — 두 구간이 {found / max(half, 1):.2f} 배")

    if SAVE:
        out_dir = tempfile.gettempdir()
        cv.imwrite(os.path.join(out_dir, f"result_{COLOR}_mask.png"), img_mask)
        cv.imwrite(os.path.join(out_dir, f"result_{COLOR}_extract.png"), img_result)
        print(f"[저장] {out_dir}/result_{COLOR}_mask.png, result_{COLOR}_extract.png")

    if SHOW == "plot":
        import matplotlib.pyplot as plt

        for i, (title, im, cmap) in enumerate(
            [("origin", cv.cvtColor(img_color, cv.COLOR_BGR2RGB), None),
             ("mask", img_mask, "gray"),
             ("result", cv.cvtColor(img_result, cv.COLOR_BGR2RGB), None)], 1
        ):
            plt.subplot(1, 3, i)
            plt.imshow(im, cmap=cmap)
            plt.title(title)
            plt.axis("off")
        plt.show()
    elif SHOW == "window":
        cv.imshow("img_origin", img_color)  # 원본
        cv.imshow("img_mask", img_mask)  # 바이너리 (검출 = 흰색)
        cv.imshow("img_result", img_result)  # 그 색만 남은 이미지
        print("\n창을 클릭해 포커스를 준 뒤 아무 키나 누르세요. (창을 닫아도 끝납니다)")
        while True:
            # macOS 는 X 버튼으로 닫으면 waitKey(0) 이 안 끝나는 경우가 있어
            # 짧게 끊어 기다리면서 창이 살아 있는지도 같이 본다.
            if (cv.waitKey(100) & 0xFF) != 255:
                break
            if cv.getWindowProperty("img_origin", cv.WND_PROP_VISIBLE) < 1:
                break
        cv.destroyAllWindows()
        cv.waitKey(1)


if __name__ == "__main__":
    main()
