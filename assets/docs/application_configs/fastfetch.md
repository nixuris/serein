# Fastfetch Configuration

This document describes the Fastfetch system information tool configuration within Serein.

## Overview

Key configuration details include:

*   **Custom Logo:** The display features a custom ASCII art logo sourced from `~/.config/fastfetch/2b.txt`, with specific padding to align with the information.
*   **Separator:** A single space (`" "`) is used as the separator between the displayed information and the values.
*   **Information Modules:** A comprehensive set of modules are enabled to display system details, each with custom icons and a consistent key color (`33`). These modules include:
    *   Operating System
    *   Uptime
    *   Kernel
    *   Memory Usage
    *   Disk Usage
    *   CPU Information (with custom format `{1} @ {7}`)
    *   GPU Information (with custom format `{1} {2}`)
    *   Installed Packages
    *   Current Shell
    *   Terminal Emulator
    *   Window Manager
    *   Media Playback Information