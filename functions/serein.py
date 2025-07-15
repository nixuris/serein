#!/usr/bin/env python3

import os
import sys
import typer

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

from commands import utils, config, update, rollback, uninstall, pkg

app = typer.Typer(
    name="serein",
    help="Serein Command-Line Tool",
    add_completion=False,
    rich_help_panel="Custom Commands"
)

# Add the config command group
app.add_typer(config.config_app, name="config")
app.add_typer(pkg.pkg_app, name="pkg")

# Add other commands
app.command(name="uninstall", help="Uninstalls Serein, removing configurations and the command.")(uninstall.uninstall_command)

# Conditionally add commands that only work for persistent installations
if utils.is_persistent_install():
    app.command(name="update", help="Updates Serein to the latest version.")(update.update_command)
    app.command(name="rollback", help="Rolls back Serein to a previous generation or manages generations.")(rollback.rollback_command)

if __name__ == "__main__":
    try:
        app(prog_name="serein")
    except KeyboardInterrupt:
        utils.info("Operation cancelled by user.")
        sys.exit(0)
