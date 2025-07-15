import typer
from typing_extensions import Annotated
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from .utils import paru_update, paru_install, paru_remove, info

pkg_app = typer.Typer(help="Manage system packages using paru.")

@pkg_app.callback(invoke_without_command=True)
def pkg_main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        interactive_mode()

@pkg_app.command("update", help="Update system packages using paru.")
def pkg_update(
    force: Annotated[bool, typer.Option("--force", "-f", help="Force update.")] = False
):
    info("Updating system packages...")
    paru_update()

@pkg_app.command("install", help="Install packages using paru.")
def pkg_install(
    packages: list[str] = typer.Argument(None, help="Packages to install.")
):
    if not packages:
        packages = inquirer.text(message="Enter packages to install:").execute().split()
    info(f"Installing packages: {', '.join(packages)}")
    paru_install(packages)

@pkg_app.command("remove", help="Remove packages using paru.")
def pkg_remove(
    packages: list[str] = typer.Argument(None, help="Packages to remove.")
):
    if not packages:
        packages = inquirer.text(message="Enter packages to remove:").execute().split()
    info(f"Removing packages: {', '.join(packages)}")
    paru_remove(packages)

from InquirerPy.utils import get_style

custom_style = get_style({
    "questionmark": "#86afef",
    "question": "",
    "input": "#86afef",
    "answer": "#86afef",
    "pointer": "#86afef",
    "selection": "#86afef",
}, style_override=False)

def interactive_mode():
    action = inquirer.select(
        message="What would you like to do?",
        style=custom_style,
        choices=[
            Choice("update", name="Update system packages"),
            Choice("install", name="Install packages"),
            Choice("remove", name="Remove packages"),
            Choice(value=None, name="Exit"),
        ],
        default=None,
    ).execute()

    if action == "update":
        info("Updating system packages...")
        paru_update()
    elif action == "install":
        packages = inquirer.text(message="Enter packages to install:", style=custom_style).execute()
        if packages:
            info(f"Installing packages: {', '.join(packages.split())}")
            paru_install(packages.split())
    elif action == "remove":
        packages = inquirer.text(message="Enter packages to remove:", style=custom_style).execute()
        if packages:
            info(f"Removing packages: {', '.join(packages.split())}")
            paru_remove(packages.split())
