r"""56. 수동 특징은 언제 무너지는가 — 숫자로 재 본다

26 강 1·3 장. 드론도 카메라도 쓰지 않는다(얼굴 실험만 사진 한 장이 필요하다).

22~24 강에서 만든 인식은 전부 **사람이 규칙을 정하는** 방식이다.
"H 는 85~105, S 는 60 이상, V 는 120 이상" 처럼 숫자를 손으로 고른다(수동 특징).
잘 도는 것처럼 보이지만, **그 숫자를 고를 때 가정한 조건에서 벗어나면 통째로 사라진다.**
얼마나 조금만 벗어나도 무너지는지 직접 재 보는 파일이다.

[실험 A — 색 임계값 (22~24 강 방식)]
`COLOR_RANGE` 를 기준 조명에서 맞춰 두고 조명만 바꿔 본다. 확인한 값:

    밝기 x1.0   H=95 S=200 V=230   검출 O
    밝기 x0.6   H=95 S=200 V=138   검출 O
    밝기 x0.5   H=95 S=200 V=115   **검출 X**  ← V 하한 120 에 걸린다
    붉은 조명   H=89 S=172 V=200   검출 O
    더 붉은 조명 H=81 S=159 V=200   **검출 X**  ← H 하한 85 를 넘어간다

조명이 **절반으로 어두워지는 것만으로** 물체가 없어진다. 흐릿하게 잡히는 게 아니라
마스크가 0 픽셀이 된다 — 프로그램 입장에서는 "아무것도 없다" 와 구분되지 않는다.
실습 때 "아까는 됐는데 지금은 안 된다" 의 정체가 대개 이것이다.

[실험 B — Haar Cascade (23 강 방식)]
`FACE_IMAGE` 에 얼굴이 있는 사진 경로를 넣으면 같은 방식으로 흔들어 본다.
얼굴 두 개(47x47, 58x58)짜리 사진으로 직접 재 본 값:

    회전   0도 2개 / 5도 3개(오검출 +1) / 10~15도 1개 / **20도 이상 0개**
    밝기   x0.3 ~ x1.6 전부 2개                      ← 의외로 밝기에는 강하다
    크기   x1.5 3개 / x1.0 2개 / **x0.75 이하 0개**   ← minSize 와 해상도 손실이 겹친다
    흐림   blur 9~15 에서 3개                        ← 흐리면 오검출이 늘기도 한다

**고개를 20도만 기울여도 얼굴이 사라진다.** Haar 특징이 "정면 얼굴의 명암 패턴" 을
가정하고 만들어졌기 때문이다. 반대로 밝기에는 강한데, 이는 명암의 **차이**를 보기 때문이다.
강의의 "조명·각도·배경이 바뀌면 성능이 급격히 떨어진다" 는 축마다 정도가 다르다.

[그래서 CNN 인가]
CNN 은 "무엇을 볼지" 를 사람이 정하지 않고 **데이터에서 배운다.** 기울어진 얼굴도, 어두운 얼굴도
데이터에 들어 있으면 그 변형까지 함께 배운다. 대신 데이터와 연산이 필요하다.
전통 방식이 틀린 게 아니라 **조건을 좁게 가정한 대신 가볍다** — 어느 쪽이 맞는지는 쓰는 자리가 정한다.
"""

import cv2 as cv
import numpy as np

# 기준 조명에서 맞춰 둔 색 범위 (50~52 의 skyblue 프리셋과 같다)
COLOR_RANGE = ((85, 60, 120), (105, 255, 255))
BALL_HSV = (95, 200, 230)  # 실험에 쓸 공의 색
MIN_AREA = 500

FACE_IMAGE = ""  # 얼굴이 있는 사진 경로를 넣으면 실험 B 도 돈다
SAVE_DIR = ""  # 경로를 주면 조건별 이미지를 저장한다


def make_scene(bright=1.0, tint=(1.0, 1.0, 1.0)):
    """공 하나가 있는 장면. bright 는 조명 세기, tint 는 색온도(BGR 배수)."""
    img = np.full((240, 320, 3), 60, np.uint8)
    ball = cv.cvtColor(np.uint8([[list(BALL_HSV)]]), cv.COLOR_HSV2BGR)[0][0].tolist()
    cv.circle(img, (160, 120), 45, ball, -1)
    channels = cv.split(img.astype(np.float32))
    scaled = [np.clip(c * t * bright, 0, 255) for c, t in zip(channels, tint)]
    return cv.merge(scaled).astype(np.uint8)


def detect_color(img):
    """고정된 색 범위로 물체를 찾는다. (마스크 픽셀 수, 물체 수, 공의 HSV)"""
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    mask = cv.inRange(hsv, np.array(COLOR_RANGE[0]), np.array(COLOR_RANGE[1]))
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, np.ones((5, 5), np.uint8))
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    found = [c for c in contours if cv.contourArea(c) >= MIN_AREA]
    return cv.countNonZero(mask), len(found), hsv[120, 160]  # 공 한가운데 픽셀


def experiment_color():
    lower, upper = COLOR_RANGE
    print(f"[실험 A] 색 임계값 — H {lower[0]}~{upper[0]}, S≥{lower[1]}, V≥{lower[2]} 로 고정")
    print("  조건            공의 HSV          마스크      검출")
    cases = [("기준", 1.0, (1, 1, 1))]
    cases += [(f"밝기 x{b}", b, (1, 1, 1)) for b in (0.8, 0.6, 0.5, 0.4, 1.3)]
    cases += [("붉은 조명", 1.0, (0.85, 1.0, 1.3)), ("더 붉은 조명", 1.0, (0.7, 1.0, 1.5)),
              ("푸른 조명", 1.0, (1.3, 1.0, 0.8))]
    for name, bright, tint in cases:
        img = make_scene(bright, tint)
        px, n, (h, s, v) = detect_color(img)
        mark = "O" if n else "X  <-- 사라짐"
        print(f"  {name:14s} H={h:3d} S={s:3d} V={v:3d}   {px:6,d}px   {mark}")
        if SAVE_DIR:
            cv.imwrite(f"{SAVE_DIR}/fragility_{name}.png", img)
    print("  → 밝기가 절반이 되면 V 하한에 걸려 '아무것도 없음' 이 된다.")


def experiment_face(path):
    """같은 사진을 회전·밝기·크기·흐림만 바꿔 가며 얼굴 수를 센다."""
    img = cv.imread(path)
    if img is None:
        raise SystemExit(f"사진을 읽지 못했습니다: {path}")
    cascade = cv.CascadeClassifier(cv.data.haarcascades + "haarcascade_frontalface_default.xml")
    if cascade.empty():  # OpenCV 5.x 에는 xml 이 없다 (48 참고)
        raise SystemExit('xml 로드 실패. pip install --only-binary=:all: "opencv-python<5"')

    def count(im):
        gray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
        return len(cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30)))

    h, w = img.shape[:2]
    print(f"\n[실험 B] Haar Cascade — {path}  (기준 {count(img)}개)")
    print("  회전:", end="")
    for angle in (0, 5, 10, 15, 20, 30, 45):
        matrix = cv.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
        rotated = cv.warpAffine(img, matrix, (w, h), borderValue=(255, 255, 255))
        print(f"  {angle}도={count(rotated)}", end="")
    print("\n  밝기:", end="")
    for alpha in (0.3, 0.5, 0.7, 1.0, 1.3, 1.6):
        print(f"  x{alpha}={count(cv.convertScaleAbs(img, alpha=alpha))}", end="")
    print("\n  크기:", end="")
    for scale in (0.25, 0.5, 0.75, 1.0, 1.5):
        print(f"  x{scale}={count(cv.resize(img, None, fx=scale, fy=scale))}", end="")
    print("\n  흐림:", end="")
    for k in (1, 5, 9, 15, 21):
        blurred = img if k == 1 else cv.GaussianBlur(img, (k, k), 0)
        print(f"  k{k}={count(blurred)}", end="")
    print("\n  → 각도에 약하고(20도면 0개) 밝기에는 강하다. 축마다 정도가 다르다.")


def main():
    experiment_color()
    if FACE_IMAGE:
        experiment_face(FACE_IMAGE)
    else:
        print("\n[실험 B] FACE_IMAGE 에 얼굴 사진 경로를 넣으면 Haar Cascade 도 흔들어 본다.")


if __name__ == "__main__":
    main()
