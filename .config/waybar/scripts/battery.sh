#!/bin/sh
# Outputs battery info for Waybar (JSON) only when a real battery is present.
# Returns empty output (so the module can be hidden) on desktops/no-battery systems.
bat=""
for d in /sys/class/power_supply/BAT* /sys/class/power_supply/CMB*; do
    [ -e "$d/type" ] || continue
    t=$(cat "$d/type" 2>/dev/null)
    [ "$t" = "Battery" ] || continue
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

icon="󰁹"
[ "$cap" -le 10 ] && icon="󰁺"
[ "$cap" -le 20 ] && [ "$cap" -gt 10 ] && icon="󰁻"
[ "$cap" -le 30 ] && [ "$cap" -gt 20 ] && icon="󰁼"
[ "$cap" -le 40 ] && [ "$cap" -gt 30 ] && icon="󰁽"
[ "$cap" -le 50 ] && [ "$cap" -gt 40 ] && icon="󰁾"
[ "$cap" -le 60 ] && [ "$cap" -gt 50 ] && icon="󰁿"
[ "$cap" -le 70 ] && [ "$cap" -gt 60 ] && icon="󰂀"
[ "$cap" -le 80 ] && [ "$cap" -gt 70 ] && icon="󰂁"
[ "$cap" -le 90 ] && [ "$cap" -gt 80 ] && icon="󰂂"
case "$status" in Charging) icon="󰂄" ;; esac

printf '{"text":"%s %s%%","tooltip":"%s: %s%%","class":"%s"}\n' "$icon" "$cap" "$status" "$cap" "$class"
