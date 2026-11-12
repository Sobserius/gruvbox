# dotfiles-mango (Gruvbox + MangoWC)

A **MangoWC** adaptation of [xylvzm/dotfiles-archlinux](https://github.com/xylvzm/dotfiles-archlinux) (originally Hyprland, Gruvbox).

It recreates the same general rice (Gruvbox palette, waybar, eww, rofi, kitty, mako) with **Hyprland replaced by [MangoWC](https://github.com/mangowm/mango)**.

## What changed from the original

| Original | This adaptation |
|---|---|
| Hyprland (`hyprland.lua`) | MangoWC (`.config/mango/config.conf`) |
| `hyprpaper` | `swaybg` |
| `hyprlock` | `swaylock-effects` (`.config/swaylock/config`) |
| `hyprctl` (record script) | `mmsg` (MangoWC IPC) — see `.config/mango/scripts/record-screen.py` |
| Waybar `hyprland/workspaces`, `hyprland/language` | `ext/workspaces`, `custom/language` (`.config/waybar/scripts/keyboard-layout.py`) |

Hardcoded `/home/xylvzm/...` paths were made portable (`$HOME` / home-relative where possible). Some Hyprland-only visuals (e.g. gradient borders) are approximated to fit MangoWC’s config format.

## Dependencies (Arch)

```bash
# official repos
sudo pacman -S --needed \
  mangowm xdg-desktop-portal xdg-desktop-portal-wlr xdg-desktop-portal-gtk polkit polkit-gnome \
  waybar rofi-wayland kitty mako libnotify playerctl \
  swaybg swayidle brightnessctl grim slurp wl-clipboard wf-recorder python \
  pipewire pipewire-pulse wireplumber xdg-utils ttf-jetbrains-mono-nerd

# AUR (example with an AUR helper)
yay -S --needed eww swaylock-effects cava wl-clip-persist cliphist satty \
  wlr-dpms sway-audio-idle-inhibit-git dimland-git
```

> `eww` is **AUR-only**. `mangowm` is in `[extra]`. Adjust `polkit-gnome`/the agent path in `.config/mango/rice-startup.sh` if you use a different agent.

## Install (apply configs)

From this folder:

```bash
# back up anything you care about first
mkdir -p ~/.config

cp -r .config/mango    ~/.config/
cp -r .config/waybar   ~/.config/
cp -r .config/eww      ~/.config/
cp -r .config/rofi     ~/.config/
cp -r .config/kitty    ~/.config/
cp -r .config/mako     ~/.config/
cp -r .config/dunst    ~/.config/
cp -r .config/swaylock ~/.config/

# optional: emacs
cp -r .emacs .emacs.d ~/
```

Or symlink individual directories if you prefer managing them from here.

## Wallpaper

`lowpoly.png` is included and installed to `~/lowpoly.png` by `install.sh`. To use a different wallpaper, change `var=wallpaper,...` in `.config/mango/config.conf`, the `swaybg` line in `.config/mango/rice-startup.sh`, and `image=` in `.config/swaylock/config`.

## Audio / file manager (Gruvbox-themed)

- **`pulsemixer`**: config in `.config/pulsemixer.cfg` and a wrapper (installed to `/usr/local/bin/pulsemixer` + a desktop entry) that launches with Gruvbox-friendly colors (no pink/magenta). Use `--no-kitty` to run inline.
- **`spf` (superfile)**: `.config/superfile/config.toml` sets `theme = "gruvbox"`. Launches via `SUPER+E` (or the **Superfile** desktop entry in rofi) using `.local/bin/superfile`.

## Keybind highlights (SUPER as main mod)

- `SUPER+Q` terminal (kitty) · `SUPER+R` launcher (rofi) · `SUPER+E` file manager
- `SUPER+C` close · `SUPER+M` quit MangoWC · `SUPER+V` toggle float
- `SUPER+Arrows` focus · `SUPER+Shift+Arrows` move
- `SUPER+1..0` view tag 1–10 · `SUPER+Shift+1..0` move to tag
- `SUPER+S` special tag/scratchpad · `SUPER+Shift+S` screenshot · `SUPER+Shift+F9` record toggle
- `SUPER+PgUp/PgDn` / `SUPER+Scroll` cycle tags · `SUPER+Shift+R` reload config
- Media/brightness keys via `wpctl`, `playerctl`, `brightnessctl`

See `.config/mango/config.conf` for the full, editable set.

## Notes

- Start MangoWC from a TTY with `mango` (or via your display manager/session entry if installed).
- The **recording** and **keyboard layout** helpers rely on `mmsg` being available in your MangoWC session.
- Waybar’s Gruvbox styling is preserved; `ext/workspaces` behavior may differ slightly from Hyprland’s module.
- Review scripts before use, especially anything that runs on startup (`.config/mango/rice-startup.sh`).

## License

Follows the upstream repository’s license (see `LICENSE`).
