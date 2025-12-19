from services.relay_rs485 import RelayRS485
import random
import time


class AppState:
    def __init__(self):

        # ================= SETTINGS LOCK =================
        self.settings_pin = "1234"
        self.settings_unlocked = False
        self.settings_unlock_time = 0

        # ================= LIGHTING DEFAULT (BOOT) =================
        self.light_defaults = {
            "light_main_12v": True,
            "light_downlight": False,
            "light_hall": False,
            "light_ambient": False,
            "light_outdoor": False,
        }

        # ================= Battery =================
        self.batt12_soc = 80
        self.batt24_soc = 62
        self.batt48_soc = 95

        self.batt12_volt = 12.6
        self.batt24_volt = 25.1
        self.batt48_volt = 52.8

        self.batt12_curr = 0.0
        self.batt24_curr = 0.0
        self.batt48_curr = 0.0

        # ================= Lighting (runtime) =================
        self.light_main_12v = False
        self.light_downlight = False
        self.light_hall = False
        self.light_ambient = False
        self.light_outdoor = False

        # ================= Solar =================
        self.solar_volt = 19.0
        self.solar_curr = 3.0
        self.solar_temp = 38.0

        self.pv1_volt = 19.0
        self.pv2_volt = 18.5

        # ================= AC Input =================
        self.ac_in_volt = 228.0
        self.ac_in_curr = 1.8
        self.ac_in_freq = 50.0

        # ================= Inverter Output =================
        self.inv_out_volt = 230.0
        self.inv_out_curr = 2.5
        self.inv_out_freq = 50.0
        self.inv_mode = "Line"   # Line / Inverter / Bypass

        # ================= INVERTER FAULT / ALARM =================
        self.inv_alarm_level = "NORMAL"   # NORMAL / WARNING / FAULT
        self.inv_fault_code = 0
        self.inv_fault_msg = "-"

        # ================= Relay Controller =================
        self.relay = RelayRS485()

        # ================= RS485 / MODBUS STATUS =================
        self.rs485_status = "INIT"      # INIT / OK / ERROR / TIMEOUT
        self.rs485_last_ok = 0
        self.rs485_error_count = 0

        # ================= APPLY LIGHT DEFAULTS (BOOT) =================
        for name, value in self.light_defaults.items():
            self.set_light(name, value)

    # ----------------------------------------------------
    #   RS485 / Modbus health update
    # ----------------------------------------------------
    def update_rs485_status(self, ok: bool):
        now = time.time()

        if ok:
            self.rs485_status = "OK"
            self.rs485_last_ok = now
        else:
            self.rs485_error_count += 1
            if now - self.rs485_last_ok > 3:
                self.rs485_status = "TIMEOUT"
            else:
                self.rs485_status = "ERROR"

    # ----------------------------------------------------
    #   Lighting Control (REAL RELAY)
    # ----------------------------------------------------
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
            if value:
                self.relay.relay_on(ch)
            else:
                self.relay.relay_off(ch)

            self.update_rs485_status(True)

        except Exception:
            self.update_rs485_status(False)

    # ----------------------------------------------------
    #   UPDATE EVERY TICK (SIMULATION)
    # ----------------------------------------------------
    def tick(self):
        self.simulate_tick()

        # ----- Solar -----
        self.solar_volt = 18.5 + random.uniform(-1.0, 1.0)
        self.solar_curr = max(0, 3.0 + random.uniform(-2.5, 2.5))
        self.solar_temp = 35 + random.uniform(-3, 5)

        self.pv1_volt = self.solar_volt
        self.pv2_volt = self.solar_volt - random.uniform(0, 1.0)

        # ----- Battery currents -----
        self.batt12_curr = random.uniform(-5, 5)
        self.batt24_curr = random.uniform(-6, 6)
        self.batt48_curr = random.uniform(-8, 8)

        for name, curr in [
            ("batt12_soc", self.batt12_curr),
            ("batt24_soc", self.batt24_curr),
            ("batt48_soc", self.batt48_curr),
        ]:
            soc = getattr(self, name)
            if curr > 0.5:
                soc += 0.05
            elif curr < -0.5:
                soc -= 0.05
            soc = max(0, min(100, soc))
            setattr(self, name, soc)

        # ----- AC Input -----
        self.ac_in_volt = 228 + random.uniform(-4, 4)
        self.ac_in_curr = max(0, 2 + random.uniform(-1.5, 1.5))
        self.ac_in_freq = 50 + random.uniform(-0.2, 0.2)

        # ----- Inverter Output -----
        self.inv_out_volt = 230 + random.uniform(-3, 3)
        self.inv_out_curr = max(0, 2.5 + random.uniform(-1.0, 1.0))
        self.inv_out_freq = 50 + random.uniform(-0.1, 0.1)

        self.inv_mode = random.choice(["Line", "Inverter", "Bypass"])

        # ----- Inverter Alarm Simulation -----
        r = random.random()
        if r < 0.85:
            self.inv_alarm_level = "NORMAL"
            self.inv_fault_code = 0
            self.inv_fault_msg = "-"
        elif r < 0.95:
            self.inv_alarm_level = "WARNING"
            self.inv_fault_code = 101
            self.inv_fault_msg = "High Load"
        else:
            self.inv_alarm_level = "FAULT"
            self.inv_fault_code = 201
            self.inv_fault_msg = "Over Voltage"

    # ----------------------------------------------------
    #   Placeholder
    # ----------------------------------------------------
    def simulate_tick(self):
        pass
