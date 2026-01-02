# RV Control Panel (Raspberry Pi)

ระบบควบคุมและแสดงผลไฟฟ้าในรถบ้าน (RV)  
พัฒนาโดยใช้ Raspberry Pi + Python (Tkinter)  
ควบคุมอุปกรณ์จริงผ่าน RS485 / Modbus

---

## 1. Project Overview

โปรเจกต์นี้ใช้เป็น HMI หลักของรถบ้าน โดยมีหน้าจอสัมผัส
ทำหน้าที่:
- แสดงสถานะแบตเตอรี่ 12V / 24V / 48V
- ควบคุมไฟ 12V ผ่านรีเลย์ RS485
- แสดงข้อมูล Solar / MPPT
- แสดงสถานะ Inverter (Read-only)
- รันแบบ Kiosk หลังบูตเครื่อง

---

## 2. Hardware Used

- Raspberry Pi (Bookworm, aarch64)
- USB to RS485 Converter
- RS485 Relay Board (8CH)
- MPPT: LV TOPSUN LT3048M60
- Inverter (RS485 / Modbus)
- Touchscreen HDMI

Serial Port:
- `/dev/ttyUSB0`  → RS485 (Relay / MPPT)

---

## 3. Software Stack

- OS: Debian Bookworm (Raspberry Pi OS)
- Python: 3.11
- GUI: Tkinter
- Communication: RS485 / Modbus
- Version Control: Git

Virtual Environment:
venv/


---

## 4. Folder Structure



rv-panel/
├── app.py # Main application
├── ui/ # UI pages
│ ├── main_page.py
│ ├── lighting_page.py
│ ├── inverter_page.py
│ └── settings_page.py
├── services/
│ ├── state.py # Global system state
│ ├── relay_rs485.py # RS485 relay driver
│ └── lt3048m60_modbus.py # MPPT Modbus driver
├── test_modbus.py
├── test_relay.py
├── venv/
└── README.md


---

## 5. How to Run

### Activate virtual environment
```bash
cd ~/rv-panel
source venv/bin/activate

Run application (ต้องมี DISPLAY)
python3 app.py


ถ้ารันผ่าน SSH ต้องใช้ ssh -X หรือรันบนจอ Pi โดยตรง

6. Current Status

 Main UI layout

 Lighting page

 RS485 relay control (REAL hardware)

 Settings page

 Git repository initialized

 Modbus MPPT data mapping (in progress)

 Inverter fault / alarm read-only page

 Kiosk autostart script

7. Next Steps

Finish Modbus register scan for LT3048M60

Bind MPPT data to Solar page

Implement Inverter fault/alarm page

Create systemd service for kiosk startup

8. Safety & Notes

RS485 line is shared → avoid concurrent access

Relay defaults are applied at boot

Do not hot-plug RS485 converter under load

Always backup project before Modbus changes


บันทึก:
- `Ctrl + O`
- `Enter`
- `Ctrl + X`

---

## ✅ STEP 4.3 — commit README

```bash
git add README.md
git commit -m "STEP 4: add project README documentation"


ตรวจสอบ:

git log --oneline

🧠 สรุป STEP 4

README นี้ = แผนที่ทั้งระบบ

ใช้ได้จริง ไม่ใช่เอกสารโชว์

รองรับการทำงานระยะยาว / ส่งต่อ / debug
