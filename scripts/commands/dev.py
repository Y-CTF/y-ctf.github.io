import click
from rich.console import Console
import subprocess

console = Console()

@click.group()
def dev():
    """Development utilities"""
    pass

@dev.command("serve")
@click.option("--port", default=1111, help="Port to serve on")
@click.option("--host", default="127.0.0.1", help="Host to bind to")
def serve(port, host):
    """Start development server (zola serve)"""
    try:
        console.print(f"[blue]Starting development server on {host}:{port}[/blue]")
        subprocess.run(["zola", "serve", "--interface", host, "--port", str(port)], check=True)
    except subprocess.CalledProcessError:
        console.print("[red]Error: Failed to start zola server[/red]")
        console.print("[yellow]Make sure zola is installed and you're in the project root[/yellow]")
    except FileNotFoundError:
        console.print("[red]Error: zola command not found[/red]")
        console.print("[yellow]Please install zola first[/yellow]")

@dev.command("build")
@click.option("--draft", is_flag=True, help="Include draft content")
def build(draft):
    """Build the site (zola build)"""
    try:
        cmd = ["zola", "build"]
        if draft:
            cmd.append("--drafts")

        console.print("[blue]Building site...[/blue]")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        console.print("[green]Build completed successfully![/green]")
        if result.stdout:
            console.print(result.stdout)
    except subprocess.CalledProcessError as e:
        console.print("[red]Build failed![/red]")
        if e.stderr:
            console.print(e.stderr)