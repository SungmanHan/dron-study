r"""42. 템플릿 매칭 — 여러 사진 중에서 원하는 드론 찾기

22 강 내용. 드론은 쓰지 않는다. `MODE` 를 1~3 으로 바꿔 가며 실행한다.

    1  장면에서 잘라낸 템플릿      -> 정확히 찾는다 (강의가 보여주는 상황)
    2  크기가 다른 템플릿          -> 못 찾는다. `SCALE_SEARCH = True` 면 다시 찾는다
    3  장면에 없는 대상            -> **그래도 사각형은 그려진다**

[원리]
템플릿을 장면 위에 왼쪽 위부터 한 칸씩 밀면서 매 위치의 유사도를 계산해 점수 배열을 만들고,
그중 가장 좋은 곳을 고른다. 점수 배열 크기는 `(장면높이 - 템플릿높이 + 1, 장면너비 - 템플릿너비 + 1)`
이라 **템플릿이 장면보다 크면 계산 자체가 안 된다**(`cv.error`).

    cv.matchTemplate(장면, 템플릿, 방법)  -> 점수 배열
    cv.minMaxLoc(배열)                    -> (최솟값, 최댓값, 최솟값 위치, 최댓값 위치)
    cv.rectangle(img, 시작점, 끝점, 색, 두께)   색은 BGR — (0,0,255) 가 빨강

[방법을 바꾸면 minLoc / maxLoc 도 같이 바뀐다]

    TM_SQDIFF          차이의 제곱합. **작을수록** 비슷 -> minLoc  (강의가 쓰는 방법)
    TM_CCOEFF_NORMED   상관계수 -1~1.   클수록 비슷    -> maxLoc

강의처럼 `TM_SQDIFF` 를 쓰면 점수가 몇십억짜리 절대값이라 **얼마나 잘 맞았는지 알 수 없다.**
"찾았다 / 못 찾았다" 를 구분하려면 정규화된 `TM_CCOEFF_NORMED` 로 바꾸고
`maxVal > 0.8` 같은 기준을 건다. 대상이 없어도 함수는 늘 가장 덜 다른 자리를 돌려주므로,
기준값이 없으면 **엉뚱한 곳에 사각형이 그려질 뿐 아무도 실패를 알려주지 않는다.**

[학습자료실 이미지로는 강의대로 안 된다 — 직접 돌려 본 결과]
22 차시 이미지 5장(드론 4대가 한 장에 있는 `드론전체이미지.jpg` + 드론 1~4 개별 png)으로
강의 코드를 그대로 돌리면 실패한다. 개별 png 가 전체 이미지에서 **잘라낸 조각이 아니라
따로 찍은 사진**이라 크기도 각도도 다르기 때문이다. 전체 이미지는 773x987 인데
개별 파일은 638x698 / 366x510 / 767x767 / 615x895 로, 장면 속 드론보다 오히려 크다.

    원래 크기 그대로 (강의 방식)  TM_CCOEFF_NORMED 최고 점수 0.03 / 0.22 / 0.13 / -0.06
    크기를 바꿔 가며 찾기          0.96(분홍) / 0.61(하늘색) / 0.23(빨강) / 0.44(볼)

분홍 드론만 0.96 으로 제대로 찾혔다(0.56 배로 줄였을 때). 빨강 프로펠러 드론은 크기를
맞춰도 0.23 인데, 개별 사진과 장면 속 드론의 **각도가 다르기** 때문이다.
템플릿 매칭은 크기·각도가 같을 때만 쓸 수 있다는 한계가 그대로 드러난다.
그래서 이 파일은 기본값으로 장면을 직접 그려서 쓴다.

[직접 그린 장면에서 세 모드를 돌린 결과 (TM_CCOEFF_NORMED)]

    MODE 1  점수 1.000  위치 오차 0 픽셀           — 같은 조각이니 당연히 만점
    MODE 2  점수 0.555  엉뚱한 자리                — 0.6 배로 줄였을 뿐인데 못 찾는다
    MODE 2 + SCALE_SEARCH  배율 1.65 에서 0.988, 오차 (1, 2) 픽셀
    MODE 3  점수 0.328  장면에 없는데도 좌표가 나온다 — 기준값이 없으면 이걸 정답으로 믿는다
"""

import cv2 as cv
import numpy as np

MODE = 1  # 1 = 같은 크기 / 2 = 크기가 다름 / 3 = 장면에 없는 대상
METHOD = "CCOEFF_NORMED"  # "CCOEFF_NORMED" (권장) 또는 "SQDIFF" (강의)
THRESHOLD = 0.8  # CCOEFF_NORMED 일 때 "찾았다" 로 볼 최소 점수
SCALE_SEARCH = False  # True 면 템플릿을 0.2~2.0 배로 바꿔 가며 찾는다
SHOW = "none"  # "window" = 결과 창 / "none" = 숫자만

# 강의 이미지를 쓰려면 두 경로를 채운다. 비워 두면 장면을 직접 그려서 쓴다.
SCENE_PATH = ""
TEMPLATE_PATH = ""

METHODS = {"SQDIFF": cv.TM_SQDIFF, "CCOEFF_NORMED": cv.TM_CCOEFF_NORMED}


def make_scene():
    """드론 4대 사진 대신 쓸 장면. 도형 네 개를 그리고 얼룩무늬를 입힌다.

    무늬가 없는 단색 도형이면 매칭이 성립하지 않는다 — 어디를 갖다 대도 똑같이 잘 맞아서
    점수는 높은데 위치가 엉뚱하게 나온다. 사진에 늘 있는 잔무늬를 흉내 내는 셈이다.
    잡음을 픽셀 단위로 뿌리면 크기를 바꿀 때 무늬가 뭉개져 없어지므로,
    작게 만들어 키워서 **크기가 변해도 살아남는 얼룩**으로 만든다.
    """
    rng = np.random.default_rng(22)  # 실행할 때마다 같은 무늬가 나오도록 고정
    scene = np.full((400, 500, 3), 245, np.uint8)
    cv.circle(scene, (110, 110), 60, (60, 60, 220), -1)  # 좌상 - 빨강 원
    cv.rectangle(scene, (300, 50), (430, 170), (220, 160, 40), -1)  # 우상 - 파랑 사각형
    cv.ellipse(scene, (110, 300), (70, 45), 20, 0, 360, (60, 190, 90), -1)  # 좌하 - 초록 타원
    pts = np.array([[310, 350], [370, 240], [430, 350]], np.int32)
    cv.fillPoly(scene, [pts], (40, 200, 230))  # 우하 - 노랑 삼각형

    small = rng.integers(0, 90, (400 // 16, 500 // 16, 3), dtype=np.int16).astype(np.uint8)
    blob = cv.resize(small, (500, 400), interpolation=cv.INTER_CUBIC)
    return np.clip(scene.astype(np.int16) - blob, 0, 255).astype(np.uint8)


def make_template(scene, mode):
    """장면에서 잘라내거나(1·2) 장면에 없는 것을 만든다(3). 정답 좌표도 같이 돌려준다."""
    if mode == 3:
        missing = np.full((90, 90, 3), 245, np.uint8)
        cv.drawMarker(missing, (45, 45), (200, 60, 200), cv.MARKER_CROSS, 70, 6)
        return missing, None  # 장면에 없다 = 정답이 없다

    x, y, w, h = 240, 190, 120, 120  # 우하 삼각형 언저리
    patch = scene[y:y + h, x:x + w].copy()
    if mode == 2:
        patch = cv.resize(patch, (int(w * 0.6), int(h * 0.6)))  # 크기를 바꾼다
    return patch, (x, y)


def match(scene_gray, template_gray, method):
    """한 번 매칭하고 (점수, 위치) 를 돌려준다. 방법에 따라 min/max 가 갈린다."""
    result = cv.matchTemplate(scene_gray, template_gray, method)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    if method == cv.TM_SQDIFF:
        return min_val, min_loc  # 차이라서 작을수록 좋다
    return max_val, max_loc


def match_multi_scale(scene_gray, template_gray, method):
    """템플릿 크기를 바꿔 가며 가장 좋은 결과를 고른다. (강의에는 없는 보완)"""
    best = None
    for scale in np.arange(0.2, 2.01, 0.05):  # 매 배율마다 매칭을 다시 한다 — 그만큼 느리다
        w = int(template_gray.shape[1] * scale)
        h = int(template_gray.shape[0] * scale)
        if w < 10 or h < 10 or h > scene_gray.shape[0] or w > scene_gray.shape[1]:
            continue
        resized = cv.resize(template_gray, (w, h))
        score, loc = match(scene_gray, resized, method)
        better = best is None or (score < best[0] if method == cv.TM_SQDIFF else score > best[0])
        if better:
            best = (score, loc, (w, h), scale)
    return best


def main():
    method = METHODS[METHOD]

    if SCENE_PATH and TEMPLATE_PATH:
        scene = cv.imread(SCENE_PATH)
        template = cv.imread(TEMPLATE_PATH)
        if scene is None or template is None:
            raise SystemExit("이미지를 읽지 못했습니다. SCENE_PATH / TEMPLATE_PATH 확인")
        answer = None
    else:
        scene = make_scene()
        template, answer = make_template(scene, MODE)

    # 매칭은 흑백으로 한다 — 1채널이라 빠르고 색 차이에 덜 흔들린다.
    scene_gray = cv.cvtColor(scene, cv.COLOR_BGR2GRAY)
    template_gray = cv.cvtColor(template, cv.COLOR_BGR2GRAY)
    print(f"[MODE {MODE}] 장면 {scene_gray.shape}  템플릿 {template_gray.shape}  방법 {METHOD}")

    # 템플릿이 장면보다 크면 여기서 cv.error 가 난다. 미리 걸러 준다.
    if (template_gray.shape[0] > scene_gray.shape[0]
            or template_gray.shape[1] > scene_gray.shape[1]):
        raise SystemExit("템플릿이 장면보다 큽니다. 템플릿은 장면보다 작아야 합니다.")

    if SCALE_SEARCH:
        score, loc, (w, h), scale = match_multi_scale(scene_gray, template_gray, method)
        print(f"  크기 탐색 결과 배율 {scale:.2f} -> {w}x{h}")
    else:
        score, loc = match(scene_gray, template_gray, method)
        h, w = template_gray.shape

    print(f"  점수 {score:,.4f}   위치(왼쪽 위) {loc}")

    # "찾았다" 판정. SQDIFF 는 절대값이라 기준을 세울 수 없다.
    if method == cv.TM_SQDIFF:
        print("  ! TM_SQDIFF 는 점수가 절대값이라 성공/실패를 판정할 수 없다")
        found = None
    else:
        found = score >= THRESHOLD
        print(f"  판정 {'찾음' if found else '못 찾음'} (기준 {THRESHOLD})")

    if answer is not None:
        off = (abs(loc[0] - answer[0]), abs(loc[1] - answer[1]))
        print(f"  정답 {answer} 과의 오차 {off} 픽셀")
    elif MODE == 3:
        print("  정답이 없는데도 좌표가 나왔다 — 대상이 없어도 함수는 늘 한 곳을 고른다")

    # 결과 그리기. 못 찾았으면 빨강 대신 회색으로 그려 구분한다.
    result_img = scene.copy()
    color = (0, 0, 255) if found is not False else (150, 150, 150)
    cv.rectangle(result_img, loc, (loc[0] + w, loc[1] + h), color, 2)

    if SHOW == "window":
        cv.imshow("template", template)
        cv.imshow("result", result_img)
        print("\n창을 클릭해 포커스를 준 뒤 아무 키나 누르세요.")
        cv.waitKey(0)
        cv.destroyAllWindows()
        cv.waitKey(1)


if __name__ == "__main__":
    main()
