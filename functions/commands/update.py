import os
import shutil
import sys
from datetime import datetime
from typing import Optional
from typing_extensions import Annotated

import typer

import resymlink
from . import utils


def update_command(
    update_type: Annotated[Optional[str], typer.Argument(help="Update type: 'stable' for latest tag, 'edge' for git pull (default)")] = "edge",
    force: Annotated[bool, typer.Option("--force", "-f", help="Force update even if on the latest version.")] = False
):
    if not utils.is_persistent_install():
        utils.error("Serein is not installed persistently. Cannot update.")
    
    persistent_dir = utils.get_persistent_dir()

    utils.info("Checking for rsync...")
    if not shutil.which("rsync"):
        utils.error("rsync is not installed. Please install it to continue.")

    original_cwd = os.getcwd()

    # Create a temporary backup of the current persistent_dir (pre-update state)
    temp_backup_dir = os.path.join(os.path.expanduser("~"), ".cache", "serein_temp_backup")
    shutil.rmtree(temp_backup_dir, ignore_errors=True) # Clean up any previous temp
    os.makedirs(temp_backup_dir, exist_ok=True)

    utils.info(f"Creating temporary backup of current state at {temp_backup_dir}...")
    rsync_temp_command = [
        "rsync", "-a",
        "--exclude=.git",
        "--exclude=.gitignore",
        "--exclude=generations",
        f"{persistent_dir}/", # Source directory (current state)
        f"{temp_backup_dir}/" # Destination directory
    ]
    _, _, _ = utils.run_command(" ".join(rsync_temp_command), error_message="Failed to create temporary backup")

    # Change to persistent_dir for git operations
    os.chdir(persistent_dir)

    before_hash, _, _ = utils.run_command("git rev-parse HEAD", error_message="Failed to get current git hash")

    # Perform the git update
    if update_type == "stable":
        utils.info("Checking for stable updates...")
        _, _, _ = utils.run_command("git fetch --tags", error_message="git fetch failed")
        latest_tag, _, _ = utils.run_command("git describe --tags $(git rev-list --tags --max-count=1)", error_message="Failed to get latest tag")
        current_tag, _, _ = utils.run_command("git describe --tags", error_message="Failed to get current tag")

        if current_tag == latest_tag and not force:
            utils.info("You are already on the latest stable release.")
            os.chdir(original_cwd) # Change back before exiting
            shutil.rmtree(temp_backup_dir) # Clean up temp
            sys.exit(0)

        utils.info(f"Updating to the latest stable release ({latest_tag})...")
        _, _, _ = utils.run_command(f"git checkout {latest_tag}", error_message="git checkout failed. You may have local changes. Please stash or commit them first.")
    else:
        utils.info("Updating to the bleeding edge (git pull)...")
        _, _, _ = utils.run_command("git pull", error_message="git pull failed. You may have local changes. Please stash or commit them first.")

    after_hash, _, _ = utils.run_command("git rev-parse HEAD", error_message="Failed to get new git hash")

    # If no changes, no new generation needed
    if before_hash == after_hash and not force:
        utils.info("Already up to date. No new generation created.")
        os.chdir(original_cwd) # Change back before exiting
        shutil.rmtree(temp_backup_dir) # Clean up temp
        sys.exit(0)

    # Change back to original CWD before creating backup
    os.chdir(original_cwd)

    # Create generation backup from the *temporary backup* (pre-update state)
    generations = utils.read_generations()
    last_gen_id = generations[-1]["id"] if generations else 0
    new_gen_id = last_gen_id + 1

    backup_dir = os.path.join(utils.get_persistent_dir(), "generations", str(new_gen_id))
    os.makedirs(backup_dir, exist_ok=True)

    utils.info(f"Creating generation backup {new_gen_id} of previous state at {backup_dir}...")

    # Use rsync to copy files from the *temporary backup* (pre-update state)
    rsync_command = [
        "rsync", "-a",
        "--exclude=.git",
        "--exclude=.gitignore",
        "--exclude=generations",
        f"{temp_backup_dir}/", # Source directory (pre-update state from temp)
        f"{backup_dir}/"      # Destination directory
    ]
    _, _, _ = utils.run_command(" ".join(rsync_command), error_message="Failed to create generation backup")

    # Add new generation to the JSON file
    new_generation = {
        "id": new_gen_id,
        "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "commit_hash": before_hash,
        "description": f"Update to {after_hash[:7]}",
        "archived": False
    }
    generations.append(new_generation)
    utils.write_generations(generations)
    
    shutil.rmtree(temp_backup_dir) # Clean up the temporary backup directory

    # Unsymlink configs
    utils.info("Unsymlinking existing configurations...")
    resymlink.unsymlink_configs(persistent_dir)

    # Resymlink configs
    utils.info("Symlinking new configurations...")
    resymlink.symlink_configs(persistent_dir)

    utils.info("Update complete. A new generation has been created.")
    utils.clear_pycache()
