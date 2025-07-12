
import os
import shutil
import typer

import resymlink
from . import utils


def uninstall_command():
    if not utils.confirm_action("Are you sure you want to uninstall Serein? This will remove all configurations and the serein command."):
        utils.info("Uninstallation cancelled.")
        return

    if utils.is_persistent_install():
        persistent_uninstall()
    else:
        one_time_uninstall()

def persistent_uninstall():
    persistent_dir = utils.get_persistent_dir()
    remove_packages = utils.confirm_action("Do you want to remove all installed packages as well?")

    utils.info("Uninstalling Serein (Persistent Mode)...")

    if remove_packages:
        utils.info("Removing installed packages...")
        minimal_packages_path = os.path.join(persistent_dir, "assets", "packages.minimal")
        full_packages_path = os.path.join(persistent_dir, "assets", "packages.full")
        
        packages_to_remove = []
        if os.path.isfile(minimal_packages_path):
            with open(minimal_packages_path, "r") as f:
                packages_to_remove.extend(f.read().splitlines())
        
        if os.path.isfile(os.path.join(persistent_dir, ".full_install")):
            utils.info("Full installation detected. Removing all packages...")
            if os.path.isfile(full_packages_path):
                with open(full_packages_path, "r") as f:
                    packages_to_remove.extend(f.read().splitlines())
        else:
            utils.info("Minimal installation detected. Removing minimal packages...")
        
        if packages_to_remove:
            packages_to_remove = [pkg for pkg in packages_to_remove if pkg.strip()]
            if packages_to_remove:
                _, _, _ = utils.run_command(f"paru -Rns --noconfirm {' '.join(packages_to_remove)}", error_message="Failed to remove packages")
            else:
                utils.info("No packages to remove.")
        else:
            utils.info("No package lists found to remove.")

    utils.info("Unsymlinking configurations...")
    resymlink.unsymlink_configs(persistent_dir)

    # Remove serein executable
    serein_bin_path = "/usr/local/bin/serein"
    if os.path.exists(serein_bin_path):
        utils.info(f"Removing {serein_bin_path}. This may require sudo privileges.")
        _, _, _ = utils.run_command(f"sudo rm {serein_bin_path}", error_message=f"Failed to remove {serein_bin_path}. Please remove it manually if necessary.")

    # Remove persistent directory
    utils.info(f"Removing Serein persistent directory: {persistent_dir}")
    shutil.rmtree(persistent_dir)

    cleanup_cache()
    utils.info("Serein has been uninstalled.")

def one_time_uninstall():
    utils.info("Uninstalling Serein (One-Time Mode)...")

    # For one-time install, we assume the user might want to remove the copied configs
    # We need a way to know which configs were copied. We'll assume minimal for now.
    # A better approach would be a marker file created during installation.
    
    utils.info("Removing configuration directories...")
    # This is a destructive action, so we should be careful and ask the user.
    configs_to_remove = resymlink.CONFIGS_MINIMAL # Assume minimal
    # In the future, we can check for a marker file to see if it was a full install.
    
    for cfg in configs_to_remove:
        target_path = os.path.join(resymlink.CONFIG_DIR, cfg)
        if os.path.isdir(target_path) and not os.path.islink(target_path):
            if utils.confirm_action(f"Found config directory '{cfg}'. Do you want to remove it?"):
                try:
                    shutil.rmtree(target_path)
                    utils.info(f"Removed directory: {target_path}")
                except OSError as e:
                    utils.error(f"Failed to remove {target_path}: {e}")
    
    # Remove serein executable
    serein_bin_path = "/usr/local/bin/serein"
    if os.path.exists(serein_bin_path):
        utils.info(f"Removing {serein_bin_path}. This may require sudo privileges.")
        _, _, _ = utils.run_command(f"sudo rm {serein_bin_path}", error_message=f"Failed to remove {serein_bin_path}. Please remove it manually if necessary.")

    cleanup_cache()
    utils.info("Serein has been uninstalled.")

def cleanup_cache():
    """Removes common cache directories."""
    utils.info("Cleaning up cache directories...")
    rofi_cache = os.path.join(os.path.expanduser("~"), ".cache", "rofi")
    rofi_icon_cache = os.path.join(os.path.expanduser("~"), ".cache", "rofi_icon")
    user_conf = os.path.join(os.path.expanduser("~"), "user.conf")

    if os.path.isdir(rofi_cache):
        utils.info(f"Removing Rofi cache: {rofi_cache}")
        shutil.rmtree(rofi_cache)
    if os.path.isdir(rofi_icon_cache):
        utils.info(f"Removing Rofi icon cache: {rofi_icon_cache}")
        shutil.rmtree(rofi_icon_cache)
    if os.path.isfile(user_conf):
        utils.info(f"Removing user.conf: {user_conf}")
        os.remove(user_conf)
