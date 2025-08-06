from __future__ import annotations

import importlib
from typing import cast

import typer
from rich.console import Console

from background_utils.logging import setup_logging

console = Console()
app = typer.Typer(no_args_is_help=True, add_completion=False, help="Background Utilities CLI")


def _lazy_import(module_path: str, attr: str | None = None) -> object:
    module = importlib.import_module(module_path)
    return getattr(module, attr) if attr else module


@app.callback()
def init(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logs")
) -> None:
    """
    Root CLI initializer.
    """
    setup_logging(level="DEBUG" if verbose else "INFO")


# Register sub-apps with explicit typing
example_app = cast(typer.Typer, _lazy_import("background_utils.cli.commands.example", "app"))
wifi_app = cast(typer.Typer, _lazy_import("background_utils.cli.commands.wifi", "app"))
app.add_typer(example_app, name="example")
app.add_typer(wifi_app, name="wifi")


def main() -> None:
    app()