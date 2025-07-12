# Wallpaper Selection Mechanism

The wallpaper selection is handled by a combination of scripts and configuration files that work together to provide a seamless experience.

**Components:**

*   **`~/Wallpapers/`**: This is the directory where you should store all your wallpaper images.
*   **`~/.config/hypr/scripts/wallselect`**: This is the main script that drives the wallpaper selection process.
*   **`~/.config/rofi/wallselect.rasi`**: This is the Rofi theme file for the wallpaper selection menu.
*   **`~/.cache/rofi_icons/`**: This directory is used to store cached thumbnails of your wallpapers for faster loading in Rofi.
*   **`~/Wallpapers/wallpaper_tracking.txt`**: This file stores the filename of the currently selected wallpaper.
*   **`~/.cache/rofi/img_path.rasi`**: This Rofi theme file is dynamically updated to set the background of other Rofi menus to the current wallpaper.

**Process:**

1.  When you run the `wallselect` script (which is likely already bound to a hotkey in your Hyprland configuration), it first scans your `~/Wallpapers/` directory for images.
2.  For each image, it generates a 300x300 thumbnail and stores it in `~/.cache/rofi_icons/`.
3.  It then launches a Rofi menu using the `wallselect.rasi` theme, which displays the generated thumbnails.
4.  When you select a wallpaper from the Rofi menu, the script does the following:
    *   It uses the `swww` command to set the selected image as your desktop wallpaper with a smooth transition effect.
    *   It saves the filename of the selected wallpaper to `~/Wallpapers/wallpaper_tracking.txt` for persistence.
    *   It updates the `~/.cache/rofi/img_path.rasi` file, specifically the `background-image` property, to point to the new wallpaper. This allows other Rofi menus to use the current wallpaper as their background.
