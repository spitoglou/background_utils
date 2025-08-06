from __future__ import annotations

import time
from typing import Optional

from loguru import logger

from background_utils.config import load_settings
from background_utils.logging import setup_logging


def run(stop_event) -> None:  # type: ignore[no-untyped-def]
    """
    Example long-running service loop.

    This function is cooperative: it stops when stop_event.is_set() is True.
    No signal handling here; the manager owns signal handling.
    """
    setup_logging()
    settings = load_settings()
    logger.info("Starting example service")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Tick interval: {settings.service_interval_seconds}s")

    ticks = 0
    try:
        while not stop_event.is_set():
            ticks += 1
            logger.info(f"Service tick #{ticks}")
            time.sleep(settings.service_interval_seconds)
    except Exception as exc:  # noqa: BLE001
        logger.exception(f"Service crashed: {exc}")
        raise
    finally:
        logger.info("Service stopped")


def main() -> None:
    """
    Single-service entry point retains backward compatibility by running this service alone.
    """
    import threading

    stop_event = threading.Event()
    try:
        run(stop_event)
    except KeyboardInterrupt:
        stop_event.set()