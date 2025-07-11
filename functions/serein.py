#!/usr/bin/env python3

import os
import shutil
import subprocess
import sys
from datetime import datetime
from typing import Optional
from typing_extensions import Annotated

# --- Dynamically add .venv site-packages to sys.path ---
script_dir = os.path.dirname(os.path.abspath(__file__))
# Assuming .venv is in the parent directory of the 'functions' directory
venv_path = os.path.join(script_dir, '..', '.venv')

# Find the site-packages directory within the virtual environment
# This can vary slightly between Python versions (e.g., python3.8, python3.9)
# We'll look for the first directory matching 'pythonX.Y' inside lib
site_packages_path = None
if os.path.isdir(venv_path):
    lib_path = os.path.join(venv_path, 'lib')
    if os.path.isdir(lib_path):
        for entry in os.listdir(lib_path):
            if entry.startswith('python') and os.path.isdir(os.path.join(lib_path, entry)):
                potential_site_packages = os.path.join(lib_path, entry, 'site-packages')
                if os.path.isdir(potential_site_packages):
                    site_packages_path = potential_site_packages
                    break

if site_packages_path and site_packages_path not in sys.path:
    sys.path.insert(0, site_packages_path)
# --- End dynamic .venv setup ---

import typer
from InquirerPy import inquirer
from InquirerPy.utils import get_style

import resymlink

# --- Helper Functions ---
def info(message):
    """Displays an informational message."""
    typer.echo(typer.style(f"[INFO] {message}", fg=typer.colors.BLUE, bold=True))

def error(message):
    """Displays an error message and exits the script."""
    typer.echo(typer.style(f"[ERROR] {message}", fg=typer.colors.RED, bold=True), err=True)
    sys.exit(1)

def run_command(command, cwd=None, check_error=True, error_message="Command failed", capture_output=True):
    """Runs a shell command and handles errors. Returns stdout, stderr, and exit_code."""
    try:
        result = subprocess.run(command, cwd=cwd, check=False, shell=True, capture_output=capture_output, text=True)
        if check_error and result.returncode != 0:
            error(f"{error_message} (Exit Code: {result.returncode}):\nStdout: {result.stdout.strip()}\nStderr: {result.stderr.strip()}")
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except FileNotFoundError:
        error(f"Command not found: {command.split()[0]}")
    except Exception as e:
        error(f"An unexpected error occurred while running command: {command}\nError: {e}")

def confirm_action(prompt):
    """Prompts the user for confirmation."""
    return typer.confirm(prompt)

app = typer.Typer(name="serein", help="Serein Command-Line Tool", add_completion=False, rich_help_panel="Custom Commands")

# --- Command Implementations ---

@app.command(name="update", help="Update system and Serein configs")
def update_command(
    update_type: Annotated[Optional[str], typer.Argument(help="Update type: 'stable' for latest tag, 'edge' for git pull (default)")] = "edge"
):
    persistent_dir = os.path.join(os.path.expanduser("~"), ".cache", "serein")

    if not os.path.isdir(persistent_dir) or not os.path.isdir(os.path.join(persistent_dir, ".git")):
        error("Serein not installed persistently. Cannot update.")

    info("Checking for rsync...")
    if not shutil.which("rsync"):
        error("rsync is not installed. Please install it to continue.")

    original_cwd = os.getcwd()

    # Create a temporary backup of the current persistent_dir (pre-update state)
    temp_backup_dir = os.path.join(os.path.expanduser("~"), ".cache", "serein_temp_backup")
    shutil.rmtree(temp_backup_dir, ignore_errors=True) # Clean up any previous temp
    os.makedirs(temp_backup_dir, exist_ok=True)

    info(f"Creating temporary backup of current state at {temp_backup_dir}...")
    rsync_temp_command = [
        "rsync", "-a",
        "--exclude=.git",
        "--exclude=.gitignore",
        "--exclude=generations",
        f"{persistent_dir}/", # Source directory (current state)
        f"{temp_backup_dir}/" # Destination directory
    ]
    _, _, _ = run_command(" ".join(rsync_temp_command), error_message="Failed to create temporary backup")

    # Change to persistent_dir for git operations
    os.chdir(persistent_dir)

    before_hash, _, _ = run_command("git rev-parse HEAD", error_message="Failed to get current git hash")

    # Perform the git update
    if update_type == "stable":
        info("Checking for stable updates...")
        _, _, _ = run_command("git fetch --tags", error_message="git fetch failed")
        latest_tag, _, _ = run_command("git describe --tags $(git rev-list --tags --max-count=1)", error_message="Failed to get latest tag")
        current_tag, _, _ = run_command("git describe --tags", error_message="Failed to get current tag")

        if current_tag == latest_tag:
            info("You are already on the latest stable release.")
            os.chdir(original_cwd) # Change back before exiting
            shutil.rmtree(temp_backup_dir) # Clean up temp
            sys.exit(0)

        info(f"Updating to the latest stable release ({latest_tag})...")
        _, _, _ = run_command(f"git checkout {latest_tag}", error_message="git checkout failed. You may have local changes. Please stash or commit them first.")
    else:
        info("Updating to the bleeding edge (git pull)...")
        _, _, _ = run_command("git pull", error_message="git pull failed. You may have local changes. Please stash or commit them first.")

    after_hash, _, _ = run_command("git rev-parse HEAD", error_message="Failed to get new git hash")

    # If no changes, no new generation needed
    if before_hash == after_hash:
        info("Already up to date. No new generation created.")
        os.chdir(original_cwd) # Change back before exiting
        shutil.rmtree(temp_backup_dir) # Clean up temp
        sys.exit(0)

    # Change back to original CWD before creating backup
    os.chdir(original_cwd)

    # Create generation backup from the *temporary backup* (pre-update state)
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
    info(f"Creating generation backup of previous state at {backup_dir}...")

    # Use rsync to copy files from the *temporary backup* (pre-update state)
    rsync_command = [
        "rsync", "-a",
        "--exclude=.git",
        "--exclude=.gitignore",
        "--exclude=generations",
        f"{temp_backup_dir}/", # Source directory (pre-update state from temp)
        f"{backup_dir}/"      # Destination directory
    ]
    _, _, _ = run_command(" ".join(rsync_command), error_message="Failed to create generation backup")

    # Store the *before_hash* for rollback
    with open(os.path.join(backup_dir, ".commit_hash"), "w") as f:
        f.write(before_hash) # Store the hash *before* the update for rollback purposes
    
    shutil.rmtree(temp_backup_dir) # Clean up the temporary backup directory

    # Unsymlink configs
    info("Unsymlinking existing configurations...")
    resymlink.unsymlink_configs(persistent_dir)

    # Resymlink configs
    info("Symlinking new configurations...")
    resymlink.symlink_configs(persistent_dir)

    info("Update complete. A new generation has been created.")

@app.command(name="rollback", help="Rollback to a previous generation")
def rollback_command(
    # No arguments for interactive mode
):
    persistent_dir = os.path.join(os.path.expanduser("~"), ".cache", "serein")
    generation_dir = os.path.join(persistent_dir, "generations")

    # Get available generations
    available_generations = []
    if os.path.isdir(generation_dir):
        for entry in os.listdir(generation_dir):
            if entry.startswith("Generation-") and os.path.isdir(os.path.join(generation_dir, entry)):
                available_generations.append(entry)
    available_generations.sort(reverse=True) # Sort newest first

    if not available_generations:
        info("No generations found to rollback or remove.")
        return

    try:
        action = inquirer.select(
            message="Choose an action:",
            choices=[
                {"name": "Rollback to a generation", "value": "rollback"},
                {"name": "Delete a generation", "value": "delete"},
            ],
            default="rollback",
            style=get_style({"pointer": "#673ab7 bold", "question": "#673ab7 bold"}),
        ).execute()

        if action == "rollback":
            selected_generation = inquirer.select(
                message="Select a generation to rollback to:",
                choices=available_generations,
                default=available_generations[0] if available_generations else None,
                style=get_style({"pointer": "#673ab7 bold", "question": "#673ab7 bold"}),
            ).execute()
            
            if selected_generation is None: # User escaped
                info("Rollback cancelled.")
                return

            target_generation_path = os.path.join(generation_dir, selected_generation)
            if not os.path.isdir(target_generation_path):
                error(f"Generation '{selected_generation}' not found.")

            commit_hash_file = os.path.join(target_generation_path, ".commit_hash")
            if not os.path.isfile(commit_hash_file):
                error(f"Generation '{selected_generation}' is old and does not have a commit hash. Cannot perform a safe rollback.")

            with open(commit_hash_file, "r") as f:
                commit_hash = f.read().strip()

            if not confirm_action(f"Are you sure you want to roll back to generation {selected_generation}?"):
                info("Rollback cancelled.")
                return

            info(f"Rolling back to generation {selected_generation} (commit {commit_hash})...")

            # Unsymlink configs
            info("Unsymlinking existing configurations...")
            resymlink.unsymlink_configs(persistent_dir)

            # Ensure target directories in ~/.config are clean before symlinking
            info("Ensuring target configuration directories are clean...")
            configs_to_manage = resymlink.get_configs_to_manage(persistent_dir)
            for cfg in configs_to_manage:
                target_path = os.path.join(resymlink.CONFIG_DIR, cfg)
                if os.path.isdir(target_path) and not os.path.islink(target_path):
                    if confirm_action(f"Warning: {target_path} exists as a real directory (not a symlink). Remove it to allow symlinking?"):
                        shutil.rmtree(target_path)
                        info(f"Removed real directory: {target_path}")
                    else:
                        error(f"Cannot symlink {cfg}. {target_path} exists as a real directory and user chose not to remove it.")

            # Restore git state by resetting the branch to the specific commit
            info(f"Resetting Serein to commit {commit_hash}...")
            original_cwd = os.getcwd()
            os.chdir(persistent_dir)

            # Use git reset --hard to revert to the specific commit
            # This will discard all current changes and set the HEAD to the specified commit
            _, _, _ = run_command(f"git reset --hard {commit_hash}", error_message="git reset failed. The repository might be in an unexpected state.")
            
            # Clean the repository of any untracked files that might interfere
            _, _, _ = run_command("git clean -fd", error_message="git clean failed. Could not remove untracked files.")

            os.chdir(original_cwd)

            # Resymlink configs
            info("Symlinking new configurations...")
            resymlink.symlink_configs(persistent_dir)

            info("Rollback complete.")

        elif action == "delete":
            selected_generation = inquirer.select(
                message="Select a generation to remove:",
                choices=available_generations,
                default=available_generations[0] if available_generations else None,
                style=get_style({"pointer": "#673ab7 bold", "question": "#673ab7 bold"}),
            ).execute()

            if selected_generation is None: # User escaped
                info("Removal cancelled.")
                return

            target_generation_path = os.path.join(generation_dir, selected_generation)
            if not os.path.isdir(target_generation_path):
                error(f"Generation '{selected_generation}' not found.")
                
            if not confirm_action(f"Are you sure you want to remove generation {selected_generation}? This is irreversible."):
                info("Removal cancelled.")
                return

            shutil.rmtree(target_generation_path)
            info(f"Generation {selected_generation} removed.")

    except KeyboardInterrupt:
        info("Operation cancelled by user.")
        sys.exit(0)

def enable_command(args):
    if args.plugin == "overview":
        info("Enabling hyprtasking (required for overview)...")
        _, _, _ = run_command("hyprpm update", error_message="hyprpm update failed")
        _, _, _ = run_command("hyprpm add https://github.com/raybbian/hyprtasking", error_message="hyprpm add failed")
        _, _, _ = run_command("hyprpm enable hyprtasking", error_message="hyprpm enable failed")
        _, _, _ = run_command("hyprpm reload -nn", error_message="hyprpm reload failed")
        _, _, _ = run_command("hyprctl reload", error_message="hyprctl reload failed")
        info("Hyprtasking enabled.")
    else:
        error("Invalid plugin specified.")

@app.command(name="disable", help="Disable a Serein feature")
def disable_command(
    plugin: Annotated[str, typer.Argument(help="Feature to disable (e.g., 'overview' for Hyprland overview plugin)")]
):
    if plugin == "overview":
        info("Disabling hyprtasking...")
        _, _, _ = run_command("hyprpm remove https://github.com/raybbian/hyprtasking", error_message="hyprpm remove failed")
        _, _, _ = run_command("hyprpm reload -nn", error_message="hyprpm reload failed")
        _, _, _ = run_command("hyprctl reload", error_message="hyprctl reload failed")
        info("Hyprtasking disabled.")
    else:
        error("Invalid plugin specified.")

@app.command(name="uninstall", help="Remove the Serein environment")
def uninstall_command():
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
                _, _, _ = run_command(f"paru -Rns --noconfirm {' '.join(packages_to_remove)}", error_message="Failed to remove packages")
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
        _, _, _ = run_command(f"sudo rm {serein_bin_path}", error_message=f"Failed to remove {serein_bin_path}. Please remove it manually if necessary.")

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

if __name__ == "__main__":
    app(prog_name="serein")