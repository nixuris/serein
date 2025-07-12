# Ranger Configuration

## Overview

The Ranger configuration includes settings for image previews, a custom trash mapping, and a custom command for file compression.

### `rc.conf`

This is the main configuration file for Ranger, defining its core behavior and keybindings:

*   **Image Previews:** Ranger is configured to display image previews directly in the terminal using `ueberzug` (`set preview_images_method ueberzug` and `set preview_images true`).
*   **Trash Mapping:** A custom keybinding `DD` is set up to move selected files to a local trash directory (`~/.local/share/Trash/files/`) instead of permanently deleting them. This provides a safety net for accidental deletions (`map DD shell mv %s ~/.local/share/Trash/files/`).

### `commands.py`

This file contains custom Python commands that extend Ranger's capabilities:

*   **`compress` Command:** A custom command named `compress` is implemented. This command allows users to:
    *   Compress marked files in the current directory.
    *   Utilizes `apack` (an external archiving utility) for the compression process.
    *   Offers tab completion for common archive extensions (`.zip`, `.tar.gz`, `.rar`, `.7z`), making it easier to specify the desired archive format.