#!/usr/bin/env python3
import shutil, subprocess, sys

def dispatch_quit():
    # MangoWC
    if shutil.which("mmsg"):
        r = subprocess.run(["mmsg", "dispatch", "quit"])
        if r.returncode == 0: return 0
    # Hyprland fallback
    if shutil.which("hyprctl"):
        r = subprocess.run(["hyprctl", "dispatch", "exit"])
        if r.returncode == 0: return 0
    # generic fallback
    if shutil.which("loginctl"):
        import os
        return subprocess.run(["loginctl", "terminate-user", str(os.getuid())]).returncode
    return 1

if len(sys.argv) != 2:
    raise SystemExit("Invalid power action; nothing executed.")

action = sys.argv[1]
subprocess.run(["eww", "close", "power"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if action == "logout":
    rc = dispatch_quit()
elif action == "suspend":
    rc = subprocess.run(["systemctl", "suspend"]).returncode
elif action == "reboot":
    rc = subprocess.run(["systemctl", "reboot"]).returncode
elif action == "shutdown":
    rc = subprocess.run(["systemctl", "poweroff"]).returncode
else:
    raise SystemExit("Invalid power action; nothing executed.")

if rc:
    print("Action was refused or failed. Check system permissions/session state.", file=sys.stderr)
raise SystemExit(rc)
