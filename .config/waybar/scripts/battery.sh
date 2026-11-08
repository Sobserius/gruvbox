#!/bin/sh
# Battery percentage for the Waybar value cell.
# The icon lives in the left cell (custom/battery-icon + CSS); do NOT emit it here.
bat=""
for d in /sys/class/power_supply/BAT* /sys/class/power_supply/CMB*; do
    [ -e "$d/type" ] || continue
    [ "$(cat "$d/type" 2>/dev/null)" = "Battery" ] || continue
    bat="$d"
    break
done
[ -n "$bat" ] || exit 0

cap=$(cat "$bat/capacity" 2>/dev/null)
status=$(cat "$bat/status" 2>/dev/null)
[ -n "$cap" ] || exit 0

class="normal"
[ "$cap" -le 30 ] && class="warning"
[ "$cap" -le 15 ] && class="critical"
case "$status" in
    Charging) class="$class charging" ;;
    Full) class="$class full" ;;
    "Not charging") class="$class plugged" ;;
esac

printf '{"text":"%s%%","tooltip":"%s: %s%%","class":"%s"}\n' "$cap" "$status" "$cap" "$class"
