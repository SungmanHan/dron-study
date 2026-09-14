"""공통 유틸 — 코딩드론 USB 동글의 시리얼 포트를 찾는다.

macOS에서는 포트 이름(/dev/cu.usbmodemXXXX)이 USB 포트를 바꿔 꽂을 때마다
달라지므로, 이름을 하드코딩하지 않고 매번 탐색한다.
"""

from serial.tools.list_ports import comports

# 확인된 동글 식별자
#   macOS : /dev/cu.usbmodem31A9388730351  "STM32 Virtual ComPort in FS Mode"
#   기타   : CP210x 계열 동글은 SLAB_USBtoUART / usbserial 로 잡힌다
KEYWORDS = ("STM32", "usbmodem", "SLAB", "usbserial")


def find_port(verbose=True):
    """드론 동글로 보이는 첫 번째 포트를 반환한다. 없으면 RuntimeError."""
    for port, desc, _hwid in sorted(comports()):
        haystack = f"{port} {desc}".lower()
        if any(k.lower() in haystack for k in KEYWORDS):
            if verbose:
                print(f"[port] {port}  ({desc})")
            return port
    raise RuntimeError(
        "드론 동글을 찾지 못했습니다. USB 연결을 확인하세요.\n"
        "  - 허브/젠더를 거치면 인식이 불안정합니다. 본체 포트에 직접 연결하세요.\n"
        "  - 충전 전용 케이블은 데이터 통신이 되지 않습니다."
    )


if __name__ == "__main__":
    print(find_port())
