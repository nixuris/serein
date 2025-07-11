import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime

import resymlink

# --- Helper Functions ---
def info(message):
    """Displays an informational message."""
    print(f"\033[1;34m[INFO]\033[0m {message}")

def error(message):
    """Displays an error message and exits the script."""
    print(f"\033[1;31m[ERROR]\033[0m {message}", file=sys.stderr)
    sys.exit(1)

def run_command(command, cwd=None, check_error=True, error_message="Command failed"):
    """Runs a shell command and handles errors."""
    try:
        result = subprocess.run(command, cwd=cwd, check=check_error, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error(f"{error_message}: {e.stderr.strip()}")
    except FileNotFoundError:
        error(f"Command not found: {command[0]}")

def confirm_action(prompt):
    """Prompts the user for confirmation."""
    while True:
        response = input(f"{prompt} [y/N]: ").strip().lower()
        if response == 'y':
            return True
        elif response == 'n' or response == '':
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

# --- Command Implementations ---

def update_command(args):
    persistent_dir = os.path.join(os.path.expanduser("~"), ".cache", "serein")

    if not os.path.isdir(persistent_dir) or not os.path.isdir(os.path.join(persistent_dir, ".git")):
        error("Serein not installed persistently. Cannot update.")

    info("Checking for rsync...")
    if not shutil.which("rsync"):
        error("rsync is not installed. Please install it to continue.")

    original_cwd = os.getcwd()
    os.chdir(persistent_dir)

    before_hash = run_command("git rev-parse HEAD", error_message="Failed to get current git hash")

    if args.type == "stable":
        info("Checking for stable updates...")
        run_command("git fetch --tags", error_message="git fetch failed")
        latest_tag = run_command("git describe --tags $(git rev-list --tags --max-count=1)", error_message="Failed to get latest tag")
        current_tag = run_command("git describe --tags", error_message="Failed to get current tag")

        if current_tag == latest_tag:
            info("You are already on the latest stable release.")
            os.chdir(original_cwd)
            sys.exit(0)

        info(f"Updating to the latest stable release ({latest_tag})...")
        run_command(f"git checkout {latest_tag}", error_message="git checkout failed. You may have local changes. Please stash or commit them first.")
    else:
        info("Updating to the bleeding edge (git pull)...")
        run_command("git pull", error_message="git pull failed. You may have local changes. Please stash or commit them first.")

    after_hash = run_command("git rev-parse HEAD", error_message="Failed to get new git hash")

    if before_hash == after_hash:
        info("Already up to date. No new generation created.")
        os.chdir(original_cwd)
        sys.exit(0)

    os.chdir(original_cwd) # Change back to original CWD before continuing

    # Create generation backup
    generation_dir = os.path.join(persistent_dir, "generations")
    os.makedirs(generation_dir, exist_ok=True)

    # Find the last generation number
    last_gen_num = 0
    for entry in os.listdir(generation_dir):
        if entry.startswith("Generation-") and os.path.isdir(os.path.join(generation_dir, entry)):
            try:
                # Extract number from "Generation-X-YYYY-MM-DD"
                parts = entry.split('-')
                if len(parts) >= 2:
                    num = int(parts[1])
                    if num > last_gen_num:
                        last_gen_num = num
            except ValueError:
                continue # Ignore directories that don't match the pattern

    generation_num = last_gen_num + 1
    backup_dir = os.path.join(generation_dir, f"Generation-{generation_num}-{datetime.now().strftime('%Y-%m-%d')}")
    info(f"Creating generation backup at {backup_dir}...")

    # Use rsync to copy files, excluding .git, .gitignore, and generations directory
    rsync_command = [
        "rsync", "-a",
        "--exclude=.git",
        "--exclude=.gitignore",
        "--exclude=generations",
        f"{persistent_dir}/", # Source directory, trailing slash is important for rsync
        f"{backup_dir}/"      # Destination directory
    ]
    run_command(" ".join(rsync_command), error_message="Failed to create generation backup")

    # Store commit hash for rollback
    with open(os.path.join(backup_dir, ".commit_hash"), "w") as f:
        f.write(after_hash)

    # Unsymlink configs
    info("Unsymlinking existing configurations...")
    resymlink.unsymlink_configs(persistent_dir)

    # Resymlink configs
    info("Symlinking new configurations...")
    resymlink.symlink_configs(persistent_dir)

    info("Update complete. A new generation has been created.")

def rollback_command(args):
    persistent_dir = os.path.join(os.path.expanduser("~"), ".cache", "serein")
    generation_dir = os.path.join(persistent_dir, "generations")

    if args.list:
        info("Available generations:")
        if not os.path.isdir(generation_dir) or not os.listdir(generation_dir):
            print("No generations found.")
            return
        for gen in sorted(os.listdir(generation_dir)):
            if os.path.isdir(os.path.join(generation_dir, gen)):
                print(f"- {gen}")
        return

    if args.remove:
        if not args.generation:
            error("Please specify a generation to remove.")
        target_generation_path = os.path.join(generation_dir, args.generation)
        if not os.path.isdir(target_generation_path):
            error(f"Generation '{args.generation}' not found.")

        if not confirm_action(f"Are you sure you want to remove generation {args.generation}? This is irreversible."):
            info("Removal cancelled.")
            return

        shutil.rmtree(target_generation_path)
        info(f"Generation {args.generation} removed.")
        return

    if not args.generation:
        error("Please specify a generation to roll back to.")

    target_generation_path = os.path.join(generation_dir, args.generation)
    if not os.path.isdir(target_generation_path):
        error(f"Generation '{args.generation}' not found.")

    commit_hash_file = os.path.join(target_generation_path, ".commit_hash")
    if not os.path.isfile(commit_hash_file):
        error(f"Generation '{args.generation}' is old and does not have a commit hash. Cannot perform a safe rollback.")

    with open(commit_hash_file, "r") as f:
        commit_hash = f.read().strip()

    if not confirm_action(f"Are you sure you want to roll back to generation {args.generation}?"):
        info("Rollback cancelled.")
        return

    info(f"Rolling back to generation {args.generation} (commit {commit_hash})...")

    # Unsymlink configs
    info("Unsymlinking existing configurations...")
    resymlink.unsymlink_configs(persistent_dir)

    # Restore git state
    original_cwd = os.getcwd()
    os.chdir(persistent_dir)

    # Check for uncommitted changes
    if run_command("git diff-index --quiet HEAD --", check_error=False) != "":
        error("You have uncommitted changes in your Serein directory. Please commit or stash them before rolling back.")

    run_command(f"git checkout {commit_hash}", error_message="git checkout failed. The repository might be in an unexpected state.")
    os.chdir(original_cwd)

    # Resymlink configs
    info("Symlinking new configurations...")
    resymlink.symlink_configs(persistent_dir)

    info("Rollback complete.")

def enable_command(args):
    if args.plugin == "overview":
        info("Enabling hyprtasking (required for overview)...")
        run_command("hyprpm update", error_message="hyprpm update failed")
        run_command("hyprpm add https://github.com/raybbian/hyprtasking", error_message="hyprpm add failed")
        run_command("hyprpm enable hyprtasking", error_message="hyprpm enable failed")
        run_command("hyprpm reload -nn", error_message="hyprpm reload failed")
        run_command("hyprctl reload", error_message="hyprctl reload failed")
        info("Hyprtasking enabled.")
    else:
        error("Invalid plugin specified.")

def disable_command(args):
    if args.plugin == "overview":
        info("Disabling hyprtasking...")
        run_command("hyprpm remove https://github.com/raybbian/hyprtasking", error_message="hyprpm remove failed")
        run_command("hyprpm reload -nn", error_message="hyprpm reload failed")
        run_command("hyprctl reload", error_message="hyprctl reload failed")
        info("Hyprtasking disabled.")
    else:
        error("Invalid plugin specified.")

def uninstall_command(args):
    persistent_dir = os.path.join(os.path.expanduser("~"), ".cache", "serein")

    if not confirm_action("Are you sure you want to uninstall Serein? This will remove all configurations and the serein command."):
        info("Uninstallation cancelled.")
        return

    remove_packages = confirm_action("Do you want to remove all installed packages as well?")

    info("Uninstalling Serein...")

    if not os.path.isdir(persistent_dir):
        error("Serein is not installed persistently.")

    if remove_packages:
        info("Removing installed packages...")
        minimal_packages_path = os.path.join(persistent_dir, "assets", "packages.minimal")
        full_packages_path = os.path.join(persistent_dir, "assets", "packages.full")
        
        packages_to_remove = []
        if os.path.isfile(minimal_packages_path):
            with open(minimal_packages_path, "r") as f:
                packages_to_remove.extend(f.read().splitlines())
        
        if os.path.isfile(os.path.join(persistent_dir, ".full_install")):
            info("Full installation detected. Removing all packages...")
            if os.path.isfile(full_packages_path):
                with open(full_packages_path, "r") as f:
                    packages_to_remove.extend(f.read().splitlines())
        else:
            info("Minimal installation detected. Removing minimal packages...")
        
        if packages_to_remove:
            # Filter out empty strings from the list
            packages_to_remove = [pkg for pkg in packages_to_remove if pkg.strip()]
            if packages_to_remove:
                run_command(f"paru -Rns --noconfirm {' '.join(packages_to_remove)}", error_message="Failed to remove packages")
            else:
                info("No packages to remove.")
        else:
            info("No package lists found to remove.")

    info("Unsymlinking configurations...")
    resymlink.unsymlink_configs(persistent_dir)

    # Remove serein executable (requires sudo)
    serein_bin_path = "/usr/local/bin/serein"
    if os.path.exists(serein_bin_path):
        info(f"Removing {serein_bin_path}. This may require sudo privileges.")
        run_command(f"sudo rm {serein_bin_path}", error_message=f"Failed to remove {serein_bin_path}. Please remove it manually if necessary.")

    # Remove persistent directory
    if os.path.isdir(persistent_dir):
        info(f"Removing Serein persistent directory: {persistent_dir}")
        shutil.rmtree(persistent_dir)

    # Remove other cache directories
    rofi_cache = os.path.join(os.path.expanduser("~"), ".cache", "rofi")
    rofi_icon_cache = os.path.join(os.path.expanduser("~"), ".cache", "rofi_icon")
    user_conf = os.path.join(os.path.expanduser("~"), "user.conf")

    if os.path.isdir(rofi_cache):
        info(f"Removing Rofi cache: {rofi_cache}")
        shutil.rmtree(rofi_cache)
    if os.path.isdir(rofi_icon_cache):
        info(f"Removing Rofi icon cache: {rofi_icon_cache}")
        shutil.rmtree(rofi_icon_cache)
    if os.path.isfile(user_conf):
        info(f"Removing user.conf: {user_conf}")
        os.remove(user_conf)

    info("Serein has been uninstalled.")

# --- Main Parser Setup ---
def main():
    parser = argparse.ArgumentParser(
        description="Serein Command-Line Tool",
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update system and Serein configs")
    update_parser.add_argument("type", nargs="?", default="edge", choices=["stable", "edge"],
                               help="Update type: 'stable' for latest tag, 'edge' for git pull (default)")
    update_parser.set_defaults(func=update_command)

    # Rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Rollback to a previous generation")
    rollback_parser.add_argument("generation", nargs="?", help="The generation to rollback to (e.g., Generation-1-2025-01-01)")
    rollback_parser.add_argument("--list", action="store_true", help="List available generations")
    rollback_parser.add_argument("--remove", action="store_true", help="Remove a specific generation")
    rollback_parser.set_defaults(func=rollback_command)

    # Enable command
    enable_parser = subparsers.add_parser("enable", help="Enable a Serein feature")
    enable_parser.add_argument("plugin", choices=["overview"], help="Feature to enable (e.g., 'overview' for Hyprland overview plugin)")
    enable_parser.set_defaults(func=enable_command)

    # Disable command
    disable_parser = subparsers.add_parser("disable", help="Disable a Serein feature")
    disable_parser.add_argument("plugin", choices=["overview"], help="Feature to disable (e.g., 'overview' for Hyprland overview plugin)")
    disable_parser.set_defaults(func=disable_command)

    # Uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Remove the Serein environment")
    uninstall_parser.set_defaults(func=uninstall_command)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)

if __name__ == "__main__":
    main()
