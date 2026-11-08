#!/bin/sh
# Outputs battery info (Pango markup, volume-style split) only when a real battery is present.
# No output => module hidden (desktops).
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

class="normal"
[ "$cap" -le 30 ] && class="warning"
[ "$cap" -le 15 ] && class="critical"
case "$status" in
    Charging) class="$class charging" ; icon="󰂄" ;;
    *) icon="󰁹" ;;
esac

# Gruvbox split: red icon cell + dark value cell (matches volume module feel)
lbg="#8c3936"; lfg="#000200"; rbg="#000200"; rfg="#e9d9b6"
[ "$cap" -le 15 ] && rfg="#8c3936"
[ "$cap" -le 30 ] && [ "$cap" -gt 15 ] && rfg="#edbb26"

text="<span background=\"${lbg}\" foreground=\"${lfg}\"> ${icon} </span><span background=\"${rbg}\" foreground=\"${rfg}\"> ${cap}% </span>"
# JSON encode minimal
text=$(printf '%s' "$text" | sed 's/\\/\\\\/g; s/"/\\"/g')
printf '{"text":"%s","tooltip":"%s: %s%%","class":"%s"}\n' "$text" "$status" "$cap" "$class"
