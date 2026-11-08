#!/bin/sh
# Screenshot helper.
#   screenshot.sh full    -> entire screen (all outputs)
#   screenshot.sh region  -> select an area with slurp (default)
mode=${1:-region}

directory="$HOME/Pictures/Screenshots"
mkdir -p "$directory" || exit 1
file="$directory/$(date +%Y%m%d_%H%M%S_%N).png"

if [ "$mode" = "full" ]; then
    grim "$file" || exit 1
else
    area=$(slurp) || exit 0
    [ -n "$area" ] || exit 0
    grim -g "$area" "$file" || exit 1
fi

if command -v wl-copy >/dev/null 2>&1; then
    wl-copy --type image/png < "$file"
fi
if command -v notify-send >/dev/null 2>&1; then
    notify-send "Screenshot saved" "$file"
fi
