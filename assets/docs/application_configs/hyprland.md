# Hyprland Configuration

This document describes the Hyprland Wayland compositor configuration within Serein, highlighting its modular structure, extensive keybindings, and visual customizations.

## Overview

The Hyprland configuration is highly modular, with the main `hyprland.conf` file sourcing several other configuration files for specific aspects such as animations, autostarts, environment variables, keybinds, miscellaneous settings, and window rules. This modularity allows for easy management and customization of the desktop environment.

### `hyprland.conf` (Main Configuration)

This is the central configuration file that ties everything together:

*   **Monitor Setup:** Configured to use the preferred monitor at auto resolution and position.
*   **Terminal:** Defines `alacritty` as the default terminal emulator.
*   **Sourcing:** Imports all other `.conf` files from the `hyprconfs/` directory, creating a cohesive and organized setup.
*   **Environment Variables:** Sets essential `XDG` environment variables (`XDG_CURRENT_DESKTOP`, `XDG_SESSION_TYPE`, `XDG_SESSION_DESKTOP`) to `Hyprland`.
*   **Input:** Configures keyboard layout (`us`), mouse following behavior, touchpad settings (e.g., disable while typing), and mouse sensitivity.
*   **General:** Defines inner and outer gaps between windows, border size (set to `0`), active and inactive border colors, and sets the default layout to `dwindle`.
*   **Decoration:** Enables window rounding, blur effects (with customizable size, passes, and vibrancy), and drop shadows for a modern aesthetic.
*   **Animations:** Enables and customizes various animations for windows, borders, fading effects, and workspace transitions using a custom bezier curve.
*   **Dwindle Layout:** Configures `pseudotile` (windows take up full monitor space, tiling effect shown on dwindle/master) and `preserve_split`.
*   **Master Layout:** `new_is_master` is set to `true`.
*   **Gestures:** Enables `workspace_swipe` for touchpad gestures.
*   **Keybinds (Basic):** Includes fundamental keybindings using the `SUPER` key (`$mainMod`) for launching the terminal, killing active windows, exiting Hyprland, launching a file manager (dolphin), toggling floating windows, launching `wofi` (application launcher), toggling split mode, moving focus, switching workspaces, moving windows to workspaces, and scrolling through workspaces.
*   **Overview Plugin:** Integrates the `hyprtasking` plugin for an overview of open windows, with a `grid` layout, customizable `gap_size`, `bg_color`, `border_size`, and `gestures` for touch interaction.

### `hyprconfs/animations.conf`

This file specifically manages the visual transitions within Hyprland:

*   **Bezier Curve:** Defines a custom bezier curve named `myBezier` for smooth animation timing.
*   **Animation Definitions:** Configures animations for `windows` (with a `popin` effect), `border`, `fade`, and `workspaces` (with a `slidefade` effect), all utilizing the `myBezier` curve.

### `hyprconfs/autostarts.conf`

This file lists commands that are executed once when Hyprland starts:

*   `dbus-update-activation-environment`: Ensures D-Bus environment variables are correctly set.
*   `swww-daemon`: Starts the `swww` wallpaper daemon.
*   `waybar`: Launches the Waybar status bar.
*   `swaync`: Starts the SwayNC notification daemon.
*   `wl-paste --type text --watch cliphist store` and `wl-paste --type image --watch cliphist store`: Set up `cliphist` to store text and image clipboard history.
*   `hyprpm reload -nn`: Reloads Hyprland plugins.

### `hyprconfs/env.conf`

This file sets various environment variables crucial for proper Wayland compatibility and application theming:

*   **Cursor:** `XCURSOR_THEME` and `XCURSOR_SIZE`.
*   **Backend:** `CLUTTER_BACKEND` and `GDK_BACKEND`.
*   **Qt Applications:** `QT_AUTO_SCREEN_SCALE_FACTOR`, `QT_QPA_PLATFORM`, `QT_QPA_PLATFORMTHEME`, `QT_SCALE_FACTOR`, `QT_WAYLAND_DISABLE_WINDOWDECORATION`.
*   **XDG Standards:** `XDG_CURRENT_DESKTOP`, `XDG_SESSION_DESKTOP`, `XDG_SESSION_TYPE`.
*   **Firefox (Mozilla):** `MOZ_ENABLE_WAYLAND`, `MOZ_DISABLE_RDD_SANDBOX`.
*   **EGL & VRR:** `EGL_PLATFORM` and `__GL_VRR_ALLOWED`.

### `hyprconfs/keybinds.conf`

This file defines an extensive set of custom keybindings for efficient interaction with the Hyprland environment:

*   **Script Directory:** Defines `$scrdir` to point to `~/.config/hypr/scripts` for easy access to utility scripts.
*   **System Control:** Keybinds for session management (lock screen, shutdown, reboot, logout), volume control, and screen brightness adjustment.
*   **Application Launchers:** Binds for Rofi (application launcher) and SwayNC (notification center).
*   **Window Management:** Keybinds for killing active windows, toggling fullscreen, toggling floating windows, and refreshing Waybar/Hyprland.
*   **Screenshots:** Binds for taking screenshots using `scrshot` with `swappy` integration and instant full-screen capture.
*   **Utilities:** Keybinds for displaying keybinding hints, accessing the clipboard manager (`clip`), and an emoji picker.
*   **Window Navigation & Resizing:** Comprehensive keybinds using `ALT` and `SUPER` for moving focus between windows, resizing windows, and moving windows.
*   **Overview Plugin:** Specific keybinds for the `hyprtasking` plugin to toggle the overview and navigate within it.
*   **Hyprtasking Plugin Configuration:** Detailed configuration for the `hyprtasking` plugin, including `grid` layout, `gap_size`, `bg_color`, `border_size`, `exit_on_hovered`, and `gestures` for touch interaction.

### `hyprconfs/misc.conf`

This file contains various miscellaneous settings for Hyprland:

*   **Cursor:** `no_hardware_cursors=false`.
*   **Debug:** `disable_logs=false`.
*   **Decoration:** Configures blur effects (brightness, contrast, optimizations, passes, size), shadow properties (color, enabled, range, render power), active and inactive window opacity, and window rounding.
*   **Dwindle Layout:** `preserve_split=true` and `pseudotile=true`.
*   **General:** Sets `border_size=0`, active and inactive border colors, inner and outer gaps, and the default layout to `dwindle`.
*   **Gestures:** Enables `workspace_swipe`.
*   **Input:** Configures touchpad settings (disable while typing, natural scroll, tap-to-click), mouse following, keyboard layout, `numlock_by_default`, and mouse sensitivity.
*   **Misc:** Enables `vrr` (Variable Refresh Rate) and disables the Hyprland logo.

### `hyprconfs/windows.conf`

This file defines `windowrulev2` rules for specific applications, controlling their behavior and appearance:

*   **Floating Windows:** Rules to force certain applications (e.g., Rofi, Blueman-manager, imv, Yad, pavucontrol) to open as floating windows.
*   **Window Sizing:** Specific size rules for applications like Blueman-manager and Yad.
*   **XWayland Video Bridge:** Special rules for `xwaylandvideobridge` to ensure it is transparent, has no animations, no initial focus, minimal size, and no blur.

This comprehensive Hyprland configuration provides a highly customized, efficient, and visually appealing Wayland desktop experience, tailored for productivity and user comfort.

### `user.conf` (User-Specific Configuration)

This file acts as a personalized configuration hub, extending and overriding default Hyprland behaviors, and defining additional keybinds and autostart applications.

*   **Monitor Configuration:** Defines specific settings for connected monitors, including refresh rates, positions, and scaling (e.g., `eDP-1`, `Unknown-1`, `HDMI-A`).
*   **Default Applications:** Sets preferred application for the terminal (`alacritty`).
*   **Sourcing Hyprland Configurations:** Explicitly sources all the modular Hyprland configuration files from `~/.config/hypr/hyprconfs/`, ensuring they are loaded as part of the user's setup.
*   **Additional Keybinds:** Includes custom keybindings for launching specific applications in the terminal:
    *   `SUPER + T`: Opens Ranger file manager.
    *   `SUPER + P`: Opens `btop` (resource monitor).
    *   `SUPER + SHIFT + P`: Opens `htop` (process viewer).
    *   `SUPER + S`: Opens `cmus` (console music player).
*   **Additional Autostart Applications (`exec-once`):** Launches other essential applications on Hyprland startup:
    *   `blueman-applet`: Bluetooth applet.
    *   `fcitx5`: Input method editor.
    *   `udiskie`: Automounter for removable media.
    *   `mpris-discord-rpc`: Discord Rich Presence integration.

This `user.conf` centralizes personal preferences and additional application launches, making it easy to manage the core Hyprland experience and integrate other tools.
