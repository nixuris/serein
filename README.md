# Serein
Personal Arch Linux Hyprland Configuration for FX507ZU4

# Installation

To install the Serein environment, run the following command in your terminal:

```bash
bash <(curl -s https://raw.githubusercontent.com/nixuris/serein/main/install.sh)
```

The installer will guide you through the rest of the process.

## Installation Script Features

The installation script is designed to be flexible and safe, with the following features:

*   **Two Installation Modes**:
    *   **Persistent (Recommended)**: Clones the repository to `$HOME/.cache/serein` and symlinks the configurations. This allows for easy updates and management using the `serein` command.
    *   **One-Time**: Clones the repository to a temporary directory and copies the configurations. This is a standalone installation that cannot be updated using the `serein` command.
*   **Git History**: You can choose to clone the repository with the full git history, which is useful for developers who may want to contribute to the project.
*   **Automatic `paru` Installation**: If `paru` is not found on your system, the script will offer to install it for you.
*   **System Update**: Before installing any packages, the script will update your system using `paru -Syu`.
*   **Minimal and Full Installation Types**:
    *   **Minimal**: Installs the bare minimum packages required for the Serein environment to function.
    *   **Full**: Installs all the packages, including those for extra features like the ranger file manager and btop system monitor.
*   **Safe Configuration Handling**: Before removing any of your existing configurations, the script will list all the configurations that will be replaced and ask for your confirmation.

# Serein CLI

The `serein` command-line tool is the central hub for managing your Serein environment. It provides the following features:

*   `update [stable|edge]`: Updates your system and Serein configurations. You can choose to update to the latest stable release or the bleeding edge.
*   `rollback <generation>`: Rolls back your Serein configurations to a previous generation.
*   `rollback list`: Lists all the available generations that you can roll back to.
*   `rollback remove <gen>`: Removes a specific generation.
*   `enable overview`: Enables the Hyprland overview plugin (hyprtasking).
*   `disable overview`: Disables the Hyprland overview plugin.
*   `detect-nvidia`: Automatically detects and configures the necessary environment variables for NVIDIA GPUs.
*   `uninstall`: Removes the Serein environment, including all configurations and the `serein` command itself.