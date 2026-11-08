#!/bin/sh
# Outputs a blank cell for the battery icon (CSS provides the SVG) only when a battery exists.
for d in /sys/class/power_supply/BAT* /sys/class/power_supply/CMB*; do
    [ -e "$d/type" ] || continue
    [ "$(cat "$d/type" 2>/dev/null)" = "Battery" ] || continue
    printf '{"text":" ","tooltip":""}\n'
    exit 0
done
exit 0
