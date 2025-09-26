import sys
from pathlib import Path
from datetime import datetime
import tomlkit
import requests
from icalendar import Calendar
from rich import print

from .base import BaseImporter


class ICSImporter(BaseImporter):
    def add_arguments(self, parser):
        parser.add_argument(
            "-i", "--input", help="Input ICS file path or URL", required=True
        )
        parser.add_argument(
            "-o",
            "--output",
            help="Output events.toml file",
            default="content/data/events.toml",
        )
        parser.add_argument(
            "--dry-run",
            help="Preview events without writing to file",
            action="store_true",
        )
        parser.add_argument(
            "--event-type", help="Event type to assign", default="event"
        )

    def fetch_ics(self, source):
        if source.startswith(("http://", "https://")):
            requests.packages.urllib3.disable_warnings()
            response = requests.get(source, verify=False)
            response.raise_for_status()
            return response.content
        else:
            path = Path(source)
            if not path.exists():
                raise FileNotFoundError(f"ICS file not found: {path}")
            return path.read_bytes()

    def parse_ics(self, ics_data, event_type):
        cal = Calendar.from_ical(ics_data)
        events = []

        for component in cal.walk():
            if component.name == "VEVENT":
                event = {}

                if "SUMMARY" in component:
                    title_text = str(component.get("SUMMARY"))
                    title_table = tomlkit.inline_table()
                    title_table["en"] = title_text
                    title_table["fr"] = title_text
                    event["title"] = title_table

                if "DESCRIPTION" in component:
                    desc_text = str(component.get("DESCRIPTION"))
                    desc_table = tomlkit.inline_table()
                    desc_table["en"] = desc_text
                    desc_table["fr"] = desc_text
                    event["description"] = desc_table

                if "DTSTART" in component:
                    dtstart = component.get("DTSTART").dt
                    if isinstance(dtstart, datetime):
                        event["start_date"] = dtstart.isoformat()
                    else:
                        event["start_date"] = datetime.combine(
                            dtstart, datetime.min.time()
                        ).isoformat()

                if "DTEND" in component:
                    dtend = component.get("DTEND").dt
                    if isinstance(dtend, datetime):
                        event["end_date"] = dtend.isoformat()
                    else:
                        event["end_date"] = datetime.combine(
                            dtend, datetime.min.time()
                        ).isoformat()

                if "LOCATION" in component:
                    event["location"] = str(component.get("LOCATION"))

                if "URL" in component:
                    event["url"] = str(component.get("URL"))

                event["type"] = event_type

                events.append(event)

        return events

    def is_duplicate_event(self, new_event, existing_event):
        # Handle both old and new title formats
        new_title = new_event.get("title", {})
        existing_title = existing_event.get("title", {})

        if isinstance(new_title, dict) and isinstance(existing_title, dict):
            title_match = (
                new_title.get("en", "").strip() == existing_title.get("en", "").strip()
            )
        elif isinstance(new_title, str) and isinstance(existing_title, str):
            title_match = new_title.strip() == existing_title.strip()
        elif isinstance(new_title, dict) and isinstance(existing_title, str):
            title_match = new_title.get("en", "").strip() == existing_title.strip()
        elif isinstance(new_title, str) and isinstance(existing_title, dict):
            title_match = new_title.strip() == existing_title.get("en", "").strip()
        else:
            title_match = False

        start_match = new_event.get("start_date", "") == existing_event.get(
            "start_date", ""
        )
        location_match = (
            new_event.get("location", "").strip()
            == existing_event.get("location", "").strip()
        )

        return title_match and start_match and location_match

    def run(self, args):
        try:
            ics_data = self.fetch_ics(args.input)
            events = self.parse_ics(ics_data, args.event_type)

            if not events:
                print("[yellow]No events found in ICS file[/yellow]")
                return

            output_path = Path(args.output)

            if output_path.exists():
                with open(output_path, "r", encoding="utf-8") as f:
                    data = tomlkit.parse(f.read())
            else:
                data = tomlkit.document()
                data["events"] = tomlkit.aot()

            existing_events = data.get("events", [])

            new_events = []
            duplicate_count = 0

            for event in events:
                is_duplicate = any(
                    self.is_duplicate_event(event, existing_event)
                    for existing_event in existing_events
                )

                if not is_duplicate:
                    new_events.append(event)
                else:
                    duplicate_count += 1

            if args.dry_run:
                print(f"[green]Found {len(events)} events total:[/green]")
                print(f"[yellow]{duplicate_count} duplicates would be skipped[/yellow]")
                print(f"[green]{len(new_events)} new events would be added:[/green]")
                for i, event in enumerate(new_events, 1):
                    title = event.get("title", "Untitled")
                    if isinstance(title, dict):
                        title = title.get("en", "Untitled")
                    print(f"{i}. {title} - {event.get('start_date', 'No date')}")
                return

            if not new_events:
                print("[yellow]No new events to add (all are duplicates)[/yellow]")
                return

            for event in new_events:
                existing_events.append(event)

            if "events" not in data:
                data["events"] = existing_events

            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(tomlkit.dumps(data))

            print(
                f"[green]Successfully added {len(new_events)} new events to {output_path}[/green]"
            )
            if duplicate_count > 0:
                print(f"[yellow]Skipped {duplicate_count} duplicate events[/yellow]")

        except FileNotFoundError as e:
            print(f"[red]Error:[/red] {e}")
            sys.exit(1)
        except requests.RequestException as e:
            print(f"[red]Error fetching ICS from URL:[/red] {e}")
            sys.exit(1)
        except Exception as e:
            print(f"[red]Error parsing ICS file:[/red] {e}")
            sys.exit(1)
