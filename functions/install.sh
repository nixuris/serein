#!/bin/bash
# Serein All-in-One Installation Script

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

# Checks if a command exists.
command_exists() {
    command -v "$1" &>/dev/null
}

# --- Stage 1: Initial Execution, Cloning, and Re-execution ---
# This stage is responsible for cloning the repository and re-executing the script from the cloned directory.
if [[ "$1" != "--run-stage-2" ]]; then
    info "Serein Hyprland Environment Installer"

    # Choose installation mode
    read -rp "Choose installation mode [P]ersistent (recommended) or [O]ne-time? [P/o]: " install_mode
    install_mode=${install_mode:-p}

    # Choose git history depth
    read -rp "Clone with full git history? (useful for developers) [y/N]: " clone_history
    clone_history=${clone_history:-n}
    clone_args=""
    if [[ ! "$clone_history" =~ ^[Yy]$ ]]; then
        clone_args="--depth=1"
    fi

    if [[ "$install_mode" =~ ^[Pp]$ ]]; then
        # Persistent Installation
        persistent_dir="$HOME/.cache/serein"
        if [ -d "$persistent_dir" ]; then
            error "Existing persistent installation found at $persistent_dir. Please remove it first or use 'serein update'."
        fi
        info "Cloning repository to $persistent_dir..."
        git clone https://github.com/nixuris/serein.git $clone_args "$persistent_dir" || error "Failed to clone repository."
        
        info "Re-executing installer from the persistent location..."
        exec bash "$persistent_dir/install.sh" --run-stage-2 --persistent
    
    elif [[ "$install_mode" =~ ^[Oo]$ ]]; then
        # One-Time Installation
        temp_dir=$(mktemp -d)
        info "Cloning repository to temporary directory: $temp_dir"
        git clone https://github.com/nixuris/serein.git $clone_args "$temp_dir" || error "Failed to clone repository."

        info "Executing installer from the temporary location..."
        exec bash "$temp_dir/functions/install.sh" --run-stage-2 --one-time
    else
        error "Invalid installation mode selected. Please choose 'P' or 'O'."
    fi
    exit 0
fi

# --- Stage 2: Main Installation Logic ---

# --- Script Setup ---
INSTALL_MODE="one-time" # Default
if [[ "$2" == "--persistent" ]]; then
    INSTALL_MODE="persistent"
fi
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# --- Paru Installation ---
# Installs paru if it is not already installed.
if ! command_exists paru; then
    read -rp "Paru is not installed. Install it now? [Y/n]: " install_paru
    if [[ -z "$install_paru" || "$install_paru" =~ ^[Yy]$ ]]; then
        build_dir="/tmp/paru-build"
        rm -rf "$build_dir"
        info "Cloning paru..."
        git clone https://aur.archlinux.org/paru.git "$build_dir"

        pushd "$build_dir" >/dev/null
            info "Building & installing paru..."
            makepkg -si --noconfirm
        popd >/dev/null
        rm -rf "$build_dir"

        if ! command_exists paru; then
            error "Paru installation failed."
        fi
    else
        error "Paru is required to continue."
    fi
fi

# --- System Update ---
# Updates the system using paru.
info "Updating system with paru -Syu..."
paru -Syu --noconfirm

# --- Installation Type ---
# Asks the user to choose between a full or minimal installation.
read -rp "Perform a full installation (includes extra packages and configs)? [Y/n]: " full_install_choice
if [[ -z "$full_install_choice" || "$full_install_choice" =~ ^[Yy]$ ]]; then
    INSTALL_TYPE="full"
else
    INSTALL_TYPE="minimal"
fi

# --- Package Lists ---
PKGS_MINIMAL=$(cat "$SCRIPT_DIR/packages.minimal")
PKGS_EXTRA=$(cat "$SCRIPT_DIR/packages.full")

# --- Config Lists ---
CONFIG_DIR="$HOME/.config"
REPO_CONFIG_DIR="$SCRIPT_DIR/.config"

CONFIGS_MINIMAL=("hypr" "waybar" "rofi" "swaylock" "swappy" "swaync")
CONFIGS_EXTRA=("alacritty" "fastfetch" "fish" "nvim" "ranger" "udiskie")

# --- Package Installation ---
# Installs the packages based on the chosen installation type.
if [ "$INSTALL_TYPE" == "full" ]; then
    info "Installing full package set..."
    paru -S --noconfirm --needed $PKGS_MINIMAL $PKGS_EXTRA
    touch "$SCRIPT_DIR/.full_install"
else
    info "Installing minimal package set..."
    paru -S --noconfirm --needed $PKGS_MINIMAL
fi

# --- Configuration Management ---
# Removes old configurations and symlinks/copies the new ones.
configs_to_install=("${CONFIGS_MINIMAL[@]}")
if [ "$INSTALL_TYPE" == "full" ]; then
    configs_to_install+=("${CONFIGS_EXTRA[@]}")
fi

info "The following configurations will be removed and replaced:"
for cfg in "${configs_to_install[@]}"; do
    echo "- $CONFIG_DIR/$cfg"
done
read -rp "Are you sure you want to continue? This will remove the configurations listed above. [y/N]: " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    info "Installation cancelled."
    exit 0
fi

info "Removing old managed configurations..."
for cfg in "${configs_to_install[@]}"; do
    if [ -d "$CONFIG_DIR/$cfg" ] || [ -L "$CONFIG_DIR/$cfg" ]; then
        info "Removing existing config: $CONFIG_DIR/$cfg"
        rm -rf "$CONFIG_DIR/$cfg"
    fi
done

mkdir -p "$CONFIG_DIR"

if [ "$INSTALL_MODE" == "persistent" ]; then
    info "Symlinking new configurations for persistent installation..."
    for cfg in "${configs_to_install[@]}"; do
        info "Symlinking config: $cfg"
        ln -s "$REPO_CONFIG_DIR/$cfg" "$CONFIG_DIR/$cfg"
    done
    info "Symlinking serein command to /usr/local/bin..."
    sudo ln -s "$SCRIPT_DIR/../serein" /usr/local/bin/serein
else
    info "Copying new configurations for one-time installation..."
    for cfg in "${configs_to_install[@]}"; do
        info "Copying config: $cfg"
        cp -r "$REPO_CONFIG_DIR/$cfg" "$CONFIG_DIR/"
    done
    info "Copying serein command to /usr/local/bin..."
    sudo cp "$SCRIPT_DIR/../serein" /usr/local/bin/serein
fi

# Create Trash dir for ranger only on full install
if [ "$INSTALL_TYPE" == "full" ]; then
    mkdir -p "$HOME/.local/share/Trash/files"
fi

# --- Final Steps ---
info "Installation complete!"
echo ""
info "--- Post-Installation Best Practices ---"
echo " - Do NOT manually modify files in ~/.cache/serein. Use the configs in ~/.config/ to make changes."
echo " - To remove rollback backups, use 'serein rollback remove <generation>' instead of 'rm -rf'."
echo ""

read -rp "Reboot now to apply all changes? [Y/n]: " reboot_choice
if [[ -z "$reboot_choice" || "$reboot_choice" =~ ^[Yy]$ ]]; then
    info "Rebooting..."
    sudo reboot
else
    info "Please reboot manually to complete the installation."
fi
