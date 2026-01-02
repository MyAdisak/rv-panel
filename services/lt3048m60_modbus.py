import time
import minimalmodbus


class LT3048M60:
    """
    LT-3048M60 (MPPT) Modbus RTU reader
    - ใช้ RS485 เส้นเดียว (port เดียว)
    - device_id โดยมาก = 1 (แก้ได้ตอนสร้าง object)
    - ฟังก์ชันอ่านเป็น Holding Register (FC3)

    หมายเหตุสำคัญ:
    - รุ่น/เฟิร์มแวร์/แบรนด์ rebrand บางตัว mapping register อาจไม่ตรงกัน
    - ถ้าอ่านแล้ว no answer ให้ลองเปลี่ยน device_id / baud / parity / mapping
    """

    def __init__(self, port="/dev/ttyUSB0", baudrate=9600, device_id=1, parity="N"):
        self.instrument = minimalmodbus.Instrument(port, device_id)

        # Serial config
        self.instrument.serial.baudrate = int(baudrate)
        self.instrument.serial.bytesize = 8
        self.instrument.serial.parity = parity  # "N" / "E" / "O"
        self.instrument.serial.stopbits = 1
        self.instrument.serial.timeout = 0.4   # เร็วพอสำหรับ tick 1s
        self.instrument.mode = minimalmodbus.MODE_RTU

        # ลดปัญหา noise บน RS485
        self.instrument.clear_buffers_before_each_transaction = True
        self.instrument.close_port_after_each_call = True

        # Cache timestamps
        self._last_ok = 0

        # ------------- Register map (DEFAULT) -------------
        # *** ถ้าอ่านไม่ตรง ให้แก้ค่าพวกนี้ทีเดียว ***
        #
        # ค่าทั่วไปของ MPPT หลายรุ่น:
        # PV Voltage / PV Current / Batt Voltage / Batt Current / Batt SOC
        #
        # scale: ส่วนมาก x0.1 หรือ x0.01
        self.REG_PV_VOLT   = 0x0000  # example
        self.REG_PV_CURR   = 0x0001  # example
        self.REG_BATT_VOLT = 0x0002  # example
        self.REG_BATT_CURR = 0x0003  # example
        self.REG_BATT_SOC  = 0x0004  # example

        self.SCALE_PV_VOLT   = 0.1
        self.SCALE_PV_CURR   = 0.1
        self.SCALE_BATT_VOLT = 0.1
        self.SCALE_BATT_CURR = 0.1
        self.SCALE_BATT_SOC  = 1.0

    # ---------------------------
    # low-level safe read helpers
    # ---------------------------
    def _read_u16(self, reg_addr):
        try:
            val = self.instrument.read_register(
                reg_addr,
                number_of_decimals=0,
                functioncode=3,
                signed=False
            )
            self._last_ok = time.time()
            return int(val)
        except Exception as e:
            # อย่า spam เยอะ
            print(f"[MPPT READ FAIL] reg=0x{reg_addr:04X} err={e}")
            return None

    def _read_s16(self, reg_addr):
        try:
            val = self.instrument.read_register(
                reg_addr,
                number_of_decimals=0,
                functioncode=3,
                signed=True
            )
            self._last_ok = time.time()
            return int(val)
        except Exception as e:
            print(f"[MPPT READ FAIL] reg=0x{reg_addr:04X} err={e}")
            return None

    # ---------------------------
    # Public API used by state.py
    # ---------------------------
    def pv_voltage(self):
        raw = self._read_u16(self.REG_PV_VOLT)
        return None if raw is None else raw * self.SCALE_PV_VOLT

    def pv_current(self):
        raw = self._read_u16(self.REG_PV_CURR)
        return None if raw is None else raw * self.SCALE_PV_CURR

    def batt_voltage(self):
        raw = self._read_u16(self.REG_BATT_VOLT)
        return None if raw is None else raw * self.SCALE_BATT_VOLT

    def batt_current(self):
        # บางรุ่นเป็น signed (ชาร์จ/คายประจุ)
        raw = self._read_s16(self.REG_BATT_CURR)
        return None if raw is None else raw * self.SCALE_BATT_CURR

    def batt_soc(self):
        raw = self._read_u16(self.REG_BATT_SOC)
        return None if raw is None else raw * self.SCALE_BATT_SOC
