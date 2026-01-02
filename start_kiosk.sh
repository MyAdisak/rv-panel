#!/bin/bash
set -e

export DISPLAY=:0
export XAUTHORITY=/home/pi/.Xauthority

sleep 3

cd /home/pi/rv-panel
source venv/bin/activate

# ปิดพักจอ/blank/dpms
xset s off || true
xset s noblank || true
xset -dpms || true

# รันแอป
exec python3 /home/pi/rv-panel/app.py
