from __future__ import annotations

import os
from typing import Optional

from loguru import logger
from rich.console import Console

_console: Optional[Console] = None
_configured = False


def setup_logging(level: str | None = None) -> None:
    """
    Configure loguru once with Rich-friendly sink.
    Level can be overridden via LOG_LEVEL env (default: INFO).
    """
    global _configured, _console
    if _configured:
        return

    log_level = (level or os.getenv("LOG_LEVEL") or "INFO").upper()

    # Remove default handler and attach rich console sink
    logger.remove()
    _console = Console(soft_wrap=True, force_terminal=False, legacy_windows=True)
    logger.add(
        _console.print,
        level=log_level,
        colorize=True,
        enqueue=False,
        backtrace=False,
        diagnose=False,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <7}</level> | {message}",
    )
    _configured = True


__all__ = ["setup_logging", "logger"]