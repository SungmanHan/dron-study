r"""49. [과제] 얼굴 · 눈 · 입 인식 + 라벨 + 녹화

23 강 과제. 웹캠 영상에서 얼굴/눈/입을 찾아 박스와 이름표를 그리고, `r` 로 녹화한다.

    r        녹화 시작 / 중지  (face_rec_날짜_시간.mp4)
    q / ESC  종료
    (영상 창을 클릭해 포커스를 준 뒤, **영문 입력 상태**에서 누를 것 — 한글이면 q 가 ㅂ 이 된다)

`SOURCE` 를 파일 경로로 바꾸면 카메라 없이도 같은 처리를 확인할 수 있다.
⚠️ OpenCV 4.x 가 필요하다(5.0 에는 분류기 자체가 없다 — 48 참고).

[부위별로 어디서 찾는가]

    Face  haarcascade_frontalface_default   화면 전체        파랑
    Eye   haarcascade_eye                   얼굴 위쪽 1/2    초록 (최대 2개)
    Lip   haarcascade_smile                 얼굴 아래쪽 1/3  빨강 (가장 큰 1개)

입술 전용 xml 은 기본 패키지에 없어서 `haarcascade_smile.xml`(입/미소)을 쓴다. 웃을 때 잘 잡힌다.
눈·입을 화면 전체에서 찾으면 콧구멍·입꼬리·배경까지 잡는다. **얼굴을 먼저 찾고 그 안의
일부 영역에서만** 찾는 게 요령이다. 잘라낸 좌표는 그 영역 기준이라 원본에 그리려면
잘라낸 위치를 더해야 한다(`x + ex`, `lower_top + ly`).

[과제 코드에서 손본 것]

1. **`eyes[:2]` 는 "가장 그럴듯한 둘" 이 아니다.** `detectMultiScale` 결과는 신뢰도 순이 아니라
   훑은 순서(위→아래, 왼→오)다. 앞의 두 개가 눈썹이나 콧구멍일 수 있다.
   → 넓이 순으로 정렬해서 큰 둘을 쓴다.
2. **`minSize=(80, 80)` 은 웹캠 전제다.** 사진 한 장으로 재 보니 47~58 픽셀짜리 얼굴은
   이 값에서 **하나도 안 잡혔다**(48 참고). 멀리 있는 얼굴까지 잡으려면 50 이하로 내린다.
3. **창의 X 버튼으로 닫으면 루프가 안 끝난다.** 키 입력만 보고 있기 때문.
   `getWindowProperty` 로 창이 살아 있는지도 같이 본다.
4. **녹화 fps 를 시작 직후의 측정값으로 잡으면 안 된다.** 이동평균이라 처음 몇 프레임은
   실제보다 낮게 나오고, 그 값으로 저장하면 영상이 느리게 재생된다.
   → 몇 프레임 지난 뒤의 값만 쓰고, 아니면 카메라 fps 로 되돌린다.
5. **`● REC` 표시는 녹화본에 남지 않는다.** `write()` 를 먼저 하고 그 뒤에 그리기 때문인데,
   과제 코드의 주석은 반대로 읽힌다. 화면에만 보이는 게 맞는 동작이라 순서는 그대로 뒀다.
6. 분류기 로드를 `main()` 안으로 옮겼다. 모듈 최상단에서 읽으면 **import 만 해도** 죽는다.

[남긴 것]
좌우 반전(예제2), 흑백 변환 + 검출(예제3), `putText` 라벨(2-7), 녹화(예제4),
`equalizeHist` 로 어두운 곳 보정, `try/finally` 로 카메라·파일 해제.
"""

import time

import cv2 as cv

SOURCE = 0  # 0 = 카메라 / "파일경로" (동영상)
SHOW = "window"  # "window" = 창 / "none" = 숫자만 (카메라 없이 동작 확인)
MIN_FACE = (80, 80)  # 웹캠 기준. 멀리 있는 얼굴까지 잡으려면 (50, 50) 이하로
FACE_NEIGHBORS = 6  # 배경이 얼굴로 잡히면 올리고, 잘 안 잡히면 5 로 내린다
LIP_NEIGHBORS = 15  # smile 분류기는 오검출이 많아 크게 준다
MAX_SECONDS = 0  # 0 = 무제한. 파일 소스 테스트용 제한

FACE_COLOR, EYE_COLOR, LIP_COLOR = (255, 0, 0), (0, 255, 0), (0, 0, 255)  # BGR
TEXT_COLOR = (255, 255, 255)
FONT = cv.FONT_HERSHEY_SIMPLEX
WINDOW = "Face / Eye / Lip Detection"


def load_cascade(filename):
    cascade = cv.CascadeClassifier(cv.data.haarcascades + filename)
    if cascade.empty():  # 경로가 틀려도 예외가 안 난다 → 직접 확인
        raise SystemExit(f"xml 로드 실패: {filename}\n  OpenCV 4.x 가 필요합니다 (현재 {cv.__version__})")
    return cascade


def draw_label(img, text, x, y, color):
    """박스 옆에 배경을 깐 이름표. 글자가 영상에 묻히지 않게."""
    (tw, th), baseline = cv.getTextSize(text, FONT, 0.6, 2)
    y = max(y, th + baseline + 2)  # 화면 위로 잘리지 않게
    cv.rectangle(img, (x, y - th - baseline - 2), (x + tw + 4, y), color, cv.FILLED)
    cv.putText(img, text, (x + 2, y - baseline), FONT, 0.6, TEXT_COLOR, 2, cv.LINE_AA)


def biggest(rects, n=1):
    """넓이가 큰 것부터 n 개. 검출 순서는 신뢰도 순이 아니다."""
    return sorted(rects, key=lambda r: r[2] * r[3], reverse=True)[:n]


def detect_and_draw(frame, cascades):
    """얼굴/눈/입을 찾아 그리고 얼굴 수를 돌려준다."""
    face_cascade, eye_cascade, lip_cascade = cascades
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)  # 분류기는 흑백 입력
    gray = cv.equalizeHist(gray)  # 밝기 평준화 — 어두운 방에서 인식률이 오른다

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1,
                                          minNeighbors=FACE_NEIGHBORS, minSize=MIN_FACE)
    for (x, y, w, h) in faces:
        cv.rectangle(frame, (x, y), (x + w, y + h), FACE_COLOR, 2)
        draw_label(frame, "Face", x, y, FACE_COLOR)

        # 눈 — 얼굴 위쪽 절반에서만. 슬라이싱은 [세로, 가로] 순서
        upper = gray[y:y + h // 2, x:x + w]
        eyes = eye_cascade.detectMultiScale(upper, scaleFactor=1.1, minNeighbors=10,
                                            minSize=(w // 8, w // 8))
        for (ex, ey, ew, eh) in biggest(eyes, 2):  # 큰 둘 = 눈일 가능성이 높다
            ex1, ey1 = x + ex, y + ey  # 잘라낸 영역 기준 → 원본 좌표
            cv.rectangle(frame, (ex1, ey1), (ex1 + ew, ey1 + eh), EYE_COLOR, 2)
            draw_label(frame, "Eye", ex1, ey1, EYE_COLOR)

        # 입 — 얼굴 아래쪽 1/3 에서만, 가장 큰 하나
        lower_top = y + h * 2 // 3
        lower = gray[lower_top:y + h, x:x + w]
        lips = lip_cascade.detectMultiScale(lower, scaleFactor=1.5, minNeighbors=LIP_NEIGHBORS,
                                            minSize=(w // 5, h // 10))
        for (lx, ly, lw, lh) in biggest(lips, 1):
            lx1, ly1 = x + lx, lower_top + ly
            cv.rectangle(frame, (lx1, ly1), (lx1 + lw, ly1 + lh), LIP_COLOR, 2)
            draw_label(frame, "Lip", lx1, ly1 + lh + 22, LIP_COLOR)  # 이름표는 박스 아래에
    return len(faces)


def start_recording(frame, fps):
    """지금 프레임 크기 그대로 mp4 녹화를 시작한다. 크기가 다르면 조용히 빈 파일이 된다(47)."""
    h, w = frame.shape[:2]
    filename = time.strftime("face_rec_%Y%m%d_%H%M%S.mp4")
    writer = cv.VideoWriter(filename, cv.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    if not writer.isOpened():  # fps 가 0 이면 여기서 걸린다
        print("녹화 파일을 열 수 없습니다:", filename)
        return None, None
    print(f"녹화 시작: {filename} ({w}x{h}, {fps}fps)")
    return writer, filename


def main():
    cascades = (load_cascade("haarcascade_frontalface_default.xml"),
                load_cascade("haarcascade_eye.xml"),
                load_cascade("haarcascade_smile.xml"))

    cap = cv.VideoCapture(SOURCE)
    if not cap.isOpened():
        raise SystemExit("카메라를 열 수 없습니다. "
                         "시스템 환경설정 > 보안 및 개인 정보 보호 > 카메라 권한을 확인하세요.")
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)

    cam_fps = cap.get(cv.CAP_PROP_FPS)
    if not cam_fps or cam_fps <= 0:  # 맥 내장 카메라는 0 을 돌려주기도 한다
        cam_fps = 30

    writer, filename = None, None
    frames = 0
    started = time.time()
    prev = started
    fps_now = 0.0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("프레임을 읽지 못했습니다.")
                break
            frames += 1
            if SOURCE == 0:
                frame = cv.flip(frame, 1)  # 거울 모드 (좌우 반전)

            face_count = detect_and_draw(frame, cascades)

            now = time.time()  # 이동평균으로 실제 처리 속도를 잰다
            fps_now = 0.9 * fps_now + 0.1 * (1.0 / max(now - prev, 1e-6))
            prev = now

            cv.putText(frame, f"Faces: {face_count}  FPS: {fps_now:.1f}", (10, 25),
                       FONT, 0.6, (0, 255, 255), 2, cv.LINE_AA)
            cv.putText(frame, "r: record   q/ESC: quit", (10, frame.shape[0] - 10),
                       FONT, 0.5, (200, 200, 200), 1, cv.LINE_AA)

            if writer is not None:
                writer.write(frame)  # 저장이 먼저 — 아래 REC 표시는 화면에만 남는다
                cv.circle(frame, (frame.shape[1] - 80, 20), 8, (0, 0, 255), cv.FILLED)
                cv.putText(frame, "REC", (frame.shape[1] - 65, 27), FONT, 0.6, (0, 0, 255), 2)

            if MAX_SECONDS and now - started > MAX_SECONDS:
                break
            if SHOW != "window":
                continue

            cv.imshow(WINDOW, frame)
            key = cv.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if key == ord("r"):
                if writer is None:
                    # 측정값은 몇 프레임 지난 뒤에야 쓸 만하다. 아니면 카메라 fps 로.
                    rec_fps = round(fps_now) if frames > 20 and fps_now > 1 else round(cam_fps)
                    writer, filename = start_recording(frame, rec_fps)
                else:
                    writer.release()
                    writer = None
                    print("녹화 저장 완료:", filename)
            if cv.getWindowProperty(WINDOW, cv.WND_PROP_VISIBLE) < 1:  # 창을 닫은 경우
                break
    finally:
        # 여기까지 못 오면 카메라가 잡힌 채로 남고, 녹화 파일은 깨진다(47).
        if writer is not None:
            writer.release()
            print("녹화 저장 완료:", filename)
        cap.release()
        cv.destroyAllWindows()
        cv.waitKey(1)
        print(f"처리한 프레임 {frames}개 — 해제 완료")


if __name__ == "__main__":
    main()
