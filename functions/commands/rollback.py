
import os
import shutil
import sys
from typing import Annotated

import typer
from InquirerPy import inquirer
from InquirerPy.utils import get_style

import resymlink
from . import utils


def rollback_command(
    no_confirm: Annotated[bool, typer.Option("--no-confirm", "-y", help="Skip confirmation prompts.")] = False,
    keep_backup: Annotated[bool, typer.Option("--keep-backup", "-k", help="Keep backup files when deleting a generation.")] = False
):
    if not utils.is_persistent_install():
        utils.error("Serein is not installed persistently. Cannot rollback.")
        
    persistent_dir = utils.get_persistent_dir()
    generations = utils.read_generations()
    
    # Filter out archived generations for the user to choose from
    available_generations = [gen for gen in generations if not gen.get("archived", False)]

    if not available_generations:
        utils.info("No generations found to rollback or remove.")
        return

    try:
        action = inquirer.select(
            message="Choose an action:",
            choices=[
                {"name": "Rollback to a generation", "value": "rollback"},
                {"name": "Delete a generation", "value": "delete"},
            ],
            default="rollback",
            style=get_style({"pointer": "#86afef bold", "question": "#86afef bold"}),
        ).execute()

        if action == "rollback":
            choice_to_generation = { 
                f'{gen["id"]}: {gen["date"]} - {gen["description"]}': gen 
                for gen in reversed(available_generations) 
            }

            selected_choice = inquirer.select(
                message="Select a generation to rollback to:",
                choices=list(choice_to_generation.keys()),
                style=get_style({"pointer": "#86afef bold", "question": "#86afef bold"}),
            ).execute()
            
            if selected_choice is None: # User escaped
                utils.info("Rollback cancelled.")
                return

            selected_generation = choice_to_generation[selected_choice]
            commit_hash = selected_generation["commit_hash"]

            if not no_confirm and not utils.confirm_action(f'Are you sure you want to roll back to generation {selected_generation["id"]}'):
                utils.info("Rollback cancelled.")
                return

            utils.info(f'Rolling back to generation {selected_generation["id"]} (commit {commit_hash})...')

            # Unsymlink configs
            utils.info("Unsymlinking existing configurations...")
            resymlink.unsymlink_configs(persistent_dir)

            # Restore git state by resetting the branch to the specific commit
            utils.info(f"Resetting Serein to commit {commit_hash}...")
            original_cwd = os.getcwd()
            os.chdir(persistent_dir)

            _, _, _ = utils.run_command(f"git reset --hard {commit_hash}", error_message="git reset failed.")
            _, _, _ = utils.run_command("git clean -fd", error_message="git clean failed.")

            os.chdir(original_cwd)

            # Resymlink configs
            utils.info("Symlinking new configurations...")
            resymlink.symlink_configs(persistent_dir)

            utils.info("Rollback complete.")

        elif action == "delete":
            choice_to_generation = { 
                f'{gen["id"]}: {gen["date"]} - {gen["description"]}': gen 
                for gen in reversed(available_generations) 
            }

            selected_choice = inquirer.select(
                message="Select a generation to remove:",
                choices=list(choice_to_generation.keys()),
                style=get_style({"pointer": "#86afef bold", "question": "#86afef bold"}),
            ).execute()

            if selected_choice is None: # User escaped
                utils.info("Removal cancelled.")
                return

            selected_generation = choice_to_generation[selected_choice]
            gen_id_to_remove = selected_generation["id"]

            if not no_confirm and not utils.confirm_action(f"Are you sure you want to remove generation {gen_id_to_remove}?"):
                utils.info("Removal cancelled.")
                return

            # Find the generation in the original list and mark it as archived
            for gen in generations:
                if gen["id"] == gen_id_to_remove:
                    gen["archived"] = True
                    break
            
            utils.write_generations(generations)
            utils.info(f"Generation {gen_id_to_remove} has been archived and will no longer appear in the list.")

            if not keep_backup:
                backup_dir_to_remove = os.path.join(utils.get_persistent_dir(), "generations", str(gen_id_to_remove))
                if os.path.isdir(backup_dir_to_remove):
                    shutil.rmtree(backup_dir_to_remove)
                    utils.info(f"Removed backup directory for generation {gen_id_to_remove}.")

    except KeyboardInterrupt:
        utils.info("Operation cancelled by user.")
        sys.exit(0)
