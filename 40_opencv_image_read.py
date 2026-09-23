r"""40. OpenCV 로 이미지 읽고 보여주기 — `imread` / `imshow`

21 강 내용. 드론은 쓰지 않는다. `SHOW` 를 바꿔 가며 실행한다.

    SHOW = "window"   cv.imshow 로 창 띄우기 (강의 방식, 터미널에서 실행)
    SHOW = "plot"     matplotlib 으로 그리기 (주피터·headless 빌드용)

[강의 코드 세 줄]
    img = cv.imread('C:\image\drone.jpg')      # 컬러로 읽기
    img = cv.imread('C:\image\drone.jpg', 0)   # 흑백으로 읽기
    cv.imshow('window_title', img)              # 창으로 보여주기

두 번째 인자는 읽는 방식이고 숫자에 이름이 붙어 있다.

    cv.IMREAD_COLOR      =  1   생략하면 이것 (컬러, 투명도 버림)
    cv.IMREAD_GRAYSCALE  =  0   강의의 그 0
    cv.IMREAD_UNCHANGED  = -1   알파 채널까지 그대로

[imshow 만 쓰면 창이 안 뜬다]
슬라이드 코드를 그대로 치면 창이 안 그려지거나 회색 사각형인 채 멈춘다.
창을 그리는 일은 `waitKey()` 안에서 일어나기 때문이다. 항상 세 줄이 한 묶음이다.

    cv.imshow(제목, img)
    cv.waitKey(0)            # 0 = 아무 키나 누를 때까지 대기
    cv.destroyAllWindows()   # 창 닫기

`waitKey(밀리초)` 로 주면 그 시간만 기다리고, 그동안 키를 안 누르면 **-1** 을 돌려준다.
창의 X 버튼으로 닫으려 하지 말고 **창에 포커스를 준 채 키를 누를 것.**

[경로가 틀려도 예외가 안 난다]
`imread` 는 실패해도 멈추지 않고 **None 을 돌려준다.**

    [ WARN:0@0.09] global loadsave.cpp:278 findDecoder imread_('...'): can't open/read file

이 경고 한 줄만 찍히고 프로그램은 계속 돈다. 그래서 진짜 에러는 한참 뒤
`imshow` 나 `shape` 에서 엉뚱한 모습으로 터진다. **읽은 직후 None 검사가 정석이다.**

[윈도우 경로 주의 — 슬라이드 두 군데]
- 슬라이드의 `cv.imread(C:\image\drone.jpg')` 는 여는 따옴표가 빠져 SyntaxError 다.
- `'C:\image\drone.jpg'` 의 `\i` 처럼 백슬래시는 이스케이프 문자로 해석될 수 있다.
  `r'C:\image\drone.jpg'` (raw 문자열) 이나 `'C:/image/drone.jpg'` 로 쓴다.
  맥은 `'/Users/이름/image/drone.jpg'` 또는 그냥 상대경로.

[색 순서가 RGB 가 아니라 BGR 이다]
OpenCV 는 파랑-초록-빨강 순으로 저장한다. 파란 픽셀을 찍어 보면 `[255 0 0]` 이다.
cv 끼리 주고받을 땐 상관없지만 matplotlib 으로 그릴 때는 **RGB 로 바꿔야** 색이 맞는다.

    plt.imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB))
"""

import os
import tempfile

import cv2 as cv
import numpy as np

SHOW = "window"  # "window" = cv.imshow / "plot" = matplotlib

# 읽을 이미지 경로. 비워 두면 아래에서 샘플 이미지를 만들어 쓴다.
IMAGE_PATH = ""


def make_sample_image():
    """실습용 이미지를 직접 그려서 저장하고 그 경로를 돌려준다.

    영상이 숫자 배열이라는 걸 확인하는 용도도 겸한다 — 배열을 만들어 색을 칠하고,
    그 위에 도형과 글자를 얹은 뒤 파일로 저장한다. 색은 전부 BGR 순서다.
    """
    img = np.full((240, 320, 3), 40, np.uint8)  # 어두운 회색 배경
    cv.rectangle(img, (40, 60), (150, 180), (255, 0, 0), -1)  # 파랑 (B=255)
    cv.circle(img, (230, 120), 55, (0, 0, 255), -1)  # 빨강 (R=255)
    cv.putText(img, "drone", (90, 220), cv.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    path = os.path.join(tempfile.gettempdir(), "drone_sample.png")
    cv.imwrite(path, img)  # 저장 성공 여부도 True/False 반환 — 예외를 안 던진다
    return path


def show_with_window(color, gray):
    """강의 방식. 창 두 개를 띄우고 키 입력을 기다린다."""
    print("\n창이 뜨면 창을 클릭해 포커스를 준 뒤 아무 키나 누르세요. (X 버튼 말고)")
    cv.imshow("color", color)
    cv.imshow("gray", gray)
    key = cv.waitKey(0)  # 이 안에서 창이 실제로 그려진다
    cv.destroyAllWindows()
    print(f"누른 키 코드: {key}  (시간 제한을 줬는데 안 눌렀으면 -1)")


def show_with_plot(color, gray):
    """주피터·headless 빌드용. BGR -> RGB 변환이 필요하다."""
    import matplotlib.pyplot as plt

    plt.subplot(1, 2, 1)
    plt.imshow(cv.cvtColor(color, cv.COLOR_BGR2RGB))  # 이걸 빼면 파랑↔빨강이 뒤바뀐다
    plt.title("color")
    plt.axis("off")

    plt.subplot(1, 2, 2)
    plt.imshow(gray, cmap="gray")  # 흑백은 cmap 을 지정해야 회색으로 나온다
    plt.title("gray")
    plt.axis("off")

    plt.show()


def main():
    path = IMAGE_PATH or make_sample_image()
    print(f"[경로] {path}")

    color = cv.imread(path)  # 생략 = IMREAD_COLOR(1)
    gray = cv.imread(path, 0)  # 0 = IMREAD_GRAYSCALE

    # 읽은 직후 검사. 실패해도 예외가 아니라 None 이라 여기서 안 막으면 뒤에서 터진다.
    if color is None or gray is None:
        raise SystemExit(f"이미지를 읽지 못했습니다. 경로를 확인하세요: {path}")

    print(f"[컬러] shape {color.shape}  dtype {color.dtype}")
    print(f"[흑백] shape {gray.shape}      dtype {gray.dtype}")
    print(f"[BGR ] 파란 사각형 한 점 = {color[120, 100]}  <- B,G,R 순서라 파랑이 맨 앞")

    if SHOW == "plot":
        show_with_plot(color, gray)
    else:
        show_with_window(color, gray)


if __name__ == "__main__":
    main()
