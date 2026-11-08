#!/bin/sh
# Outputs battery info (Pango) only when a real battery is present. No output => hidden.
bat=""
for d in /sys/class/power_supply/BAT* /sys/class/power_supply/CMB*; do
    [ -e "$d/type" ] || continue
    [ "$(cat "$d/type" 2>/dev/null)" = "Battery" ] || continue
    bat="$d"; break
done
[ -n "$bat" ] || exit 0
cap=$(cat "$bat/capacity" 2>/dev/null)
status=$(cat "$bat/status" 2>/dev/null)
[ -n "$cap" ] || exit 0

rfg="#e9d9b6"; class="normal"
[ "$cap" -le 30 ] && rfg="#edbb26" && class="warning"
[ "$cap" -le 15 ] && rfg="#8c3936" && class="critical"
icon="󰁹"
case "$status" in
    Charging) icon="󰂄"; class="$class charging" ;;
    Full) class="$class full" ;;
    "Not charging") class="$class plugged" ;;
esac

# left = icon on red frame, right = percentage on dark cell (volume-like split)
text="<span foreground=\"#000200\"> ${icon} </span><span background=\"#000200\" foreground=\"${rfg}\"> ${cap}% </span>"
text=$(printf '%s' "$text" | sed 's/\\/\\\\/g; s/"/\\"/g')
printf '{"text":"%s","tooltip":"%s: %s%%","class":"%s"}\n' "$text" "$status" "$cap" "$class"
