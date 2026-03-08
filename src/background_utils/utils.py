"""Shared utilities for background_utils services."""

from __future__ import annotations

import threading
import time


def interruptible_sleep(
    seconds: float,
    stop_event: threading.Event,
    chunk: float = 0.5,
) -> None:
    """Sleep for *seconds*, waking early if *stop_event* is set.

    Instead of one long ``time.sleep()`` call, sleeps in small *chunk*-second
    intervals so the service can respond promptly to a shutdown signal.
    """
    end_time = time.time() + seconds
    while time.time() < end_time and not stop_event.is_set():
        time.sleep(chunk)
