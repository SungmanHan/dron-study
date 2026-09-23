r"""45. 영상 입력 — `VideoCapture` (카메라 / 동영상 파일)

23 강 내용. 드론은 쓰지 않는다. `SOURCE` 를 바꿔 실행한다.

    SOURCE = 0        카메라 (맥북 내장은 0번, 외장은 1, 2 …)
    SOURCE = "경로"   동영상 파일
    SOURCE = "demo"   합성 영상을 만들어 읽는다 — **카메라 없이 전 과정 확인용** (기본값)

`VideoCapture` 는 정수를 넣으면 카메라, 문자열을 넣으면 파일이다. 나머지 코드는 똑같다.

[한 프레임을 처리하는 골격]
    cap = cv.VideoCapture(SOURCE)
    while True:
        ret, frame = cap.read()     # ret: 읽었는지, frame: BGR numpy 배열
        if not ret:
            break                   # 카메라가 끊겼거나 파일이 끝났다
        ...                         # 여기서 프레임을 가공한다
        cv.imshow("frame", frame)
        if cv.waitKey(30) & 0xFF == 27:   # ESC
            break
    cap.release()

`ret` 을 확인하지 않고 바로 `imshow(frame)` 을 부르면, 카메라 권한이 없을 때
`frame` 이 `None` 이라 엉뚱한 에러가 난다. 강의 예제1 에 빠져 있는 줄이 `if not ret: break` 다.
`& 0xFF` 는 `waitKey` 반환값의 하위 8비트만 쓰겠다는 뜻이다(상위 비트가 섞여 오는 환경 대비).

[set() 은 명령이 아니라 요청이다]
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)   # 강의의 cap.set(3, 640) 과 같다
    cap.get(cv.CAP_PROP_FRAME_WIDTH)        # 실제로 적용된 값 (float)

카메라가 지원하지 않는 해상도면 가까운 값으로 바뀌거나 무시된다. **동영상 파일에 set 하면
아예 무시된다** — 320x240 파일에 640x480 을 요청해도 그대로 320x240 이었다.
숫자 3·4·5 는 각각 `CAP_PROP_FRAME_WIDTH` · `FRAME_HEIGHT` · `FPS` 다.

[끝나면 반드시 release]
카메라를 잡은 채로 프로그램이 죽으면 다음 실행에서 카메라가 안 열린다
(드론 실습에서 포트를 물고 죽던 것과 같은 상황이다). `try/finally` 로 감싼다.

[슬라이드 주석 오류]
`cv.flip(frame, 1)` 옆 주석이 "Flip camera vertically / 상하반전" 인데 **좌우 반전**이다.
상하 반전은 `flip(frame, 0)`, 둘 다는 `-1`.

[맥에서 카메라가 안 열릴 때]
시스템 환경설정 → 보안 및 개인 정보 보호 → 카메라 에서 터미널(또는 VS Code)을 허용해야 한다.
허용 전에는 `isOpened()` 가 False 이거나 검은 화면만 나온다.
"""

import os
import tempfile

import cv2 as cv
import numpy as np

SOURCE = "demo"  # 0 (카메라) / "파일경로" / "demo"
SHOW = "window"  # "window" = 창 / "none" = 숫자만 (카메라 없이 동작 확인)
GRAY_WINDOW = True  # 흑백 창도 같이 띄운다 (강의 예제2)
FLIP = True  # 좌우 반전 (거울 모드)
WAIT_MS = 30  # waitKey 대기. 30ms ≈ 초당 33프레임


def make_demo_video(seconds=3, fps=20, size=(320, 240)):
    """카메라 대신 쓸 영상을 만들어 저장하고 경로를 돌려준다."""
    path = os.path.join(tempfile.gettempdir(), "demo_source.mp4")
    writer = cv.VideoWriter(path, cv.VideoWriter_fourcc(*"mp4v"), fps, size)
    if not writer.isOpened():
        raise SystemExit("합성 영상을 만들지 못했습니다.")
    w, h = size
    for i in range(seconds * fps):
        frame = np.full((h, w, 3), 30, np.uint8)
        x = int(w / 2 + (w / 2 - 40) * np.sin(i / 8.0))
        cv.circle(frame, (x, h // 2), 24, (0, 200, 255), -1)
        cv.putText(frame, f"frame {i}", (10, 28), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        writer.write(frame)
    writer.release()  # 닫아야 파일이 완성된다 (47 참고)
    return path


def main():
    source = make_demo_video() if SOURCE == "demo" else SOURCE
    print(f"[소스] {source!r}")

    cap = cv.VideoCapture(source)
    if not cap.isOpened():
        raise SystemExit(
            "영상을 열지 못했습니다.\n"
            " - 카메라: 시스템 환경설정 > 보안 및 개인 정보 보호 > 카메라 권한 확인\n"
            " - 파일: 경로 확인"
        )

    # 요청은 해 보고, 실제로 뭐가 됐는지는 get 으로 확인한다.
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
    print(f"  적용된 크기 {int(cap.get(cv.CAP_PROP_FRAME_WIDTH))}"
          f"x{int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))}"
          f"  fps {cap.get(cv.CAP_PROP_FPS):.1f}")

    count = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:  # 파일이 끝났거나 카메라가 끊겼다. frame 은 None 이다
                print("  프레임을 더 읽지 못했습니다 (파일 끝 또는 카메라 중단)")
                break
            count += 1

            if FLIP:
                frame = cv.flip(frame, 1)  # 1 = 좌우 (0 = 상하, -1 = 둘 다)
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)  # 얼굴 인식이 쓰는 그 변환(48)

            if SHOW == "window":
                cv.imshow("frame", frame)
                if GRAY_WINDOW:
                    cv.imshow("gray", gray)
                key = cv.waitKey(WAIT_MS) & 0xFF
                if key in (27, ord("q")):  # ESC 또는 q
                    print("  키 입력으로 종료")
                    break
    finally:
        # 여기까지 못 오면 카메라가 잡힌 채로 남는다.
        cap.release()
        cv.destroyAllWindows()
        cv.waitKey(1)  # macOS 에서 창이 실제로 닫히도록
        print(f"  읽은 프레임 {count}개 — 해제 완료")


if __name__ == "__main__":
    main()
