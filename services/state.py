import time
import random

from services.relay_rs485 import RelayRS485


class AppState:
    def __init__(self):
        # ================= PORT CONFIG =================
        self.rs485_port = "/dev/serial/by-id/usb-1a86_USB2.0-Ser_-if00-port0"
        self.rs485_baud = 9600

        # ================= RELAY (ID255 broadcast) =================
        # รีเลย์ของคุณทดสอบแล้ว "ขยับ" ด้วย ID255
        self.relay = RelayRS485(
            port=self.rs485_port,
            baudrate=self.rs485_baud,
            slave_id=255
        )

        # ================= MPPT (ยังไม่ต่อสาย = ปิดไว้ก่อน) =================
        self.enable_mppt = False
        self.mppt_id = 1
        self.solar_driver = None  # จะสร้างเมื่อ enable_mppt=True

        # ================= SETTINGS LOCK =================
        self.settings_pin = "1234"
        self.settings_unlocked = False
        self.settings_unlock_time = 0

        # ================= Battery =================
        self.batt12_soc = 0.0
        self.batt12_volt = 0.0
        self.batt12_curr = 0.0

        self.batt24_soc = 62
        self.batt48_soc = 95
        self.batt24_volt = 25.1
        self.batt48_volt = 52.8
        self.batt24_curr = 0.0
        self.batt48_curr = 0.0

        # ================= Lighting (runtime) =================
        self.light_main_12v = False
        self.light_downlight = False
        self.light_hall = False
        self.light_ambient = False
        self.light_outdoor = False

        # ค่าเริ่มต้นตอนบูต
        self.light_defaults = {
            "light_main_12v": False,
            "light_downlight": False,
        }

        # ================= Solar =================
        self.solar_volt = 0.0
        self.solar_curr = 0.0
        self.solar_temp = 0.0
        self.pv1_volt = 0.0
        self.pv2_volt = 0.0

        # ================= Inverter / AC (จำลองก่อน) =================
        self.ac_in_volt = 220.0
        self.ac_in_curr = 0.0
        self.ac_in_freq = 50.0

        self.inv_out_volt = 230.0
        self.inv_out_curr = 0.0
        self.inv_out_freq = 50.0

        self.inv_mode = "Line"
        self.inv_alarm_level = "NORMAL"
        self.inv_fault_code = 0
        self.inv_fault_msg = "-"

        # ================= RS485 STATUS =================
        self.rs485_status = "INIT"
        self.rs485_last_ok = 0

        # APPLY DEFAULTS
        self.apply_defaults()

    # -------------------------------------------------
    def apply_defaults(self):
        for name, val in self.light_defaults.items():
            self.set_light(name, val)

    # -------------------------------------------------
    def update_rs485_status(self, ok: bool):
        now = time.time()
        if ok:
            self.rs485_status = "OK"
            self.rs485_last_ok = now
        else:
            if now - self.rs485_last_ok > 5:
                self.rs485_status = "TIMEOUT"

    # -------------------------------------------------
    def set_light(self, name: str, value: bool):
        """
        ถูกเรียกจาก UI โดยตรง
        """
        print(f"[UI->STATE] {name} => {value}")

        setattr(self, name, bool(value))

        mapping = {
            "light_main_12v": 1,
            "light_downlight": 2,
            "light_hall": 3,
            "light_ambient": 4,
            "light_outdoor": 5,
        }

        ch = mapping.get(name)
        if not ch:
            return

        try:
            if value:
                self.relay.on(ch)
            else:
                self.relay.off(ch)
            self.update_rs485_status(True)
        except Exception as e:
            print("[Relay ERROR]", e)
            self.update_rs485_status(False)

    # -------------------------------------------------
    def _ensure_mppt(self):
        """
        สร้าง MPPT driver เฉพาะตอนเปิดใช้งานจริง
        (ตอนนี้ยังไม่ต่อสาย = ปิด)
        """
        if not self.enable_mppt:
            return
        if self.solar_driver is not None:
            return

        from services.lt3048m60_modbus import LT3048M60
        self.solar_driver = LT3048M60(
            port=self.rs485_port,
            baudrate=self.rs485_baud,
            device_id=self.mppt_id
        )

    # -------------------------------------------------
    def tick(self):
        """
        logic loop ทุก 1 วินาที
        """
        # ---------- MPPT ----------
        try:
            if self.enable_mppt:
                self._ensure_mppt()

                v_pv = self.solar_driver.pv_voltage()
                i_pv = self.solar_driver.pv_current()
                v_batt = self.solar_driver.batt_voltage()
                soc = self.solar_driver.batt_soc()

                if v_pv is not None:
                    self.solar_volt = float(v_pv)
                    self.solar_curr = float(i_pv or 0.0)
                    self.pv1_volt = float(v_pv)
                    self.batt12_volt = float(v_batt or 0.0)
                    self.batt12_soc = float(soc or 0.0)
                    self.update_rs485_status(True)
                else:
                    self.update_rs485_status(False)
        except Exception as e:
            print("[MPPT READ ERROR]", e)
            self.update_rs485_status(False)

        # ---------- SIMULATED VALUES ----------
        self.ac_in_volt = 220 + random.uniform(-2, 2)
        self.ac_in_freq = 50.0
        self.inv_out_volt = 230 + random.uniform(-1, 1)
        self.inv_out_freq = 50.0
