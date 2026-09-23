r"""41. 흑백처리 — `imread(경로, 0)` 과 `cvtColor(BGR2GRAY)`

22 강 내용. 드론은 쓰지 않는다. 이미지가 없으면 샘플을 그려서 쓴다.

윤곽선·모양 검출 전에 흑백으로 바꾸는 일이 잦다. 채널이 1 개라 데이터가 1/3 이고,
조명·색 차이의 영향도 줄어든다. 방법은 두 가지다.

    ① cv.imread(경로, 0)                    읽을 때부터 1채널. 원본 컬러는 남지 않는다
    ② cv.cvtColor(img, cv.COLOR_BGR2GRAY)   컬러 원본을 두고 흑백본을 따로 만든다

이름이 `BGR2GRAY` 인 것은 OpenCV 가 BGR 로 읽기 때문이다. `2` 는 to.
색상 인식이 목적이면 ② 를 쓴다. **한 번 흑백이 된 이미지는 색을 되돌릴 수 없다.**
`cv.cvtColor(gray, cv.COLOR_GRAY2BGR)` 은 3채널로 늘려 줄 뿐, 세 채널 값이 모두 같아
여전히 회색이다(이 파일 마지막에서 확인한다).

[두 방법의 결과가 완전히 같지는 않다 — 강의에 없는 이야기]
같은 사진을 두 방법으로 읽어 픽셀을 빼 보면 차이가 있다. 강의 이미지로 측정한 값:

    PNG   최대 차이 1    (44만 픽셀 중 9만 개가 1 만큼 다름)  — 반올림 차이
    JPEG  최대 차이 12   (76만 픽셀 중 3만 개가 다름)         — 그 이상

JPEG 은 압축할 때 색을 밝기(휘도)와 색차로 나눠 저장한다. `imread(경로, 0)` 은 그
밝기 성분을 바로 꺼내 오고, `cvtColor` 는 컬러로 다 펼친 뒤 다시 계산하는 것으로 보인다
(경로가 다르다는 뜻이고, 어느 쪽이 틀린 건 아니다). 실습 결과가 눈에 띄게 달라지진 않지만
"두 방법은 같다" 고 말할 수는 없다.

[흑백 변환은 단순 평균이 아니다]
사람 눈이 초록에 민감한 것을 반영한 가중합이다.

    Gray = 0.299 * R + 0.587 * G + 0.114 * B

직접 계산한 값과 `cvtColor` 결과를 비교하면 차이가 최대 1(반올림)이다 — 아래에서 확인한다.
"""

import os
import tempfile

import cv2 as cv
import numpy as np

SHOW = "none"  # "window" = 창으로 비교 / "none" = 숫자만 (기본)

# 비교할 이미지. 비워 두면 샘플을 그려서 쓴다. 강의 이미지를 쓰려면 경로를 넣는다.
IMAGE_PATH = ""


def make_sample_image():
    """밝기 차이가 잘 보이도록 색이 다른 도형 몇 개를 그려 저장한다."""
    img = np.full((240, 360, 3), 255, np.uint8)
    cv.rectangle(img, (20, 40), (120, 200), (0, 0, 255), -1)  # 빨강 (BGR)
    cv.rectangle(img, (130, 40), (230, 200), (0, 255, 0), -1)  # 초록
    cv.rectangle(img, (240, 40), (340, 200), (255, 0, 0), -1)  # 파랑
    path = os.path.join(tempfile.gettempdir(), "gray_sample.png")
    cv.imwrite(path, img)
    return path


def main():
    path = IMAGE_PATH or make_sample_image()
    print(f"[경로] {path}")

    # ① 읽을 때 흑백으로
    gray1 = cv.imread(path, 0)  # 0 == cv.IMREAD_GRAYSCALE
    # ② 컬러로 읽고 변환
    color = cv.imread(path)
    if gray1 is None or color is None:
        raise SystemExit(f"이미지를 읽지 못했습니다: {path}")
    gray2 = cv.cvtColor(color, cv.COLOR_BGR2GRAY)

    print(f"  원본 컬러  shape {color.shape}   {color.nbytes:,} 바이트")
    print(f"  ① imread0  shape {gray1.shape}      {gray1.nbytes:,} 바이트 (1/3)")
    print(f"  ② cvtColor shape {gray2.shape}")

    # 두 방법의 차이 — 같은 그림이라도 픽셀 값은 딱 맞아떨어지지 않는다.
    diff = cv.absdiff(gray1, gray2)
    print("\n[① 과 ② 의 차이]")
    print(f"  최대 차이 {diff.max()} / 다른 픽셀 {int(np.count_nonzero(diff)):,} 개 / 전체 {diff.size:,} 개")

    # 가중합 공식 확인 — 사람 눈은 초록에 가장 민감하다.
    b, g, r = cv.split(color.astype(np.float64))
    manual = np.round(0.299 * r + 0.587 * g + 0.114 * b).astype(np.uint8)
    d = cv.absdiff(manual, gray2)
    print("\n[Gray = 0.299R + 0.587G + 0.114B]")
    print(f"  직접 계산 vs cvtColor  최대 차이 {d.max()} (0~1 이면 반올림 차이일 뿐 공식이 맞다는 뜻)")
    for name, bgr in (("빨강", (0, 0, 255)), ("초록", (0, 255, 0)), ("파랑", (255, 0, 0))):
        px = np.uint8([[bgr]])
        print(f"  {name} BGR{bgr} -> 밝기 {int(cv.cvtColor(px, cv.COLOR_BGR2GRAY)[0][0])}")
    print("  → 같은 255 라도 초록이 가장 밝고 파랑이 가장 어둡게 변환된다")

    # 되돌리기는 안 된다.
    back = cv.cvtColor(gray2, cv.COLOR_GRAY2BGR)
    print("\n[흑백은 되돌릴 수 없다]")
    print(f"  GRAY2BGR shape {back.shape} — 3채널이 되긴 한다")
    print(f"  세 채널 값이 전부 같은가: {bool((back[:, :, 0] == back[:, :, 2]).all())}  (= 여전히 회색)")
    print(f"  원본과 같은가: {bool((back == color).all())}")

    if SHOW == "window":
        cv.imshow("color", color)
        cv.imshow("gray1 (imread 0)", gray1)
        cv.imshow("gray2 (cvtColor)", gray2)
        print("\n창을 클릭해 포커스를 준 뒤 아무 키나 누르세요.")
        cv.waitKey(0)
        cv.destroyAllWindows()
        cv.waitKey(1)  # macOS 에서 창이 실제로 닫히도록 한 번 더


if __name__ == "__main__":
    main()
