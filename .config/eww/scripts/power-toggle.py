#!/usr/bin/env python3
import json, os, shutil, subprocess, sys

def run(cmd, **kw):
    return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kw)

def get_screen():
    # MangoWC / wlroots via mmsg
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
    # Hyprland fallback
    if shutil.which("hyprctl"):
        try:
            monitors = json.loads(subprocess.check_output(["hyprctl", "monitors", "-j"], text=True, timeout=3))
            if monitors:
                selected = next((m for m in monitors if m.get("focused")), monitors[0])
                return selected.get("name")
        except Exception:
            pass
    # wlr-randr fallback (parse first connected output name)
    if shutil.which("wlr-randr"):
        try:
            out = subprocess.check_output(["wlr-randr"], text=True, stderr=subprocess.DEVNULL, timeout=3)
            for line in out.splitlines():
                if line and not line.startswith(" ") and " " in line:
                    return line.split()[0]
        except Exception:
            pass
    return None

try:
    run(["eww", "daemon"], timeout=5)
    run(["eww", "update", "power_choice="], check=False)
    screen = get_screen()
    cmd = ["eww", "open", "--toggle"]
    if screen:
        cmd += ["--screen", screen]
    cmd.append("power")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        # fallback without --screen
        subprocess.run(["eww", "open", "--toggle", "power"], check=True)
except (subprocess.SubprocessError, FileNotFoundError) as e:
    print(f"Power popup failed: {e}", file=sys.stderr)
    raise SystemExit(1)
