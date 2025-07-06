#!/bin/bash
# Serein Resymlink Script

# --- Helper Functions ---
# Displays an informational message.
info() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

# Displays an error message and exits the script.
error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1" >&2
    exit 1
}

# --- Config Lists ---
CONFIG_DIR="$HOME/.config"
REPO_CONFIG_DIR="$HOME/.cache/serein/.config"

CONFIGS_MINIMAL=("hypr" "waybar" "rofi" "swaylock" "swappy" "swaync")
CONFIGS_EXTRA=("alacritty" "fastfetch" "fish" "nvim" "ranger" "udiskie")

configs_to_manage=("${CONFIGS_MINIMAL[@]}")
if [ -f "$HOME/.cache/serein/.full_install" ]; then
    configs_to_manage+=("${CONFIGS_EXTRA[@]}")
fi

# --- Main Logic ---
# This script is responsible for symlinking and unsymlinking the configurations.
case "$1" in
    --symlink)
        info "Symlinking configurations..."
        for cfg in "${configs_to_manage[@]}"; do
            if [ -d "$REPO_CONFIG_DIR/$cfg" ]; then
                ln -s "$REPO_CONFIG_DIR/$cfg" "$CONFIG_DIR/$cfg"
            fi
        done
        ;;
    --unsymlink)
        info "Removing existing symlinks..."
        for cfg in "${configs_to_manage[@]}"; do
            if [ -L "$CONFIG_DIR/$cfg" ]; then
                rm "$CONFIG_DIR/$cfg"
            fi
        done
        ;;
    *)
        echo "Usage: $0 {--symlink|--unsymlink}"
        exit 1
        ;;
esac
