# Serein
A simple Hyprland environment.
# Installation

To install the Serein environment, run the following command in your terminal:

```bash
bash <(curl -s https://raw.githubusercontent.com/nixuris/serein/main/functions/install.sh)
```

The installer will guide you through the rest of the process.

## Installation Script Features

The installation script is designed to be flexible and safe, with the following features:

*   **Two Installation Modes**:
    *   **Persistent**: Clones the repository to `$HOME/.cache/serein` and symlinks the configurations. This allows for easy updates and management using the `serein` command.
    *   **One-Time**: Clones the repository to a temporary directory and copies the configurations. This is a standalone installation that won't have the `serein` cli tool.
*   **Stable or Edge Installation**:
    *   **Stable**: Clones the latest stable release tag, ensuring a well-tested configuration. This is the recommended choice for most users.
    *   **Edge**: Performs a shallow clone of the main branch for those who want the latest, cutting-edge features.
*   **System Update**: Before installing any packages, the script will update your system using `paru -Syu`.
*   **Minimal and Full Installation Types**:
    *   **Minimal (Recommended)**: Installs the bare minimum packages and symlink/copy the bare minimum config files required for the Serein environment to function.
    *   **Full**: Installs all the packages, and symlink/copy extra configurations like alacritty, fastfetch, fish, neovim, ranger, udiskie.
*   **Safe Configuration Handling**: Before removing any of your existing configurations, the script will list all the configurations that will be replaced and ask for your confirmation.

# Serein CLI

The `serein` command-line tool is the central hub for managing your Serein environment. It provides a robust set of features for updating, managing configurations, and maintaining your Hyprland setup.

## Commands

*   `serein update [stable|edge] [--force|-f]`:
    *   Updates your system and Serein configurations.
    *   `stable`: Updates to the latest stable release tag.
    *   `edge` (default): Performs a `git pull` to get the latest bleeding-edge features.
    *   `--force`, `-f`: Force update even if on the latest version.
*   `serein rollback [--no-confirm|-y] [--keep-backup|-k]`:
    *   Allows you to revert to a previous configuration "generation" or manage existing backups.
    *   Provides an interactive prompt to choose between rolling back or deleting a generation.
    *   `--no-confirm`, `-y`: Skips confirmation prompts for actions.
    *   `--keep-backup`, `-k`: When deleting a generation, keeps the backup files instead of removing them.
*   `serein enable <plugin>`:
    *   Enables a specific Serein feature or plugin.
    *   Currently supports:
        *   `overview`: Enables the Hyprland overview plugin (hyprtasking).
*   `serein disable <plugin>`:
    *   Disables a specific Serein feature or plugin.
    *   Currently supports:
        *   `overview`: Disables the Hyprland overview plugin (hyprtasking).
*   `serein uninstall`:
    *   Removes the Serein environment, including all configurations and the `serein` command itself.
    *   Optionally removes all packages installed by Serein.

## Configuration Management (`serein config`)

The `serein config` subcommand provides granular control over your Serein configurations.

*   `serein config`:
    *   Runs an interactive mode, allowing you to select configurations to enable or disable using a checkbox interface.
*   `serein config list`:
    *   Lists all available Serein configurations and their current status (enabled, unmanaged, disabled).
*   `serein config enable <config_name>`:
    *   Enables a specific configuration by creating a symlink from the Serein repository to your `~/.config` directory.
*   `serein config disable <config_name>`:
    *   Disables a specific configuration by removing its symlink from your `~/.config` directory.

For more detailed information and examples, please refer to the dedicated Serein CLI documentation.

# Documentation

For more detailed information about the inner workings of this environment, including guides for the installer, command-line tool, and utility scripts, please see the main documentation page.

[**View the Serein Documentation**](./assets/docs/README.md)

