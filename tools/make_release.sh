#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

TS="$(date +%Y%m%d_%H%M%S)"
OUT="rv-panel_release_${TS}.tgz"

# 1) สร้าง FULL DUMP ก่อน (สร้างใน ROOT ตามเดิม)
python3 tools/dump_all.py >/dev/null

# 2) ทำ staging copy เพื่อให้ tar อ่านไฟล์ "นิ่งๆ"
STAGE="/tmp/rv-panel_stage_${TS}"
rm -rf "$STAGE"
mkdir -p "$STAGE"

# copy ทั้งโปรเจกต์ แต่ตัดของที่ไม่เอาออก
rsync -a --delete \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='venv' \
  --exclude='.venv' \
  --exclude='*.pyc' \
  --exclude='*.log' \
  --exclude='*.swp' \
  --exclude='rv-panel_release_*.tgz' \
  "$ROOT"/ "$STAGE"/

# 3) tar จาก STAGE -> ออกไฟล์ไว้ที่ ROOT (นอก staging)
tar -czf "$ROOT/$OUT" -C "$STAGE" .

# 4) cleanup staging
rm -rf "$STAGE"

echo "OK => $ROOT/$OUT"
ls -lah "$ROOT/$OUT"
