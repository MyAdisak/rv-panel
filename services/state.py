import time
import threading

from services.relay_rs485 import RelayRS485

try:
    import minimalmodbus
    import serial
except Exception:
    minimalmodbus = None
    serial = None


class AppState:
    def __init__(self):
        # ==================================================
        # PORTS (UDEV FIXED NAMES)
        # ==================================================
        # รีเลย์ (broadcast)
        self.rs485_port_relay = "/dev/rs485_relay"
        self.rs485_baud_relay = 9600

        # บัสอ่านค่า (inverter / mppt)
        self.rs485_port_bus = "/dev/rs485_bus"
        self.rs485_baud_bus = 9600

        # locks แยกกันคนละพอร์ต
        self.lock_relay = threading.Lock()
        self.lock_bus = threading.Lock()

        # ==================================================
        # RELAY (ID=255 broadcast, no reply expected)
        # ==================================================
        self.relay = RelayRS485(
            port=self.rs485_port_relay,
            baudrate=self.rs485_baud_relay,
            slave_id=255
        )

        # ==================================================
        # INVERTER (Modbus RTU)
        # ==================================================
        self.enable_inverter = True
        self.inverter_id = 1
        self.inverter_parity = "N"  # "N" / "E" / "O"
        self.inverter_driver = None
        self._inverter_port_selected = None  # chosen port (bus)

        # ==================================================
        # REGISTER MAP (CONFIRMED FROM MODPOLL)
        # ==================================================
        self.inv_reg_start = 0
        self.inv_reg_count = 50

        # AC
        self.inv_reg_ac_v = 4        # modpoll[5]  = 220V  -> regs[4]
        self.inv_reg_ac_f = 5        # modpoll[6]  = 50Hz  -> regs[5]

        # 48V battery
        self.inv_reg_charge_v = 34   # modpoll[35] = 536 -> 53.6V (CHG) -> regs[34]
        self.inv_reg_batt_v = 36     # modpoll[37] = 500 -> 50.0V (BATT)-> regs[36]

        # SOC register (ยังไม่ใช้เป็นหลัก)
        self.inv_reg_soc = 35        # modpoll[36]=550 (55.0) ในชุดที่คุณอ่านมา

        # ==================================================
        # VOLTAGE-BASED SOC (YOUR CALIBRATION)
        # ==================================================
        self.use_voltage_soc = True
        self.soc_v_min = 44.0   # 0%
        self.soc_v_max = 53.0   # 100%

        # ==================================================
        # BATTERY / POWER STATE
        # ==================================================
        self.batt12_soc = 0.0
        self.batt12_volt = 0.0
        self.batt12_curr = 0.0

        self.batt24_soc = 0.0
        self.batt24_volt = 0.0
        self.batt24_curr = 0.0

        self.batt48_soc = 0.0
        self.batt48_volt = 0.0              # Battery voltage (50.0V)
        self.batt48_charge_volt = 0.0       # Charging voltage (53.6V)
        self.batt48_curr = 0.0

        # ==================================================
        # SOLAR (ถ้ายังไม่ต่อ = 0)
        # ==================================================
        self.enable_mppt = False
        self.mppt_id = 1
        self.solar_driver = None

        self.solar_volt = 0.0
        self.solar_curr = 0.0
        self.solar_temp = 0.0
        self.pv1_volt = 0.0
        self.pv2_volt = 0.0

        # ==================================================
        # AC / INVERTER STATUS
        # ==================================================
        self.ac_in_volt = 0.0
        self.ac_in_curr = 0.0
        self.ac_in_freq = 0.0

        self.inv_out_volt = 0.0
        self.inv_out_curr = 0.0
        self.inv_out_freq = 0.0

        self.inv_mode = "-"
        self.inv_alarm_level = "NORMAL"
        self.inv_fault_code = 0
        self.inv_fault_msg = "-"

        # ==================================================
        # LIGHTING STATE
        # ==================================================
        self.light_main_12v = False
        self.light_downlight = False
        self.light_hall = False
        self.light_ambient = False
        self.light_outdoor = False

        self.light_defaults = {
            "light_main_12v": True,
            "light_downlight": False,
        }

        # ==================================================
        # RS485 STATUS
        # ==================================================
        self.rs485_status = "INIT"
        self.rs485_last_ok = 0

        self.apply_defaults()

    # ======================================================
    # HELPERS
    # ======================================================
    def apply_defaults(self):
        for name, val in self.light_defaults.items():
            self.set_light(name, val)

    def update_rs485_status(self, ok: bool):
        now = time.time()
        if ok:
            self.rs485_status = "OK"
            self.rs485_last_ok = now
        else:
            if now - self.rs485_last_ok > 5:
                self.rs485_status = "TIMEOUT"

    def _soc_from_voltage(self, v: float) -> float:
        vmin = float(getattr(self, "soc_v_min", 44.0))
        vmax = float(getattr(self, "soc_v_max", 53.0))
        if vmax <= vmin:
            return 0.0
        soc = (float(v) - vmin) * 100.0 / (vmax - vmin)
        if soc < 0:
            soc = 0.0
        if soc > 100:
            soc = 100.0
        return soc

    # ======================================================
    # RELAY CONTROL
    # ======================================================
    def set_light(self, name: str, value: bool):
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
            with self.lock_relay:
                if value:
                    self.relay.on(ch)
                else:
                    self.relay.off(ch)
            self.update_rs485_status(True)
        except Exception as e:
            print("[RELAY ERROR]", e)
            self.update_rs485_status(False)

    # ======================================================
    # INVERTER (MODBUS)
    # ======================================================
    def _make_inverter_instrument(self, port: str):
        if minimalmodbus is None or serial is None:
            raise RuntimeError("minimalmodbus not installed")

        ins = minimalmodbus.Instrument(port, self.inverter_id)
        ins.serial.baudrate = self.rs485_baud_bus
        ins.serial.bytesize = 8
        ins.serial.stopbits = 1
        ins.serial.timeout = 1.0
        ins.serial.parity = {
            "N": serial.PARITY_NONE,
            "E": serial.PARITY_EVEN,
            "O": serial.PARITY_ODD,
        }.get(self.inverter_parity.upper(), serial.PARITY_NONE)

        ins.mode = minimalmodbus.MODE_RTU
        ins.clear_buffers_before_each_transaction = True
        try:
            ins.close_port_after_each_call = True
        except Exception:
            pass

        return ins

    def _ensure_inverter(self):
        if not self.enable_inverter:
            return
        if self.inverter_driver is not None:
            return

        # ใช้ bus เป็นหลัก (คุณ fix udev แล้ว)
        self._inverter_port_selected = self.rs485_port_bus
        self.inverter_driver = self._make_inverter_instrument(self._inverter_port_selected)
        print("[INVERTER] using port:", self._inverter_port_selected)

    def _read_inverter_regs(self):
        self._ensure_inverter()
        if self.inverter_driver is None:
            return None

        last_err = None
        for _ in range(3):
            try:
                with self.lock_bus:
                    regs = self.inverter_driver.read_registers(
                        self.inv_reg_start,
                        self.inv_reg_count,
                        functioncode=3
                    )
                return regs
            except Exception as e:
                last_err = e
                time.sleep(0.05)
        raise last_err

    def _apply_inverter_map(self, regs):
        # AC
        v_ac = float(regs[self.inv_reg_ac_v])
        f_ac = float(regs[self.inv_reg_ac_f])

        if 100 <= v_ac <= 300:
            self.ac_in_volt = v_ac
            self.inv_out_volt = v_ac

        if 40 <= f_ac <= 70:
            self.ac_in_freq = f_ac
            self.inv_out_freq = f_ac

        # Charging voltage (CHG)
        v_chg = float(regs[self.inv_reg_charge_v]) / 10.0
        if 40 <= v_chg <= 65:
            self.batt48_charge_volt = v_chg

        # Battery voltage (BATT)
        v_batt = float(regs[self.inv_reg_batt_v]) / 10.0
        if 40 <= v_batt <= 65:
            self.batt48_volt = v_batt

        # SOC from voltage (your calibration)
        if getattr(self, "use_voltage_soc", True):
            self.batt48_soc = self._soc_from_voltage(self.batt48_volt)
        else:
            # fallback: try read SOC register with auto scaling
            soc_raw = float(regs[self.inv_reg_soc])
            soc = soc_raw / 10.0 if soc_raw > 100 else soc_raw
            if soc < 0:
                soc = 0.0
            if soc > 100:
                soc = 100.0
            self.batt48_soc = soc

    # ======================================================
    # MAIN TICK (call every ~1s)
    # ======================================================
    def tick(self):
        ok = False

        if self.enable_inverter:
            try:
                regs = self._read_inverter_regs()
                if regs and len(regs) >= self.inv_reg_count:
                    self._apply_inverter_map(regs)
                    ok = True
            except Exception as e:
                print("[INVERTER READ ERROR]", e)
                ok = False

        self.update_rs485_status(ok)
