import click
from rich.console import Console
from rich.table import Table
from pathlib import Path
from datetime import datetime
from slugify import slugify
import frontmatter

console = Console()

@click.group()
def writeups():
    """Writeup management utilities"""
    pass

@writeups.command("create")
@click.option("--ctf", prompt="CTF name", help="Name of the CTF")
@click.option("--challenge", prompt="Challenge name", help="Name of the challenge")
@click.option("--category", prompt="Category", help="Challenge category")
@click.option("--author", prompt="Author", help="Author name")
@click.option("--difficulty", type=click.Choice(["easy", "medium", "hard"]), prompt="Difficulty", help="Challenge difficulty")
@click.option("--points", type=int, prompt="Points", help="Points value")
def create_writeup(ctf, challenge, category, author, difficulty, points):
    """Create a new writeup template"""
    ctf_slug = slugify(ctf)
    challenge_slug = slugify(challenge)
    writeup_dir = Path("content/writeups") / ctf_slug / challenge_slug

    if writeup_dir.exists():
        console.print(f"[yellow]Writeup directory already exists: {writeup_dir}[/yellow]")
        if not click.confirm("Continue anyway?"):
            return

    writeup_dir.mkdir(parents=True, exist_ok=True)
    files_dir = writeup_dir / "files"
    files_dir.mkdir(exist_ok=True)

    template = f"""+++
title = "{challenge}"
description = "[Brief description of the challenge]"
authors = ["{author}"]
date = {datetime.now().date().isoformat()}

[taxonomies]
categories = ["{category}"]

[extra]
ctf = "{ctf}"
difficulty = "{difficulty}"
points = {points}
+++

## Description

[Describe the challenge here]

## Solution

[Explain your solution approach]

### Analysis

[Detail your analysis steps]

### Exploit

[Show the exploit code/steps]

### Flag

```
[FLAG_HERE]
```

## Files

[List any relevant files in the files/ directory]

## References

- [Any references or links]
"""

    index_file = writeup_dir / "index.md"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(template)

    console.print(f"[green]✓ Created writeup template at {writeup_dir}[/green]")
    console.print(f"[blue]  ├── index.md[/blue]")
    console.print(f"[blue]  └── files/[/blue]")
    console.print(f"\n[yellow]Next steps:[/yellow]")
    console.print(f"1. Edit {index_file}")
    console.print(f"2. Add challenge files to {files_dir}")
    console.print("3. Commit and push to the writeups repository")

@writeups.command("list")
@click.option("--ctf", help="Filter by CTF name")
@click.option("--category", help="Filter by category")
@click.option("--format", type=click.Choice(["table", "compact"]), default="table", help="Output format")
def list_writeups(ctf, category, format):
    """List all writeups"""
    writeups_dir = Path("content/writeups")
    if not writeups_dir.exists():
        console.print("[red]Writeups directory not found[/red]")
        return

    writeups_list = []

    for ctf_dir in writeups_dir.iterdir():
        if not ctf_dir.is_dir() or ctf_dir.name.startswith('.'):
            continue

        if ctf and ctf.lower() not in ctf_dir.name.lower():
            continue

        for challenge_dir in ctf_dir.iterdir():
            if not challenge_dir.is_dir() or challenge_dir.name.startswith('.'):
                continue

            index_file = challenge_dir / "index.md"
            if not index_file.exists():
                continue

            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                if content.startswith('+++'):
                    parts = content.split('+++', 2)
                    if len(parts) >= 2:
                        import tomlkit
                        metadata = tomlkit.parse(parts[1])
                    else:
                        continue
                else:
                    continue

                writeup_category = metadata.get('taxonomies', {}).get('categories', [''])[0] if metadata.get('taxonomies', {}).get('categories') else ''

                if category and category.lower() != writeup_category.lower():
                    continue

                writeups_list.append({
                    'title': metadata.get('title', challenge_dir.name),
                    'ctf': metadata.get('extra', {}).get('ctf', ctf_dir.name),
                    'category': writeup_category,
                    'author': ', '.join(metadata.get('authors', [])) if metadata.get('authors') else '',
                    'difficulty': metadata.get('extra', {}).get('difficulty', ''),
                    'points': metadata.get('extra', {}).get('points', ''),
                    'path': str(challenge_dir.relative_to(Path.cwd()))
                })

            except Exception:
                continue

    if not writeups_list:
        console.print("[yellow]No writeups found[/yellow]")
        return

    if format == "compact":
        for i, writeup in enumerate(writeups_list, 1):
            console.print(f"{i}. {writeup['title']} ({writeup['ctf']}) - {writeup['category']}")
    else:
        table = Table(title="Writeups")
        table.add_column("Title", style="cyan")
        table.add_column("CTF", style="green")
        table.add_column("Category", style="yellow")
        table.add_column("Author", style="magenta")
        table.add_column("Difficulty", style="red")
        table.add_column("Points", style="blue")

        for writeup in writeups_list:
            table.add_row(
                writeup['title'],
                writeup['ctf'],
                writeup['category'],
                writeup['author'],
                str(writeup['difficulty']),
                str(writeup['points'])
            )
        console.print(table)