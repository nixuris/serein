import click
import subprocess
from pathlib import Path

# Import our new generation manager
from .generations import gen_manager


@click.group()
def cli():
    """Serein Command-Line Tool (Python Version)"""
    pass


@cli.command()
def update():
    """Update system and Serein configs"""
    click.echo("Updating...")


@cli.group()
def rollback():
    """Rollback to a previous generation"""
    pass


@rollback.command(name="list")
def list_generations():
    """List available generations"""
    generations = gen_manager.get_all()
    if not generations:
        click.echo("No generations found.")
        return

    # Use click's styling for better UX
    click.secho("Available generations:", fg="cyan")
    for gen in generations:
        click.echo(
            f"  [{click.style(str(gen['id']), fg='yellow')}] "
            f"{gen['date']} - {gen['description']} "
            f"({click.style(gen['commit_hash'][:7], fg='green')})"
        )


@rollback.command(name="to")
@click.argument("generation_id", type=int)
def rollback_to(generation_id: int):
    """Rolls back to a specific generation ID."""
    target_generation = gen_manager.find_by_id(generation_id)

    if not target_generation:
        click.secho(f"Error: Generation with ID '{generation_id}' not found.", fg="red")
        return

    commit_hash = target_generation["commit_hash"]
    description = target_generation["description"]

    click.secho(f"You are about to roll back to generation {generation_id}:", fg="yellow")
    click.echo(f"  Commit: {commit_hash}")
    click.echo(f"  Description: {description}")

    # --- Pre-flight Check (Context-Aware Operation) ---
    try:
        # The root of the git repo is two levels up from the `serein` module directory
        git_repo_path = Path(__file__).parent.parent.parent
        subprocess.run(
            ["git", "diff-index", "--quiet", "HEAD", "--"],
            check=True,
            cwd=git_repo_path,
            capture_output=True,  # Hide stdout/stderr unless there's an error
        )
    except subprocess.CalledProcessError:
        click.secho(
            "Error: You have uncommitted changes in your Serein directory.", fg="red"
        )
        click.echo("Please commit or stash them before rolling back.")
        return
    except FileNotFoundError:
        click.secho("Error: `git` command not found. Is Git installed?", fg="red")
        return

    # --- Confirmation (Better UX) ---
    if not click.confirm("\nAre you sure you want to proceed?"):
        click.echo("Rollback cancelled.")
        return

    # --- Execution ---
    try:
        serein_root = Path(__file__).parent.parent.parent
        resymlink_script = serein_root / "functions" / "resymlink.sh"

        if not resymlink_script.exists():
            click.secho("Error: resymlink.sh script not found!", fg="red")
            return

        click.echo("Unsymlinking current configuration...")
        subprocess.run(
            [resymlink_script, "--unsymlink"], check=True, capture_output=True
        )

        click.echo(f"Checking out commit {commit_hash[:7]}...")
        subprocess.run(
            ["git", "checkout", commit_hash], check=True, cwd=serein_root, capture_output=True
        )

        click.echo("Resymlinking new configuration...")
        subprocess.run([resymlink_script, "--symlink"], check=True, capture_output=True)

        click.secho("\nRollback complete.", fg="green")

    except subprocess.CalledProcessError as e:
        click.secho("\nAn error occurred during rollback:", fg="red")
        # Decode stderr for a user-friendly error message
        click.secho(e.stderr.decode().strip(), fg="red")


if __name__ == "__main__":
    cli()
