import sys
import click
from rich.console import Console
from rich.table import Table
from pathlib import Path
from datetime import datetime
from slugify import slugify
import requests
import re
import hashlib
import time
import random
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent.parent))
requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)

from importers.ctf import CTFImporter
from constants import WRITEUP_TEMPLATE, CTF_INDEX_TEMPLATE, IMAGE_DOWNLOAD_HEADERS

console = Console()


@click.group()
def writeups():
    """Writeup management utilities"""
    pass


@writeups.command("new")
@click.option("-c", "--ctf", prompt="CTF name", help="Name of the CTF")
@click.option(
    "-n", "--challenge", prompt="Challenge name", help="Name of the challenge"
)
@click.option("-C", "--category", prompt="Category", help="Challenge category")
@click.option("-a", "--author", prompt="Author", help="Author name")
def create_writeup(ctf, challenge, category, author):
    """Create a new writeup template"""
    ctf_slug = slugify(ctf)
    challenge_slug = slugify(challenge)
    ctf_dir = Path("content/writeups") / ctf_slug
    writeup_dir = ctf_dir / challenge_slug

    if writeup_dir.exists():
        console.print(
            f"[yellow]Writeup directory already exists: {writeup_dir}[/yellow]"
        )
        if not click.confirm("Continue anyway?"):
            return

    ctf_dir.mkdir(parents=True, exist_ok=True)
    ctf_index_file = ctf_dir / "_index.md"

    if not ctf_index_file.exists():
        ctf_index_content = CTF_INDEX_TEMPLATE.format(ctf=ctf)
        with open(ctf_index_file, "w", encoding="utf-8") as f:
            f.write(ctf_index_content)
        console.print(f"[green]✓ Created CTF index file: {ctf_index_file}[/green]")

    writeup_dir.mkdir(parents=True, exist_ok=True)
    files_dir = writeup_dir / "files"
    files_dir.mkdir(exist_ok=True)

    template = WRITEUP_TEMPLATE.format(
        challenge=challenge,
        author=author,
        date=datetime.now().date().isoformat(),
        category=category,
        ctf=ctf,
        difficulty="{difficulty}",
        points="{points}",
    )

    index_file = writeup_dir / "index.md"
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(template)

    console.print(f"[green]✓ Created writeup template at {writeup_dir}[/green]")
    console.print(f"[blue]  ├── index.md[/blue]")
    console.print(f"[blue]  └── files/[/blue]")
    console.print(f"\n[yellow]Next steps:[/yellow]")
    console.print(f"1. Edit {index_file}")
    console.print(f"2. Add challenge files to {files_dir}")
    console.print("3. Commit and push to the writeups repository")


@writeups.command("import")
@click.option("-c", "--ctf", required=True, help="CTF name to import")
@click.option(
    "-a", "--auth", required=True, help="Authorization token (Bearer <token>)"
)
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


@writeups.command("list")
@click.option("-c", "--ctf", help="Filter by CTF name")
@click.option("-C", "--category", help="Filter by category")
@click.option(
    "--format",
    type=click.Choice(["table", "compact"]),
    default="table",
    help="Output format",
)
@click.option("-p", "--show-path", is_flag=True, help="Show file paths")
def list_writeups(ctf, category, format, show_path):
    """List all writeups"""
    writeups_dir = Path("content/writeups")
    if not writeups_dir.exists():
        console.print("[red]Writeups directory not found[/red]")
        return

    writeups_list = []

    for ctf_dir in writeups_dir.iterdir():
        if not ctf_dir.is_dir() or ctf_dir.name.startswith("."):
            continue

        if ctf and ctf.lower() not in ctf_dir.name.lower():
            continue

        for challenge_dir in ctf_dir.iterdir():
            if not challenge_dir.is_dir() or challenge_dir.name.startswith("."):
                continue

            index_file = challenge_dir / "index.md"
            if not index_file.exists():
                continue

            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    content = f.read()

                if content.startswith("+++"):
                    parts = content.split("+++", 2)
                    if len(parts) >= 2:
                        import tomlkit

                        metadata = tomlkit.parse(parts[1])
                    else:
                        continue
                else:
                    continue

                writeup_category = (
                    metadata.get("taxonomies", {}).get("categories", [""])[0]
                    if metadata.get("taxonomies", {}).get("categories")
                    else ""
                )

                filter_category = writeup_category or "none"

                if category and category.lower() != filter_category.lower():
                    continue

                files_dir = challenge_dir / "files"
                file_count = 0

                if files_dir.exists():
                    for file_path in files_dir.iterdir():
                        if file_path.is_file():
                            file_count += 1

                writeups_list.append(
                    {
                        "title": metadata.get("title", challenge_dir.name),
                        "ctf": metadata.get("extra", {}).get("ctf", ctf_dir.name),
                        "category": writeup_category or "none",
                        "author": (
                            ", ".join(metadata.get("authors", []))
                            if metadata.get("authors")
                            else ""
                        ),
                        "path": f"content/writeups/{ctf_dir.name}/{challenge_dir.name}",
                        "file_count": file_count,
                    }
                )

            except Exception as e:
                console.print(f"[red]Failed to read {index_file}: {e}[/red]")
                continue

    if not writeups_list:
        console.print("[yellow]No writeups found[/yellow]")
        return

    if format == "compact":
        for i, writeup in enumerate(writeups_list, 1):
            line = f"{i}. {writeup['title']} ({writeup['ctf']}) - {writeup['category']}"
            if writeup["file_count"] > 0:
                line += f" [{writeup['file_count']} files]"
            if show_path:
                line += f" [{writeup['path']}]"
            console.print(line)
    else:
        table = Table(title="Writeups")
        table.add_column("Title", style="cyan", max_width=30)
        table.add_column("CTF", style="green", max_width=20)
        table.add_column("Category", style="yellow", max_width=15)
        table.add_column("Author", style="magenta", max_width=20)
        table.add_column("Files", style="blue", justify="center", max_width=8)
        if show_path:
            table.add_column("Path", style="dim", max_width=40)

        for writeup in writeups_list:
            category_display = writeup["category"]
            if category_display == "none":
                category_display = "[red]none[/red]"

            author_display = writeup["author"]
            if len(author_display) > 18:
                author_display = author_display[:15] + "..."

            file_display = (
                str(writeup["file_count"])
                if writeup["file_count"] > 0
                else "[dim]0[/dim]"
            )

            row_data = [
                writeup["title"],
                writeup["ctf"],
                category_display,
                author_display,
                file_display,
            ]
            if show_path:
                row_data.append(writeup["path"])

            table.add_row(*row_data)
        console.print(table)


@writeups.command("images")
@click.option("--dry-run", is_flag=True, help="Preview changes without making them")
@click.option("-c", "--ctf", help="Only process writeups for this CTF")
def localize_images(dry_run, ctf):
    """Download remote images and update markdown links to use local files"""
    writeups_dir = Path("content/writeups")
    if not writeups_dir.exists():
        console.print("[red]Writeups directory not found[/red]")
        return

    processed_count = 0
    downloaded_count = 0
    error_count = 0

    for ctf_dir in writeups_dir.iterdir():
        if not ctf_dir.is_dir() or ctf_dir.name.startswith("."):
            continue

        if ctf and ctf.lower() not in ctf_dir.name.lower():
            continue

        for challenge_dir in ctf_dir.iterdir():
            if not challenge_dir.is_dir() or challenge_dir.name.startswith("."):
                continue

            index_file = challenge_dir / "index.md"
            if not index_file.exists():
                continue

            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    content = f.read()
                image_pattern = r"!\[[^\]]*\]\(([^)]+)\)"
                matches = re.findall(image_pattern, content)

                remote_images = [
                    url for url in matches if url.startswith(("http://", "https://"))
                ]

                if not remote_images:
                    continue

                console.print(
                    f"[blue]Processing {ctf_dir.name}/{challenge_dir.name}[/blue]"
                )

                files_dir = challenge_dir / "files"
                updated_content = content

                for i, image_url in enumerate(remote_images):
                    try:
                        parsed_url = urlparse(image_url)
                        original_filename = Path(parsed_url.path).name

                        if not original_filename:
                            url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
                            original_filename = f"image_{url_hash}.png"

                        if "." not in original_filename:
                            original_filename += ".png"

                        local_filename = original_filename
                        local_path = files_dir / local_filename

                        counter = 1
                        while local_path.exists():
                            name, ext = original_filename.rsplit(".", 1)
                            local_filename = f"{name}_{counter}.{ext}"
                            local_path = files_dir / local_filename
                            counter += 1

                        if dry_run:
                            console.print(
                                f"  Would download: {image_url} -> files/{local_filename}"
                            )
                        else:
                            files_dir.mkdir(exist_ok=True)

                            success = False
                            max_retries = 3

                            for attempt in range(max_retries):
                                try:
                                    if i > 0 or attempt > 0:
                                        delay = random.uniform(2, 5) + (attempt * 2)
                                        time.sleep(delay)

                                    console.print(
                                        f"  Downloading: {image_url} (attempt {attempt + 1})"
                                    )

                                    headers = IMAGE_DOWNLOAD_HEADERS

                                    response = requests.get(
                                        image_url,
                                        timeout=30,
                                        verify=False,
                                        headers=headers,
                                    )
                                    response.raise_for_status()

                                    with open(local_path, "wb") as f:
                                        f.write(response.content)

                                    downloaded_count += 1
                                    console.print(
                                        f"  [green]Saved as: files/{local_filename}[/green]"
                                    )
                                    success = True
                                    break

                                except requests.exceptions.HTTPError as e:
                                    if e.response.status_code == 429:
                                        console.print(
                                            f"  [yellow]Rate limited, waiting before retry...[/yellow]"
                                        )
                                        time.sleep(random.uniform(10, 20))
                                    elif attempt == max_retries - 1:
                                        raise
                                except Exception as e:
                                    if attempt == max_retries - 1:
                                        raise
                                    console.print(
                                        f"  [yellow]Attempt {attempt + 1} failed: {e}[/yellow]"
                                    )

                            if not success:
                                raise Exception(f"Failed after {max_retries} attempts")

                            updated_content = updated_content.replace(
                                f"]({image_url})", f"](files/{local_filename})"
                            )

                    except Exception as e:
                        console.print(f"  [red]Error processing {image_url}: {e}[/red]")
                        error_count += 1
                        continue

                if not dry_run and updated_content != content:
                    with open(index_file, "w", encoding="utf-8") as f:
                        f.write(updated_content)
                    console.print(f"  [green]Updated {index_file.name}[/green]")

                processed_count += 1

            except Exception as e:
                console.print(f"[red]Failed to process {index_file}: {e}[/red]")
                error_count += 1
                continue

        console.print(f"\n[green]Summary:[/green]")
    console.print(f"  Processed: {processed_count} writeups")
    if not dry_run:
        console.print(f"  Downloaded: {downloaded_count} images")
    console.print(f"  Errors: {error_count}")

    if dry_run:
        console.print(
            f"\n[yellow]This was a dry run. Use without --dry-run to actually download images.[/yellow]"
        )
