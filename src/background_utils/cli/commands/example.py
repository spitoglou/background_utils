from __future__ import annotations

from datetime import datetime

import rich
import typer
from rich.table import Table

from background_utils.logging import setup_logging

console = rich.get_console()
app = typer.Typer(no_args_is_help=True, add_completion=False, help="Example commands")


@app.command("hello")
def hello(name: str = "world", excited: bool = False) -> None:
    """
    Simple example command.
    """
    setup_logging()
    greeting = f"Hello, {name}{'!' if excited else '.'}"
    console.print(f"[bold green]{greeting}[/bold green]")


@app.command("time")
def show_time(fmt: str | None = typer.Option(None, help="Datetime format string")) -> None:
    """
    Show current time in a rich table.
    """
    now = datetime.now()
    formatted = now.strftime(fmt) if fmt else now.isoformat(timespec="seconds")

    table = Table(title="Current Time")
    table.add_column("ISO", style="cyan")
    table.add_row(formatted)
    console.print(table)