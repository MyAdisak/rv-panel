import serial
import time
import threading

def crc16(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF

class RelayRS485:
    """
    Relay via Modbus RTU (FC05 Write Single Coil)
    - ON  = 0xFF00
    - OFF = 0x0000
    - channel 1 => coil 0, channel 2 => coil 1, ...
    Works with ID=255 (0xFF) for broadcast (no reply expected).
    """

    def __init__(
        self,
        port: str = "/dev/ttyUSB0",
        baudrate: int = 9600,
        slave_id: int = 0xFF,   # 255 broadcast
        timeout: float = 0.2
    ):
        self.port = port
        self.baudrate = baudrate
        self.slave_id = slave_id & 0xFF
        self.timeout = timeout
        self._lock = threading.Lock()
        self._ser = None

    def open(self):
        if self._ser and self._ser.is_open:
            return
        self._ser = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=8,
            parity=serial.PARITY_NONE,
            stopbits=1,
            timeout=self.timeout
        )

    def close(self):
        if self._ser and self._ser.is_open:
            self._ser.close()

    def _send_fc05(self, coil_addr: int, on: bool):
        # coil_addr: 0-based
        hi = (coil_addr >> 8) & 0xFF
        lo = coil_addr & 0xFF
        val_hi, val_lo = (0xFF, 0x00) if on else (0x00, 0x00)

        frame = bytes([self.slave_id, 0x05, hi, lo, val_hi, val_lo])
        c = crc16(frame)
        pkt = frame + bytes([c & 0xFF, (c >> 8) & 0xFF])

        # broadcast = no reply. just write+flush and short delay
        self._ser.write(pkt)
        self._ser.flush()
        time.sleep(0.05)

    def set_channel(self, ch: int, on: bool):
        """
        ch: 1..N
        """
        if ch < 1:
            raise ValueError("Channel must start at 1")
        coil_addr = ch - 1

        with self._lock:
            self.open()
            self._send_fc05(coil_addr, on)

    def on(self, ch: int):
        self.set_channel(ch, True)

    def off(self, ch: int):
        self.set_channel(ch, False)

if __name__ == "__main__":
    # quick manual test
    r = RelayRS485(port="/dev/ttyUSB0", baudrate=9600, slave_id=0xFF)
    print("Relay1 ON")
    r.on(1)
    time.sleep(1)
    print("Relay1 OFF")
    r.off(1)
    print("DONE")
