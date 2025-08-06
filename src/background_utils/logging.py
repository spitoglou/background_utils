from __future__ import annotations

import os
from pathlib import Path

from loguru import logger
from rich.console import Console

_console: Console | None = None
_configured = False


def _windows_log_dir() -> Path:
    localappdata = os.getenv("LOCALAPPDATA")
    if not localappdata:
        # Fallback to current directory if env var missing
        return Path(".") / "logs"
    return Path(localappdata) / "background-utils"


def _ensure_log_file() -> tuple[Path, Path]:
    """
    Ensure the Windows-specific log directory and file exist.
    Returns (log_dir, log_file).
    """
    log_dir = _windows_log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "background-utils.log"
    # Touch file if it does not exist
    if not log_file.exists():
        log_file.touch()
    return log_dir, log_file


def setup_logging(level: str | None = None) -> None:
    """
    Configure loguru once with Rich-friendly sink and a file sink on Windows.
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

    # File sink (Windows tray access)
    try:
        _, log_file = _ensure_log_file()
        logger.add(
            log_file.as_posix(),
            level=log_level,
            enqueue=False,
            backtrace=False,
            diagnose=False,
            rotation="5 MB",
            retention=5,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <7} | {message}",
        )
    except Exception:
        # Silently ignore file sink setup issues; console logging remains
        pass

    _configured = True


__all__ = ["setup_logging", "logger"]