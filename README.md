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

The `serein` command-line tool is the central hub for managing your Serein environment. It provides the following features:

*   `update [stable|edge]`: Updates your system and Serein configurations. You can choose to update to the latest stable release or the bleeding edge.
*   `rollback`: Display two choices for the rollback of Serein Environment. Either remove or rollback to selected generation.
*   `enable overview`: Enables the Hyprland overview plugin (hyprtasking).
*   `disable overview`: Disables the Hyprland overview plugin.
*   `uninstall`: Removes the Serein environment, including all configurations and the `serein` command itself, all the packages earlier if wanted.

# Documentation

For more detailed information about the inner workings of this environment, including guides for the installer, command-line tool, and utility scripts, please see the main documentation page.

[**View the Serein Documentation**](./assets/docs/README.md)

