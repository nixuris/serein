import os
import shutil
import sys
import typer
from InquirerPy import inquirer
from InquirerPy.utils import get_style

import resymlink
from . import utils

config_app = typer.Typer(name="config", help="Manage Serein configurations and features.")

import os
import shutil
import sys
import typer
from InquirerPy import inquirer
from InquirerPy.utils import get_style

import resymlink
from . import utils

config_app = typer.Typer(name="config", help="Manage Serein configurations and features.")

def enable_overview():
    """Enables the Hyprland overview feature (hyprtasking)."""
    if utils.is_overview_enabled():
        utils.info("Overview feature is already enabled.")
        return

    utils.info("Enabling hyprtasking (required for overview)...")
    
    # Check if the repository is added, if not, add it.
    stdout, _, _ = utils.run_command("hyprpm list", check_error=False)
    if "Hyprtasking" not in stdout:
        utils.info("Hyprtasking plugin repository not found, adding it...")
        utils.run_command("hyprpm add https://github.com/raybbian/hyprtasking", error_message="hyprpm add failed")
    
    utils.run_command("hyprpm update", error_message="hyprpm update failed")
    utils.run_command("hyprpm enable hyprtasking", error_message="hyprpm enable failed")
    utils.run_command("hyprpm reload -nn", error_message="hyprpm reload failed")
    utils.run_command("hyprctl reload", error_message="hyprctl reload failed")
    utils.info("Hyprtasking enabled successfully.")

def disable_overview():
    """Disables the Hyprland overview feature (hyprtasking)."""
    if not utils.is_overview_enabled():
        utils.info("Overview feature is already disabled.")
        return

    utils.info("Disabling hyprtasking...")
    utils.run_command("hyprpm disable hyprtasking", error_message="hyprpm disable failed")
    utils.run_command("hyprpm reload -nn", error_message="hyprpm reload failed")
    utils.run_command("hyprctl reload", error_message="hyprctl reload failed")
    utils.info("Hyprtasking disabled successfully.")

@config_app.command(name="list", help="List all available configurations and their status.")
def config_list():
    """Lists all available configurations and their status."""
    if not utils.is_persistent_install():
        utils.error("Configuration management is only available for persistent installations.")
        return

    utils.info("Available Serein Configurations:")
    all_configs = resymlink.CONFIGS_MINIMAL + resymlink.CONFIGS_EXTRA
    repo_config_dir = os.path.join(utils.get_persistent_dir(), "config")

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
    
    # Add overview status
    overview_status = typer.style("enabled", fg=typer.colors.GREEN) if utils.is_overview_enabled() else typer.style("disabled", fg=typer.colors.WHITE)
    typer.echo(f"- overview: {overview_status}")


@config_app.command(name="enable", help="Enable a specific configuration or feature.")
def config_enable(config_name: str):
    """Enables a specific configuration or feature."""
    if not utils.is_persistent_install():
        utils.error("Configuration management is only available for persistent installations.")
        return

    if config_name == "overview":
        enable_overview()
        return

    all_configs = resymlink.CONFIGS_MINIMAL + resymlink.CONFIGS_EXTRA
    if config_name not in all_configs:
        utils.error(f"Unknown configuration: {config_name}")
        return

    repo_config_dir = os.path.join(utils.get_persistent_dir(), "config")
    source_path = os.path.join(repo_config_dir, config_name)
    target_path = os.path.join(resymlink.CONFIG_DIR, config_name)

    if not os.path.exists(source_path):
        utils.error(f"Source directory not found for {config_name} in the Serein repository.")
        return

    if os.path.islink(target_path) and os.readlink(target_path) == source_path:
        utils.info(f"Configuration '{config_name}' is already enabled.")
        return

    if os.path.exists(target_path):
        if not utils.confirm_action(f"Warning: '{target_path}' already exists and is not a Serein symlink. Overwrite it?"):
            utils.info("Enable operation cancelled.")
            return
        if os.path.islink(target_path):
            os.remove(target_path)
        else:
            shutil.rmtree(target_path)

    try:
        os.symlink(source_path, target_path)
        utils.info(f"Successfully enabled configuration: {config_name}")
    except OSError as e:
        utils.error(f"Failed to enable configuration {config_name}: {e}")

@config_app.command(name="disable", help="Disable a specific configuration or feature.")
def config_disable(config_name: str):
    """Disables a specific configuration or feature."""
    if not utils.is_persistent_install():
        utils.error("Configuration management is only available for persistent installations.")
        return

    if config_name == "overview":
        disable_overview()
        return

    repo_config_dir = os.path.join(utils.get_persistent_dir(), "config")
    source_path = os.path.join(repo_config_dir, config_name)
    target_path = os.path.join(resymlink.CONFIG_DIR, config_name)

    if not os.path.islink(target_path):
        utils.info(f"Configuration '{config_name}' is not an enabled Serein symlink. Nothing to do.")
        return

    if os.readlink(target_path) != source_path:
        utils.info(f"Configuration '{config_name}' is a symlink, but it does not point to the Serein repository. It will not be removed.")
        return

    try:
        os.remove(target_path)
        utils.info(f"Successfully disabled configuration: {config_name}")
    except OSError as e:
        utils.error(f"Failed to disable configuration {config_name}: {e}")

@config_app.callback(invoke_without_command=True)
def config_main(ctx: typer.Context):
    """Manage Serein configurations interactively."""
    if ctx.invoked_subcommand is not None:
        return

    if not utils.is_persistent_install():
        utils.error("Configuration management is only available for persistent installations.")
        return

    all_items = resymlink.CONFIGS_MINIMAL + resymlink.CONFIGS_EXTRA + ["overview"]
    repo_config_dir = os.path.join(utils.get_persistent_dir(), "config")

    # Get the current state of all items
    current_states = {}
    for item in all_items:
        if item == "overview":
            current_states[item] = utils.is_overview_enabled()
        else:
            target_path = os.path.join(resymlink.CONFIG_DIR, item)
            source_path = os.path.join(repo_config_dir, item)
            current_states[item] = os.path.islink(target_path) and os.readlink(target_path) == source_path

    # Create choices for the interactive prompt
    choices = [
        {"name": item, "value": item, "enabled": current_states[item]} for item in sorted(all_items)
    ]

    try:
        selected_items = inquirer.checkbox(
            message="Select configurations to enable/disable (Space to toggle, Enter to confirm):",
            choices=choices,
            cycle=False,
            style=get_style({"pointer": "#86afef bold", "question": "#86afef bold"}),
        ).execute()

        if selected_items is None: # User escaped
            utils.info("Configuration change cancelled.")
            return

        # Determine which items to enable and disable
        for item in all_items:
            should_be_enabled = item in selected_items
            is_currently_enabled = current_states[item]

            if should_be_enabled and not is_currently_enabled:
                config_enable(item)
            elif not should_be_enabled and is_currently_enabled:
                config_disable(item)

        utils.info("Configuration changes applied successfully.")

    except KeyboardInterrupt:
        utils.info("Operation cancelled by user.")
        sys.exit(0)
