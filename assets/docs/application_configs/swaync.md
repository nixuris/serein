# SwayNC Configuration

This document describes the SwayNC notification daemon configuration within Serein, detailing its functional and visual aspects.

## Overview

SwayNC is configured to provide a highly customized notification and control center experience, with a strong emphasis on visual styling and functional widgets.

### `config.json` (Functional Configuration)

This file defines the behavior and layout of the SwayNC control center and notifications:

*   **Control Center Dimensions & Positioning:** The control center has a width of `425` pixels and is positioned at the `top` and `center` of the screen, with specific margins.
*   **Behavioral Settings:**
    *   `fit-to-screen`: `true`
    *   `hide-on-action`: `true` (control center hides when an action is taken)
    *   `hide-on-clear`: `false` (control center does not hide when notifications are cleared)
    *   `image-visibility`: `when-available`
    *   `keyboard-shortcuts`: `true`
    *   `script-fail-notify`: `true`
*   **Notification Sizing:** Configures the size of notification body images (`100x200`), icons (`48px`), and the overall notification window width (`400px`).
*   **Timeouts:** Sets default notification display time to `5` seconds, with `critical` notifications lasting `20` seconds and `low` priority notifications `5` seconds.
*   **Widgets:** The control center includes a variety of functional widgets:
    *   **Label:** Displays "Notification Center".
    *   **MPRIS:** Media player control with custom image sizing.
    *   **Volume:** Volume control with a custom " " label.
    *   **Backlight:** Screen backlight control (for `nvidia_wmi_ec_backlight`) with a "⛭ " label.
    *   **Keyboard Backlight:** Keyboard backlight control (for `asus::kbd_backlight`) with a " " label.
    *   **Title:** Displays "󰂚 Notifications" and includes a "Clear All" button.
    *   **Do Not Disturb (DND):** A toggle for DND mode.
    *   **Notifications:** The main area for displaying notifications.

### `style.css` (Visual Styling)

This file dictates the aesthetic appearance of SwayNC, using a custom color palette and `JetBrains Mono Nerd Font`.

*   **Color Palette:** Defines a dark theme with blue/gray accents for backgrounds, text, hover states, and switches.
*   **Notification Styling:** Notifications feature `10px` border-radius, `2px` solid borders, and custom backgrounds. Close buttons, action buttons, group headers, and body images are all styled for a cohesive look.
*   **Widget Styling:** Each widget (title, DND, label, backlight, volume) has specific font sizes, margins, and color schemes to integrate seamlessly into the overall design.
*   **General Elements:** Consistent styling is applied to notification summaries, timestamps, body text, images, and floating notifications.