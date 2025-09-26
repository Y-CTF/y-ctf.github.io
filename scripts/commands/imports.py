"""Import commands for the Y-CTF CLI"""

import click
from rich.console import Console
from pathlib import Path

from ..importers.ctf import CTFImporter
from ..importers.ics import ICSImporter

console = Console()

@click.group()
def import_():
    """Import data from various sources"""
    pass

@import_.command("ctf")
@click.option("-c", "--ctf-name", required=True, help="CTF name to import")
@click.option("-a", "--auth", required=True, help="Authorization token (Bearer <token>)")
@click.option("-o", "--output", default="content/writeups", help="Output directory")
@click.option("--dry-run", is_flag=True, help="Preview without writing files")
def import_ctf(ctf_name, auth, output, dry_run):
    """Import writeups from CTFNote"""
    class Args:
        def __init__(self):
            self.ctf_name = ctf_name
            self.auth = auth
            self.output = output
            self.dry_run = dry_run

    importer = CTFImporter()
    importer.run(Args())

@import_.command("ics")
@click.option("-i", "--input", "input_source", required=True, help="Input ICS file path or URL")
@click.option("-o", "--output", default="content/data/events.toml", help="Output events.toml file")
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