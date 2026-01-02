#!/usr/bin/env python3
import os
import sys
from datetime import datetime

EXCLUDE_DIRS = {
    ".git", "__pycache__", "venv", ".venv", ".mypy_cache", ".pytest_cache",
    "node_modules", "dist", "build"
}
EXCLUDE_FILES = {
    ".DS_Store",
}
INCLUDE_EXT = {".py", ".sh", ".service", ".md", ".txt", ".ini", ".hal", ".json", ".yaml", ".yml"}

def should_skip_dir(path: str) -> bool:
    parts = path.split(os.sep)
    return any(p in EXCLUDE_DIRS for p in parts)

def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(root, f"rvpanel_FULL_DUMP_{ts}.txt")

    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        if should_skip_dir(os.path.relpath(dirpath, root)):
            dirnames[:] = []
            continue

        for fn in filenames:
            if fn in EXCLUDE_FILES:
                continue
            fp = os.path.join(dirpath, fn)
            rel = os.path.relpath(fp, root)

            ext = os.path.splitext(fn)[1].lower()
            if ext and ext not in INCLUDE_EXT:
                continue

            # กันไฟล์ใหญ่/ไบนารีหลุดมา
            try:
                if os.path.getsize(fp) > 2_000_000:
                    continue
            except OSError:
                continue

            files.append(rel)

    files.sort()

    with open(out, "w", encoding="utf-8") as w:
        w.write(f"RV-PANEL FULL DUMP\n")
        w.write(f"ROOT: {root}\n")
        w.write(f"GENERATED: {datetime.now().isoformat()}\n")
        w.write(f"FILES: {len(files)}\n")
        w.write("=" * 80 + "\n\n")

        for rel in files:
            fp = os.path.join(root, rel)
            w.write("#" * 80 + "\n")
            w.write(f"# FILE: {rel}\n")
            w.write("#" * 80 + "\n")
            try:
                with open(fp, "r", encoding="utf-8", errors="replace") as r:
                    w.write(r.read())
            except Exception as e:
                w.write(f"\n[READ ERROR] {e}\n")
            w.write("\n\n")

    print(out)

if __name__ == "__main__":
    main()
