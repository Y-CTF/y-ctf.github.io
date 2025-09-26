# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "python-slugify",
#     "requests",
#     "rich",
#     "tomlkit",
#     "icalendar",
#     "click",
# ]
# ///

import click
from commands.imports import import_
from commands.events import events
from commands.writeups import writeups
from commands.maintenance import maintenance
from commands.dev import dev

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Y-CTF Repository Management CLI

    A tiny tool for managing the Y-CTF website repository,
    including imports, maintenance, and utilities.
    """
    pass

cli.add_command(import_)
cli.add_command(events)
cli.add_command(writeups)
cli.add_command(maintenance)
cli.add_command(dev)

if __name__ == "__main__":
    cli()