from __future__ import annotations

import signal
import threading
import time
from dataclasses import dataclass
from types import FrameType
from typing import Callable, Iterable, List, Optional

from background_utils.logging import setup_logging, logger


ServiceFunc = Callable[[threading.Event], None]


@dataclass
class ServiceSpec:
    name: str
    target: ServiceFunc


class ServiceManager:
    def __init__(self, services: Iterable[ServiceSpec], shutdown_timeout: float = 10.0) -> None:
        self.services: List[ServiceSpec] = list(services)
        self.shutdown_timeout = shutdown_timeout
        self.stop_event = threading.Event()
        self.threads: list[threading.Thread] = []

    def _signal_handler(self, signum: int, frame: Optional[FrameType]) -> None:  # type: ignore[override]
        logger.info(f"Received signal {signum}. Initiating shutdown...")
        self.stop()

    def start(self) -> None:
        setup_logging()
        # Make it obvious which manager is running and which services are included
        svc_names = ", ".join(spec.name for spec in self.services) or "<none>"
        logger.info(f"Service Manager starting {len(self.services)} services: {svc_names}")

        # Install signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Spawn all service threads
        for spec in self.services:
            logger.info(f"Launching service: {spec.name}")
            t = threading.Thread(
                target=self._run_service_wrapper,
                name=f"svc-{spec.name}",
                args=(spec,),
                daemon=False,  # make non-daemon so process lifecycle waits for all
            )
            self.threads.append(t)
            t.start()
            logger.info(f"Service thread started: {spec.name}")

    def _run_service_wrapper(self, spec: ServiceSpec) -> None:
        logger.info(f"[{spec.name}] run() entering")
        try:
            spec.target(self.stop_event)
            logger.info(f"[{spec.name}] run() exited normally")
        except Exception as exc:  # noqa: BLE001
            # Log crash but DO NOT stop other services (per requirement)
            logger.exception(f"[{spec.name}] crashed: {exc}")

    def wait(self) -> None:
        try:
            while not self.stop_event.is_set():
                # Periodic liveness heartbeat to confirm manager loop active
                time.sleep(1.0)
                alive = [t.name for t in self.threads if t.is_alive()]
                logger.debug(f"Manager heartbeat; alive threads: {alive}")
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        if not self.stop_event.is_set():
            self.stop_event.set()
            logger.info("Stopping services...")

        # Join all threads with timeout
        deadline = time.time() + self.shutdown_timeout
        for t in self.threads:
            remaining = max(0.0, deadline - time.time())
            if remaining == 0.0:
                break
            t.join(timeout=remaining)

        # Report any threads still alive
        alive = [t.name for t in self.threads if t.is_alive()]
        if alive:
            logger.warning(f"Some services did not stop in time: {alive}")
        else:
            logger.info("All services stopped cleanly.")

    def run(self) -> None:
        self.start()
        self.wait()
        self.stop()


def _collect_default_services() -> list[ServiceSpec]:
    # Local imports to avoid import-time side effects
    from background_utils.services.example_service import run as example_run  # noqa: WPS433
    from background_utils.services.battery_monitor import run as battery_run  # noqa: WPS433
    try:
        from background_utils.services.my_service import run as my_run  # type: ignore  # noqa: WPS433
    except Exception as exc:
        logger.warning(f"my_service not available ({exc}); it will not be started.")
        my_run = None  # type: ignore

    specs: list[ServiceSpec] = [
        ServiceSpec(name="example", target=example_run),
        ServiceSpec(name="battery", target=battery_run),
    ]
    if my_run is not None:
        specs.append(ServiceSpec(name="my_service", target=my_run))
    return specs


def main() -> None:
    """
    Combined entry point: runs all available services on dedicated threads.
    Continues running remaining services if any one crashes.
    Graceful shutdown on Ctrl+C or SIGTERM with 10s timeout.
    """
    # Ensure logging is initialized before any thread output
    setup_logging()
    mgr = ServiceManager(services=_collect_default_services(), shutdown_timeout=10.0)
    mgr.run()


if __name__ == "__main__":
    main()