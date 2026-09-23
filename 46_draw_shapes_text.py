r"""46. 도형과 텍스트 그리기 — 빈 스케치북에 선 · 원 · 사각형 · 글자

23 강 내용. 영상도 드론도 필요 없다. 얼굴 인식에서 박스와 라벨을 그릴 때 쓰는 함수들이다.

[스케치북 만들기]
    img = np.zeros((480, 640, 3), np.uint8)   # (높이, 너비, 채널) — 전부 0 = 검정
    img[:] = (255, 255, 255)                  # 전체를 흰색으로
    img[100:200, 200:300] = (255, 255, 255)   # 일부만

`np.zeros` 의 모양은 `(높이, 너비)` 인데 `cap.set(640, 480)` 은 `(너비, 높이)` 순서다.
**배열은 세로가 먼저, 카메라 설정과 그리기 함수는 가로가 먼저**다. 이 파일에서 제일 헷갈리는 부분.

    슬라이싱        img[y시작:y끝, x시작:x끝]      세로 먼저
    그리기 함수     cv.line(img, (x, y), (x, y))   가로 먼저

[함수들]
    cv.line(img, 시작점, 끝점, 색, 두께, 선종류)
    cv.circle(img, **중심점**, 반지름, 색, 두께, 선종류)   ← 슬라이드는 "시작점" 이라고 적혀 있다
    cv.rectangle(img, 한 꼭짓점, 마주보는 꼭짓점, 색, 두께)
    cv.polylines(img, [좌표배열], 닫힘여부, 색, 두께, 선종류)
    cv.putText(img, 글자, 좌표, 글꼴, 크기, 색, 두께)

- 두께에 `-1`(= `cv.FILLED`)을 주면 속을 채운다.
- 사각형의 두 점은 **마주보는 꼭짓점이기만 하면** 된다. (오른쪽 위, 왼쪽 아래) 로 줘도 그려진다.
- `putText` 의 좌표는 글자의 **왼쪽 아래**다. y 를 너무 작게 주면 글자가 화면 위로 잘린다.
- 선 종류는 `LINE_4`(4방향) / `LINE_8`(기본) / `LINE_AA`(부드러움). 차이는 **대각선과 곡선**에서 보인다.
- 함수들은 새 이미지를 돌려주는 게 아니라 **넘긴 배열을 직접 고친다.** `img = cv.rectangle(img, ...)`
  처럼 다시 받을 필요가 없다(받아도 같은 배열이다).

[글꼴]
    FONT_HERSHEY_SIMPLEX          보통 산세리프
    FONT_HERSHEY_PLAIN            작은 산세리프
    FONT_HERSHEY_SCRIPT_SIMPLEX   필기체
    FONT_HERSHEY_TRIPLEX          세리프
    FONT_ITALIC                   기울임 — 단독 글꼴이 아니라 **다른 글꼴과 `|` 로 조합**한다

**한글은 나오지 않는다.** Hershey 글꼴에 한글 글리프가 없어서 `???` 로 찍힌다.
한글이 필요하면 Pillow 로 그린 뒤 numpy 배열로 되돌리는 방법을 쓴다.

[슬라이드에서 정리한 것]
- 원의 두 번째 인자는 "시작점" 이 아니라 중심점이다.
- 도형 예제에 `cv.destroyAllWindows()` 가 두 번 들어가 있다. 한 번이면 된다.
- 줄 끝의 `₩` 는 한글 윈도우 글꼴에서 백슬래시(`\`)가 그렇게 보이는 것이다. 맥에서는 `\`.
"""

import os
import tempfile

import cv2 as cv
import numpy as np

SHOW = "none"  # "window" = 창 / "none" = 파일로 저장만 (기본)
WIDTH, HEIGHT = 640, 480


def draw_shapes():
    """선 · 원 · 사각형 · 다각형. 색은 전부 BGR 순서다."""
    img = np.zeros((HEIGHT, WIDTH, 3), np.uint8)  # 검은 바탕

    # 슬라이싱으로 영역 칠하기 — [세로, 가로] 순서, 끝 값은 포함되지 않는다
    img[20:60, 20:120] = (255, 255, 255)  # y 20~59, x 20~119 (100 x 40)

    yellow, blue, red = (0, 255, 255), (255, 0, 0), (0, 0, 255)

    # 선 종류 비교 — 대각선에서 계단 모양 차이가 보인다
    cv.line(img, (50, 120), (400, 90), yellow, 3, cv.LINE_8)  # 기본
    cv.line(img, (50, 150), (400, 120), blue, 8, cv.LINE_4)  # 가장 거칠다
    cv.line(img, (50, 190), (400, 160), red, 13, cv.LINE_AA)  # 가장 매끄럽다

    # 원 — 두 번째 인자는 중심점. 두께 -1(FILLED) 이면 속을 채운다
    cv.circle(img, (200, 280), 50, yellow, 9, cv.LINE_8)  # 속 빈 원
    cv.circle(img, (350, 280), 50, yellow, cv.FILLED, cv.LINE_AA)  # 속 찬 원

    # 사각형 — 두 점은 마주보는 꼭짓점이면 순서가 어떻든 상관없다
    cv.rectangle(img, (560, 240), (460, 380), (60, 220, 60), 4)  # (오른쪽 위, 왼쪽 아래)
    cv.rectangle(img, (620, 300), (580, 420), (60, 220, 60), cv.FILLED)

    # 다각형 — 정수 좌표 배열을 리스트로 감싸서 넘긴다. True = 닫힌 도형
    pts = np.array([[80, 400], [160, 330], [240, 400], [160, 440]], np.int32)
    cv.polylines(img, [pts], True, (200, 100, 255), 3, cv.LINE_AA)
    return img


def draw_texts():
    """글꼴 다섯 가지 + 한글이 안 되는 것 확인."""
    img = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
    white = (255, 255, 255)
    fonts = [
        ("FONT_HERSHEY_SIMPLEX", cv.FONT_HERSHEY_SIMPLEX),
        ("FONT_HERSHEY_PLAIN", cv.FONT_HERSHEY_PLAIN),
        ("FONT_HERSHEY_SCRIPT_SIMPLEX", cv.FONT_HERSHEY_SCRIPT_SIMPLEX),
        ("FONT_HERSHEY_TRIPLEX", cv.FONT_HERSHEY_TRIPLEX),
        ("TRIPLEX | FONT_ITALIC", cv.FONT_HERSHEY_TRIPLEX | cv.FONT_ITALIC),
    ]
    for i, (name, font) in enumerate(fonts, 1):
        # 좌표는 글자의 왼쪽 아래. 50 픽셀씩 내려가며 한 줄씩
        cv.putText(img, "learning opencv python", (20, 50 * i), font, 1, white, 1)

    cv.putText(img, "hangul: 한글", (20, 320), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 255), 2)
    cv.putText(img, "^ ??? 로 나온다", (20, 360), cv.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 1)

    # 라벨 배경 — getTextSize 로 글자 크기를 먼저 재서 칸을 깔아 준다 (49 의 라벨이 이 방식)
    text = "Face"
    (tw, th), baseline = cv.getTextSize(text, cv.FONT_HERSHEY_SIMPLEX, 0.8, 2)
    x, y = 20, 430
    cv.rectangle(img, (x, y - th - baseline), (x + tw + 6, y), (0, 0, 255), cv.FILLED)
    cv.putText(img, text, (x + 3, y - baseline), cv.FONT_HERSHEY_SIMPLEX, 0.8, white, 2)
    print(f"  '{text}' 글자 크기 {tw}x{th}, baseline {baseline}")
    return img


def main():
    shapes = draw_shapes()
    texts = draw_texts()

    if SHOW == "window":
        cv.imshow("shapes", shapes)
        cv.imshow("texts", texts)
        print("창을 클릭해 포커스를 준 뒤 아무 키나 누르세요.")
        cv.waitKey(0)
        cv.destroyAllWindows()
        cv.waitKey(1)
    else:
        out = tempfile.gettempdir()
        cv.imwrite(os.path.join(out, "draw_shapes.png"), shapes)
        cv.imwrite(os.path.join(out, "draw_texts.png"), texts)
        print(f"  저장: {out}/draw_shapes.png, draw_texts.png")


if __name__ == "__main__":
    main()
