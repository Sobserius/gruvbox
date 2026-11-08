#!/usr/bin/env python3
import json, os, re, shutil, subprocess, sys

def run(cmd, **kw):
    return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kw)

def notify(msg):
    if shutil.which("notify-send"):
        subprocess.run(["notify-send", "Power menu", msg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def candidates():
    names = []
    # mmsg (MangoWC)
    if shutil.which("mmsg"):
        try:
            out = subprocess.check_output(["mmsg", "get", "all-monitors"], text=True, stderr=subprocess.DEVNULL, timeout=3)
            s = out.strip()
            if s and s[0] not in "[{":
                m = re.search(r"[\[{]", s)
                if m: s = s[m.start():]
            data = json.loads(s)
            items = data if isinstance(data, list) else ([data] if isinstance(data, dict) else [])
            focused = None
            for it in items:
                if not isinstance(it, dict): continue
                n = it.get("name") or it.get("output")
                if n: names.append(str(n))
                if it.get("focused") or it.get("focus"): focused = n
            if focused and str(focused) in names:
                names.remove(str(focused)); names.insert(0, str(focused))
        except Exception:
            pass
    # wlr-randr
    if shutil.which("wlr-randr"):
        try:
            out = subprocess.check_output(["wlr-randr"], text=True, stderr=subprocess.DEVNULL, timeout=3)
            for line in out.splitlines():
                if not line or line[0].isspace(): continue
                m = re.match(r'^([A-Za-z][A-Za-z0-9_.-]*)\b', line)
                if m: names.append(m.group(1))
        except Exception:
            pass
        # json mode on newer wlr-randr
        try:
            out = subprocess.check_output(["wlr-randr", "--json"], text=True, stderr=subprocess.DEVNULL, timeout=3)
            data = json.loads(out)
            if isinstance(data, list):
                for it in data:
                    if isinstance(it, dict) and it.get("name"): names.append(it["name"])
        except Exception:
            pass
    # hyprctl
    if shutil.which("hyprctl"):
        try:
            monitors = json.loads(subprocess.check_output(["hyprctl", "monitors", "-j"], text=True, timeout=3))
            for it in monitors or []:
                if isinstance(it, dict) and it.get("name"): names.append(it["name"])
        except Exception:
            pass
    # swaymsg
    if shutil.which("swaymsg"):
        try:
            outs = json.loads(subprocess.check_output(["swaymsg", "-t", "get_outputs", "-r"], text=True, stderr=subprocess.DEVNULL, timeout=3))
            for it in outs or []:
                if isinstance(it, dict) and it.get("name"): names.append(it["name"])
        except Exception:
            pass
    # dedupe keep order
    seen=set(); res=[]
    for n in names:
        if n and n not in seen: seen.add(n); res.append(n)
    return res

def eww_open():
    eww = shutil.which("eww")
    if not eww:
        return False, "eww not installed (AUR: eww)"
    cfg = os.path.expanduser("~/.config/eww")
    run([eww, "-c", cfg, "daemon"], timeout=8)
    run([eww, "-c", cfg, "close", "power"])
    run([eww, "-c", cfg, "update", "power_choice="])

    screens = candidates()
    attempts = []
    # try every detected screen explicitly (fixes "failed to get primary monitor" on GTK/Wayland)
    for s in screens:
        attempts.append((f"--screen {s}", [eww, "-c", cfg, "open", "--screen", s, "power"]))
    attempts.append(("no-screen", [eww, "-c", cfg, "open", "power"]))
    attempts.append(("screen-0", [eww, "-c", cfg, "open", "--screen", "0", "power"]))

    errs = []
    for label, cmd in attempts:
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            return True, ""
        msg = (r.stderr or r.stdout or "").strip().replace("\n", " | ")
        errs.append(f"{label}: {msg}")

    detail = " ;; ".join(errs[-3:]) if errs else "no attempts"
    if not screens:
        detail += " ;; no monitor names detected (try: wlr-randr)"
    else:
        detail += f" ;; detected: {','.join(screens)}"
    return False, detail

def fallback_menu():
    if shutil.which("wlogout"):
        subprocess.Popen(["wlogout"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    return False

ok, err = eww_open()
if not ok:
    if not fallback_menu():
        notify((err[:180] + "...") if len(err) > 180 else err)
        print(f"Power popup failed: {err}", file=sys.stderr)
        sys.exit(1)
