# Scripts Guide

This document provides an overview of the utility scripts found in the `.config/hypr/scripts` directory. These scripts are used to perform various actions within the Serein environment, from managing system settings to launching applications.

## Script Descriptions

*   **`bright`**: Adjusts the screen brightness using `brightnessctl` and displays a notification with the current brightness level.

*   **`clip`**: A clipboard manager that uses `cliphist` to store clipboard history and `rofi` to display it. It allows you to select and paste from your clipboard history.

*   **`emoji`**: An emoji picker that uses `rofi` to display a list of emojis. Selecting an emoji copies it to your clipboard.

*   **`hints`**: Displays a list of keybindings for the Serein environment using `yad`.

*   **`killin`**: Forcefully kills the active window by getting its process ID and sending a `kill` signal.

*   **`notify_send`**: A sophisticated wrapper script for sending desktop notifications via `gdbus`. It provides more advanced features than the standard `notify-send` command.

*   **`refresh`**: Restarts the Waybar status bar and reloads the Hyprland configuration. This is useful for applying changes to your Waybar or Hyprland settings without a full restart.

*   **`scrshot`**: A comprehensive screenshot tool that uses `grim`, `slurp`, and `swappy`. It provides options for capturing the entire screen, a selected window, or a specific region, as well as editing screenshots.

*   **`session`**: A session manager that uses `rofi` to display a menu with options to lock the screen, shut down, reboot, or log out of the current session.

*   **`sttt`**: A Python script that creates visually appealing transitions in your terminal using the `curses` library. It offers several different transition effects.

*   **`volume`**: Controls the system volume using `wpctl` and displays a notification with the current volume level. It can be used to increase, decrease, and mute the volume.

*   **`wallselect`**: A wallpaper selector that uses `rofi` to display your wallpapers and `swww` to set the selected wallpaper as your background.
