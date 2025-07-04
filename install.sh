#!/bin/bash
# Hyprland Install Script

# Function to check if a command exists
command_exists() {
    command -v "$1" &>/dev/null
}

# Get the directory of the script itself
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# --- Paru Installation ---
if ! command_exists paru; then
    read -rp "Paru is not installed. Install it now? [Y/n]: " install_paru
    if [[ -z "$install_paru" || "$install_paru" =~ ^[Yy]$ ]]; then
        build_dir="/tmp/paru-build"
        rm -rf "$build_dir"
        echo "Cloning paru..."
        git clone https://aur.archlinux.org/paru.git "$build_dir"

        pushd "$build_dir" >/dev/null
            echo "Building & installing paru..."
            makepkg -si --noconfirm
        popd >/dev/null
        rm -rf "$build_dir"

        if ! command_exists paru; then
            echo "Paru installation failed. Exiting." >&2
            exit 1
        fi
    else
        echo "Paru is required to continue. Exiting." >&2
        exit 1
    fi
fi

# --- System Update ---
echo "Updating system with paru -Syu..."
paru -Syu --noconfirm

# --- Installation Type ---
read -rp "Perform a full installation (includes extra packages and configs)? [Y/n]: " full_install_choice
if [[ -z "$full_install_choice" || "$full_install_choice" =~ ^[Yy]$ ]]; then
    INSTALL_TYPE="full"
else
    INSTALL_TYPE="minimal"
fi

# --- Package Lists ---
PKGS_MINIMAL="swww swaylock grim slurp swappy wl-clipboard cliphist libnotify yad playerctl swaync alacritty waybar hyprland rofi-wayland imagemagick xdg-desktop-portal-hyprland xdg-desktop-portal-gtk jq bc papirus-icon-theme catppuccin-gtk-theme-frappe nwg-look bibata-cursor-theme ttf-jetbrains-mono-nerd noto-fonts noto-fonts-emoji noto-fonts-cjk cpio"
PKGS_EXTRA="ranger btop ueberzugpp udiskie udisks2"

# --- Config Lists ---
CONFIG_DIR="$HOME/.config"
REPO_CONFIG_DIR="$SCRIPT_DIR/.config"

CONFIGS_MINIMAL=("hypr" "waybar" "rofi" "swaylock" "swappy" "swaync")
CONFIGS_EXTRA=("alacritty" "fastfetch" "fish" "nvim" "ranger" "udiskie")

# --- Package Installation ---
if [ "$INSTALL_TYPE" == "full" ]; then
    echo "Installing full package set..."
    paru -S --noconfirm --needed $PKGS_MINIMAL $PKGS_EXTRA
else
    echo "Installing minimal package set..."
    paru -S --noconfirm --needed $PKGS_MINIMAL
fi

# --- Configuration Management ---
configs_to_install=("${CONFIGS_MINIMAL[@]}")
if [ "$INSTALL_TYPE" == "full" ]; then
    configs_to_install+=("${CONFIGS_EXTRA[@]}")
fi

echo "Removing old managed configurations..."
for cfg in "${configs_to_install[@]}"; do
    if [ -d "$CONFIG_DIR/$cfg" ]; then
        echo "Removing existing config: $CONFIG_DIR/$cfg"
        rm -rf "$CONFIG_DIR/$cfg"
    fi
done

echo "Copying new configurations..."
mkdir -p "$CONFIG_DIR"

for cfg in "${configs_to_install[@]}"; do
    echo "Copying config: $cfg"
    cp -r "$REPO_CONFIG_DIR/$cfg" "$CONFIG_DIR/"
done

# Create Trash dir for ranger only on full install
if [ "$INSTALL_TYPE" == "full" ]; then
    mkdir -p "$HOME/.local/share/Trash/files"
fi

# --- Hyprland Plugin ---
echo "Enabling hyprtasking (required for overview)..."
hyprpm update
hyprpm add https://github.com/raybbian/hyprtasking
hyprpm enable hyprtasking

echo "Installation complete. Your Hyprland environment should be good to go."
echo "Please reboot for all changes to take effect."
