import click
from rich.console import Console
from pathlib import Path
import shutil
import tomlkit

console = Console()

@click.group()
def maintenance():
    """Repository maintenance utilities"""
    pass

@maintenance.command("check")
def check_repo():
    """Check repository health and consistency"""
    console.print("[green]Checking repository health...[/green]")

    if not Path(".git").exists():
        console.print("[red]Error: Not in a git repository[/red]")
        return

    required_dirs = ["content", "templates", "static"]
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            console.print(f"✓ {dir_name}/ directory exists")
        else:
            console.print(f"[yellow]⚠ {dir_name}/ directory missing[/yellow]")

    events_file = Path("content/data/events.toml")
    if events_file.exists():
        console.print("✓ events.toml exists")
        try:
            with open(events_file, 'r', encoding='utf-8') as f:
                data = tomlkit.parse(f.read())
                event_count = len(data.get('events', []))
                console.print(f"✓ Found {event_count} events")
        except Exception as e:
            console.print(f"[red]✗ Error parsing events.toml: {e}[/red]")
    else:
        console.print("[yellow]⚠ events.toml not found[/yellow]")

    console.print("[green]Repository check complete![/green]")

@maintenance.command("clean")
@click.option("--dry-run", is_flag=True, help="Preview what would be cleaned")
def clean_repo(dry_run):
    """Clean up temporary files and caches"""
    console.print("[blue]Cleaning repository...[/blue]")

    patterns_to_clean = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/.DS_Store",
        "**/Thumbs.db",
    ]

    for pattern in patterns_to_clean:
        for path in Path(".").glob(pattern):
            if dry_run:
                console.print(f"Would remove: {path}")
            else:
                if path.is_dir():
                    shutil.rmtree(path)
                    console.print(f"Removed directory: {path}")
                else:
                    path.unlink()
                    console.print(f"Removed file: {path}")

    if dry_run:
        console.print("[yellow]Dry run complete - no files were actually removed[/yellow]")
    else:
        console.print("[green]Cleanup complete![/green]")