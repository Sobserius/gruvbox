#!/usr/bin/env python3
"""Enable/disable the Waybar battery module based on real hardware.

The Gruvbox Waybar setup ships without a battery module by default (desktops).
When a battery is detected, this script injects a `group/bat` that is an exact
structural clone of `group/audio` (colored icon cell + dark value cell).

Run by install.sh, or manually after copying configs:
    python3 ~/.config/waybar/scripts/setup-battery.py
"""
import json
import os
import sys
from pathlib import Path

CONFIG = Path(os.environ.get("HOME", str(Path.home()))) / ".config/waybar/config.jsonc"
BATTERY_KEYS = ("group/bat", "group/battery", "custom/battery", "custom/battery-icon", "battery")


def has_battery() -> bool:
    root = Path("/sys/class/power_supply")
    if not root.is_dir():
        return False
    for entry in root.iterdir():
        try:
            if (entry / "type").read_text().strip() == "Battery":
                return True
        except (OSError, UnicodeDecodeError):
            continue
    return False


def strip_battery(cfg: dict) -> None:
    for key in BATTERY_KEYS:
        cfg.pop(key, None)
    right = cfg.get("modules-right")
    if isinstance(right, list):
        right[:] = [m for m in right if m not in BATTERY_KEYS]


def add_battery(cfg: dict) -> None:
    right = cfg.setdefault("modules-right", [])
    if "group/bat" not in right:
        try:
            index = right.index("group/audio")
        except ValueError:
            index = 0
        right.insert(index, "group/bat")
    cfg["group/bat"] = {
        "orientation": "horizontal",
        "modules": ["custom/battery-icon", "custom/battery"],
    }
    # Exactly like custom/audio-icon: an empty label whose SVG comes from CSS.
    cfg["custom/battery-icon"] = {
        "format": " ",
        "tooltip": False,
        "align": 0.5,
    }
    cfg["custom/battery"] = {
        "exec": 'sh "$HOME/.config/waybar/scripts/battery.sh"',
        "return-type": "json",
        "interval": 10,
        "tooltip": True,
        "format": "{text}",
    }


def main() -> int:
    if not CONFIG.is_file():
        print(f"waybar config not found: {CONFIG}", file=sys.stderr)
        return 1

    try:
        cfg = json.loads(CONFIG.read_text())
    except json.JSONDecodeError as exc:
        print(f"cannot parse {CONFIG}: {exc}", file=sys.stderr)
        return 1
    if not isinstance(cfg, dict):
        print(f"{CONFIG} is not a JSON object", file=sys.stderr)
        return 1

    strip_battery(cfg)
    if has_battery():
        add_battery(cfg)
        print("battery detected: Waybar battery module enabled")
    else:
        print("no battery detected: Waybar battery module disabled")

    CONFIG.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
