# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "python-slugify",
#     "requests",
#     "rich",
#     "tomlkit",
#     "icalendar",
#     "click",
#     "frontmatter"
# ]
# ///

import click
from commands.events import events
from commands.writeups import writeups


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Y-CTF Repository Management CLI

    A tiny tool for managing the Y-CTF website repository,
    including imports, maintenance, and utilities.
    """
    pass


cli.add_command(events)
cli.add_command(writeups)

if __name__ == "__main__":
    cli()
