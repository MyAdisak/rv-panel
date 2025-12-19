import minimalmodbus
import time

PORT = "/dev/ttyUSB0"

# ค่าที่พบบ่อยสุดในบอร์ดรีเลย์ RS485
SLAVE_IDS = [1, 2, 3, 10]
BAUDRATES = [9600, 19200]

print("=== MODBUS RTU AUTO TEST ===")

for sid in SLAVE_IDS:
    for baud in BAUDRATES:
        try:
            print(f"\nลอง → Slave={sid}, Baud={baud}")
            ins = minimalmodbus.Instrument(PORT, sid)
            ins.serial.baudrate = baud
            ins.serial.bytesize = 8
            ins.serial.parity = minimalmodbus.serial.PARITY_NONE
            ins.serial.stopbits = 1
            ins.serial.timeout = 1
            ins.mode = minimalmodbus.MODE_RTU

            # ลองอ่าน Coil 0 (รีเลย์ช่องแรก)
            val = ins.read_bit(0, functioncode=1)
            print("✅ สำเร็จ! อ่านค่าได้ =", val)
            print(">>> ใช้ค่านี้ได้เลย <<<")
            exit(0)

        except Exception as e:
            print("❌ ไม่ได้:", e)

print("\n❌ ไม่พบอุปกรณ์ตอบกลับ")
print("ให้เช็ก: Slave ID / Baud / สาย A-B / DIP Switch")
