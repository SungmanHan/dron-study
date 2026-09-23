r"""57. 합성곱이 하는 일 — 커널 · 특징맵 · 풀링

26 강 2·4 장. CNN 의 C(Convolution)가 실제로 무슨 계산인지 손으로 해 본다.
드론도 카메라도 필요 없고, 이미지가 없으면 직접 그려서 쓴다.

[합성곱 = 작은 숫자판을 이미지 위에 밀면서 곱하고 더하기]
3x3 커널 하나를 이미지 전체에 밀면서 겹친 부분끼리 곱해 더한 값을 새 그림에 적는다.
그 결과가 **특징맵(feature map)** 이고, 값이 큰 자리 = 그 커널이 찾는 무늬가 강한 자리다.

    세로 엣지 커널        가로 엣지 커널        블러(평균)
    -1  0  1             -1 -2 -1            1/9 씩 9칸
    -2  0  2              0  0  0
    -1  0  1              1  2  1

`cv.filter2D(img, -1, kernel)` 한 줄이면 된다. 커널마다 **반응하는 무늬가 다르다** —
직접 그린 그림에서 영역별 평균 반응을 재 보면 이렇다.

    커널              세로 막대   가로 막대   원
    세로 엣지          14.4       4.2      43.6
    가로 엣지           5.1      21.3      49.9

세로 커널은 세로 경계에, 가로 커널은 가로 경계에 3~4 배 세게 반응한다.
원은 모든 방향의 곡선이라 둘 다 크게 반응한다 — 이게 "특징" 이 뜻하는 것이다. 22 강에서 쓴 `morphologyEx` 도 같은 식으로
작은 창을 밀며 계산하는 연산이다 — 새로운 개념이 아니다.

[CNN 이 다른 점은 이 숫자를 사람이 안 정한다는 것]
위 커널의 −1, 0, 1 은 사람이 "세로 경계를 찾으려면 좌우 차이를 보면 되겠지" 하고 고른 값이다.
CNN 은 그 아홉 개 숫자를 **데이터로 학습해서 찾는다**(자동 특징 학습).
그래서 "무엇을 보면 되는지" 를 몰라도 되고, 사람이 생각 못 한 무늬도 쓴다.

[층을 쌓으면 보는 단위가 커진다]
1 층에서 나온 엣지 특징맵에 커널을 또 밀면, 2 층은 "엣지의 조합"(모서리·무늬)을 본다.
3 층은 그 조합(부품), 그다음은 물체 — 얕은 층은 선, 깊은 층은 의미를 본다.
이 파일은 1 층 → 풀링 → 2 층까지만 흉내 낸다.

[풀링 = 요약해서 크기 줄이기]
2x2 칸에서 가장 큰 값만 남기면(맥스 풀링) 크기가 절반이 된다.
계산량이 줄고, 물체가 한두 픽셀 움직여도 결과가 잘 안 변한다(위치에 덜 민감해진다).

[파라미터 개수 감각]
사람이 만드는 커널은 한두 개지만, CNN 은 한 층에 수십~수백 개를 두고 그걸 다 학습한다.
아래에서 층별 파라미터 수를 세어 본다 — "대량의 데이터가 필요하다" 는 말의 근거다.
"""

import os
import tempfile

import cv2 as cv
import numpy as np

IMAGE_PATH = ""  # 비우면 도형을 그려서 쓴다
SAVE = True  # 특징맵을 파일로 저장

KERNELS = {
    "vertical_edge": np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], np.float32),
    "horizontal_edge": np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], np.float32),
    "blur": np.ones((3, 3), np.float32) / 9.0,
    "sharpen": np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], np.float32),
}


def make_image():
    """세로선·가로선·대각선·원이 있는 그림. 커널마다 반응이 다르게."""
    img = np.full((200, 260), 40, np.uint8)
    cv.rectangle(img, (20, 30), (70, 170), 220, cv.FILLED)  # 세로로 긴 막대
    cv.rectangle(img, (90, 40), (240, 70), 200, cv.FILLED)  # 가로로 긴 막대
    cv.line(img, (100, 180), (240, 90), 255, 6)  # 대각선
    cv.circle(img, (170, 140), 25, 180, cv.FILLED)  # 원
    return img


def apply_kernel(img, kernel):
    """합성곱 한 번. 음수도 보려고 float 으로 계산한 뒤 0~255 로 정규화해 돌려준다."""
    raw = cv.filter2D(img.astype(np.float32), -1, kernel)
    shown = cv.normalize(np.abs(raw), None, 0, 255, cv.NORM_MINMAX).astype(np.uint8)
    return raw, shown


def max_pool(img, size=2):
    """2x2 칸에서 가장 큰 값만 남긴다 — 크기가 절반이 된다."""
    h, w = img.shape[0] // size * size, img.shape[1] // size * size
    tiles = img[:h, :w].reshape(h // size, size, w // size, size)
    return tiles.max(axis=(1, 3))


def count_params(in_ch, out_ch, k=3):
    """합성곱 한 층의 학습 대상 숫자 개수 = (커널 크기 x 입력 채널 + 편향) x 출력 채널."""
    return (k * k * in_ch + 1) * out_ch


def main():
    img = cv.imread(IMAGE_PATH, 0) if IMAGE_PATH else make_image()
    if img is None:
        raise SystemExit(f"이미지를 읽지 못했습니다: {IMAGE_PATH}")
    print(f"[입력] shape {img.shape}  (흑백 1채널)")

    out_dir = tempfile.gettempdir()
    maps = {}
    # 커널이 "무엇에" 반응하는지 — 영역별 평균 반응을 비교한다
    regions = {"세로 막대": (slice(30, 170), slice(20, 70)),
               "가로 막대": (slice(40, 70), slice(90, 240)),
               "원": (slice(115, 165), slice(145, 195))}
    print("\n[1층] 커널 하나 = 특징맵 하나")
    for name, kernel in KERNELS.items():
        raw, shown = apply_kernel(img, kernel)
        maps[name] = shown
        # 값이 가장 큰 자리 = 그 커널이 찾는 무늬가 가장 강한 자리
        y, x = np.unravel_index(np.argmax(np.abs(raw)), raw.shape)
        print(f"  {name:16s} 값 범위 {raw.min():7.0f} ~ {raw.max():7.0f}   가장 센 자리 (x={x}, y={y})")
        if SAVE:
            cv.imwrite(os.path.join(out_dir, f"conv_{name}.png"), shown)
        if not IMAGE_PATH and name.endswith("_edge"):  # 직접 그린 그림일 때만 위치를 안다
            parts = "  ".join(f"{rn} {np.abs(raw[rs]).mean():5.1f}" for rn, rs in regions.items())
            print(f"  {'':16s} 영역별 평균 반응  {parts}")

    print("\n[풀링] 2x2 최댓값만 남기기")
    pooled = max_pool(maps["vertical_edge"])
    print(f"  {maps['vertical_edge'].shape} -> {pooled.shape}   (칸 수 {maps['vertical_edge'].size:,} -> {pooled.size:,})")

    print("\n[2층] 1층 결과에 다시 커널을 민다 = 엣지의 조합을 본다")
    raw2, shown2 = apply_kernel(pooled, KERNELS["horizontal_edge"])
    print(f"  세로엣지 -> 풀링 -> 가로엣지   값 범위 {raw2.min():.0f} ~ {raw2.max():.0f}")
    if SAVE:
        cv.imwrite(os.path.join(out_dir, "conv_layer2.png"), shown2)
        print(f"  저장: {out_dir}/conv_*.png")

    print("\n[파라미터 수] 이 숫자를 전부 데이터로 맞춰 간다")
    layers = [("1층 3x3 커널 32개 (입력 3채널)", 3, 32),
              ("2층 3x3 커널 64개 (입력 32채널)", 32, 64),
              ("3층 3x3 커널 128개 (입력 64채널)", 64, 128)]
    total = 0
    for label, in_ch, out_ch in layers:
        n = count_params(in_ch, out_ch)
        total += n
        print(f"  {label:32s} {n:8,d}개")
    print(f"  {'합계 (작은 CNN 세 층)':32s} {total:8,d}개")
    print(f"  사람이 손으로 고른 이 파일의 커널은 {len(KERNELS) * 9}개였다.")


if __name__ == "__main__":
    main()
