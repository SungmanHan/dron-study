r"""63. YOLO 준비 확인 — 무엇을 깔고, 무엇을 받고, 무엇이 나오는가

29 강 1·2 장. 드론·카메라 없이 **설치 상태만** 점검한다. 추론은 다음 단계다
(강의도 이번 차시에는 모델을 로드만 하고 추론은 하지 않는다).

[객체 탐지 = 무엇이 + 어디에]
분류는 "이 사진은 개" 까지지만, 탐지는 **여러 개**의 대상마다 클래스·신뢰도·박스를 함께 낸다.
YOLO 는 이미지를 한 번만 신경망에 통과시켜 이걸 동시에 예측한다(26 강의 1 단계 검출기).

[설치]
    source .venv/bin/activate
    pip install ultralytics

`ultralytics` 하나만 적어도 **torch 가 함께 딸려 온다.** 지금까지 쓴 패키지들과 자릿수가 다른
용량이라(수백 MB 급) 설치에 시간이 걸린다. 디스크와 네트워크를 확인하고 시작할 것.

[모델 파일은 코드에 없다 — 처음 실행할 때 받는다]
    model = YOLO("yolo11n.pt")
이 줄이 파일을 찾지 못하면 Ultralytics 서버에서 가중치를 **자동으로 내려받아** 현재 작업 폴더에 둔다.
즉 첫 실행에는 인터넷이 필요하고, 실행한 폴더에 `.pt` 파일이 생긴다(이 저장소는 `.gitignore` 로 제외).

⚠️ 강의 자료 안에서 파일명이 갈린다 — 설명은 `yolov11n.pt`, 예제 코드는 `yolo11n.pt` 다.
공식 표기는 **v 가 없는 `yolo11n.pt`** 이고, 예제 코드 쪽이 맞다.

[크기별 라인업 — 실습에는 n]
    yolo11n.pt   nano    가장 가볍고 빠르다. 노트북 CPU·드론 영상용
    yolo11s.pt   small
    yolo11m.pt   medium
    yolo11l.pt   large
    yolo11x.pt   xlarge  가장 정확하지만 느리다

작업을 바꾸려면 이름만 바꾼다 — `yolo11n-seg.pt`(분할) `-pose.pt`(자세) `-cls.pt`(분류) `-obb.pt`(회전 박스).

[결과 객체의 모양]
    results = model.predict(source="사진.jpg", save=True)   # 이미지 1장 -> Results 1개짜리 리스트
    r = results[0]
    for box in r.boxes:
        cls_id = int(box.cls[0])               # 클래스 번호
        name   = r.names[cls_id]               # 이름 (COCO 80종: person, bus, cup …)
        conf   = float(box.conf[0])            # 신뢰도 0~1
        x1, y1, x2, y2 = box.xyxy[0].tolist()  # 좌상단·우하단 (픽셀)
    annotated = r.plot()                       # 박스가 그려진 **BGR** 배열 → 62 의 to_surface 로 넘기면 된다

`save=True` 면 `runs/detect/predict*/` 에 결과 이미지가 저장된다.
**신뢰도 임계값과 NMS 는 여기서도 그대로 쓰인다** — 58 에서 손으로 짠 그 후처리를
ultralytics 가 내부에서 해 주는 것뿐이다(`conf=`, `iou=` 인자로 조절한다).

[설치하지 않고도 갈 수 있는 길]
OpenCV 의 `cv.dnn` 은 이미 들어 있다(58 에서 확인). ONNX 로 변환된 모델 파일만 구하면
    net = cv.dnn.readNet("yolo.onnx")  →  blobFromImage  →  forward  →  NMSBoxes
로 torch 없이 추론할 수 있다. 대신 전처리·후처리를 직접 짜야 한다 —
ultralytics 는 그 편의를 대신 제공하는 쪽이다.
"""

import importlib.util
import os
import platform
import sys

MODEL_FILE = "yolo11n.pt"  # 이 폴더에 있으면 로드까지 해 본다 (없으면 받지 않는다)
DOWNLOAD = False  # True 로 바꾸면 모델이 없을 때 내려받는다 (인터넷 필요)

LINEUP = [("yolo11n.pt", "nano", "가장 가볍고 빠르다 — 실습용"),
          ("yolo11s.pt", "small", ""),
          ("yolo11m.pt", "medium", ""),
          ("yolo11l.pt", "large", ""),
          ("yolo11x.pt", "xlarge", "가장 정확하지만 느리다")]
TASKS = [("yolo11n.pt", "detect", "박스 + 클래스"),
         ("yolo11n-seg.pt", "segment", "픽셀 단위 분할"),
         ("yolo11n-cls.pt", "classify", "이미지 분류"),
         ("yolo11n-pose.pt", "pose", "사람 관절 좌표"),
         ("yolo11n-obb.pt", "obb", "회전된 박스")]


def installed(name):
    return importlib.util.find_spec(name) is not None


def main():
    print(f"[환경] Python {platform.python_version()} / {platform.system()} {platform.machine()}")
    print(f"  실행 폴더: {os.getcwd()}")

    print("\n[패키지]")
    for name in ("ultralytics", "torch", "cv2", "pygame", "numpy"):
        mark = "O" if installed(name) else "X"
        print(f"  [{mark}] {name}")

    if not installed("ultralytics"):
        print("\n  ultralytics 가 없습니다. venv 를 켠 뒤:")
        print("      pip install ultralytics")
        print("  torch 가 함께 딸려 오므로 용량이 큽니다(수백 MB 급). 시간이 걸립니다.")
    else:
        import ultralytics  # 설치돼 있을 때만 불러온다

        print(f"\n  ultralytics {ultralytics.__version__}")
        if installed("torch"):
            import torch

            print(f"  torch {torch.__version__} / CUDA 사용 가능: {torch.cuda.is_available()}")
            print("  (맥은 CUDA 가 없다. CPU 또는 mps 로 돈다 — nano 모델이면 쓸 만하다)")

    print("\n[모델 파일]")
    if os.path.exists(MODEL_FILE):
        size_mb = os.path.getsize(MODEL_FILE) / 1024 / 1024
        print(f"  {MODEL_FILE} 있음 ({size_mb:.1f} MB)")
        if installed("ultralytics"):
            from ultralytics import YOLO

            model = YOLO(MODEL_FILE)  # 파일이 있으니 내려받지 않는다
            names = getattr(model, "names", {}) or {}
            print(f"  로드 성공 — 클래스 {len(names)}종"
                  + (f" (예: {', '.join(list(names.values())[:5])} …)" if names else ""))
    else:
        print(f"  {MODEL_FILE} 없음 — `YOLO(\"{MODEL_FILE}\")` 첫 실행 때 자동으로 내려받는다(인터넷 필요).")
        if DOWNLOAD and installed("ultralytics"):
            from ultralytics import YOLO

            print("  DOWNLOAD = True 라 지금 받는다 …")
            YOLO(MODEL_FILE)
            print(f"  받음: {os.path.abspath(MODEL_FILE)}")
        else:
            print("  이 파일은 임의로 내려받지 않는다. 받으려면 DOWNLOAD = True.")

    print("\n[크기별 라인업]  뒤로 갈수록 정확하고 느리다")
    for filename, label, note in LINEUP:
        print(f"  {filename:16s} {label:7s} {note}")

    print("\n[작업별 파일명]  이름만 바꾸면 하는 일이 바뀐다")
    for filename, task, note in TASKS:
        print(f"  {filename:18s} {task:9s} {note}")

    print("\n[다음 단계] 62 의 화면에 `results[0].plot()` 을 넣으면 탐지 결과가 그려진다.")
    print("  ultralytics 없이 가려면 ONNX 모델 + cv.dnn (58 참고) — 전처리·후처리를 직접 짜야 한다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
