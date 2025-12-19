#!/bin/bash

# รอ X desktop พร้อม
sleep 5

cd /home/pi/rv-panel
source venv/bin/activate

# ปิด screensaver / blank
xset s off
xset s noblank
xset -dpms

# รันแอป
python3 app.py
