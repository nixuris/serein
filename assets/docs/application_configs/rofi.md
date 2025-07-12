# Rofi Configuration

This document describes the Rofi application launcher configuration within Serein, highlighting its modular setup and extensive visual customization for various functionalities.

## Overview

Rofi is extensively customized with multiple `.rasi` files, each tailored for specific functionalities (e.g., clipboard, emoji, session management, wallpaper selection), all importing a base theme for consistent styling.

### `config.rasi` (Base Configuration)

This file serves as the central point for importing the main visual theme and setting global Rofi behaviors:

*   **Theme Import:** Imports the primary theme from `~/.config/rofi/themes/menu.rasi`.
*   **Hover Select:** Enables `hover-select: true` for easier navigation by hovering over entries.
*   **Mouse Actions:** Defines mouse actions for accepting entries, including `MousePrimary`, `MouseSecondary`, and `MouseDPrimary`.

### `themes/menu.rasi` (Main Theme)

This is the core styling file, providing the visual foundation for all Rofi menus:

*   **Dynamic Background:** Imports `~/.cache/rofi/img_path.rasi`, which dynamically sets the background based on the current wallpaper, ensuring a consistent visual experience.
*   **Modi:** Configured for `drun` (application launcher) and `window` (window switcher) modes.
*   **Icons & Formats:** Icons are enabled (`show-icons: true`), and custom display formats are set for `drun` (`{name}`) and `window` (`{w} · {c} · {t}`).
*   **Font & Colors:** Uses `JetBrains Mono Nerd Font 10` and defines a custom color scheme with a dark background (`#1b1e25`), light foreground (`#edeeff`), and distinct colors for selected, active, and urgent states.
*   **Window Styling:** Features real transparency, centered positioning, `800px` width, `500px` height, `20px` border-radius, and uses the defined background color.
*   **Layout & Element Styling:** Detailed styling for the input bar, listbox, prompt, entry field, and individual elements, including padding, spacing, alignment, and rounded corners for elements.

### `clip.rasi` (Clipboard Manager)

This configuration customizes Rofi for clipboard management:

*   **Base Import:** Imports `config.rasi`.
*   **Entry Field:** Sets a `width` of `30%` and a placeholder text of "Search Messages".
*   **Listview:** Configured to display entries in `2` columns and `8` lines.

### `config-emoji.rasi` (Emoji Picker)

This configuration customizes Rofi for selecting emojis:

*   **Base Import:** Imports `config.rasi`.
*   **Entry Field:** Sets a `width` of `30%` and a placeholder text of "💫 Search Emojis".
*   **Listview:** Configured to display entries in `1` column and `8` lines.

### `session.rasi` (Session Manager)

This configuration customizes Rofi for session management options:

*   **Base Import:** Imports `config.rasi`.
*   **Entry Field:** The entry field is disabled (`enabled: false`).
*   **Input Bar:** Custom padding and transparent background.
*   **Prompt:** The prompt colon is disabled.
*   **Listview:** Configured to display entries in `1` column and `8` lines.

### `wallselect.rasi` (Wallpaper Selector)

This configuration customizes Rofi for wallpaper selection:

*   **Base Import:** Imports `config.rasi`.
*   **Modi & Icons:** Sets `modi` to `drun` and enables icons.
*   **Window Styling:** Configures the window to be fullscreen with `2000px` width, transparent background, and no border or border-radius.
*   **Listview:** Optimized for displaying wallpaper thumbnails, configured with `6` columns and `1` line, significant spacing, and padding.
*   **Responsive Elements:** Includes media queries to adjust element orientation based on aspect ratio.