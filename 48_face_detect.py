r"""48. 얼굴 인식 — Haar Cascade (`CascadeClassifier`)

23 강 예제3·5-2. `SOURCE` 를 바꿔 실행한다.

    SOURCE = 0          카메라 (강의 방식, 기본값)
    SOURCE = "사진.jpg"  이미지 한 장 — **카메라 없이 확인할 때**
    SOURCE = "영상.mp4"  동영상 파일

[⚠️ OpenCV 5.0 에는 이 기능이 아예 없다]
얼굴 인식은 `cv.CascadeClassifier` 와 미리 학습된 xml 파일로 한다. 그런데 **5.0 패키지에는
둘 다 빠져 있다.** 캐시에 남아 있던 5.0.0.93 휠을 열어 확인한 결과:

    cv2/data/        __init__.py 하나뿐 — haarcascade xml **0개**
    cv2.abi3.so      "CascadeClassifier" 문자열 **0건**

4.x 를 설치해야 한다. `--only-binary=:all:` 은 소스 컴파일로 새는 것을 막는다
(이 맥에서 pip 가 주는 최신 바이너리는 4.10.0.84 다. 그냥 `pip install opencv-python` 하면
5.0 을 소스에서 빌드하려 든다).

    pip install --only-binary=:all: "opencv-python<5"

[분류기 로드]
    cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')

`cv.data.haarcascades` 는 pip 로 깐 패키지 안의 xml 폴더 경로다(4.10 기준 xml 17 개).
**경로가 틀려도 에러가 안 난다** — 빈 분류기가 만들어지고 한참 뒤에 터진다.
`imread` 가 None 을 돌려주던 것과 같은 종류다. 로드 직후 `empty()` 로 확인한다.

xml 파일만 바꾸면 대상이 바뀐다 — `haarcascade_eye`(눈), `haarcascade_upperbody`(상체),
`haarcascade_frontalface_alt2`(정면 얼굴, 오검출이 조금 적음), `haarcascade_frontalcatface`(고양이).

[검출]
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

- 입력은 **흑백**이다. 밝기 차이로 특징을 찾기 때문.
- `scaleFactor` 1.1 = 10% 씩 줄여 가며 여러 크기를 본다. 작을수록 꼼꼼하고 느리다.
- `minNeighbors` 같은 자리에서 몇 번 겹쳐 잡혀야 인정할지. 클수록 오검출이 준다.
- 결과는 `(x, y, w, h)` 의 배열. 못 찾으면 빈 튜플이다.

[파라미터를 사진 한 장으로 재 보면 — minSize 가 더 결정적이다]
얼굴 두 개(47x47, 58x58)가 있는 사진에서:

    minNeighbors 3 / 5 / 6   -> 전부 2개 (차이 없음)
    minSize (30,30) / (50,50) -> 2개      minSize (80,80) -> **0개**

과제 코드의 `minSize=(80, 80)` 은 웹캠 앞 가까운 얼굴(보통 150~250 픽셀)에는 맞지만,
조금만 멀어지면 통째로 놓친다. `minNeighbors` 부터 만지기 전에 크기 조건을 먼저 본다.

[눈은 얼굴 안에서만 찾는다]
눈 분류기를 화면 전체에 돌리면 콧구멍·입꼬리까지 눈으로 잡는다. 얼굴을 먼저 찾고
그 안에서만 찾으면 오검출이 줄고 빨라진다. 잘라낸 영역(ROI)은 **원본 배열의 창문**이라
`roi_color` 에 그리면 `frame` 에도 그려진다 — 좌표를 더할 필요가 없다.

    roi_gray = gray[y:y + h, x:x + w]     # 슬라이싱은 [세로, 가로]
    roi_color = frame[y:y + h, x:x + w]

단, 얼굴이 충분히 커야 한다. 위 사진의 47~58 픽셀짜리 얼굴에서는 눈이 하나도 잡히지 않았다
(선글라스 탓도 있다). 웹캠 앞에서 실습하면 잘 잡힌다.

[한 가지 더 — 오검출은 실제로 일어난다]
같은 사진에 `haarcascade_profileface` 를 돌렸더니 사람 얼굴이 아닌 바닥 쪽에 1 개가 잡혔다
(minNeighbors 3). 박스가 그려졌다고 해서 거기에 얼굴이 있는 건 아니다.
"""

import os

import cv2 as cv

SOURCE = 0  # 0 = 카메라 / "파일경로" (이미지 또는 동영상)
FACE_XML = "haarcascade_frontalface_default.xml"  # alt2 로 바꾸면 오검출이 조금 준다
SCALE_FACTOR = 1.1
MIN_NEIGHBORS = 5
MIN_SIZE = (50, 50)
DRAW_EYES = True
SHOW = "window"  # "window" = 창 / "none" = 숫자만

IMAGE_EXT = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def load_cascade(filename):
    """분류기를 읽고 비었는지 확인한다. 경로가 틀려도 예외가 안 나기 때문."""
    cascade = cv.CascadeClassifier(cv.data.haarcascades + filename)
    if cascade.empty():
        raise SystemExit(
            f"xml 을 읽지 못했습니다: {filename}\n"
            f"  찾은 위치: {cv.data.haarcascades}\n"
            f"  OpenCV 5.x 에는 xml 이 없습니다. "
            f'pip install --only-binary=:all: "opencv-python<5"'
        )
    return cascade


def detect(frame, face_cascade, eye_cascade):
    """얼굴을 찾아 박스를 그리고, 얼굴 안에서만 눈을 찾는다. 찾은 얼굴 수를 돌려준다."""
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)  # Haar Cascade 는 흑백 입력
    faces = face_cascade.detectMultiScale(gray, scaleFactor=SCALE_FACTOR,
                                          minNeighbors=MIN_NEIGHBORS, minSize=MIN_SIZE)
    for (x, y, w, h) in faces:
        cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)  # 얼굴 = 파랑
        cv.putText(frame, "Face", (x, max(y - 8, 14)), cv.FONT_HERSHEY_SIMPLEX,
                   0.7, (255, 0, 0), 2)
        if not DRAW_EYES:
            continue
        # ROI 는 원본의 창문이라, roi_color 에 그리면 frame 에 그려진다
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = frame[y:y + h, x:x + w]
        for (ex, ey, ew, eh) in eye_cascade.detectMultiScale(roi_gray):
            cv.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)  # 눈 = 초록
    return len(faces)


def main():
    print(f"[분류기] {cv.data.haarcascades}")
    print(f"  설치된 xml {len([f for f in os.listdir(cv.data.haarcascades) if f.endswith('.xml')])}개"
          f" / OpenCV {cv.__version__}")
    face_cascade = load_cascade(FACE_XML)
    eye_cascade = load_cascade("haarcascade_eye.xml")

    # 이미지 한 장이면 루프 없이 한 번만 처리한다.
    if isinstance(SOURCE, str) and SOURCE.lower().endswith(IMAGE_EXT):
        frame = cv.imread(SOURCE)
        if frame is None:
            raise SystemExit(f"이미지를 읽지 못했습니다: {SOURCE}")
        print(f"  얼굴 {detect(frame, face_cascade, eye_cascade)}개")
        if SHOW == "window":
            cv.imshow("Face Detection", frame)
            cv.waitKey(0)
            cv.destroyAllWindows()
            cv.waitKey(1)
        return

    cap = cv.VideoCapture(SOURCE)
    if not cap.isOpened():
        raise SystemExit("영상을 열지 못했습니다. 카메라 권한(시스템 환경설정) 또는 경로 확인")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv.flip(frame, 1) if SOURCE == 0 else frame  # 카메라만 거울 모드
            count = detect(frame, face_cascade, eye_cascade)

            if SHOW != "window":
                continue
            cv.putText(frame, f"Faces: {count}", (10, 25), cv.FONT_HERSHEY_SIMPLEX,
                       0.7, (0, 255, 255), 2)
            cv.imshow("Face Detection", frame)
            # 영상 창을 클릭해 포커스를 준 뒤, 영문 상태에서 q 를 누른다 (한글이면 ㅂ 이 입력된다)
            if (cv.waitKey(1) & 0xFF) in (ord("q"), 27):
                break
    finally:
        cap.release()
        cv.destroyAllWindows()
        cv.waitKey(1)


if __name__ == "__main__":
    main()
