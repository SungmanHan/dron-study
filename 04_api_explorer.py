"""04. 사용 가능한 명령/상수 목록 뽑기

CodingDrone 은 문서가 부실해서 라이브러리를 직접 들여다보는 편이 빠르다.
inspect 로 훑기 때문에 라이브러리 버전이 바뀌어도 실제 존재하는 것만 나온다.
"""

import enum
import inspect

from CodingDrone import protocol
from CodingDrone.drone import Drone


def command_rows():
    """Drone 클래스의 공개 메서드를 (이름, 시그니처, 설명) 으로 반환."""
    rows = []
    for name, fn in inspect.getmembers(Drone, inspect.isfunction):
        if name.startswith("_"):
            continue
        try:
            params = [
                str(p) for n, p in inspect.signature(fn).parameters.items() if n != "self"
            ]
            sig = "(" + ", ".join(params) + ")"
        except (ValueError, TypeError):
            sig = "(?)"
        doc = (inspect.getdoc(fn) or "").strip()
        rows.append((name, sig, doc.splitlines()[0] if doc else ""))
    return rows


def show_table(title, rows, sig_width=52, doc_width=40):
    if not rows:
        return
    w = max(len(r[0]) for r in rows)
    print(f"\n■ {title}  ({len(rows)}개)")
    print("-" * (w + sig_width + doc_width + 4))
    for name, sig, doc in sorted(rows):
        print(f"{name:<{w}}  {sig[:sig_width]:<{sig_width}}  {doc[:doc_width]}")


def show_commands():
    rows = command_rows()
    groups = {
        "전송 (send*)": [r for r in rows if r[0].startswith("send")],
        "조회 (get*)": [r for r in rows if r[0].startswith("get")],
        "설정 (set*)": [r for r in rows if r[0].startswith("set")],
        "연결/기타": [r for r in rows if not r[0].startswith(("send", "get", "set"))],
    }
    for title, group in groups.items():
        show_table(title, group)


def find(keyword):
    """이름으로 명령 검색. 예) find("takeoff")"""
    for name, sig, _doc in sorted(command_rows()):
        if keyword.lower() in name.lower():
            print(f"{name}{sig}")


def show_enum(name):
    obj = getattr(protocol, name, None)
    if not (inspect.isclass(obj) and issubclass(obj, enum.Enum)):
        print(f"{name}: 없음")
        return
    print(f"\n■ {name}")
    for m in obj:
        if isinstance(m.value, int):
            print(f"  {m.name:<24} = 0x{m.value:02X}")
        else:
            print(f"  {m.name}")


def list_all_enums():
    return [
        n
        for n, o in inspect.getmembers(protocol)
        if inspect.isclass(o) and issubclass(o, enum.Enum) and n != "Enum"
    ]


# 실습에서 실제로 쓰는 enum 만 추림.
# 각 enum 의 None_ 과 EndOfType 은 실제 명령이 아니라 경계값이므로 무시한다.
KEY_ENUMS = [
    "DeviceType",         # 통신 상대. Drone=0x10, Controller=0x20, Base(내 PC)=0x70
    "DataType",           # 패킷 종류. State=0x40, Attitude=0x41, Joystick=0x71
    "ModeControlFlight",  # 조종 모드. 보통 Attitude 사용
    "FlightEvent",        # TakeOff / Landing / Stop / Flip*
    "Direction",
    "Headless",
]


if __name__ == "__main__":
    show_commands()
    for n in KEY_ENUMS:
        show_enum(n)
    print("\n[protocol 의 모든 enum]")
    print(list_all_enums())
