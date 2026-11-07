#!/usr/bin/env python3
import json, subprocess, sys

def query(*args):
    try:
        r = subprocess.run(["playerctl", *args], capture_output=True, text=True, timeout=2)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""

status = query("status")
if not status:
    print("")
    sys.exit(0)
title = query("metadata", "title") or "Untitled"
artist = query("metadata", "artist")
icon = "󰐊" if status == "Playing" else "󰏤"
text = f"{icon} {title}" + (f" — {artist}" if artist else "")
if len(text) > 42:
    text = text[:39] + "…"
print(text)
