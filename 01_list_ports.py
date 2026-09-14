"""01. 시리얼 포트 목록 확인

가장 먼저 해야 할 일. 동글이 OS에 인식되었는지 여기서 갈린다.

실행 결과 예시 (macOS):
    /dev/cu.Bluetooth-Incoming-Port          | n/a
    /dev/cu.usbmodem31A9388730351            | STM32 Virtual ComPort in FS Mode

Bluetooth-Incoming-Port 는 macOS 기본 포트이므로 무시한다.
STM32 Virtual ComPort 가 코딩드론 동글이다. CDC 방식이라 별도 드라이버가 필요 없다.

주의: macOS 에서는 /dev/tty.* 가 아니라 /dev/cu.* 를 써야 한다.
      tty 쪽은 open() 에서 블로킹된다.
"""

from serial.tools.list_ports import comports

if __name__ == "__main__":
    ports = sorted(comports())
    if not ports:
        print("포트가 하나도 없습니다. USB 연결을 확인하세요.")
    for port, desc, hwid in ports:
        print(f"{port:<42} | {desc}")
