For some reason when testing in podman, after choosing clone full history, full installation, persistance installation, after installing all packages it follow with these lines:
```
Removing old managed configurations...
Copying new configurations...
Copying config: hypr
Copying config: waybar
Copying config: rofi
Copying config: swaylock
Copying config: swappy
Copying config: swaync
Copying config: alacritty
Copying config: fastfetch
Copying config: fish
Copying config: nvim
Copying config: ranger
Copying config: udiskie
Enabling hyprtasking (required for overview)...

✖ You don't seem to be running Hyprland.
→ The hyprpm state store doesn't exist. Creating now...

✖ Could not update. Dependencies not satisfied. Hyprpm requires: cmake, meson, cpio, pkg-config, git, g++, gcc
✖ HYPRLAND_INSTANCE_SIGNATURE was not set! (Is Hyprland running?) (3)

✖ You don't seem to be running Hyprland.

✖ Could not clone the plugin repository. Dependencies not satisfied. Hyprpm requires: cmake, meson, cpio, pkg-config, git, g++, gcc
✖ Couldn't enable plugin (missing?)
Installation complete. Your Hyprland environment should be good to go.
Please reboot for all changes to take effect.
```
Which is completely off what it's intended to do.
