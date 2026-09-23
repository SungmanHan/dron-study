r"""47. 영상 저장 — `VideoWriter` (조용히 실패하는 자리가 셋)

23 강 예제4. `SOURCE` 를 `"demo"` 로 두면 카메라 없이도 저장 과정을 확인할 수 있다.

    writer = cv.VideoWriter(파일명, fourcc, fps, (너비, 높이))
    writer.write(frame)
    writer.release()        # ← 이게 파일을 완성한다

`fourcc` 는 코덱을 네 글자로 적은 것이다. `cv.VideoWriter_fourcc(*'mp4v')` 의 `*` 는
`'mp4v'` 를 `'m','p','4','v'` 네 글자로 풀어서 넘기는 문법이다.

[이 맥에서 열린 코덱]
    mp4v (.mp4)  DIVX (.avi)  XVID (.avi)  avc1 (.mp4)  MJPG (.avi)   — 다섯 다 isOpened() True

강의는 `DIVX` + `.avi` 를 쓰는데, macOS 기본 플레이어(QuickTime)가 avi 를 못 열기 때문에
`mp4v` + `.mp4` 가 편하다.

[조용히 실패하는 셋 — 직접 확인한 값]

1. **fps 가 0 이면 열리지 않는다.**
   맥 내장 카메라는 `cap.get(cv.CAP_PROP_FPS)` 를 0 으로 돌려주는 경우가 있다.
   그 값을 그대로 넘기면 `isOpened()` 가 **False** 가 되고, 이후 `write()` 는 아무 일도 안 한다.
   → 0 이면 30 같은 기본값으로 바꾼다.

2. **저장 크기와 프레임 크기가 다르면 아무것도 저장되지 않는다.**
   320x240 으로 연 writer 에 640x480 프레임 20 장을 넣어 봤다. 에러도 경고도 없고,
   결과 파일은 **257 바이트 / 0 프레임**. → 크기는 카메라에서 읽어 그대로 쓴다.

3. **`release()` 를 빠뜨리면 파일이 깨진다.**
   30 프레임을 쓰고 release 없이 끝낸 파일은 **44 바이트**였고, 다시 열면
   `moov atom not found` 와 함께 `isOpened()` 가 False 다. 강의 예제4 슬라이드에
   `out.release()` 가 빠져 있다. `try/finally` 로 보장한다.
   (정상 저장본은 27KB / 30 프레임 / fps 20 / 320x240 으로 읽혔다)

[재생 속도가 실제와 다르게 나올 때]
저장 파일의 재생 속도는 `fps` 인자가 정한다. 얼굴 인식처럼 무거운 처리가 끼면 실제로는
초당 10 장밖에 못 쓰는데 fps 30 으로 저장돼 **빨리 감기처럼** 보인다.
그래서 49 는 측정한 처리 속도를 fps 로 넣는다.
"""

import os
import tempfile
import time

import cv2 as cv
import numpy as np

SOURCE = "demo"  # 0 (카메라) / "파일경로" / "demo" (합성 영상)
SECONDS = 3  # 카메라일 때 녹화할 시간
CODEC, EXT = "mp4v", "mp4"  # ("DIVX", "avi") 도 열린다 — 맥에서는 mp4 가 편하다
SHOW = "none"  # "window" = 녹화하면서 보기 / "none"


def demo_frames(n=60, size=(320, 240)):
    """카메라 대신 쓸 프레임을 만들어 낸다."""
    w, h = size
    for i in range(n):
        frame = np.full((h, w, 3), 30, np.uint8)
        x = int(w / 2 + (w / 2 - 40) * np.sin(i / 8.0))
        cv.circle(frame, (x, h // 2), 24, (0, 200, 255), -1)
        cv.putText(frame, f"frame {i}", (10, 28), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        yield frame


def open_writer(path, fps, size):
    """writer 를 열고, 열렸는지 확인해서 돌려준다."""
    if not fps or fps <= 0:  # 함정 1 — 0 이면 열리지 않는다
        print(f"  fps 가 {fps} 라 30 으로 대체")
        fps = 30
    writer = cv.VideoWriter(path, cv.VideoWriter_fourcc(*CODEC), fps, size)
    if not writer.isOpened():
        raise SystemExit(f"저장 파일을 열지 못했습니다: {path} (코덱 {CODEC})")
    return writer


def main():
    path = os.path.join(tempfile.gettempdir(), f"record_out.{EXT}")
    writer = None
    written = 0
    started = time.time()

    try:
        if SOURCE == "demo":
            size = (320, 240)
            writer = open_writer(path, 20, size)
            for frame in demo_frames(size=size):
                writer.write(frame)  # 함정 2 — frame 크기가 size 와 같아야 한다
                written += 1
                if SHOW == "window":
                    cv.imshow("recording", frame)
                    if (cv.waitKey(30) & 0xFF) in (27, ord("q")):
                        break
        else:
            cap = cv.VideoCapture(SOURCE)
            if not cap.isOpened():
                raise SystemExit("영상을 열지 못했습니다. 카메라 권한 또는 경로 확인")
            try:
                # 저장 크기는 카메라에서 읽은 실제 값을 쓴다. get() 은 float 이라 round.
                size = (round(cap.get(cv.CAP_PROP_FRAME_WIDTH)),
                        round(cap.get(cv.CAP_PROP_FRAME_HEIGHT)))
                writer = open_writer(path, cap.get(cv.CAP_PROP_FPS), size)
                print(f"  저장 크기 {size}")
                while time.time() - started < SECONDS:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    writer.write(frame)
                    written += 1
                    if SHOW == "window":
                        cv.imshow("recording", frame)
                        if (cv.waitKey(1) & 0xFF) in (27, ord("q")):
                            break
            finally:
                cap.release()
    finally:
        # 함정 3 — 여기 못 오면 파일이 깨진 채로 남는다
        if writer is not None:
            writer.release()
        cv.destroyAllWindows()
        cv.waitKey(1)

    print(f"[저장] {path}")
    print(f"  쓴 프레임 {written}개 / 파일 {os.path.getsize(path):,} 바이트")

    # 저장이 제대로 됐는지는 다시 열어 보면 안다 (크기가 몇백 바이트면 함정 2·3 을 의심)
    cap = cv.VideoCapture(path)
    print(f"  다시 읽기: isOpened={cap.isOpened()}  "
          f"프레임수={int(cap.get(cv.CAP_PROP_FRAME_COUNT))}  "
          f"fps={cap.get(cv.CAP_PROP_FPS):.1f}  "
          f"크기={int(cap.get(cv.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))}")
    cap.release()


if __name__ == "__main__":
    main()
