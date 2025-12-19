import serial
import time


class RelayRS485:
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.ser = None

        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=8,
                parity=serial.PARITY_NONE,
                stopbits=1,
                timeout=0.5
            )
            time.sleep(0.2)
            print(f"RS485 connected: {self.port}")

        except Exception as e:
            print("RS485 init failed:", e)
            self.ser = None

    def relay_on(self, ch: int):
        if not self.ser:
            return
        # คำสั่งตัวอย่าง (ปรับตามบอร์ดจริงได้)
        cmd = bytes([0x01, 0x05, 0x00, ch - 1, 0xFF, 0x00])
        self.ser.write(cmd)

    def relay_off(self, ch: int):
        if not self.ser:
            return
        cmd = bytes([0x01, 0x05, 0x00, ch - 1, 0x00, 0x00])
        self.ser.write(cmd)
