"""공통 유틸 — 동글 포트 탐색(`find_port`) + 명령 완료 대기(`countdown`).

macOS에서는 포트 이름(/dev/cu.usbmodemXXXX)이 USB 포트를 바꿔 꽂을 때마다
달라지므로, 이름을 하드코딩하지 않고 매번 탐색한다.
"""

from time import sleep

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


def countdown(seconds, label=""):
    """남은 초를 찍으면서 기다린다 — 비행 명령의 "완료 대기" 용.

    비행 명령은 대부분 보내는 즉시 리턴한다(`sendControlWhile` 만 예외).
    드론이 실제로 다 움직이기 전에 다음 줄이 실행되면 명령이 서로 덮어쓰이므로,
    이동에 걸리는 시간만큼 파이썬 쪽에서 기다려 줘야 한다.

    그냥 `sleep(5)` 와 동작은 같고, 지금 뭘 기다리는지 눈에 보인다는 점만 다르다.
    대기 중 Ctrl+C 를 누르면 `KeyboardInterrupt` 가 올라와 호출한 쪽 `finally` 로 간다.
    """
    for i in range(int(seconds), 0, -1):
        print(f"  {label} {i}" if label else f"  {i}")
        sleep(1)


if __name__ == "__main__":
    print(find_port())
