# Serein CLI Documentation

This document provides comprehensive information about the `serein` command-line tool, the central utility for managing your Serein Hyprland environment.

## Overview

The `serein` CLI is designed to simplify tasks such as updating your system and Serein configurations, managing configuration generations, enabling/disabling features, and uninstalling the environment.

## Architecture Overview

The `serein` CLI is built using Python with the `typer` library. It has been modularized for better maintainability and scalability. Here's a brief overview of the structure:

*   **`serein` (executable)**: A Bash wrapper script located in the root of the repository. This script's primary role is to activate the Python virtual environment (`.venv`) and then execute the main Python script. This ensures that the CLI always runs with its required dependencies.

*   **`functions/serein.py`**: The main entry point for the Python application. This script is responsible for initializing `typer` and registering all the available commands. It acts as a dispatcher, directing the user's input to the appropriate command module.

*   **`functions/commands/`**: This directory is a Python package that contains the core logic for each CLI command. It is organized as follows:
    *   `__init__.py`: An empty file that marks the `commands` directory as a Python package, allowing for modular imports.
    *   `utils.py`: A collection of shared helper functions used by multiple commands (e.g., for printing colored output, running shell commands, checking for persistent installation).
    *   `config.py`: Contains all the logic for the `serein config` subcommand, including listing, enabling, and disabling configurations.
    *   `update.py`: Implements the `serein update` command.
    *   `rollback.py`: Implements the `serein rollback` command.
    *   `uninstall.py`: Implements the `serein uninstall` command.
    *   `feature.py`: Implements the `serein enable` and `serein disable` commands for managing plugins.

This modular design separates concerns, making it easier to debug issues, add new commands, and understand the overall structure of the application.

## Commands

### `serein update [stable|edge] [--force|-f]`

Updates your system and Serein configurations. This command ensures your environment is up-to-date with the latest changes from the Serein repository.

*   **Arguments:**
    *   `[stable|edge]`: Specifies the type of update.
        *   `stable`: Updates to the latest stable release tag of the Serein repository. This is recommended for most users for a well-tested configuration.
        *   `edge` (default): Performs a `git pull` on the `main` branch to get the very latest, cutting-edge features. Use this if you want the newest changes as soon as they are available.

*   **Options:**
    *   `--force`, `-f`: Forces an update even if the system detects that you are already on the latest version. This can be useful if you suspect a corrupted installation or want to re-apply configurations.

*   **Behavior:**
    *   Before updating, `serein` creates a backup of your current Serein configuration, saving it as a new "generation." This allows for easy rollback if any issues arise after the update.
    *   It performs a `paru -Syu` to update your system packages.
    *   It then pulls the latest Serein repository changes (based on `stable` or `edge`).
    *   Finally, it re-symlinks your configurations to ensure they reflect the updated repository content.

### `serein rollback [--no-confirm|-y] [--keep-backup|-k]`

Allows you to revert your Serein environment to a previous configuration "generation" or manage existing backups. This is a crucial command for disaster recovery or testing different configurations.

*   **Interactive Mode:**
    *   When run without specific arguments, `serein rollback` presents an interactive menu with two main choices:
        *   **Rollback to a generation:** Allows you to select a previously saved generation (backup) to restore your Serein configurations to that state. This involves resetting the Serein repository to the commit hash associated with that generation and re-symlinking configurations.
        *   **Delete a generation:** Allows you to remove a specific generation from the list of available backups. By default, this also deletes the associated backup files.

*   **Options:**
    *   `--no-confirm`, `-y`: Skips all confirmation prompts during the rollback or deletion process. Use with caution, as this can lead to unintended data loss.
    *   `--keep-backup`, `-k`: When choosing to "Delete a generation," this option prevents the actual backup files from being removed from the filesystem. Only the entry in the generations list will be marked as archived.

### `serein enable <plugin>`

Enables a specific Serein feature or plugin. This command integrates additional functionalities into your Hyprland environment.

*   **Arguments:**
    *   `<plugin>`: The name of the feature or plugin to enable.

*   **Currently Supported Plugins:**
    *   `overview`: Enables the Hyprland overview plugin (hyprtasking). This command will install `hyprtasking` via `hyprpm` and reload Hyprland to activate it.

### `serein disable <plugin>`

Disables a specific Serein feature or plugin. This command removes or deactivates functionalities previously enabled.

*   **Arguments:**
    *   `<plugin>`: The name of the feature or plugin to disable.

*   **Currently Supported Plugins:**
    *   `overview`: Disables the Hyprland overview plugin (hyprtasking). This command will remove `hyprtasking` via `hyprpm` and reload Hyprland.

### `serein uninstall`

Removes the entire Serein environment from your system. This command is designed to clean up all Serein-related files and configurations.

*   **Interactive Prompt:**
    *   The command will ask for confirmation before proceeding with the uninstallation.
    *   It will also ask if you want to remove all packages that were installed as part of the Serein environment (both minimal and full installation packages).

*   **Behavior:**
    *   Unsymlinks all Serein-managed configurations from your `~/.config` directory.
    *   Removes the `serein` executable from `/usr/local/bin`.
    *   Deletes the Serein persistent directory (`~/.cache/serein`).
    *   Cleans up common cache directories related to Serein (e.g., Rofi cache, `user.conf`).
    *   If chosen, removes all packages installed by Serein using `paru -Rns`.

## Configuration Management (`serein config`)

The `serein config` subcommand provides granular control over which Serein configurations are active in your `~/.config` directory. This is particularly useful for users who want to selectively enable or disable parts of the Serein environment.

### `serein config` (Interactive Mode)

When you run `serein config` without any subcommands, it launches an interactive interface.

*   **Behavior:**
    *   Presents a list of all available Serein configurations (both minimal and extra).
    *   Each configuration is displayed with its current status (enabled or disabled).
    *   You can use the spacebar to toggle the enabled/disabled state of each configuration.
    *   Press Enter to confirm your selections. The CLI will then automatically enable or disable the chosen configurations by creating or removing symlinks in your `~/.config` directory.

### `serein config list`

Lists all available Serein configurations and their current status.

*   **Output:**
    *   For each configuration, it shows:
        *   Its name (e.g., `hypr`, `nvim`, `alacritty`).
        *   Its status: `enabled` (symlinked to Serein repo), `enabled (external)` (symlinked but not to Serein repo), `unmanaged` (exists but not a symlink), `disabled` (does not exist or is not managed by Serein).

### `serein config enable <config_name>`

Enables a specific Serein configuration by creating a symlink.

*   **Arguments:**
    *   `<config_name>`: The name of the configuration directory to enable (e.g., `nvim`, `fish`, `ranger`).

*   **Behavior:**
    *   Creates a symbolic link from the corresponding configuration directory within the Serein repository (`~/.cache/serein/config/<config_name>`) to your `~/.config` directory (`~/.config/<config_name>`).
    *   If a directory or symlink already exists at the target path, it will prompt for confirmation before overwriting (unless `--no-confirm` is used).

### `serein config disable <config_name>`

Disables a specific Serein configuration by removing its symlink.

*   **Arguments:**
    *   `<config_name>`: The name of the configuration directory to disable.

*   **Behavior:**
    *   Removes the symbolic link from your `~/.config` directory (`~/.config/<config_name>`) if it points to the Serein repository.
    *   It will not remove directories or symlinks that are not managed by Serein (i.e., not pointing to the Serein repository).
