import threading
import time

import psutil

from background_utils.logging import logger, setup_logging


def run(stop_event: threading.Event, interval_seconds: float = 60.0) -> None:
    """
    Battery monitor loop that cooperatively stops when stop_event is set.
    """
    setup_logging()
    logger.info("Starting battery monitor")

    while not stop_event.is_set():
        try:
            battery = psutil.sensors_battery()
            if battery:
                logger.info(f"Battery percentage: {battery.percent}%")
                if battery.power_plugged:
                    logger.info("Power is plugged in.")
                else:
                    logger.info("Power is not plugged in.")
                if (
                    battery.percent is not None 
                    and battery.percent < 15 
                    and not battery.power_plugged
                ):
                    logger.warning("Battery low! Plug in the charger.")
            else:
                logger.warning("Battery information not available")
        except Exception as e:  # noqa: BLE001
            logger.exception(f"Error checking battery status: {e}")

        # Sleep in small chunks to be more responsive to stop_event
        end_time = time.time() + interval_seconds
        while time.time() < end_time and not stop_event.is_set():
            time.sleep(0.5)

    logger.info("Battery monitor stopped")


def main() -> None:
    """
    Backward-compatible single-service entry point.
    """
    stop_event = threading.Event()
    try:
        run(stop_event)
    except KeyboardInterrupt:
        stop_event.set()