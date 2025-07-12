
from typing import Annotated
import typer
from . import utils


def enable_command(plugin: Annotated[str, typer.Argument(help="Feature to enable (e.g., 'overview' for Hyprland overview plugin)")]):
    if plugin == "overview":
        utils.info("Enabling hyprtasking (required for overview)...")
        _, _, _ = utils.run_command("hyprpm update", error_message="hyprpm update failed")
        _, _, _ = utils.run_command("hyprpm add https://github.com/raybbian/hyprtasking", error_message="hyprpm add failed")
        _, _, _ = utils.run_command("hyprpm enable hyprtasking", error_message="hyprpm enable failed")
        _, _, _ = utils.run_command("hyprpm reload -nn", error_message="hyprpm reload failed")
        _, _, _ = utils.run_command("hyprctl reload", error_message="hyprctl reload failed")
        utils.info("Hyprtasking enabled.")
    else:
        utils.error("Invalid plugin specified.")


def disable_command(
    plugin: Annotated[str, typer.Argument(help="Feature to disable (e.g., 'overview' for Hyprland overview plugin)")]
):
    if plugin == "overview":
        utils.info("Disabling hyprtasking...")
        _, _, _ = utils.run_command("hyprpm remove https://github.com/raybbian/hyprtasking", error_message="hyprpm remove failed")
        _, _, _ = utils.run_command("hyprpm reload -nn", error_message="hyprpm reload failed")
        _, _, _ = utils.run_command("hyprctl reload", error_message="hyprctl reload failed")
        utils.info("Hyprtasking disabled.")
    else:
        utils.error("Invalid plugin specified.")
