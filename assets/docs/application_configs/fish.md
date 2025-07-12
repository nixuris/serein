# Fish Shell Configuration

This document describes the Fish shell configuration within Serein, designed for an enhanced command-line experience with custom aesthetics and utility.

## Overview

The Fish shell configuration is modular, with `config.fish` handling the main setup, `conf.d/npm.fish` managing NPM global paths, and `functions/` containing custom prompt and greeting functions.

### `config.fish`

This is the primary configuration file, executed for interactive shell sessions. It includes:

*   **Visual Effects:** Executes `~/.config/hypr/scripts/sttt scanline` for a terminal visual effect and `fastfetch` for system information display upon session start.
*   **Environment Variables:** Sets `EDITOR` and `VISUAL` to `nvim`.
*   **Path Management:** Adds `~/.local/bin` and `~/.cargo/bin` to the system's `PATH` for easy access to local executables.
*   **Color Customization:** Defines custom colors for Fish shell commands, parameters, and error messages.
*   **Aliases:**
    *   `xs`: `paru -S` (install packages)
    *   `xr`: `paru -Rns` (remove packages and dependencies)
    *   `xu`: `paru` (update system)
    *   `nvidia-gpu`: Sets environment variables for NVIDIA GPU offloading (`__NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia`).
    *   `e`, `vim`, `vi`: All alias to `nvim` for consistent editor access.
    *   `se`: `sudo -E -s nvim` for elevated text editing while preserving the environment.

### `conf.d/npm.fish`

This file ensures that global Node Package Manager (NPM) packages installed to `~/.local/bin` are correctly added to the shell's `PATH`, making them directly executable.

### `functions/fish_greeting.fish`

This function is currently commented out, meaning no custom greeting message is displayed when a new Fish shell session is initiated.

### `functions/fish_prompt.fish`

Defines a custom, visually distinct command prompt. It uses Unicode characters and color codes to display the current working directory, resembling a folder icon followed by a stylized arrow, enhancing the shell's aesthetic appeal.
