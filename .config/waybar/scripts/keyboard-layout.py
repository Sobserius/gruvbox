#!/usr/bin/env python3
import json, subprocess, sys

layout = ""
try:
    out = subprocess.check_output(["mmsg", "get", "keyboardlayout"], text=True, stderr=subprocess.DEVNULL).strip()
    # mmsg may return plain text or JSON depending on version
    try:
        data = json.loads(out)
        if isinstance(data, dict):
            layout = data.get("layout") or data.get("keyboardlayout") or data.get("name") or ""
        elif isinstance(data, str):
            layout = data
    except Exception:
        layout = out.splitlines()[0] if out else ""
except Exception:
    layout = ""

layout = (layout or "us").strip().upper()[:3]
print(json.dumps({"text": layout, "tooltip": f"Keyboard layout: {layout}"}))
