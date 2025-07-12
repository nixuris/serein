
import os
import shutil
import typer
from InquirerPy import inquirer
from InquirerPy.utils import get_style

import resymlink
from . import utils

config_app = typer.Typer(name="config", help="Manage Serein configurations.")

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

@config_app.command(name="enable", help="Enable a specific configuration by creating a symlink.")
def config_enable(config_name: str):
    """Enables a specific configuration by creating a symlink."""
    if not utils.is_persistent_install():
        utils.error("Configuration management is only available for persistent installations.")
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

@config_app.command(name="disable", help="Disable a specific configuration by removing its symlink.")
def config_disable(config_name: str):
    """Disables a specific configuration by removing its symlink."""
    if not utils.is_persistent_install():
        utils.error("Configuration management is only available for persistent installations.")
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

    all_configs = resymlink.CONFIGS_MINIMAL + resymlink.CONFIGS_EXTRA
    repo_config_dir = os.path.join(utils.get_persistent_dir(), "config")

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
            utils.info("Configuration change cancelled.")
            return

        # Determine which configs to enable and disable
        for cfg in all_configs:
            should_be_enabled = cfg in selected_configs
            is_currently_enabled = current_states[cfg]

            if should_be_enabled and not is_currently_enabled:
                config_enable(cfg)
            elif not should_be_enabled and is_currently_enabled:
                config_disable(cfg)

        utils.info("Configuration changes applied successfully.")

    except KeyboardInterrupt:
        utils.info("Operation cancelled by user.")
        sys.exit(0)
