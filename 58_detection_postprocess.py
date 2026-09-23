r"""58. 탐지 모델의 출력 다루기 — 신뢰도 · IoU · NMS

26 강 5 장. 모델 파일 없이, **탐지기가 뱉은 결과를 정리하는 부분**만 떼어 본다.
드론도 카메라도 필요 없다.

[YOLO 같은 1 단계 검출기의 출력은 "정답 박스" 가 아니다]
한 번의 순전파로 **수천 개의 후보 박스**가 나온다. 각각에 신뢰도(confidence)와
클래스 확률이 붙어 있고, 같은 물체 하나에 박스가 여러 개 겹쳐 나온다.
쓸 수 있는 결과로 만들려면 두 단계를 거친다.

    ① 신뢰도 임계값   score < 0.5 같은 것들을 버린다
    ② NMS            겹치는 박스 중 점수가 가장 높은 것만 남긴다

이 두 가지는 모델이 아니라 **후처리**다. 그래서 모델 없이도 그대로 해 볼 수 있다.

[IoU — 두 박스가 얼마나 겹치는가]
    IoU = 교집합 넓이 / 합집합 넓이       (0 = 안 겹침, 1 = 완전히 같음)
NMS 는 "점수가 가장 높은 박스를 하나 고르고, 그것과 IoU 가 기준 이상인 박스를 버린다" 를
남는 박스가 없을 때까지 반복한다. 손으로 20 줄이면 짜진다(아래 `nms_manual`).

[OpenCV 에 이미 들어 있다]
    keep = cv.dnn.NMSBoxes(boxes, scores, score_threshold, nms_threshold)
`boxes` 는 `[x, y, w, h]` 목록, 반환은 **남길 인덱스 배열**이다.
이 파일은 손으로 짠 NMS 와 `cv.dnn.NMSBoxes` 결과가 같은지 맞춰 본다(직접 돌려 보면 일치한다).

[임계값이 결과를 바꾼다]
    NMS 임계값이 낮다 → 조금만 겹쳐도 지운다 → 붙어 있는 물체 둘을 하나로 만들 수 있다
    NMS 임계값이 높다 → 잘 안 지운다 → 한 물체에 박스가 여러 개 남는다
정답은 장면마다 다르다. 아래 스윕으로 감을 잡는다.

[실제 모델을 붙이려면 — 이 저장소에는 모델 파일이 없다]
    net = cv.dnn.readNet("yolo.onnx")                       # 모델 파일 (수십 MB)
    blob = cv.dnn.blobFromImage(frame, 1/255, (640, 640),   # 크기·스케일을 모델에 맞춘다
                                swapRB=True, crop=False)
    net.setInput(blob); out = net.forward()                 # 후보 박스 수천 개
    ... 신뢰도 임계값 + NMSBoxes ...                          # 여기가 이 파일의 내용

`cv.dnn` 모듈 자체는 설치된 OpenCV 에 들어 있다(아래에서 확인한다). 없는 것은 **학습된 가중치 파일**뿐이다.
크고 라이선스도 제각각이라 저장소에 넣지 않았다. 모델을 구하면 위 네 줄이면 붙는다.
"""

import os
import tempfile

import cv2 as cv
import numpy as np

SCORE_THRESHOLD = 0.5  # 이보다 낮은 후보는 버린다
NMS_THRESHOLD = 0.4  # 이보다 많이 겹치면 점수 낮은 쪽을 버린다

# 한 장면의 후보들. 물체는 셋인데 박스는 여섯 — 겹친 것들이 같은 물체다.
# (x, y, w, h, score, 이름)
CANDIDATES = [
    (100, 80, 120, 140, 0.92, "person-A"),
    (108, 86, 118, 136, 0.85, "person-A 중복"),
    (95, 75, 130, 150, 0.61, "person-A 중복"),
    (300, 120, 90, 90, 0.88, "cup"),
    (305, 126, 88, 92, 0.55, "cup 중복"),
    (180, 300, 70, 60, 0.35, "약한 후보"),  # 신뢰도 임계값에서 걸린다
]


def iou(box_a, box_b):
    """두 박스의 겹침 비율. 박스는 (x, y, w, h)."""
    ax, ay, aw, ah = box_a
    bx, by, bw, bh = box_b
    left, top = max(ax, bx), max(ay, by)
    right, bottom = min(ax + aw, bx + bw), min(ay + ah, by + bh)
    inter = max(0, right - left) * max(0, bottom - top)
    if inter == 0:
        return 0.0
    return inter / float(aw * ah + bw * bh - inter)  # 합집합 = 둘의 합 − 교집합


def nms_manual(boxes, scores, score_threshold, nms_threshold):
    """점수가 높은 것부터 고르고, 그것과 많이 겹치는 것은 버린다."""
    order = [i for i in sorted(range(len(boxes)), key=lambda i: scores[i], reverse=True)
             if scores[i] >= score_threshold]  # ① 신뢰도 임계값
    keep = []
    while order:
        best = order.pop(0)
        keep.append(best)
        order = [i for i in order if iou(boxes[best], boxes[i]) <= nms_threshold]  # ② 겹치면 버린다
    return keep


def main():
    boxes = [c[:4] for c in CANDIDATES]
    scores = [c[4] for c in CANDIDATES]
    names = [c[5] for c in CANDIDATES]
    print(f"[후보] {len(boxes)}개 — 물체는 셋인데 박스는 여섯이다")
    for i, (box, score, name) in enumerate(zip(boxes, scores, names)):
        print(f"  {i} {name:14s} {box}  score={score:.2f}")

    print("\n[IoU] 같은 물체의 박스끼리는 크게 나온다")
    for a, b in ((0, 1), (0, 2), (3, 4), (0, 3)):
        print(f"  {a} vs {b}: {iou(boxes[a], boxes[b]):.3f}  ({names[a]} / {names[b]})")

    keep_manual = sorted(nms_manual(boxes, scores, SCORE_THRESHOLD, NMS_THRESHOLD))
    keep_cv = sorted(int(i) for i in cv.dnn.NMSBoxes(boxes, scores, SCORE_THRESHOLD, NMS_THRESHOLD))
    print(f"\n[NMS] score>={SCORE_THRESHOLD}, IoU>{NMS_THRESHOLD} 는 버린다")
    print(f"  손으로 짠 NMS       -> {keep_manual}  {[names[i] for i in keep_manual]}")
    print(f"  cv.dnn.NMSBoxes    -> {keep_cv}")
    print(f"  두 결과가 같은가: {keep_manual == keep_cv}")

    print("\n[임계값을 바꾸면]")
    print("  score  nms   남는 박스")
    for score_th in (0.3, 0.5, 0.9):
        for nms_th in (0.1, 0.4, 0.9):
            kept = cv.dnn.NMSBoxes(boxes, scores, score_th, nms_th)
            print(f"  {score_th:<6.1f}{nms_th:<5.1f} {len(kept)}개 {sorted(int(i) for i in kept)}")
    print("  → 신뢰도를 올리면 후보가 줄고, NMS 를 낮추면 겹친 박스를 더 많이 지운다.")

    print(f"\n[cv.dnn] 모듈 있음: {hasattr(cv, 'dnn')}  / readNet: {hasattr(cv.dnn, 'readNet')}"
          f" / blobFromImage: {hasattr(cv.dnn, 'blobFromImage')}")
    print("  없는 것은 학습된 가중치 파일뿐이다 — 구하면 위 docstring 의 네 줄로 붙는다.")

    # 결과를 그림으로 — 버린 박스는 회색, 남긴 박스는 초록
    canvas = np.full((420, 460, 3), 245, np.uint8)
    for i, (box, score) in enumerate(zip(boxes, scores)):
        x, y, w, h = box
        kept = i in keep_cv
        color = (60, 170, 60) if kept else (190, 190, 190)
        cv.rectangle(canvas, (x, y), (x + w, y + h), color, 2 if kept else 1)
        cv.putText(canvas, f"{score:.2f}", (x + 3, y + 18), cv.FONT_HERSHEY_SIMPLEX,
                   0.5, color, 2 if kept else 1)
    path = os.path.join(tempfile.gettempdir(), "nms_result.png")
    cv.imwrite(path, canvas)
    print(f"  그림 저장: {path} (초록 = 남은 박스)")


if __name__ == "__main__":
    main()
