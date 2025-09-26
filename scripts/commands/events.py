"""Event management commands for the Y-CTF CLI"""

import sys
import click
from rich.console import Console
from rich.table import Table
from pathlib import Path
from datetime import datetime
import json
import tomlkit

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from importers.ics import ICSImporter

console = Console()


@click.group()
def events():
    """Event management utilities"""
    pass


@events.command("new")
@click.option("--title", prompt="Event title (English)", help="Event title in English")
@click.option("--title-fr", help="Event title in French (optional)")
@click.option(
    "--description",
    prompt="Event description (English)",
    help="Event description in English",
)
@click.option("--description-fr", help="Event description in French (optional)")
@click.option(
    "--start-date", prompt="Start date (YYYY-MM-DD HH:MM)", help="Start date and time"
)
@click.option("--start-timezone", default="+01:00", help="Start timezone offset")
@click.option("--end-date", help="End date (YYYY-MM-DD HH:MM, optional)")
@click.option("--end-timezone", default="+01:00", help="End timezone offset")
@click.option("--location", prompt="Location", help="Event location")
@click.option(
    "--event-type",
    type=click.Choice(["competition", "meeting", "conference", "training", "workshop"]),
    prompt="Event type",
    help="Type of event",
)
@click.option("--url", help="Optional external URL")
@click.option(
    "--registration-deadline", help="Registration deadline (YYYY-MM-DD HH:MM, optional)"
)
def create_event(
    title,
    title_fr,
    description,
    description_fr,
    start_date,
    start_timezone,
    end_date,
    end_timezone,
    location,
    event_type,
    url,
    registration_deadline,
):
    """Create a new event entry"""
    events_file = Path("content/data/events.toml")

    try:
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
        start_iso = start_datetime.isoformat() + start_timezone

        if end_date:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
            end_iso = end_datetime.isoformat() + end_timezone
        else:
            end_iso = None

        if registration_deadline:
            reg_datetime = datetime.strptime(registration_deadline, "%Y-%m-%d %H:%M")
            reg_iso = reg_datetime.isoformat() + start_timezone
        else:
            reg_iso = None

    except ValueError as e:
        console.print(f"[red]Invalid date format: {e}[/red]")
        console.print("[yellow]Use format: YYYY-MM-DD HH:MM[/yellow]")
        return

    if events_file.exists():
        with open(events_file, "r", encoding="utf-8") as f:
            data = tomlkit.parse(f.read())
    else:
        data = tomlkit.document()
        data["events"] = tomlkit.aot()

    event = tomlkit.table()

    title_table = tomlkit.inline_table()
    title_table["en"] = title
    title_table["fr"] = title_fr or title
    event["title"] = title_table

    desc_table = tomlkit.inline_table()
    desc_table["en"] = description
    desc_table["fr"] = description_fr or description
    event["description"] = desc_table

    event["start_date"] = start_iso
    if end_iso:
        event["end_date"] = end_iso
    event["location"] = location
    event["type"] = event_type

    if url:
        event["url"] = url
    if reg_iso:
        event["registration_deadline"] = reg_iso

    if "events" not in data:
        data["events"] = tomlkit.aot()

    data["events"].append(event)

    events_file.parent.mkdir(parents=True, exist_ok=True)
    with open(events_file, "w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(data))

    console.print(f"[green]✓ Added new event to {events_file}[/green]")
    console.print(f"[blue]Title:[/blue] {title}")
    console.print(f"[blue]Date:[/blue] {start_iso}")
    console.print(f"[blue]Type:[/blue] {event_type}")


@events.command("import")
@click.option(
    "-i", "--input", "input_source", required=True, help="Input ICS file path or URL"
)
@click.option(
    "-o", "--output", default="content/data/events.toml", help="Output events.toml file"
)
@click.option("--dry-run", is_flag=True, help="Preview events without writing to file")
@click.option("--event-type", default="event", help="Event type to assign")
def import_ics(input_source, output, dry_run, event_type):
    """Import events from ICS calendar"""

    class Args:
        def __init__(self):
            self.input = input_source
            self.output = output
            self.dry_run = dry_run
            self.event_type = event_type

    importer = ICSImporter()
    importer.run(Args())


@events.command("list")
@click.option(
    "--format",
    type=click.Choice(["table", "json", "compact"]),
    default="table",
    help="Output format",
)
@click.option("--upcoming", is_flag=True, help="Show only upcoming events")
def list_events(format, upcoming):
    """List all events"""
    events_file = Path("content/data/events.toml")
    if not events_file.exists():
        console.print("[red]No events.toml found[/red]")
        return

    try:
        with open(events_file, "r", encoding="utf-8") as f:
            data = tomlkit.parse(f.read())
            events_list = data.get("events", [])
    except Exception as e:
        console.print(f"[red]Error reading events: {e}[/red]")
        return

    if upcoming:
        now = datetime.now()
        events_list = [
            e
            for e in events_list
            if datetime.fromisoformat(e.get("start_date", "").replace("Z", "+00:00"))
            > now
        ]

    if format == "json":
        print(json.dumps(events_list, indent=2, default=str))
    elif format == "compact":
        for i, event in enumerate(events_list, 1):
            title = event.get("title", {})
            if isinstance(title, dict):
                title = title.get("en", "Untitled")
            console.print(f"{i}. {title} - {event.get('start_date', 'No date')}")
    else:  # table format
        table = Table(title="Events")
        table.add_column("Title", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Start Date", style="yellow")
        table.add_column("Location", style="magenta")

        for event in events_list:
            title = event.get("title", {})
            if isinstance(title, dict):
                title = title.get("en", "Untitled")

            # Format start date
            start_date = event.get("start_date", "")
            if start_date:
                try:
                    dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                    formatted_date = dt.strftime("%Y-%m-%d %H:%M")
                except (ValueError, AttributeError):
                    formatted_date = start_date
            else:
                formatted_date = ""

            table.add_row(
                title, event.get("type", ""), formatted_date, event.get("location", "")
            )
        console.print(table)


@events.command("validate")
def validate_events():
    """Validate events.toml structure and content"""
    events_file = Path("content/data/events.toml")
    if not events_file.exists():
        console.print("[red]No events.toml found[/red]")
        return

    try:
        with open(events_file, "r", encoding="utf-8") as f:
            data = tomlkit.parse(f.read())
            events_list = data.get("events", [])

        errors = []
        warnings = []

        for i, event in enumerate(events_list, 1):
            # Check required fields
            if "title" not in event:
                errors.append(f"Event {i}: Missing 'title' field")
            elif isinstance(event["title"], dict):
                if "en" not in event["title"]:
                    errors.append(f"Event {i}: Missing 'title.en' field")

            if "start_date" not in event:
                errors.append(f"Event {i}: Missing 'start_date' field")
            else:
                try:
                    datetime.fromisoformat(event["start_date"].replace("Z", "+00:00"))
                except ValueError:
                    errors.append(f"Event {i}: Invalid 'start_date' format")

            if "type" not in event:
                warnings.append(f"Event {i}: Missing 'type' field")

            # Check translation consistency
            title = event.get("title", {})
            description = event.get("description", {})
            if isinstance(title, dict) and isinstance(description, dict):
                if ("en" in title) != ("en" in description):
                    warnings.append(
                        f"Event {i}: Inconsistent language fields between title and description"
                    )

        if errors:
            console.print("[red]Validation errors:[/red]")
            for error in errors:
                console.print(f"  ✗ {error}")

        if warnings:
            console.print("[yellow]Warnings:[/yellow]")
            for warning in warnings:
                console.print(f"  ⚠ {warning}")

        if not errors and not warnings:
            console.print("[green]✓ All events are valid![/green]")

    except Exception as e:
        console.print(f"[red]Error validating events: {e}[/red]")


@events.command("prune")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview what would be pruned without making changes",
)
@click.option("--before", help="Prune events before this date (YYYY-MM-DD)")
def prune_events(dry_run, before):
    """Remove past events"""
    events_file = Path("content/data/events.toml")
    if not events_file.exists():
        console.print("[red]No events.toml found[/red]")
        return

    try:
        with open(events_file, "r", encoding="utf-8") as f:
            data = tomlkit.parse(f.read())
            events_list = data.get("events", [])

        if not events_list:
            console.print("[yellow]No events found[/yellow]")
            return

        if before:
            try:
                cutoff_date = datetime.strptime(before, "%Y-%m-%d")
            except ValueError:
                console.print("[red]Invalid date format. Use YYYY-MM-DD[/red]")
                return
        else:
            cutoff_date = datetime.now()

        events_to_keep = []
        events_to_remove = []

        for event in events_list:
            start_date_str = event.get("start_date", "")
            if start_date_str:
                try:
                    event_date = datetime.fromisoformat(
                        start_date_str.replace("Z", "+00:00")
                    )
                    if event_date < cutoff_date:
                        events_to_remove.append(event)
                    else:
                        events_to_keep.append(event)
                except (ValueError, AttributeError):
                    events_to_keep.append(event)
            else:
                events_to_keep.append(event)

        if not events_to_remove:
            console.print("[green]No past events to prune[/green]")
            return

        console.print(
            f"[yellow]Found {len(events_to_remove)} past events to prune:[/yellow]"
        )
        for event in events_to_remove:
            title = event.get("title", {})
            if isinstance(title, dict):
                title = title.get("en", "Untitled")
            start_date = event.get("start_date", "")
            console.print(f"  - {title} ({start_date})")

        if dry_run:
            console.print(
                f"[blue]Dry run complete - would remove {len(events_to_remove)} events[/blue]"
            )
            return

        if not click.confirm(f"Remove {len(events_to_remove)} past events?"):
            console.print("[yellow]Operation cancelled[/yellow]")
            return

        data["events"] = tomlkit.aot()
        for event in events_to_keep:
            data["events"].append(event)

        with open(events_file, "w", encoding="utf-8") as f:
            f.write(tomlkit.dumps(data))

        console.print(f"[green]✓ Removed {len(events_to_remove)} past events[/green]")
        console.print(f"[blue]Kept {len(events_to_keep)} future/current events[/blue]")

    except Exception as e:
        console.print(f"[red]Error pruning events: {e}[/red]")
