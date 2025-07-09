# Serein CLI Tool

The `serein` command-line tool is the central hub for managing your Serein environment. It provides a set of commands to handle updates, rollbacks, and other aspects of your configuration. This document explains how each command works under the hood.

## Commands

### `update [stable|edge]`

This command updates your Serein environment.

*   **`stable`**: Updates to the latest stable release tag. This is the recommended choice for most users.
*   **`edge`**: Performs a shallow clone of the main branch for those who want the latest, cutting-edge features.

**Under the hood:**

1.  The script first checks if Serein is installed persistently (i.e., in `$HOME/.cache/serein`).
2.  It then navigates to the persistent directory and updates the repository using `git pull` for the edge version or `git checkout` with the latest tag for the stable version.
3.  Before updating, it creates a generation backup of your current configuration using `rsync`. This backup is stored in `$HOME/.cache/serein/generations`.
4.  After the update, it re-symlinks the configuration files using the `resymlink.sh` script.

### `rollback <generation>`

This command rolls back your Serein environment to a previous generation.

**Under the hood:**

1.  The script first checks for the specified generation in the `$HOME/.cache/serein/generations` directory.
2.  It then reads the commit hash from the `.commit_hash` file within the generation's directory.
3.  It unsymlinks the current configuration files.
4.  It uses `git checkout` to revert the repository to the specified commit hash.
5.  Finally, it re-symlinks the configuration files.

### `rollback list`

This command lists all the available generations that you can roll back to.

**Under the hood:**

This command simply lists the contents of the `$HOME/.cache/serein/generations` directory.

### `rollback remove <gen>`

This command removes a specific generation.

**Under the hood:**

This command removes the specified generation's directory from `$HOME/.cache/serein/generations`.

### `enable overview`

This command enables the Hyprland overview plugin (hyprtasking).

**Under the hood:**

This command uses `hyprpm` to add, enable, and reload the `hyprtasking` plugin.

### `disable overview`

This command disables the Hyprland overview plugin.

**Under the hood:**

This command uses `hyprpm` to remove and reload the `hyprtasking` plugin.

### `uninstall`

This command removes the Serein environment.

**Under the hood:**

1.  The script first asks for confirmation.
2.  It then gives you the option to remove all the packages that were installed with Serein.
3.  It unsymlinks all the configuration files.
4.  It removes the `serein` command from `/usr/local/bin`.
5.  Finally, it removes the persistent directory (`$HOME/.cache/serein`) and other related files.
