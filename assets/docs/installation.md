# Installation Guide

This document provides a detailed explanation of the `install.sh` script, which is used to install the Serein environment.

## Script Stages

The installation process is divided into two main stages.

### Stage 1: Initial Execution and Cloning

When you first run the installation script, it gathers your preferences for the installation. It asks for:

*   **Installation Mode**: Persistent or One-time.
*   **Installation Version**: Stable or Edge.
*   **Installation Type**: Full or Minimal.
*   **Paru Installation**: Confirms if you want to install the `paru` AUR helper if it's not already installed.
*   **Reboot**: Asks if you want to reboot automatically after the installation.

Based on your choices, it then clones the Serein repository to either a persistent location (`~/.cache/serein`) or a temporary directory. After cloning, it re-executes itself from the new location to begin Stage 2.

### Stage 2: Main Installation Logic

This stage performs the core installation tasks:

1.  **Paru Installation**: If you confirmed it, the script will clone the `paru` repository from the AUR, build it, and install it.
2.  **System Update**: It runs `paru -Syu` to ensure your system is up-to-date before installing new packages.
3.  **Package Installation**: Based on your choice of a "Full" or "Minimal" installation, it installs the corresponding set of packages from the `assets/packages.minimal` and `assets/packages.full` files.
4.  **Configuration Management**: 
    *   It identifies the list of configurations to be replaced.
    *   It asks for your confirmation before removing any existing configurations in your `~/.config` directory.
    *   Depending on whether you chose a persistent or one-time installation, it will either symlink or copy the configuration files from the repository to your `~/.config` directory.
5.  **Serein CLI**: For persistent installations, it symlinks the `serein` command to `/usr/local/bin` to make it accessible system-wide.
6.  **Final Steps**: It creates a Trash directory for Ranger (on full installations) and provides some post-installation best practices.
7.  **Reboot**: If you chose to reboot automatically, it will reboot your system to complete the installation.
