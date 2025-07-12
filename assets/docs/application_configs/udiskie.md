# Udiskie Configuration

This document describes the Udiskie automounter configuration within Serein, focusing on its automation and notification features.

## Overview

The Udiskie configuration (`config.yml`) is set up for convenient and automated handling of removable media.

### `program_options`

This section defines the core behavior of Udiskie:

*   **`automount: true`:** Udiskie is configured to automatically mount removable storage devices (like USB drives, external hard drives) as soon as they are connected to the system. This eliminates the need for manual mounting.
*   **`notify: true`:** User notifications are enabled. This means you will receive visual alerts or messages when a device is successfully mounted or unmounted, providing clear feedback on Udiskie's operations.
*   **`tray: auto`:** Udiskie will manage its own presence in the system tray. It will appear in the tray when there are mounted devices or relevant events, and may hide when inactive, ensuring a clean system tray while still providing access when needed.