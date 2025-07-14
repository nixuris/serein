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
    *   `config.py`: Contains all the logic for the `serein config` subcommand, including listing, enabling, and disabling configurations and features.
    *   `update.py`: Implements the `serein update` command.
    *   `rollback.py`: Implements the `serein rollback` command.
    *   `uninstall.py`: Implements the `serein uninstall` command.

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

## Configuration Management (`serein config`)

The `serein config` subcommand provides granular control over which Serein configurations and features are active.

### `serein config` (Interactive Mode)

When you run `serein config` without any subcommands, it launches an interactive interface.

*   **Behavior:**
    *   Presents a list of all available Serein configurations (e.g., `hypr`, `nvim`) and features (e.g., `overview`).
    *   Each item is displayed with its current status (enabled or disabled).
    *   You can use the spacebar to toggle the enabled/disabled state of each item.
    *   Press Enter to confirm your selections. The CLI will then automatically enable or disable the chosen configurations/features.

### `serein config list`

Lists all available Serein configurations and features and their current status.

*   **Output:**
    *   For each item, it shows its name and its status: `enabled`, `enabled (external)`, `unmanaged`, or `disabled`.

### `serein config enable <item_name>`

Enables a specific Serein configuration or feature.

*   **Arguments:**
    *   `<item_name>`: The name of the configuration or feature to enable (e.g., `nvim`, `overview`).

*   **Behavior:**
    *   For a configuration, it creates a symbolic link from the Serein repository to your `~/.config` directory.
    *   For a feature like `overview`, it will install and enable the necessary plugins (e.g., `hyprtasking`).

### `serein config disable <item_name>`

Disables a specific Serein configuration or feature.

*   **Arguments:**
    *   `<item_name>`: The name of the configuration or feature to disable.

*   **Behavior:**
    *   For a configuration, it removes the symbolic link from your `~/.config` directory.
    *   For a feature like `overview`, it will disable the corresponding plugin.
