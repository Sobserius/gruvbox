#!/bin/sh
# MangoWC startup (Gruvbox rice) — Waybar

logdir="$HOME/.local/state/rice-startup"
mkdir -p "$logdir"
uid="$(id -u)"

start_once() {
    name="$1"
    shift
    if ! pgrep -u "$uid" -x "$name" >/dev/null 2>&1; then
        "$@" >>"$logdir/$name.log" 2>&1 &
    fi
}

# Notifications (mako)
start_once mako mako

# Wallpaper
if [ -f "$HOME/lowpoly.png" ]; then
    start_once swaybg swaybg -i "$HOME/lowpoly.png" -m fill
else
    start_once swaybg swaybg -c '#000200'
fi

# Bar (Waybar)
start_once waybar waybar \
    -c "$HOME/.config/waybar/config.jsonc" \
    -s "$HOME/.config/waybar/style.css"

# Eww daemon (popups/widgets used by bar clicks)
eww -c "$HOME/.config/eww" daemon >>"$logdir/eww.log" 2>&1 &

# Now-playing notifications (kept from original rice)
if [ -f "$HOME/.config/dunst/now-playing.py" ]; then
    if ! pgrep -u "$uid" -f "now-playing.py" >/dev/null 2>&1; then
        python3 "$HOME/.config/dunst/now-playing.py" >>"$logdir/now-playing.log" 2>&1 &
    fi
fi

# Polkit agent (needed for GUI privilege prompts) — adjust if you use another
if command -v /usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 >/dev/null 2>&1; then
    start_once polkit-gnome-au /usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1
fi
