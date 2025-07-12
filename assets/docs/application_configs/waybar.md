# Waybar Configuration

This document describes the Waybar status bar configuration within Serein, detailing its dual-bar setup, module functionalities, and extensive visual styling.

## Overview

Waybar is configured with two distinct bars: a top bar for general system information and a left-side vertical bar for quick access to specific utilities. Both bars are extensively styled to integrate seamlessly with the Serein environment.

### `config` (Functional Configuration)

#### Top Bar

*   **Position & Dimensions:** Located at the `top` of the screen, with a `width` of `1000px`, `height` of `43px`, and a `margin-top` of `10px`.
*   **Left Modules:** Displays the current window title (`hyprland/window`) and custom padding/end modules for visual spacing.
*   **Right Modules:** Includes `cpu` usage, `temperature`, `memory` usage, `pulseaudio` (volume control), `pulseaudio#microphone` (microphone volume), and `backlight` (screen brightness), along with custom padding/end modules.
*   **Module Specifics:**
    *   **`backlight`:** Uses `intel_backlight`, shows percentage with icons, and allows brightness adjustment via scrolling.
    *   **`cpu`:** Displays CPU usage percentage with an icon.
    *   **`hyprland/window`:** Shows the current window's title with an icon, limited to `80` characters.
    *   **`memory`:** Displays used memory in GB and percentage, with different formats and icons based on usage levels.
    *   **`pulseaudio` & `pulseaudio#microphone`:** Show volume with icons, allow `pavucontrol` launch on click, and volume adjustment via scrolling.
    *   **`temperature`:** Displays CPU temperature with an icon, with a critical threshold of `82°C`.

#### Left Bar

*   **Position & Dimensions:** Located on the `left` side, with a `width` of `53px`, `height` of `750px`, and a `margin-left` of `10px`.
*   **Left Modules:** Features a custom logo (`custom/logo`) that launches Rofi, a `clock`, and the system `tray`.
*   **Right Modules:** Includes `network` status, `custom/swaync` (SwayNC notification indicator), `battery` status, and a `custom/power` module for session management.
*   **Module Specifics:**
    *   **`battery`:** Displays battery capacity with icons, and different formats for charging/plugged states.
    *   **`clock`:** Displays time vertically, with an alternative format for the date, and calendar actions.
    *   **`custom/logo`:** Displays a custom icon and executes `rofi -show drun` on click.
    *   **`custom/power`:** Displays a power icon and executes the session script (`~/.config/hypr/scripts/session`) on click.
    *   **`custom/swaync`:** Shows SwayNC notification status with various icons (for DND, inhibited, notification count) and allows clicks to open/close SwayNC.
    *   **`network`:** Displays network status with icons, bandwidth information, and a detailed tooltip.
    *   **`tray`:** Configures icon size and spacing for system tray items.

### `style.css` (Visual Styling)

This file defines the visual appearance of both Waybar instances, ensuring a cohesive and aesthetically pleasing look.

*   **Font:** Uses `JetBrainsMono Nerd Font` with bold weight and `13px` font size.
*   **Window Styling:** Both Waybar instances have a dark background (`#1b1e25`) and `7px` border-radius.
*   **Tooltip Styling:** Tooltips feature a dark background, rounded corners, and blue text (`#86afef`).
*   **Workspaces & Taskbar:** Custom styling for buttons, including active, persistent, and hover states with animations and transitions.
*   **Module Styling:** A consistent style is applied to most modules, including colors (`#86afef`), background (`#242830`), opacity, margins, and padding. Specific modules like `custom-logo` have distinct styling for visual emphasis.
*   **Rounded Corners:** `custom-r_end` and `custom-l_end` modules have rounded corners to create a segmented, visually appealing look for the bar sections.