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
import json

# --- Helper Functions ---

def get_generations_path():
    """Returns the path to the generations.json file."""
    return os.path.join(get_persistent_dir(), "generations.json")

def read_generations():
    """Reads and parses the generations.json file. Creates it if it doesn't exist."""
    generations_path = get_generations_path()
    if not os.path.exists(generations_path):
        # If the file doesn't exist, create it with an empty list
        with open(generations_path, "w") as f:
            json.dump({"generations": []}, f, indent=4)
        return []
    try:
        with open(generations_path, "r") as f:
            data = json.load(f)
            # Basic validation
            if "generations" in data and isinstance(data["generations"], list):
                return data["generations"]
            else:
                # Handle corrupted or invalid format
                error("generations.json is malformed. Please fix or delete it.")
                return [] # Should not be reached due to error()
    except (json.JSONDecodeError, FileNotFoundError):
        error("Could not read or parse generations.json. Please fix or delete it.")
        return [] # Should not be reached due to error()

def write_generations(generations_data):
    """Writes the given data to the generations.json file."""
    generations_path = get_generations_path()
    with open(generations_path, "w") as f:
        json.dump({"generations": generations_data}, f, indent=4)
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
config_app = typer.Typer(name="config", help="Manage Serein configurations.")
app.add_typer(config_app)

@config_app.command(name="list", help="List all available configurations and their status.")
def config_list():
    """Lists all available configurations and their status."""
    if not is_persistent_install():
        error("Configuration management is only available for persistent installations.")
        return

    info("Available Serein Configurations:")
    all_configs = resymlink.CONFIGS_MINIMAL + resymlink.CONFIGS_EXTRA
    repo_config_dir = os.path.join(get_persistent_dir(), "config")

    for cfg in sorted(all_configs):
        source_path = os.path.join(repo_config_dir, cfg)
        target_path = os.path.join(resymlink.CONFIG_DIR, cfg)
        status = ""

        if not os.path.exists(source_path):
            status = typer.style("source missing", fg=typer.colors.RED)
        elif os.path.islink(target_path):
            if os.readlink(target_path) == source_path:
                status = typer.style("enabled", fg=typer.colors.GREEN)
            else:
                status = typer.style("enabled (external)", fg=typer.colors.YELLOW)
        elif os.path.exists(target_path):
            status = typer.style("unmanaged", fg=typer.colors.YELLOW)
        else:
            status = typer.style("disabled", fg=typer.colors.WHITE)
        
        typer.echo(f"- {cfg}: {status}")

@config_app.command(name="enable", help="Enable a specific configuration by creating a symlink.")
def config_enable(config_name: str):
    """Enables a specific configuration by creating a symlink."""
    if not is_persistent_install():
        error("Configuration management is only available for persistent installations.")
        return

    all_configs = resymlink.CONFIGS_MINIMAL + resymlink.CONFIGS_EXTRA
    if config_name not in all_configs:
        error(f"Unknown configuration: {config_name}")
        return

    repo_config_dir = os.path.join(get_persistent_dir(), "config")
    source_path = os.path.join(repo_config_dir, config_name)
    target_path = os.path.join(resymlink.CONFIG_DIR, config_name)

    if not os.path.exists(source_path):
        error(f"Source directory not found for {config_name} in the Serein repository.")
        return

    if os.path.islink(target_path) and os.readlink(target_path) == source_path:
        info(f"Configuration '{config_name}' is already enabled.")
        return

    if os.path.exists(target_path):
        if not confirm_action(f"Warning: '{target_path}' already exists and is not a Serein symlink. Overwrite it?"):
            info("Enable operation cancelled.")
            return
        if os.path.islink(target_path):
            os.remove(target_path)
        else:
            shutil.rmtree(target_path)

    try:
        os.symlink(source_path, target_path)
        info(f"Successfully enabled configuration: {config_name}")
    except OSError as e:
        error(f"Failed to enable configuration {config_name}: {e}")

@config_app.command(name="disable", help="Disable a specific configuration by removing its symlink.")
def config_disable(config_name: str):
    """Disables a specific configuration by removing its symlink."""
    if not is_persistent_install():
        error("Configuration management is only available for persistent installations.")
        return

    repo_config_dir = os.path.join(get_persistent_dir(), "config")
    source_path = os.path.join(repo_config_dir, config_name)
    target_path = os.path.join(resymlink.CONFIG_DIR, config_name)

    if not os.path.islink(target_path):
        info(f"Configuration '{config_name}' is not an enabled Serein symlink. Nothing to do.")
        return

    if os.readlink(target_path) != source_path:
        info(f"Configuration '{config_name}' is a symlink, but it does not point to the Serein repository. It will not be removed.")
        return

    try:
        os.remove(target_path)
        info(f"Successfully disabled configuration: {config_name}")
    except OSError as e:
        error(f"Failed to disable configuration {config_name}: {e}")

@config_app.callback(invoke_without_command=True)
def config_main(ctx: typer.Context):
    """Manage Serein configurations interactively."""
    if ctx.invoked_subcommand is not None:
        return

    if not is_persistent_install():
        error("Configuration management is only available for persistent installations.")
        return

    all_configs = resymlink.CONFIGS_MINIMAL + resymlink.CONFIGS_EXTRA
    repo_config_dir = os.path.join(get_persistent_dir(), "config")

    # Get the current state of all configs
    current_states = {}
    for cfg in all_configs:
        target_path = os.path.join(resymlink.CONFIG_DIR, cfg)
        source_path = os.path.join(repo_config_dir, cfg)
        current_states[cfg] = os.path.islink(target_path) and os.readlink(target_path) == source_path

    # Create choices for the interactive prompt
    choices = [
        {"name": cfg, "value": cfg, "enabled": current_states[cfg]} for cfg in sorted(all_configs)
    ]

    try:
        selected_configs = inquirer.checkbox(
            message="Select configurations to enable/disable (Space to toggle, Enter to confirm):",
            choices=choices,
            cycle=False,
            style=get_style({"pointer": "#673ab7 bold", "question": "#673ab7 bold"}),
        ).execute()

        if selected_configs is None: # User escaped
            info("Configuration change cancelled.")
            return

        # Determine which configs to enable and disable
        for cfg in all_configs:
            should_be_enabled = cfg in selected_configs
            is_currently_enabled = current_states[cfg]

            if should_be_enabled and not is_currently_enabled:
                config_enable(cfg)
            elif not should_be_enabled and is_currently_enabled:
                config_disable(cfg)

        info("Configuration changes applied successfully.")

    except KeyboardInterrupt:
        info("Operation cancelled by user.")
        sys.exit(0)

# --- Command Implementations ---

def is_persistent_install():
    """Checks if Serein is installed persistently."""
    return os.path.isdir(os.path.join(os.path.expanduser("~"), ".cache", "serein", ".git"))

def get_persistent_dir():
    """Returns the persistent directory path."""
    return os.path.join(os.path.expanduser("~"), ".cache", "serein")

@app.command(name="update", help="Update system and Serein configs")
def update_command(
    update_type: Annotated[Optional[str], typer.Argument(help="Update type: 'stable' for latest tag, 'edge' for git pull (default)")] = "edge",
    force: Annotated[bool, typer.Option("--force", "-f", help="Force update even if on the latest version.")] = False
):
    if not is_persistent_install():
        error("Serein is not installed persistently. Cannot update.")
    
    persistent_dir = get_persistent_dir()

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

        if current_tag == latest_tag and not force:
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
    if before_hash == after_hash and not force:
        info("Already up to date. No new generation created.")
        os.chdir(original_cwd) # Change back before exiting
        shutil.rmtree(temp_backup_dir) # Clean up temp
        sys.exit(0)

    # Change back to original CWD before creating backup
    os.chdir(original_cwd)

    # Create generation backup from the *temporary backup* (pre-update state)
    generations = read_generations()
    last_gen_id = generations[-1]["id"] if generations else 0
    new_gen_id = last_gen_id + 1

    backup_dir = os.path.join(get_persistent_dir(), "generations", str(new_gen_id))
    os.makedirs(backup_dir, exist_ok=True)

    info(f"Creating generation backup {new_gen_id} of previous state at {backup_dir}...")

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

    # Add new generation to the JSON file
    new_generation = {
        "id": new_gen_id,
        "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "commit_hash": before_hash,
        "description": f"Update to {after_hash[:7]}",
        "archived": False
    }
    generations.append(new_generation)
    write_generations(generations)
    
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
    no_confirm: Annotated[bool, typer.Option("--no-confirm", "-y", help="Skip confirmation prompts.")] = False,
    keep_backup: Annotated[bool, typer.Option("--keep-backup", "-k", help="Keep backup files when deleting a generation.")] = False
):
    if not is_persistent_install():
        error("Serein is not installed persistently. Cannot rollback.")
        
    persistent_dir = get_persistent_dir()
    generations = read_generations()
    
    # Filter out archived generations for the user to choose from
    available_generations = [gen for gen in generations if not gen.get("archived", False)]

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
            choice_to_generation = { 
                f'{gen["id"]}: {gen["date"]} - {gen["description"]}': gen 
                for gen in reversed(available_generations) 
            }

            selected_choice = inquirer.select(
                message="Select a generation to rollback to:",
                choices=list(choice_to_generation.keys()),
                style=get_style({"pointer": "#673ab7 bold", "question": "#673ab7 bold"}),
            ).execute()
            
            if selected_choice is None: # User escaped
                info("Rollback cancelled.")
                return

            selected_generation = choice_to_generation[selected_choice]
            commit_hash = selected_generation["commit_hash"]

            if not no_confirm and not confirm_action(f'Are you sure you want to roll back to generation {selected_generation["id"]}'):
                info("Rollback cancelled.")
                return

            info(f'Rolling back to generation {selected_generation["id"]} (commit {commit_hash})...')

            # Unsymlink configs
            info("Unsymlinking existing configurations...")
            resymlink.unsymlink_configs(persistent_dir)

            # Restore git state by resetting the branch to the specific commit
            info(f"Resetting Serein to commit {commit_hash}...")
            original_cwd = os.getcwd()
            os.chdir(persistent_dir)

            _, _, _ = run_command(f"git reset --hard {commit_hash}", error_message="git reset failed.")
            _, _, _ = run_command("git clean -fd", error_message="git clean failed.")

            os.chdir(original_cwd)

            # Resymlink configs
            info("Symlinking new configurations...")
            resymlink.symlink_configs(persistent_dir)

            info("Rollback complete.")

        elif action == "delete":
            choice_to_generation = { 
                f'{gen["id"]}: {gen["date"]} - {gen["description"]}': gen 
                for gen in reversed(available_generations) 
            }

            selected_choice = inquirer.select(
                message="Select a generation to remove:",
                choices=list(choice_to_generation.keys()),
                style=get_style({"pointer": "#673ab7 bold", "question": "#673ab7 bold"}),
            ).execute()

            if selected_choice is None: # User escaped
                info("Removal cancelled.")
                return

            selected_generation = choice_to_generation[selected_choice]
            gen_id_to_remove = selected_generation["id"]

            if not no_confirm and not confirm_action(f"Are you sure you want to remove generation {gen_id_to_remove}?"):
                info("Removal cancelled.")
                return

            # Find the generation in the original list and mark it as archived
            for gen in generations:
                if gen["id"] == gen_id_to_remove:
                    gen["archived"] = True
                    break
            
            write_generations(generations)
            info(f"Generation {gen_id_to_remove} has been archived and will no longer appear in the list.")

            if not keep_backup:
                backup_dir_to_remove = os.path.join(get_persistent_dir(), "generations", str(gen_id_to_remove))
                if os.path.isdir(backup_dir_to_remove):
                    shutil.rmtree(backup_dir_to_remove)
                    info(f"Removed backup directory for generation {gen_id_to_remove}.")

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
    if not confirm_action("Are you sure you want to uninstall Serein? This will remove all configurations and the serein command."):
        info("Uninstallation cancelled.")
        return

    if is_persistent_install():
        persistent_uninstall()
    else:
        one_time_uninstall()

def persistent_uninstall():
    persistent_dir = get_persistent_dir()
    remove_packages = confirm_action("Do you want to remove all installed packages as well?")

    info("Uninstalling Serein (Persistent Mode)...")

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
            packages_to_remove = [pkg for pkg in packages_to_remove if pkg.strip()]
            if packages_to_remove:
                _, _, _ = run_command(f"paru -Rns --noconfirm {' '.join(packages_to_remove)}", error_message="Failed to remove packages")
            else:
                info("No packages to remove.")
        else:
            info("No package lists found to remove.")

    info("Unsymlinking configurations...")
    resymlink.unsymlink_configs(persistent_dir)

    # Remove serein executable
    serein_bin_path = "/usr/local/bin/serein"
    if os.path.exists(serein_bin_path):
        info(f"Removing {serein_bin_path}. This may require sudo privileges.")
        _, _, _ = run_command(f"sudo rm {serein_bin_path}", error_message=f"Failed to remove {serein_bin_path}. Please remove it manually if necessary.")

    # Remove persistent directory
    info(f"Removing Serein persistent directory: {persistent_dir}")
    shutil.rmtree(persistent_dir)

    cleanup_cache()
    info("Serein has been uninstalled.")

def one_time_uninstall():
    info("Uninstalling Serein (One-Time Mode)...")

    # For one-time install, we assume the user might want to remove the copied configs
    # We need a way to know which configs were copied. We'll assume minimal for now.
    # A better approach would be a marker file created during installation.
    
    info("Removing configuration directories...")
    # This is a destructive action, so we should be careful and ask the user.
    configs_to_remove = resymlink.CONFIGS_MINIMAL # Assume minimal
    # In the future, we can check for a marker file to see if it was a full install.
    
    for cfg in configs_to_remove:
        target_path = os.path.join(resymlink.CONFIG_DIR, cfg)
        if os.path.isdir(target_path) and not os.path.islink(target_path):
            if confirm_action(f"Found config directory '{cfg}'. Do you want to remove it?"):
                try:
                    shutil.rmtree(target_path)
                    info(f"Removed directory: {target_path}")
                except OSError as e:
                    error(f"Failed to remove {target_path}: {e}")
    
    # Remove serein executable
    serein_bin_path = "/usr/local/bin/serein"
    if os.path.exists(serein_bin_path):
        info(f"Removing {serein_bin_path}. This may require sudo privileges.")
        _, _, _ = run_command(f"sudo rm {serein_bin_path}", error_message=f"Failed to remove {serein_bin_path}. Please remove it manually if necessary.")

    cleanup_cache()
    info("Serein has been uninstalled.")

def cleanup_cache():
    """Removes common cache directories."""
    info("Cleaning up cache directories...")
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


if __name__ == "__main__":
    # Always add commands that work for both installation types
    app.command(name="uninstall")(uninstall_command)
    app.command(name="disable")(disable_command)
    # The enable command needs to be registered in a way that Typer can handle it.
    # A simple way is to create a small wrapper or directly register it if it follows the Typer model.
    # For now, let's assume we need to wrap it or adjust its definition.
    # A simplified approach:
    @app.command(name="enable", help="Enable a Serein feature")
    def enable_command_wrapper(plugin: Annotated[str, typer.Argument(help="Feature to enable (e.g., 'overview' for Hyprland overview plugin)")]):
        class Args:
            def __init__(self, plugin):
                self.plugin = plugin
        enable_command(Args(plugin))

    # Conditionally add commands that only work for persistent installations
    if is_persistent_install():
        app.command(name="update")(update_command)
        app.command(name="rollback")(rollback_command)

    app(prog_name="serein")
