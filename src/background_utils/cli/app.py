from __future__ import annotations

import typer

from background_utils.logging import setup_logging

app = typer.Typer(no_args_is_help=True, add_completion=False, help="Background Utilities CLI")


@app.callback()
def init(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logs"),
) -> None:
    """
    Root CLI initializer.
    """
    setup_logging(level="DEBUG" if verbose else "INFO")


# Register sub-apps
from background_utils.cli.commands.example import app as example_app  # noqa: E402
from background_utils.cli.commands.wifi import app as wifi_app  # noqa: E402

app.add_typer(example_app, name="example")
app.add_typer(wifi_app, name="wifi")


def main() -> None:
    app()
