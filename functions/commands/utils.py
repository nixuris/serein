import os
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

