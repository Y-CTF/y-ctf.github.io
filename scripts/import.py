# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "python-slugify",
#     "requests",
#     "rich",
#     "tomlkit",
#     "icalendar",
# ]
# ///

import argparse
import sys
from rich import print

from importers.ctf import CTFImporter
from importers.ics import ICSImporter


IMPORTERS = {
    'ctf': CTFImporter(),
    'ics': ICSImporter(),
}

def main():
    parser = argparse.ArgumentParser(
        description='CTF importer/syncer from different sources',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Available importers: {', '.join(IMPORTERS.keys())}"
    )

    subparsers = parser.add_subparsers(
        dest='importer',
    )

    for name, importer in IMPORTERS.items():
        subparser = subparsers.add_parser(name)
        importer.add_arguments(subparser)

    args = parser.parse_args()

    if not args.importer:
        parser.print_help()
        sys.exit(1)

    importer = IMPORTERS[args.importer]
    importer.run(args)


if __name__ == "__main__":
    main()