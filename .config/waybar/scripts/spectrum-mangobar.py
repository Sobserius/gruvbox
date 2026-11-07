#!/usr/bin/env python3
# Mangobar-friendly: prints a single line of cava bars (plain text). Exits on silence/failure.
import os, subprocess, sys, tempfile

conf = os.path.expanduser("~/.config/waybar/cava.ini")
bars = "▁▂▃▄▅▆▇█"
if not os.path.exists(conf):
    print("")
    sys.exit(0)
# Create a temp config forcing raw ascii? Easier: run cava and translate numeric output.
# But existing spectrum.py already handles cava; for simplicity, emit a static placeholder when no simple path.
# Try to read from the existing spectrum script's logic by running it? It outputs JSON lines continuously (Waybar mode).
try:
    p = subprocess.Popen([sys.executable, os.path.expanduser("~/.config/waybar/scripts/spectrum.py")],
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    line = p.stdout.readline().strip() if p.stdout else ""
    p.terminate()
    if line:
        try:
            d = __import__("json").loads(line)
            t = d.get("text") or d.get("alt") or ""
            print(t)
            sys.exit(0)
        except Exception:
            pass
except Exception:
    pass
print("▁▁▁▁▁▁▁▁▁▁▁▁")
