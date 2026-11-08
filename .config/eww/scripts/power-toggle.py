#!/usr/bin/env python3
import json, os, shutil, subprocess, sys

def run(cmd, **kw):
    return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kw)

def notify(msg):
    if shutil.which("notify-send"):
        subprocess.run(["notify-send", "Power menu", msg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def get_screen():
    if shutil.which("mmsg"):
        try:
            out = subprocess.check_output(["mmsg", "get", "all-monitors"], text=True, stderr=subprocess.DEVNULL, timeout=3)
            data = json.loads(out)
            if isinstance(data, list) and data:
                focused = next((m for m in data if isinstance(m, dict) and (m.get("focused") or m.get("focus"))), data[0])
                name = (focused or {}).get("name") or (focused or {}).get("output")
                if name: return name
        except Exception:
            pass
    if shutil.which("hyprctl"):
        try:
            monitors = json.loads(subprocess.check_output(["hyprctl", "monitors", "-j"], text=True, timeout=3))
            if monitors:
                selected = next((m for m in monitors if m.get("focused")), monitors[0])
                return selected.get("name")
        except Exception:
            pass
    if shutil.which("wlr-randr"):
        try:
            out = subprocess.check_output(["wlr-randr"], text=True, stderr=subprocess.DEVNULL, timeout=3)
            for line in out.splitlines():
                if line and not line.startswith(" ") and " " in line:
                    return line.split()[0]
        except Exception:
            pass
    return None

def eww_open():
    eww = shutil.which("eww")
    if not eww:
        return False, "eww not installed (AUR: eww)"
    cfg = os.path.expanduser("~/.config/eww")
    run([eww, "-c", cfg, "daemon"], timeout=8)
    run([eww, "-c", cfg, "update", "power_choice="])
    screen = get_screen()
    attempts = []
    if screen:
        attempts.append([eww, "-c", cfg, "open", "--toggle", "--screen", screen, "power"])
    attempts.append([eww, "-c", cfg, "open", "--toggle", "power"])
    attempts.append([eww, "-c", cfg, "open", "power"])
    last = ""
    for cmd in attempts:
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            return True, ""
        last = (r.stderr or r.stdout or "").strip()
    return False, last or "eww open failed"

def fallback_menu():
    # simple fallback if eww can't show the popup
    if shutil.which("wlogout"):
        subprocess.Popen(["wlogout"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    return False

ok, err = eww_open()
if not ok:
    if not fallback_menu():
        notify(f"failed: {err}")
        print(f"Power popup failed: {err}", file=sys.stderr)
        sys.exit(1)
