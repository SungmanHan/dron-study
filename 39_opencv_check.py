"""39. OpenCV 설치 확인 — 버전 / 중복 설치 / GUI 백엔드

21 강 내용. 드론은 쓰지 않는다. 영상 인식 실습 전에
`import cv2` 가 되는지, 그리고 **어떤 cv2 가 잡혔는지** 를 먼저 확인한다.

[패키지 이름과 모듈 이름이 다르다]
    pip install opencv-python   ->   import cv2
설치는 `opencv-python`, import 는 `cv2` 다. `import opencv` 는 없다.
`as cv` 는 별칭일 뿐이라 이후 `cv.imread(...)` 로 짧게 부를 수 있다.

[강의대로 둘 다 설치하면 안 된다]
슬라이드는 `opencv-python` 과 `opencv-contrib-python` 을 둘 다 깔라고 하는데,
두 패키지는 **같은 `cv2/` 디렉터리를 설치한다**
(설치된 `opencv-python` 의 dist-info RECORD 를 열어 보면 파일이 전부 `cv2/...` 였다. contrib 도 같은 자리다).
pip 는 파일을 합치지 않고 덮어쓰므로, 같이 깔면 나중에 설치한 쪽 파일 위에
앞의 것이 섞여 남아 버전 불일치나 기능 누락이 생긴다.
contrib 쪽이 메인 모듈을 포함하므로 **둘 중 하나만** 고른다.

    pip uninstall opencv-python opencv-contrib-python   # 섞였으면 둘 다 지우고
    pip install opencv-contrib-python                   # 하나만 다시

`opencv-python-headless` 는 GUI 를 뺀 빌드다. 이게 깔리면 `imshow` 가 에러를 낸다.
아래 GUI 항목이 `NONE` 으로 나오면 headless 를 의심한다.

[확인한 환경 — 슬라이드와 다른 점]
슬라이드 출력은 `4.4.0` (촬영 당시). 이 저장소에서 확인한 값은 **5.0.0** 이다.
버전이 다르다고 잘못된 게 아니다. `cv.__version__` 이 찍히면 설치는 성공한 것.

[영상은 숫자 행렬이다]
그래서 numpy 가 함께 필요하다. `imread` 가 돌려주는 것도 numpy 배열이고,
컬러는 `(높이, 너비, 3)`, 흑백은 `(높이, 너비)` 모양이다.
CodingDrone 이 numpy 를 이미 의존성으로 깔아 두므로 따로 설치할 일은 보통 없다.
"""

from importlib.metadata import PackageNotFoundError, version

OPENCV_PACKAGES = ("opencv-python", "opencv-contrib-python", "opencv-python-headless")


def check_module(name, label):
    """모듈 하나를 import 해 보고 버전을 찍는다. 없으면 설치 명령을 알려준다."""
    try:
        module = __import__(name)
    except ImportError:
        print(f"  [X] {label:<12} 없음 -> pip install {label}")
        return None
    print(f"  [O] {label:<12} {getattr(module, '__version__', '?')}")
    return module


def check_duplicate_install():
    """cv2 를 설치하는 패키지가 몇 개나 깔려 있는지 본다. 두 개 이상이면 섞인 상태다."""
    installed = []
    for name in OPENCV_PACKAGES:
        try:
            installed.append(f"{name}=={version(name)}")
        except PackageNotFoundError:
            pass

    print("\n[OpenCV 배포판]")
    for item in installed:
        print(f"  - {item}")
    if not installed:
        print("  - 없음 (pip 로 설치한 기록이 없다)")
    elif len(installed) > 1:
        print("  !! 같은 cv2 를 설치하는 패키지가 여러 개다. 하나만 남기고 지울 것.")


def main():
    print("[모듈]")
    cv = check_module("cv2", "opencv-python")
    check_module("numpy", "numpy")
    check_module("matplotlib", "matplotlib")

    check_duplicate_install()

    if cv is None:
        raise SystemExit("\ncv2 를 찾지 못했습니다. pip install opencv-contrib-python")

    # GUI 백엔드 — imshow 로 창을 띄울 수 있는 빌드인지 확인한다.
    # macOS 는 COCOA, 리눅스는 GTK/QT, headless 빌드는 NONE 으로 나온다.
    gui = "확인 실패"
    for line in cv.getBuildInformation().splitlines():
        if line.strip().startswith("GUI:"):
            gui = line.split(":", 1)[1].strip() or "NONE"
            break
    print(f"\n[GUI 백엔드] {gui}")
    if gui in ("NONE", ""):
        print("  !! 창을 띄울 수 없는 빌드다. 40 번은 SHOW = 'plot' 로 실행할 것.")

    # 영상 = 숫자 행렬. 빈 이미지를 직접 만들어 모양을 확인한다.
    import numpy as np

    color = np.zeros((40, 60, 3), np.uint8)  # 높이 40, 너비 60, 채널 3(BGR)
    gray = np.zeros((40, 60), np.uint8)  # 흑백은 채널이 없다
    print("\n[영상은 배열이다]")
    print(f"  컬러 shape {color.shape}  dtype {color.dtype}  (높이, 너비, 채널)")
    print(f"  흑백 shape {gray.shape}      dtype {gray.dtype}  (높이, 너비)")
    print(f"  한 칸의 값 범위 0 ~ 255 — 지금은 전부 {color[0, 0]} (검정)")


if __name__ == "__main__":
    main()
