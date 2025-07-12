import os
import sys

def info(message):
    """Displays an informational message."""
    print(f"\033[1;34m[INFO]\033[0m {message}")

def error(message):
    """Displays an error message and exits the script."""
    print(f"\033[1;31m[ERROR]\033[0m {message}", file=sys.stderr)
    sys.exit(1)

# --- Config Lists ---
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config")

CONFIGS_MINIMAL = ["hypr", "waybar", "rofi", "swaylock", "swappy", "swaync"]
CONFIGS_EXTRA = ["alacritty", "fastfetch", "fish", "nvim", "ranger", "udiskie"]

def get_configs_to_manage(persistent_dir):
    configs_to_manage = list(CONFIGS_MINIMAL)
    full_install_marker = os.path.join(persistent_dir, ".full_install")
    if os.path.isfile(full_install_marker):
        configs_to_manage.extend(CONFIGS_EXTRA)
    return configs_to_manage

def symlink_configs(persistent_dir):
    info("Symlinking configurations...")
    REPO_CONFIG_DIR = os.path.join(persistent_dir, "config")
    configs = get_configs_to_manage(persistent_dir)
    for cfg in configs:
        source_path = os.path.join(REPO_CONFIG_DIR, cfg)
        target_path = os.path.join(CONFIG_DIR, cfg)

        if os.path.isdir(source_path):
            if os.path.exists(target_path) and not os.path.islink(target_path):
                info(f"Skipping {target_path}: exists and is not a symlink. Please move or remove it manually if you want to symlink.")
                continue
            elif os.path.islink(target_path):
                # If it's already a symlink, ensure it points to the correct place
                if os.readlink(target_path) == source_path:
                    info(f"Symlink for {cfg} already exists and is correct.")
                    continue
                else:
                    info(f"Removing existing incorrect symlink for {cfg}.")
                    os.remove(target_path)
            
            try:
                os.symlink(source_path, target_path)
                info(f"Symlinked {source_path} to {target_path}")
            except OSError as e:
                error(f"Failed to symlink {source_path} to {target_path}: {e}")
        else:
            info(f"Source directory for {cfg} not found: {source_path}. Skipping.")

def unsymlink_configs(persistent_dir):
    info("Removing existing symlinks...")
    REPO_CONFIG_DIR = os.path.join(persistent_dir, "config") # Define here as well
    configs = get_configs_to_manage(persistent_dir)
    for cfg in configs:
        target_path = os.path.join(CONFIG_DIR, cfg)

        if os.path.islink(target_path):
            try:
                os.remove(target_path)
                info(f"Removed symlink: {target_path}")
            except OSError as e:
                error(f"Failed to remove symlink {target_path}: {e}")
        elif os.path.exists(target_path):
            info(f"Skipping {target_path}: exists but is not a symlink.")
        else:
            info(f"No symlink or directory found for {cfg} at {target_path}. Skipping.")
