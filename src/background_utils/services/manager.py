from __future__ import annotations

import os
import signal
import subprocess
import threading
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from types import FrameType

# Lazy import notes:
# PIL and pystray can fail to import in headless or non-GUI environments.
# We import them lazily within tray-specific functions to allow ServiceManager
# to be imported/used without GUI dependencies.
# Types are hinted via `type: ignore` or string annotations where needed.
from background_utils.logging import logger, setup_logging

ServiceFunc = Callable[[threading.Event], None]


@dataclass
class ServiceSpec:
    name: str
    target: ServiceFunc


class ServiceManager:
    def __init__(self, services: Iterable[ServiceSpec], shutdown_timeout: float = 10.0) -> None:
        self.services: list[ServiceSpec] = list(services)
        self.shutdown_timeout = shutdown_timeout
        self.stop_event = threading.Event()
        self.threads: list[threading.Thread] = []
        self._stopped_once = threading.Event()

    def _signal_handler(self, signum: int, frame: FrameType | None) -> None:
        logger.info(f"Received signal {signum}. Initiating shutdown...")
        self.stop()

    def _install_signal_handlers(self) -> None:
        """
        Install signal handlers only if running in the main thread of the main interpreter.
        On Windows and when called from background threads (e.g., tray), signal.signal will fail.
        """
        try:
            if threading.current_thread() is threading.main_thread():
                signal.signal(signal.SIGINT, self._signal_handler)
                signal.signal(signal.SIGTERM, self._signal_handler)
                logger.debug("Signal handlers installed")
            else:
                logger.debug("Skipping signal handlers (not in main thread)")
        except Exception as exc:  # noqa: BLE001
            logger.debug(f"Skipping signal handlers due to: {exc!r}")

    def start(self) -> None:
        setup_logging()
        # Ensure a fresh stop_event for each start/restart
        if self.stop_event.is_set():
            self.stop_event.clear()
        self._stopped_once.clear()
        # Make it obvious which manager is running and which services are included
        svc_names = ", ".join(spec.name for spec in self.services) or "<none>"
        logger.info(f"Service Manager starting {len(self.services)} services: {svc_names}")

        # Install signal handlers (safe)
        self._install_signal_handlers()

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
        finally:
            logger.info(f"[{spec.name}] wrapper exiting")

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
        # Idempotent stop; log only first transition
        first = False
        if not self.stop_event.is_set():
            self.stop_event.set()
            first = True
        if first:
            logger.info("Stopping services...")
            logger.info(
                f"Stop event set. Active threads: {[t.name for t in self.threads if t.is_alive()]}"
            )
        else:
            logger.debug("Stop requested (already stopping)")

        # If threads list is empty, nothing to join – still mark stopped
        if not self.threads:
            logger.info("No threads to stop")
            self._stopped_once.set()
            return

        # Join all threads with timeout
        logger.info(f"Joining {len(self.threads)} threads with {self.shutdown_timeout}s timeout...")
        deadline = time.time() + self.shutdown_timeout
        for i, t in enumerate(self.threads):
            remaining = max(0.0, deadline - time.time())
            if remaining == 0.0:
                logger.warning(
                            "Timeout reached, skipping remaining threads"
                        )
                break
            logger.info(
                f"Joining thread {i+1}/{len(self.threads)}: {t.name} (timeout: {remaining:.1f}s)"
            )
            t.join(timeout=remaining)
            if t.is_alive():
                logger.warning(f"Thread {t.name} still alive after join")
            else:
                logger.info(f"Thread {t.name} stopped successfully")

        # Report any threads still alive
        alive = [t.name for t in self.threads if t.is_alive()]
        if alive:
            logger.warning(f"Some services did not stop in time: {alive}")
        else:
            logger.info("All services stopped cleanly.")
        # Flag we completed a stop attempt (success or timeout)
        self._stopped_once.set()
        logger.info("ServiceManager.stop() completed")

    def run(self) -> None:
        self.start()
        self.wait()
        self.stop()


# -------------------- Tray Controller --------------------
# Rewritten to use pystray exclusively. Removes all native win32 tray code.

def _create_tray_image() -> object:
    from PIL import Image, ImageDraw
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((8, 8, size - 8, size - 8), fill=(30, 144, 255, 255))
    return img


class TrayController:
    def __init__(
        self, 
        manager_factory: Callable[[], ServiceManager], 
        log_path_provider: Callable[[], str]
    ) -> None:
        self._image = _create_tray_image()
        self._manager_factory = manager_factory
        self._manager: ServiceManager | None = None
        self._log_path_provider = log_path_provider
        self._lock = threading.Lock()
        self._exiting = False
        self._icon = None  # pystray.Icon

    def _ensure_manager(self) -> None:
        with self._lock:
            if self._manager is None:
                self._manager = self._manager_factory()

    # Menu actions - non-blocking to keep tray responsive
    def _view_log(self, icon, item) -> None:
        logger.info("MENU: View Log clicked")
        path = self._log_path_provider()
        logger.info(f"Opening log: {path}")
        try:
            subprocess.Popen(["notepad.exe", path], shell=False)
        except Exception as exc:
            logger.warning(f"Failed to open log in Notepad: {exc!r}")

    def _stop_services(self, icon, item) -> None:
        logger.info("MENU: Stop Services clicked")
        
        def _do_stop():
            logger.info("THREAD: _do_stop thread started")
            try:
                logger.info("THREAD: Acquiring lock...")
                with self._lock:
                    logger.info("THREAD: Lock acquired")
                    if self._exiting:
                        logger.debug("Stop Services ignored: exiting in progress")
                        return
                    logger.info("THREAD: Getting existing manager reference...")
                    mgr = self._manager  # Don't call _ensure_manager, just use existing
                    logger.info(f"THREAD: Manager reference obtained: {mgr is not None}")
                logger.info("THREAD: Lock released")
                if mgr:
                    logger.info("Tray requested: Stop Services (background)")
                    logger.info(
                        f"Manager has {len(mgr.threads)} threads, "
                        f"stop_event.is_set()={mgr.stop_event.is_set()}"
                    )
                    mgr.stop()
                    logger.info("Stop Services completed")
                else:
                    logger.warning("No manager available to stop")
            except Exception as exc:
                logger.exception(f"Error in _do_stop thread: {exc}")
            finally:
                logger.info("THREAD: _do_stop thread exiting")
        
        # Run in background to avoid blocking pystray event loop
        logger.info("Creating stop thread...")
        t = threading.Thread(target=_do_stop, name="tray-stop", daemon=True)
        logger.info("Starting stop thread...")
        t.start()
        logger.info("Stop thread started")

    def _restart_services(self, icon, item) -> None:
        logger.info("MENU: Restart Services clicked")
        
        def _do_restart():
            logger.info("THREAD: _do_restart thread started")
            try:
                with self._lock:
                    if self._exiting:
                        logger.debug("Restart ignored: exiting in progress")
                        return
                    logger.info("Tray requested: Restart Services (background)")
                    mgr = self._manager  # Don't call _ensure_manager, just use existing
                if mgr:
                    logger.info("Stopping services for restart...")
                    logger.info(
                        f"Manager has {len(mgr.threads)} threads, "
                        f"stop_event.is_set()={mgr.stop_event.is_set()}"
                    )
                    mgr.stop()
                    # Wait for stop to complete
                    try:
                        logger.info("Waiting for stop to complete...")
                        mgr._stopped_once.wait(timeout=5.0)  # type: ignore[attr-defined]
                        logger.info("Stop completed, creating new manager...")
                    except Exception as exc:
                        logger.warning(f"Error waiting for stop: {exc!r}")
                    time.sleep(0.5)
                    with self._lock:
                        self._manager = self._manager_factory()
                        new_mgr = self._manager
                    if new_mgr:
                        logger.info("Starting new service manager...")
                        threading.Thread(
                            target=new_mgr.run, 
                            name="svc-restart", 
                            daemon=False
                        ).start()
                        logger.info("Restart Services completed")
                else:
                    logger.warning("No manager available to restart")
            except Exception as exc:
                logger.exception(f"Error in _do_restart thread: {exc}")
            finally:
                logger.info("THREAD: _do_restart thread exiting")
        
        # Run in background to avoid blocking pystray event loop
        logger.info("Creating restart thread...")
        t = threading.Thread(target=_do_restart, name="tray-restart", daemon=True)
        logger.info("Starting restart thread...")
        t.start()
        logger.info("Restart thread started")

    def _exit_tray(self, icon, item) -> None:
        logger.info("MENU: Exit clicked")
        
        def _do_exit():
            with self._lock:
                self._exiting = True
                mgr = self._manager  # Don't call _ensure_manager, just use existing
            logger.info("Exiting tray (background)")
            # Stop services
            try:
                if mgr:
                    logger.info("Stopping services during exit...")
                    mgr.stop()
            except Exception as exc:
                logger.warning(f"Error stopping services: {exc!r}")
            # Stop tray
            try:
                if self._icon is not None:
                    self._icon.stop()
            except Exception as exc:
                logger.debug(f"Issue stopping tray icon: {exc!r}")
            finally:
                os._exit(0)
        
        # Run in background to avoid blocking pystray event loop
        threading.Thread(target=_do_exit, name="tray-exit", daemon=True).start()

    def _create_pystray(self) -> bool:
        try:
            # Force Windows backend when available to avoid backend mismatch on Win11
            from pystray import Icon, Menu, MenuItem
            try:
                # Hint import so pystray selects _win32 backend
                import pystray._win32  # type: ignore  # noqa: F401
            except Exception:
                pass
        except Exception as exc:
            logger.warning(f"pystray is unavailable: {exc!r}")
            return False

        # Build menu factory so we can rebuild it if needed
        def build_menu() -> object:
            return Menu(
                MenuItem("View Log", self._view_log),
                MenuItem("Stop Services", self._stop_services),
                MenuItem("Restart Services", self._restart_services),
                MenuItem("Exit", self._exit_tray),
            )

        try:
            icon = Icon("background-utils", self._image, "Background Utils", menu=build_menu())
            # Keep reference and builder for future updates
            self._icon = icon
            self._build_menu = build_menu
        except Exception as exc:
            logger.warning(f"Failed to construct pystray icon: {exc!r}")
            self._icon = None
            return False
        logger.info("Tray icon (pystray) constructed")
        return True

    def run(self) -> None:
        # Start services initially
        self._ensure_manager()
        if self._manager:
            threading.Thread(target=self._manager.run, name="svc-run", daemon=False).start()

        # Create pystray icon
        if not self._create_pystray():
            logger.warning("Tray could not be initialized; running without tray.")
            try:
                while True:
                    time.sleep(1.0)
            except KeyboardInterrupt:
                if self._manager:
                    self._manager.stop()
            return

        # Run the pystray loop in this thread (blocking until Exit)
        icon = self._icon
        if icon is None:
            logger.warning("Tray icon unexpectedly None; running without tray loop.")
            try:
                while True:
                    time.sleep(1.0)
            except KeyboardInterrupt:
                if self._manager:
                    self._manager.stop()
            return

        # Use blocking run() instead of run_detached() to ensure menu callbacks work
        def setup(_icon) -> None:
            try:
                logger.info("Tray setup callback called")
                _icon.visible = True
                logger.info("Tray icon made visible")
            except Exception as exc:
                logger.warning(f"Error in tray setup: {exc!r}")

        # Run in a separate thread so main thread can handle KeyboardInterrupt
        tray_thread = threading.Thread(
            target=lambda: icon.run(setup=setup),
            name="tray-main",
            daemon=True
        )
        tray_thread.start()
        
        # Give tray time to initialize
        time.sleep(1.0)
        logger.info("Tray thread started, entering main loop")

        # Keep process alive while services run; allow Ctrl+C to break
        try:
            while not self._exiting:
                time.sleep(0.5)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received in main thread")
            # Stop services synchronously
            self._ensure_manager()
            mgr = self._manager
            if mgr:
                logger.info("Stopping services from KeyboardInterrupt")
                mgr.stop()
            # Exit
            self._exiting = True
            try:
                if self._icon:
                    self._icon.stop()
            except Exception:
                pass
            os._exit(0)



def _windows_log_path() -> str:
    localappdata = os.getenv("LOCALAPPDATA") or "."
    return os.path.join(localappdata, "background-utils", "background-utils.log")


def _collect_default_services() -> list[ServiceSpec]:
    # Local imports to avoid import-time side effects
    from background_utils.services.battery_monitor import run as battery_run
    from background_utils.services.example_service import run as example_run
    from background_utils.services.gmail_notifier import run as gmail_run
    try:
        from background_utils.services.my_service import (
            run as my_run,
        )
    except Exception as exc:
        logger.warning(f"my_service not available ({exc}); it will not be started.")
        my_run = None

    specs: list[ServiceSpec] = [
        ServiceSpec(name="example", target=example_run),
        ServiceSpec(name="battery", target=battery_run),
        ServiceSpec(name="gmail", target=gmail_run),
    ]
    if my_run is not None:
        specs.append(ServiceSpec(name="my_service", target=my_run))
    return specs


def main() -> None:
    """
    Combined entry point with Windows tray icon.
    Tray menu:
      - View Log: opens %LOCALAPPDATA%\\background-utils\\background-utils.log
      - Stop Services: graceful shutdown of threads
      - Restart Services: stop and start again
      - Exit: close tray (also stops services)
    """
    setup_logging()

    def manager_factory() -> ServiceManager:
        return ServiceManager(services=_collect_default_services(), shutdown_timeout=10.0)

    # If running without a console or when user just wants background tray, run tray.
    # The tray runs in the main thread; service manager runs in a worker thread and will
    # skip installing signal handlers there, preventing ValueError.
    tray = TrayController(manager_factory=manager_factory, log_path_provider=_windows_log_path)
    tray.run()


if __name__ == "__main__":
    main()