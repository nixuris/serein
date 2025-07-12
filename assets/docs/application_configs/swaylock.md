# Swaylock Configuration

This document describes the Swaylock screen locker configuration within Serein.

## Overview

The Swaylock configuration (`config`) is primarily dedicated to defining the color scheme for various elements of the lock screen, providing a visually consistent and informative experience. It utilizes a pastel-like color palette.

### Key Color Settings:

*   **Background:** The lock screen background is set to a very dark gray/black (`#040405`).
*   **Input Ring Colors:** The ring around the password input field changes color based on the state:
    *   **Default:** `#6272A4` (blue/purple)
    *   **Caps Lock Active:** `#fab387` (orange/peach)
    *   **Cleared Input:** `#f5e0dc` (light pink/white)
    *   **Verified (Correct Password):** `#89b4fa` (light blue)
    *   **Wrong (Incorrect Password):** `#eba0ac` (red/pink)
*   **Text Colors:** Text elements, such as the password input and status messages, also adapt their color:
    *   **General Text:** `#cdd6f4` (light blue/purple)
    *   **Caps Lock Text:** `#fab387` (orange/peach)
    *   **Cleared Text:** `#f5e0dc` (light pink/white)
    *   **Verified Text:** `#89b4fa` (light blue)
    *   **Wrong Text:** `#eba0ac` (red/pink)
*   **Highlight Colors:** Specific highlights for keys and backspace are defined:
    *   **Key Highlight:** `#86afef` (blue)
    *   **Backspace Highlight:** `#f5e0dc` (light pink/white)
    *   **Caps Lock Key Highlight:** `#a6e3a1` (light green)
    *   **Caps Lock Backspace Highlight:** `#f5e0dc` (light pink/white)
*   **Transparency:** Most `inside-color` and `line-color` settings are fully transparent (`00000000`), indicating that the inner part of the input circle and any surrounding lines are not visible, contributing to a clean aesthetic.
*   **Layout Text:** The layout text (e.g., keyboard layout indicator) matches the general text color (`#cdd6f4`).