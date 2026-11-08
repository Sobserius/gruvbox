#!/usr/bin/env python3
import json
import os
import subprocess
import sys

WINDOWS = ('music', 'calendar')
if len(sys.argv) != 2 or sys.argv[1] not in WINDOWS:
    raise SystemExit('Choose music or calendar')

BASE = os.path.expanduser('~/.config/eww')


def eww(*args):
    return subprocess.run(['eww', '-c', BASE, *args], capture_output=True, text=True)


def screen():
    # Hyprland: use the focused output's model. Elsewhere (MangoWC etc.),
    # eww's numeric monitor index 0 works and avoids GTK's primary-monitor error.
    try:
        r = subprocess.run(['hyprctl', 'monitors', '-j'], capture_output=True, text=True, timeout=3)
        monitors = json.loads(r.stdout)
        if r.returncode == 0 and monitors:
            focused = next((m for m in monitors if m.get('focused')), monitors[0])
            return focused.get('model') or '0'
    except (OSError, ValueError, KeyError, IndexError, subprocess.SubprocessError):
        pass
    return '0'


try:
    # daemon is idempotent: an already-running daemon is left alone.
    subprocess.run(['eww', '-c', BASE, 'daemon'], stdout=subprocess.DEVNULL, timeout=5)
    window = sys.argv[1]
    monitor = screen()
    p = eww('open', '--toggle', '--screen', monitor, window)
    if p.returncode and monitor != '0':
        p = eww('open', '--toggle', '--screen', '0', window)
    if p.returncode:
        print(p.stderr.strip() or p.stdout.strip() or 'Eww popup failed', file=sys.stderr)
        raise SystemExit(1)
except (subprocess.SubprocessError, FileNotFoundError) as e:
    print(f'Eww popup failed: {e}', file=sys.stderr)
    raise SystemExit(1)
