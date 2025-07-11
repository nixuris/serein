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

# --- Input Gathering Functions ---
get_user_choices() {
    info "Serein Hyprland Environment Installer"
    info "Please answer the following questions to configure your installation."

    # Choose installation mode
    read -rp "Choose installation mode [P]ersistent or [O]ne-time? [P/o]: " INSTALL_MODE_CHOICE
    INSTALL_MODE_CHOICE=${INSTALL_MODE_CHOICE:-p}

    # Choose installation version
    read -rp "Choose installation version [S]table or [E]dge? [S/e]: " INSTALL_VERSION_CHOICE
    INSTALL_VERSION_CHOICE=${INSTALL_VERSION_CHOICE:-s}

    # Choose installation type
    read -rp "[F]ull installation or [M]inimal installation (recommended)? [F/m]: " FULL_INSTALL_CHOICE
    FULL_INSTALL_CHOICE=${FULL_INSTALL_CHOICE:-F}

    # Confirm Paru installation
    if ! command_exists paru; then
      read -rp "Paru is not installed. Install it now? (required for the installation) [Y/n]: " PARU_INSTALL_CHOICE
        PARU_INSTALL_CHOICE=${PARU_INSTALL_CHOICE:-y}
    else
        PARU_INSTALL_CHOICE="n" # Paru is already installed
    fi

    # Confirm reboot
    read -rp "Reboot automatically after installation? [Y/n]: " REBOOT_CHOICE
    REBOOT_CHOICE=${REBOOT_CHOICE:-y}
}

# --- Stage 1: Initial Execution, Cloning, and Re-execution ---
run_stage_1() {
    local install_mode=$1
    local install_version=$2

    local clone_args=""
    if [[ "$install_version" =~ ^[Ee]$ ]]; then
        info "Using bleeding edge installation (shallow clone)."
        clone_args="--depth=1"
    else
        info "Using stable installation (cloning latest tag)."
        latest_tag=$(git ls-remote --tags https://github.com/nixuris/serein.git | awk '{print $2}' | grep -v '{}' | awk -F/ '{print $3}' | sort -V | tail -n 1)
        if [ -z "$latest_tag" ]; then
            error "Could not find latest stable tag. Please try the edge installation."
        fi
        clone_args="--branch $latest_tag --single-branch"
    fi

    if [[ "$install_mode" =~ ^[Pp]$ ]]; then
        # Persistent Installation
        local persistent_dir="$HOME/.cache/serein"
        if [ -d "$persistent_dir" ]; then
            error "Existing persistent installation found at $persistent_dir. Please remove it first or use 'serein update'."
        fi
        info "Cloning repository to $persistent_dir..."
        git clone https://github.com/nixuris/serein.git $clone_args "$persistent_dir" || error "Failed to clone repository."
        
        info "Re-executing installer from the persistent location..."
        exec bash "$persistent_dir/functions/install.sh" --run-stage-2 --persistent "$FULL_INSTALL_CHOICE" "$PARU_INSTALL_CHOICE" "$REBOOT_CHOICE"
    
    elif [[ "$install_mode" =~ ^[Oo]$ ]]; then
        # One-Time Installation
        local temp_dir=$(mktemp -d)
        info "Cloning repository to temporary directory: $temp_dir"
        git clone https://github.com/nixuris/serein.git $clone_args "$temp_dir" || error "Failed to clone repository."

        info "Executing installer from the temporary location..."
        exec bash "$temp_dir/functions/install.sh" --run-stage-2 --one-time "$FULL_INSTALL_CHOICE" "$PARU_INSTALL_CHOICE" "$REBOOT_CHOICE"
    else
        error "Invalid installation mode selected. Please choose 'P' or 'O'."
    fi
}

# --- Stage 2: Main Installation Logic ---
run_stage_2() {
    # --- Script Setup ---
    local INSTALL_MODE="one-time" # Default
    if [[ "$2" == "--persistent" ]]; then
        INSTALL_MODE="persistent"
    fi
    local FULL_INSTALL_CHOICE=$3
    local PARU_INSTALL_CHOICE=$4
    local REBOOT_CHOICE=$5

    local SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
    local REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

    # --- Paru Installation ---
    if [[ "$PARU_INSTALL_CHOICE" =~ ^[Yy]$ ]]; then
        local build_dir="/tmp/paru-build"
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
    elif ! command_exists paru; then
        error "Paru is required to continue."
    fi

    # --- System Update ---
    info "Updating system with paru -Syu..."
    paru -Syu --noconfirm

    # --- Python Environment Setup ---
    info "Setting up Python virtual environment..."
    python3 -m venv "$REPO_ROOT/.venv" || error "Failed to create Python virtual environment."
    source "$REPO_ROOT/.venv/bin/activate" || error "Failed to activate virtual environment."
    pip install --upgrade pip || error "Failed to upgrade pip."
    pip install "typer[all]" typing-extensions inquirerpy || error "Failed to install Python dependencies."
    deactivate # Deactivate the venv after installation

    # --- Installation Type ---
    local INSTALL_TYPE="minimal"
    if [[ "$FULL_INSTALL_CHOICE" =~ ^[Ff]$ ]]; then
        INSTALL_TYPE="full"
    fi

    # --- Package Lists ---
    local PKGS_MINIMAL=$(cat "$REPO_ROOT/assets/packages.minimal")
    local PKGS_EXTRA=$(cat "$REPO_ROOT/assets/packages.full")

    # --- Config Lists ---
    local CONFIG_DIR="$HOME/.config"
    local REPO_CONFIG_DIR="$REPO_ROOT/.config"

    local CONFIGS_MINIMAL=("hypr" "waybar" "rofi" "swaylock" "swappy" "swaync")
    local CONFIGS_EXTRA=("alacritty" "fastfetch" "fish" "nvim" "ranger" "udiskie")

    # --- Package Installation ---
    if [ "$INSTALL_TYPE" == "full" ]; then
        info "Installing full package set..."
        paru -S --noconfirm --needed $PKGS_MINIMAL $PKGS_EXTRA
        touch "$REPO_ROOT/.full_install"
    else
        info "Installing minimal package set..."
        paru -S --noconfirm --needed $PKGS_MINIMAL
    fi

    # --- Configuration Management ---
    local configs_to_install=("${CONFIGS_MINIMAL[@]}")
    if [ "$INSTALL_TYPE" == "full" ]; then
        configs_to_install+=("${CONFIGS_EXTRA[@]}")
    fi

    info "The following configurations will be removed and replaced:"
    for cfg in "${configs_to_install[@]}"; do
        echo "- $CONFIG_DIR/$cfg"
    done
    read -rp "Are you sure you want to continue? This will remove the configurations listed above. [Y/n]: " confirm
    if [[ "$confirm" =~ ^[Nn]$ ]]; then
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
    local ROFI_IMG_PATH="$HOME/.cache/rofi"
    if [ "$INSTALL_MODE" == "persistent" ]; then
        info "Symlinking new configurations for persistent installation..."
        for cfg in "${configs_to_install[@]}"; do
            info "Symlinking config: $cfg"
            ln -s "$REPO_CONFIG_DIR/$cfg" "$CONFIG_DIR/$cfg"
        done
        cp "$REPO_ROOT/.config/user.conf" "$HOME"
        mkdir -p "$ROFI_IMG_PATH"
        cp "$REPO_ROOT/.config/img_path.rasi" "$ROFI_IMG_PATH"
        cp -rf "$REPO_ROOT/assets/Wallpapers" "$HOME"
        info "Symlinking serein command to /usr/local/bin..."
        sudo ln -s "$REPO_ROOT/serein" /usr/local/bin/serein
    else
        info "Copying new configurations for one-time installation..."
        for cfg in "${configs_to_install[@]}"; do
            info "Copying config: $cfg"
            cp -r "$REPO_CONFIG_DIR/$cfg" "$CONFIG_DIR/"
        done
        cp "$REPO_ROOT/.config/user.conf" "$HOME"
        mkdir -p "$ROFI_IMG_PATH"
        cp "$REPO_ROOT/.config/img_path.rasi" "$ROFI_IMG_PATH"
        cp -rf "$REPO_ROOT/assets/Wallpapers" "$HOME"
        info "Skipping serein CLI installation for one-time mode."
    fi

    # Create Trash dir for ranger only on full install
    if [ "$INSTALL_TYPE" == "full" ]; then
        mkdir -p "$HOME/.local/share/Trash/files"
    fi

    # --- Final Steps ---
    info "Installation complete!"
    echo ""
    if [ "$INSTALL_MODE" == "persistent" ]; then
        info "--- Post-Installation Best Practices ---"
        echo " - Do NOT manually modify files in ~/.cache/serein. Use the 'serein' command to manage your environment."
        echo " - To remove rollback backups, use 'serein rollback' instead of 'rm -rf'."
    fi
    echo " - Please make sure you put wallpapers in the ~/Wallpapers directory."
    echo " - The hyprland user config will be put at ~/user.conf, edit it according to the wiki or example configurations."    
    echo " - Prioritize adjust the important section in ~/usr.conf."    
    echo ""

    if [[ "$REBOOT_CHOICE" =~ ^[Yy]$ ]]; then
        info "Rebooting..."
        sudo reboot
    else
        info "Please reboot manually to complete the installation."
    fi
}

# --- Main Script Logic ---
main() {
    if [[ "$1" == "--run-stage-2" ]]; then
        run_stage_2 "$@"
    else
        get_user_choices
        run_stage_1 "$INSTALL_MODE_CHOICE" "$INSTALL_VERSION_CHOICE"
    fi
}

main "$@"
