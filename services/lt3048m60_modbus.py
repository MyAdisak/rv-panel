from pymodbus.client.serial import ModbusSerialClient


class LT3048M60:
    def __init__(self,
                 port="/dev/ttyUSB0",
                 baudrate=9600,
                 device_id=1):

        self.device_id = device_id
        self.client = ModbusSerialClient(
            port=port,
            baudrate=baudrate,
            parity="N",
            stopbits=1,
            bytesize=8,
            timeout=1
        )
        self.client.connect()

    # ---------------- PV (INPUT REGISTERS) ----------------
    def pv_voltage(self):
        rr = self.client.read_input_registers(
            address=0x3100,
            count=1,
            device_id=self.device_id
        )
        return None if rr.isError() else rr.registers[0] / 10.0

    def pv_current(self):
        rr = self.client.read_input_registers(
            address=0x3101,
            count=1,
            device_id=self.device_id
        )
        return None if rr.isError() else rr.registers[0] / 100.0

    # ---------------- Battery (INPUT REGISTERS) ----------------
    def batt_voltage(self):
        rr = self.client.read_input_registers(
            address=0x3104,
            count=1,
            device_id=self.device_id
        )
        return None if rr.isError() else rr.registers[0] / 10.0

    def batt_current(self):
        rr = self.client.read_input_registers(
            address=0x3105,
            count=1,
            device_id=self.device_id
        )
        return None if rr.isError() else rr.registers[0] / 100.0

    def batt_soc(self):
        rr = self.client.read_input_registers(
            address=0x311A,
            count=1,
            device_id=self.device_id
        )
        return None if rr.isError() else rr.registers[0]

    # ---------------- Status (INPUT REGISTERS) ----------------
    def charging_state(self):
        rr = self.client.read_input_registers(
            address=0x3201,
            count=1,
            device_id=self.device_id
        )
        if rr.isError():
            return "UNKNOWN"

        code = rr.registers[0]
        return {
            0: "No Charge",
            1: "Float",
            2: "Boost",
            3: "Equalize"
        }.get(code, f"Code {code}")

    def fault_code(self):
        rr = self.client.read_input_registers(
            address=0x3200,
            count=1,
            device_id=self.device_id
        )
        return None if rr.isError() else rr.registers[0]
