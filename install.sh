#!/bin/sh
# Gruvbox + MangoWC rice installer
# Adapted from https://github.com/Sobserius/dotfiles install style.
# Run as your normal user — sudo will ask for your password.
set -eu

repo=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

say()  { printf '\033[1;35m::\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m::\033[0m %s\n' "$*"; }

if [ "$(id -u)" -eq 0 ]; then
	echo "Run this as your normal user, not as root (it installs into \$HOME)." >&2
	exit 1
fi

aur_helper=""
detect_aur_helper() {
	if command -v paru >/dev/null 2>&1; then
		aur_helper="paru"
	elif command -v yay >/dev/null 2>&1; then
		aur_helper="yay"
	fi
}

install_aur_helper() {
	detect_aur_helper
	[ -n "$aur_helper" ] && { say "AUR helper found: $aur_helper"; return; }

	if ! command -v pacman >/dev/null 2>&1; then
		warn "pacman not found — cannot bootstrap an AUR helper. Install yay or paru manually."
		return
	fi

	say "no yay/paru found — bootstrapping yay-bin (AUR helper)"
	sudo -v
	sudo pacman -S --needed --noconfirm --color=auto base-devel git

	tmp=$(mktemp -d)
	trap 'rm -rf "$tmp"' EXIT INT TERM
	git clone --depth 1 https://aur.archlinux.org/yay-bin.git "$tmp/yay-bin"
	(cd "$tmp/yay-bin" && makepkg -si --noconfirm --needed)
	rm -rf "$tmp"
	trap - EXIT INT TERM

	detect_aur_helper
	[ -n "$aur_helper" ] && say "installed AUR helper: $aur_helper" || warn "AUR helper install may have failed — install yay/paru manually"
}

# Official repo dependencies (MangoWC Gruvbox rice)
deps="base-devel git
mangowm
xdg-desktop-portal xdg-desktop-portal-wlr xdg-desktop-portal-gtk
polkit polkit-gnome
waybar rofi-wayland kitty mako libnotify playerctl
swaybg swayidle brightnessctl
grim slurp wl-clipboard wf-recorder python
pipewire pipewire-pulse wireplumber
xdg-utils ttf-jetbrains-mono-nerd
cava pulsemixer superfile"

# AUR dependencies (installed via yay/paru if available)
# Note: mangobar-git is optional (native Mango bar); rice defaults to Waybar.
aur_deps="eww swaylock-effects wl-clip-persist cliphist satty wlr-dpms sway-audio-idle-inhibit-git dimland-git"

if command -v pacman >/dev/null 2>&1; then
	say "installing repo dependencies (sudo will ask for your password)"
	sudo -v
	# shellcheck disable=SC2086
	sudo pacman -S --needed --noconfirm --color=auto $deps || warn "some repo packages failed (check names/availability on your system)"

	install_aur_helper
	if [ -n "$aur_helper" ]; then
		say "installing AUR dependencies with $aur_helper"
		# shellcheck disable=SC2086
		$aur_helper -S --needed --noconfirm $aur_deps || warn "some AUR packages failed — install them manually (notably: eww swaylock-effects)"
	else
		warn "skipping AUR deps (no helper). Install manually: $aur_deps"
	fi
else
	say "pacman not found — install dependencies with your package manager (see README.md)."
fi

say "copying configs into $HOME"
mkdir -p "$HOME/.config" "$HOME/Pictures/Screenshots" "$HOME/Videos/Recordings"
if [ -d "$repo/.config" ]; then
	cp -a "$repo/.config/." "$HOME/.config/"
fi
if [ -f "$repo/.emacs" ]; then
	cp -a "$repo/.emacs" "$HOME/.emacs"
fi
if [ -d "$repo/.emacs.d" ]; then
	cp -a "$repo/.emacs.d" "$HOME/.emacs.d"
fi
if [ -d "$repo/.local" ]; then
	cp -a "$repo/.local/." "$HOME/.local/"
fi

if [ -f "$repo/lowpoly.png" ]; then
	cp -a "$repo/lowpoly.png" "$HOME/lowpoly.png"
fi

# Battery is hardware-dependent: add the Waybar module only when a battery exists.
if [ -f "$HOME/.config/waybar/scripts/setup-battery.py" ]; then
	say "checking for a battery (Waybar module)"
	python3 "$HOME/.config/waybar/scripts/setup-battery.py" || warn "could not configure the Waybar battery module"
fi

# Gruvbox-friendly pulsemixer launcher (no pink/magenta) — shadows /usr/bin by default
if [ -f "$repo/.local/bin/pulsemixer" ]; then
	say "installing pulsemixer Gruvbox wrapper to /usr/local/bin"
	sudo install -Dm755 "$repo/.local/bin/pulsemixer" /usr/local/bin/pulsemixer
fi

warn "wallpaper: installed ~/lowpoly.png (or set var=wallpaper in ~/.config/mango/config.conf)."
warn "superfile (spf) uses the Gruvbox theme; pulsemixer launches with Gruvbox colors (no pink)."

if command -v systemctl >/dev/null 2>&1; then
	say "enabling pipewire user services"
	systemctl --user enable --now pipewire pipewire-pulse wireplumber 2>/dev/null ||
		warn "could not enable them here — run: systemctl --user enable --now pipewire pipewire-pulse wireplumber"
fi

say "done — start MangoWC from a TTY with: mango   (reload config in-session: Super+Shift+R)"
