import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from typing import Optional
from typing_extensions import Annotated

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
import typer
from rich.console import Console
from rich.style import Style

console = Console()


def info(message):
    """Displays an informational message."""
    style = Style(color="#86afef", bold=True)
    console.print(f"[INFO] {message}", style=style)


def error(message):
    """Displays an error message and exits the script."""
    style = Style(color="red", bold=True)
    console.print(f"[ERROR] {message}", style=style, stderr=True)
    sys.exit(1)

def run_command(command, cwd=None, check_error=True, error_message="Command failed", capture_output=True):
    """Runs a shell command and handles errors. Returns stdout, stderr, and exit_code."""
    try:
        # If we don't capture output, it will be streamed to the terminal directly.
        # In that case, result.stdout and result.stderr will be None.
        result = subprocess.run(command, cwd=cwd, check=False, shell=True, capture_output=capture_output, text=True)
        
        stdout_val = result.stdout.strip() if result.stdout else ""
        stderr_val = result.stderr.strip() if result.stderr else ""

        if check_error and result.returncode != 0:
            # Don't print stdout/stderr if it was already streamed live
            if capture_output:
                error(f"{error_message} (Exit Code: {result.returncode}):\nStdout: {stdout_val}\nStderr: {stderr_val}")
            else:
                error(f"{error_message} (Exit Code: {result.returncode})")

        return stdout_val, stderr_val, result.returncode
    except FileNotFoundError:
        error(f"Command not found: {command.split()[0]}")
    except Exception as e:
        error(f"An unexpected error occurred while running command: {command}\nError: {e}")

def confirm_action(prompt):
    """Prompts the user for confirmation."""
    return typer.confirm(prompt)

def is_persistent_install():
    """Checks if Serein is installed persistently."""
    return os.path.isdir(os.path.join(os.path.expanduser("~"), ".cache", "serein", ".git"))

def get_persistent_dir():
    """Returns the persistent directory path."""
    return os.path.join(os.path.expanduser("~"), ".cache", "serein")

def clear_pycache():
    """Removes all __pycache__ directories within the functions directory."""
    functions_dir = os.path.dirname(os.path.abspath(__file__))
    for root, dirs, files in os.walk(functions_dir):
        if "__pycache__" in dirs:
            pycache_dir = os.path.join(root, "__pycache__")
            shutil.rmtree(pycache_dir)

def is_overview_enabled():
    """Checks if the hyprtasking plugin for overview is enabled via hyprpm."""
    stdout, _, returncode = run_command("hyprpm list", check_error=False)
    if returncode != 0:
        return False

    lines = stdout.lower().splitlines()
    in_hyprtasking_section = False
    for line in lines:
        # A new repository section resets the check
        if 'repository ' in line:
            if 'hyprtasking' in line:
                in_hyprtasking_section = True
            else:
                in_hyprtasking_section = False
        
        if in_hyprtasking_section:
            if 'enabled:' in line and 'true' in line:
                return True
                
    return False

def paru_install(packages):
    command = f"paru -S --noconfirm {' '.join(packages)}"
    run_command(command, capture_output=False)

def paru_remove(packages):
    command = f"paru -Rns --noconfirm {' '.join(packages)}"
    run_command(command, capture_output=False)

def paru_update():
    run_command("paru -Syu --noconfirm", capture_output=False)

