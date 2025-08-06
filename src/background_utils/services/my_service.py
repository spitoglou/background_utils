from __future__ import annotations

import threading
import time

from background_utils.config import load_settings
from background_utils.logging import setup_logging, logger


def run(stop_event: threading.Event) -> None:
    """
    Example placeholder service demonstrating the common interface.

    Replace this logic with real work. It cooperatively stops when stop_event is set.
    """
    setup_logging()
    settings = load_settings()
    interval = max(1.0, float(getattr(settings, "service_interval_seconds", 5.0)))
    logger.info("Starting my_service (placeholder)")
    logger.info(f"Tick interval: {interval}s")

    ticks = 0
    try:
        while not stop_event.is_set():
            ticks += 1
            logger.info(f"my_service tick #{ticks}")
            # Do some lightweight placeholder work
            time.sleep(interval)
    except Exception as exc:  # noqa: BLE001
        logger.exception(f"my_service crashed: {exc}")
        raise
    finally:
        logger.info("my_service stopped")


def main() -> None:
    """
    Backward-compatible single-service entry. Not wired to an entry point by default,
    but can be run directly for testing.
    """
    stop_event = threading.Event()
    try:
        run(stop_event)
    except KeyboardInterrupt:
        stop_event.set()


if __name__ == "__main__":
    main()