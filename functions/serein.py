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

import resymlink

# --- Helper Functions ---
def info(message):
    """Displays an informational message."""
    typer.echo(typer.style(f"[INFO] {message}", fg=typer.colors.BLUE, bold=True))

def error(message):
    """Displays an error message and exits the script."""
    typer.echo(typer.style(f"[ERROR] {message}", fg=typer.colors.RED, bold=True), err=True)
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
    os.chdir(persistent_dir)

    # Change to persistent_dir for git operations
    os.chdir(persistent_dir)

    before_hash = run_command("git rev-parse HEAD", error_message="Failed to get current git hash")

    # Perform the git update
    if update_type == "stable":
        info("Checking for stable updates...")
        run_command("git fetch --tags", error_message="git fetch failed")
        latest_tag = run_command("git describe --tags $(git rev-list --tags --max-count=1)", error_message="Failed to get latest tag")
        current_tag = run_command("git describe --tags", error_message="Failed to get current tag")

        if current_tag == latest_tag:
            info("You are already on the latest stable release.")
            os.chdir(original_cwd) # Change back before exiting
            sys.exit(0)

        info(f"Updating to the latest stable release ({latest_tag})...")
        run_command(f"git checkout {latest_tag}", error_message="git checkout failed. You may have local changes. Please stash or commit them first.")
    else:
        info("Updating to the bleeding edge (git pull)...")
        run_command("git pull", error_message="git pull failed. You may have local changes. Please stash or commit them first.")

    after_hash = run_command("git rev-parse HEAD", error_message="Failed to get new git hash")

    # If no changes, no new generation needed
    if before_hash == after_hash:
        info("Already up to date. No new generation created.")
        os.chdir(original_cwd) # Change back before exiting
        sys.exit(0)

    # Change back to original CWD before creating backup
    os.chdir(original_cwd)

    # Create generation backup of the *previous* state
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

    # Use rsync to copy files from the *previous* state (before git pull/checkout)
    # The persistent_dir is already in the *new* state, so we need to checkout the old state temporarily for backup
    # This is complex. A simpler approach is to copy the current state (which is the new state)
    # and store the *previous* commit hash.
    # Let's stick to the original rsync source, but ensure the commit hash is correct.

    # The rsync source is the persistent_dir, which is now the *updated* state.
    # The crucial part is that the .commit_hash file stores the *before_hash*.
    rsync_command = [
        "rsync", "-a",
        "--exclude=.git",
        "--exclude=.gitignore",
        "--exclude=generations",
        f"{persistent_dir}/", # Source directory (now updated state)
        f"{backup_dir}/"      # Destination directory
    ]
    run_command(" ".join(rsync_command), error_message="Failed to create generation backup")

    # Store the *before_hash* for rollback
    with open(os.path.join(backup_dir, ".commit_hash"), "w") as f:
        f.write(before_hash) # Store the hash *before* the update for rollback purposes

    # Unsymlink configs
    info("Unsymlinking existing configurations...")
    resymlink.unsymlink_configs(persistent_dir)

    # Resymlink configs
    info("Symlinking new configurations...")
    resymlink.symlink_configs(persistent_dir)

    info("Update complete. A new generation has been created.")

@app.command(name="rollback", help="Rollback to a previous generation")
def rollback_command(
    generation: Annotated[Optional[str], typer.Argument(help="The generation to rollback to (e.g., Generation-1-2025-01-01)")] = None,
    list_generations: Annotated[bool, typer.Option("--list", "-l", help="List available generations")] = False,
    remove: Annotated[bool, typer.Option("--remove", "-r", help="Remove a specific generation")] = False
):
    persistent_dir = os.path.join(os.path.expanduser("~"), ".cache", "serein")
    generation_dir = os.path.join(persistent_dir, "generations")

    if list_generations:
        info("Available generations:")
        if not os.path.isdir(generation_dir) or not os.listdir(generation_dir):
            typer.echo("No generations found.")
            return
        for gen in sorted(os.listdir(generation_dir)):
            if os.path.isdir(os.path.join(generation_dir, gen)):
                typer.echo(f"- {gen}")
        return

    if remove:
        if not generation:
            error("Please specify a generation to remove.")
        target_generation_path = os.path.join(generation_dir, generation)
        if not os.path.isdir(target_generation_path):
            error(f"Generation '{generation}' not found.")

        if not confirm_action(f"Are you sure you want to remove generation {generation}? This is irreversible."):
            info("Removal cancelled.")
            return

        shutil.rmtree(target_generation_path)
        info(f"Generation {generation} removed.")
        return

    if not generation:
        error("Please specify a generation to roll back to.")

    target_generation_path = os.path.join(generation_dir, generation)
    if not os.path.isdir(target_generation_path):
        error(f"Generation '{generation}' not found.")

    commit_hash_file = os.path.join(target_generation_path, ".commit_hash")
    if not os.path.isfile(commit_hash_file):
        error(f"Generation '{generation}' is old and does not have a commit hash. Cannot perform a safe rollback.")

    with open(commit_hash_file, "r") as f:
        commit_hash = f.read().strip()

    if not confirm_action(f"Are you sure you want to roll back to generation {generation}?"):
        info("Rollback cancelled.")
        return

    info(f"Rolling back to generation {generation} (commit {commit_hash})...")

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

@app.command(name="enable", help="Enable a Serein feature")
def enable_command(
    plugin: Annotated[str, typer.Argument(help="Feature to enable (e.g., 'overview' for Hyprland overview plugin)")]
):
    if plugin == "overview":
        info("Enabling hyprtasking (required for overview)...")
        run_command("hyprpm update", error_message="hyprpm update failed")
        run_command("hyprpm add https://github.com/raybbian/hyprtasking", error_message="hyprpm add failed")
        run_command("hyprpm enable hyprtasking", error_message="hyprpm enable failed")
        run_command("hyprpm reload -nn", error_message="hyprpm reload failed")
        run_command("hyprctl reload", error_message="hyprctl reload failed")
        info("Hyprtasking enabled.")
    else:
        error("Invalid plugin specified.")

@app.command(name="disable", help="Disable a Serein feature")
def disable_command(
    plugin: Annotated[str, typer.Argument(help="Feature to disable (e.g., 'overview' for Hyprland overview plugin)")]
):
    if plugin == "overview":
        info("Disabling hyprtasking...")
        run_command("hyprpm remove https://github.com/raybbian/hyprtasking", error_message="hyprpm remove failed")
        run_command("hyprpm reload -nn", error_message="hyprpm reload failed")
        run_command("hyprctl reload", error_message="hyprctl reload failed")
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

if __name__ == "__main__":
    app(prog_name="serein")