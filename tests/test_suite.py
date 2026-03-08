from __future__ import annotations

import importlib
import os
import threading
import time
from types import SimpleNamespace
from typing import Any

import pytest
from typer.testing import CliRunner

# Modules under test
import background_utils.config as cfg
import background_utils.logging as blog
import background_utils.services.battery_monitor as battery_monitor
import background_utils.services.example_service as example_service
import background_utils.services.my_service as my_service

# CLI imports
from background_utils.cli.app import app as cli_app
from background_utils.services.manager import ServiceManager, ServiceSpec, TrayController

# ---------------------------
# Helpers / Fixtures
# ---------------------------


@pytest.fixture(autouse=True)
def isolate_env(monkeypatch: pytest.MonkeyPatch) -> None:
    # Ensure predictable environment for pydantic-settings
    monkeypatch.delenv("BGU_LOG_LEVEL", raising=False)
    monkeypatch.delenv("BGU_SERVICE_INTERVAL_SECONDS", raising=False)
    monkeypatch.delenv("BGU_ENVIRONMENT", raising=False)
    monkeypatch.setenv("PYTHONIOENCODING", "utf-8")
    monkeypatch.setenv("PYTHONUTF8", "1")


@pytest.fixture
def runner() -> CliRunner:
    # Typer's CliRunner does not support mix_stderr kw in current versions
    return CliRunner()


class DummyStopper:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def __call__(self, stop_event: threading.Event) -> None:
        # Immediately stop to be fast
        self.calls.append("run")
        stop_event.set()


# ---------------------------
# config.py tests
# ---------------------------


def test_settings_defaults() -> None:
    s = cfg.load_settings()
    assert s.log_level == "INFO"
    assert s.environment == "development"
    assert s.service_interval_seconds == pytest.approx(5.0)


def test_settings_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BGU_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("BGU_ENVIRONMENT", "production")
    monkeypatch.setenv("BGU_SERVICE_INTERVAL_SECONDS", "2.5")
    s = cfg.load_settings()
    assert s.log_level == "DEBUG"
    assert s.environment == "production"
    assert s.service_interval_seconds == pytest.approx(2.5)


# ---------------------------
# logging.py tests
# ---------------------------


def test_setup_logging_idempotent(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    # Force LOCALAPPDATA to tmp path for deterministic file location on Windows/non-Windows
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    # Reset module globals
    import importlib as _il

    _il.reload(blog)
    # First call
    blog.setup_logging(level="INFO")
    # Second call should be no-op (no exceptions)
    blog.setup_logging(level="DEBUG")


def test_windows_log_dir_created(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    import importlib as _il

    _il.reload(blog)
    blog.setup_logging(level="INFO")
    # Ensure log file exists
    log_dir = tmp_path / "background-utils"
    log_file = log_dir / "background-utils.log"
    assert log_dir.exists()
    assert log_file.exists()


# ---------------------------
# CLI tests
# ---------------------------


def test_cli_root_help(runner: CliRunner) -> None:
    result = runner.invoke(cli_app, ["--help"])
    assert result.exit_code == 0
    assert "Background Utilities CLI" in result.stdout


def test_cli_verbose_flag(runner: CliRunner) -> None:
    # Simply ensure it runs and returns 0
    result = runner.invoke(cli_app, ["-v", "--help"])
    assert result.exit_code == 0


def test_example_command_hello(runner: CliRunner) -> None:
    result = runner.invoke(cli_app, ["example", "hello", "--name", "Tester", "--excited"])
    assert result.exit_code == 0
    assert "Hello, Tester!" in result.stdout


def test_example_command_time(runner: CliRunner) -> None:
    result = runner.invoke(cli_app, ["example", "time"])
    assert result.exit_code == 0
    assert "Current Time" in result.stdout


def test_wifi_commands_mocked(monkeypatch: pytest.MonkeyPatch, runner: CliRunner) -> None:
    # Avoid calling Windows netsh; monkeypatch private helpers
    import background_utils.cli.commands.wifi as wifi

    # Mock the Windows check
    monkeypatch.setattr("os.name", "nt")

    # Create simple mock profile with expected structure
    def mock_gather_profiles() -> tuple[list[wifi.WifiProfile], int]:
        return [wifi.WifiProfile(name="SSID1", password="pass")], 0

    def mock_list_networks() -> list[dict[str, str]]:
        return [
            {
                "ssid": "SSID2",
                "type": "Infrastructure",
                "authentication": "WPA2",
                "encryption": "CCMP",
            }
        ]

    monkeypatch.setattr(wifi, "_gather_profiles", mock_gather_profiles)
    monkeypatch.setattr(wifi, "_list_networks", mock_list_networks)

    res1 = runner.invoke(cli_app, ["wifi", "show-passwords", "--output", "json"])
    if res1.exit_code != 0:
        print(f"Error output: {res1.stdout}\nStderr: {getattr(res1, 'stderr', 'N/A')}")
    assert res1.exit_code == 0
    assert "SSID1" in res1.stdout
    assert "pass" in res1.stdout

    res2 = runner.invoke(cli_app, ["wifi", "list-networks", "--output", "json"])
    if res2.exit_code != 0:
        print(f"Error output: {res2.stdout}\nStderr: {getattr(res2, 'stderr', 'N/A')}")
    assert res2.exit_code == 0
    assert "SSID2" in res2.stdout


def test_wifi_service_error_handling(monkeypatch: pytest.MonkeyPatch, runner: CliRunner) -> None:
    """Test that Windows service errors are handled gracefully."""
    import background_utils.cli.commands.wifi as wifi

    # Mock the Windows check
    monkeypatch.setattr("os.name", "nt")

    # Mock _run to simulate service not running error
    def mock_run_service_error(cmd: list[str]) -> tuple[int, str, str]:
        return 1, "", "The Wireless AutoConfig Service (wlansvc) is not running."

    monkeypatch.setattr(wifi, "_run", mock_run_service_error)

    # Test show-passwords with service error
    res1 = runner.invoke(cli_app, ["wifi", "show-passwords"])
    assert res1.exit_code == 1
    assert "Wi-Fi Service Issue" in res1.stdout
    assert "net start wlansvc" in res1.stdout

    # Test list-networks with service error
    res2 = runner.invoke(cli_app, ["wifi", "list-networks"])
    assert res2.exit_code == 1
    assert "Wi-Fi Service Issue" in res2.stdout
    assert "net start wlansvc" in res2.stdout


# ---------------------------
# Services tests (cooperative loops)
# ---------------------------


def test_example_service_runs_and_stops_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    # Respect pydantic constraint ge=0.1
    monkeypatch.setenv("BGU_SERVICE_INTERVAL_SECONDS", "0.1")
    stop = threading.Event()

    # Run briefly in thread
    t = threading.Thread(target=example_service.run, args=(stop,), daemon=True)
    t.start()

    try:
        # Let it tick once
        time.sleep(0.12)
        stop.set()
        t.join(timeout=1.0)
        assert not t.is_alive()
    finally:
        # Ensure cleanup
        stop.set()
        if t.is_alive():
            t.join(timeout=0.5)


def test_my_service_runs_and_stops_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BGU_SERVICE_INTERVAL_SECONDS", "0.1")
    stop = threading.Event()

    t = threading.Thread(target=my_service.run, args=(stop,), daemon=True)
    t.start()

    try:
        time.sleep(0.12)
        stop.set()
        t.join(timeout=1.0)
        assert not t.is_alive()
    finally:
        # Ensure cleanup
        stop.set()
        if t.is_alive():
            t.join(timeout=0.5)


def test_battery_monitor_mocked_psutil(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeBattery:
        def __init__(self, percent: int, power_plugged: bool) -> None:
            self.percent = percent
            self.power_plugged = power_plugged

    fake_psutil = SimpleNamespace(
        sensors_battery=lambda: FakeBattery(percent=10, power_plugged=False)
    )
    monkeypatch.setitem(importlib.import_module("sys").modules, "psutil", fake_psutil)

    stop = threading.Event()
    t = threading.Thread(target=battery_monitor.run, args=(stop, 0.05), daemon=True)
    t.start()

    try:
        time.sleep(0.06)
        stop.set()
        t.join(timeout=1.0)
        assert not t.is_alive()
    finally:
        # Ensure cleanup
        stop.set()
        if t.is_alive():
            t.join(timeout=0.5)


# ---------------------------
# ServiceManager tests
# ---------------------------


def test_service_manager_start_and_stop() -> None:
    def target(e: threading.Event) -> None:
        # block until stop requested; returns None
        e.wait()

    svc = ServiceSpec(name="dummy", target=target)
    mgr = ServiceManager(services=[svc], shutdown_timeout=0.5)

    try:
        mgr.start()
        # Ensure thread started
        time.sleep(0.05)
        assert any(t.is_alive() for t in mgr.threads)
    finally:
        mgr.stop()
        # Give threads time to stop
        time.sleep(0.1)
        # Force join any remaining threads
        for t in mgr.threads:
            if t.is_alive():
                t.join(timeout=0.5)

    # After stop, threads should not be alive
    assert all(not t.is_alive() for t in mgr.threads)


def test_service_manager_thread_timeout_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    # Create a target that ignores stop_event so join timeout logic triggers warnings
    def stubborn(_e: threading.Event) -> None:
        time.sleep(1.5)  # longer than shutdown_timeout used below

    mgr = ServiceManager(services=[ServiceSpec("stubborn", stubborn)], shutdown_timeout=0.2)
    try:
        mgr.start()
        time.sleep(0.05)
        # Request stop which will try to join with short timeout
        mgr.stop()
    finally:
        # Hard cleanup best-effort (thread may still be alive briefly)
        for t in mgr.threads:
            t.join(timeout=1.0)


# ---------------------------
# TrayController tests (headless-friendly)
# ---------------------------


def test_tray_controller_initialization() -> None:
    """Test TrayController can be initialized without hanging."""

    # Simple initialization test without running the tray
    def manager_factory() -> ServiceManager:
        return ServiceManager([], shutdown_timeout=0.1)

    def log_path_provider() -> str:
        return os.path.join(".", "background-utils.log")

    # Just test initialization - don't run the tray
    tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

    # Verify it was created successfully
    assert tray is not None
    assert tray._manager_factory is not None
    assert tray._log_path_provider is not None


# ---------------------------
# Import smoke tests
# ---------------------------


def test_cli_entry_importable() -> None:
    mod = importlib.import_module("background_utils.cli.app")
    assert hasattr(mod, "app")


def test_service_entry_importable() -> None:
    mod = importlib.import_module("background_utils.services.example_service")
    assert hasattr(mod, "main")


# ---------------------------
# Battery monitor - additional coverage
# ---------------------------


def test_battery_monitor_plugged_in(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cover the 'power plugged in' path (line 22)."""

    class FakeBattery:
        percent = 85
        power_plugged = True

    monkeypatch.setattr(
        "background_utils.services.battery_monitor.psutil",
        SimpleNamespace(sensors_battery=lambda: FakeBattery()),
    )
    stop = threading.Event()
    t = threading.Thread(target=battery_monitor.run, args=(stop, 0.05), daemon=True)
    t.start()
    time.sleep(0.08)
    stop.set()
    t.join(timeout=1.0)
    assert not t.is_alive()


def test_battery_monitor_no_battery(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cover the 'battery is None' path (line 32)."""
    monkeypatch.setattr(
        "background_utils.services.battery_monitor.psutil",
        SimpleNamespace(sensors_battery=lambda: None),
    )
    stop = threading.Event()
    t = threading.Thread(target=battery_monitor.run, args=(stop, 0.05), daemon=True)
    t.start()
    time.sleep(0.08)
    stop.set()
    t.join(timeout=1.0)
    assert not t.is_alive()


def test_battery_monitor_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cover the exception handler (lines 33-34)."""

    def exploding_battery() -> None:
        raise RuntimeError("sensor failure")

    monkeypatch.setattr(
        "background_utils.services.battery_monitor.psutil",
        SimpleNamespace(sensors_battery=exploding_battery),
    )
    stop = threading.Event()
    t = threading.Thread(target=battery_monitor.run, args=(stop, 0.05), daemon=True)
    t.start()
    time.sleep(0.08)
    stop.set()
    t.join(timeout=1.0)
    assert not t.is_alive()


def test_battery_monitor_low_battery(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cover the low battery warning path (lines 25-30)."""

    class FakeBattery:
        percent = 10
        power_plugged = False

    monkeypatch.setattr(
        "background_utils.services.battery_monitor.psutil",
        SimpleNamespace(sensors_battery=lambda: FakeBattery()),
    )
    stop = threading.Event()
    t = threading.Thread(target=battery_monitor.run, args=(stop, 0.05), daemon=True)
    t.start()
    time.sleep(0.08)
    stop.set()
    t.join(timeout=1.0)
    assert not t.is_alive()


def test_battery_monitor_main(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cover battery_monitor.main() (lines 46-50)."""
    # Make run() exit immediately by pre-setting stop and patching
    calls = []

    def fake_run(stop_event: threading.Event, interval_seconds: float = 60.0) -> None:
        calls.append("run")

    monkeypatch.setattr(battery_monitor, "run", fake_run)
    battery_monitor.main()
    assert "run" in calls


# ---------------------------
# Example service - exception handler
# ---------------------------


def test_example_service_exception_handler(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cover the exception handler (lines 31-33) in example_service.run()."""
    monkeypatch.setenv("BGU_SERVICE_INTERVAL_SECONDS", "0.1")

    # Patch time.sleep inside the module to raise after first tick
    call_count = 0
    original_sleep = time.sleep

    def exploding_sleep(secs: float) -> None:
        nonlocal call_count
        call_count += 1
        if call_count >= 2:
            raise RuntimeError("boom")
        original_sleep(secs)

    monkeypatch.setattr("background_utils.services.example_service.time.sleep", exploding_sleep)

    stop = threading.Event()
    t = threading.Thread(target=example_service.run, args=(stop,), daemon=True)
    t.start()
    t.join(timeout=3.0)
    assert not t.is_alive()
    stop.set()


def test_example_service_main(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cover example_service.main() (lines 42-48)."""
    calls = []

    def fake_run(stop_event: threading.Event) -> None:
        calls.append("run")

    monkeypatch.setattr(example_service, "run", fake_run)
    example_service.main()
    assert "run" in calls


# ---------------------------
# My service - exception handler
# ---------------------------


def test_my_service_exception_handler(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cover the exception handler (lines 29-31) in my_service.run()."""
    monkeypatch.setenv("BGU_SERVICE_INTERVAL_SECONDS", "1.0")

    call_count = 0
    original_sleep = time.sleep

    def exploding_sleep(secs: float) -> None:
        nonlocal call_count
        call_count += 1
        if call_count >= 2:
            raise RuntimeError("boom")
        original_sleep(min(secs, 0.05))

    monkeypatch.setattr("background_utils.services.my_service.time.sleep", exploding_sleep)

    stop = threading.Event()
    t = threading.Thread(target=my_service.run, args=(stop,), daemon=True)
    t.start()
    t.join(timeout=3.0)
    assert not t.is_alive()
    stop.set()


def test_my_service_main(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cover my_service.main() (lines 41-45)."""
    calls = []

    def fake_run(stop_event: threading.Event) -> None:
        calls.append("run")

    monkeypatch.setattr(my_service, "run", fake_run)
    my_service.main()
    assert "run" in calls


# ---------------------------
# ServiceManager - additional coverage
# ---------------------------


def test_service_manager_service_crash() -> None:
    """Cover the crash logging path (lines 90-92) in _run_service_wrapper."""

    def crashing_service(stop_event: threading.Event) -> None:
        raise RuntimeError("service exploded")

    svc = ServiceSpec(name="crasher", target=crashing_service)
    mgr = ServiceManager(services=[svc], shutdown_timeout=1.0)
    mgr.start()
    time.sleep(0.2)
    mgr.stop()
    # Thread should have exited despite crash
    assert all(not t.is_alive() for t in mgr.threads)


def test_service_manager_restart_clears_stop_event() -> None:
    """Cover stop_event.clear() on restart (line 63)."""

    def dummy(e: threading.Event) -> None:
        e.wait()

    mgr = ServiceManager(services=[ServiceSpec("d", dummy)], shutdown_timeout=0.5)
    mgr.start()
    time.sleep(0.05)
    mgr.stop()
    assert mgr.stop_event.is_set()
    # Restart — start() should clear the stop_event
    mgr.threads.clear()
    mgr.start()
    assert not mgr.stop_event.is_set()
    time.sleep(0.05)
    mgr.stop()
    for t in mgr.threads:
        t.join(timeout=1.0)


def test_service_manager_stop_no_threads() -> None:
    """Cover the 'no threads to stop' path (lines 121-124)."""
    mgr = ServiceManager(services=[], shutdown_timeout=0.5)
    mgr.stop()
    assert mgr._stopped_once.is_set()


def test_service_manager_stop_idempotent() -> None:
    """Cover repeated stop (line 118)."""

    def dummy(e: threading.Event) -> None:
        e.wait()

    mgr = ServiceManager(services=[ServiceSpec("d", dummy)], shutdown_timeout=0.5)
    mgr.start()
    time.sleep(0.05)
    mgr.stop()
    # Second stop should be a no-op
    mgr.stop()
    for t in mgr.threads:
        t.join(timeout=1.0)


def test_service_manager_signal_handler(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cover signal handler (lines 41-42)."""

    def dummy(e: threading.Event) -> None:
        e.wait()

    mgr = ServiceManager(services=[ServiceSpec("d", dummy)], shutdown_timeout=0.5)
    mgr.start()
    time.sleep(0.05)
    # Simulate signal
    mgr._signal_handler(2, None)
    assert mgr.stop_event.is_set()
    for t in mgr.threads:
        t.join(timeout=1.0)


# ---------------------------
# Manager helpers
# ---------------------------


def test_windows_log_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cover _windows_log_path (lines 394-395)."""
    from background_utils.services.manager import _windows_log_path

    monkeypatch.setenv("LOCALAPPDATA", "C:\\Users\\test\\AppData\\Local")
    result = _windows_log_path()
    assert "background-utils" in result
    assert "background-utils.log" in result


def test_windows_log_path_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cover _windows_log_path fallback when LOCALAPPDATA is not set."""
    from background_utils.services.manager import _windows_log_path

    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    result = _windows_log_path()
    assert "background-utils.log" in result


def test_collect_default_services() -> None:
    """Cover _collect_default_services (lines 400-419)."""
    from background_utils.services.manager import _collect_default_services

    services = _collect_default_services()
    names = [s.name for s in services]
    assert "example" in names
    assert "battery" in names
    assert "gmail" in names
    assert "my_service" in names


def test_collect_default_services_missing_my_service(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cover the ImportError path for my_service (lines 409-410)."""
    import background_utils.services.manager as manager_mod

    # Make my_service unimportable
    original_import = __builtins__.__import__ if hasattr(__builtins__, "__import__") else __import__

    def failing_import(name, *args, **kwargs):
        if "my_service" in name:
            raise ImportError("simulated missing")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", failing_import)

    services = manager_mod._collect_default_services()
    names = [s.name for s in services]
    assert "my_service" not in names
    assert "example" in names


# ---------------------------
# TrayController - additional coverage
# ---------------------------


class TestTrayControllerActions:
    """Test TrayController menu actions (headless, no pystray)."""

    def _make_tray(self) -> TrayController:
        def _wait_svc(e: threading.Event) -> None:
            e.wait()

        def factory() -> ServiceManager:
            return ServiceManager([ServiceSpec("d", _wait_svc)], shutdown_timeout=0.5)

        return TrayController(
            manager_factory=factory,
            log_path_provider=lambda: "test.log",
        )

    def test_view_log_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Cover _view_log (lines 191-198)."""
        tray = self._make_tray()
        opened = []
        monkeypatch.setattr(
            "background_utils.services.manager.subprocess.Popen",
            lambda cmd, **kw: opened.append(cmd),
        )
        tray._view_log(None, None)
        assert len(opened) == 1
        assert "notepad.exe" in opened[0]

    def test_view_log_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Cover _view_log exception path (lines 197-198)."""
        tray = self._make_tray()
        monkeypatch.setattr(
            "background_utils.services.manager.subprocess.Popen",
            lambda cmd, **kw: (_ for _ in ()).throw(OSError("notepad missing")),
        )
        # Should not raise
        tray._view_log(None, None)

    def test_stop_services(self) -> None:
        """Cover _stop_services (lines 200-224)."""
        tray = self._make_tray()
        tray._ensure_manager()
        assert tray._manager is not None
        tray._manager.start()
        time.sleep(0.05)
        tray._stop_services(None, None)
        time.sleep(0.8)  # Wait for background thread
        assert tray._manager.stop_event.is_set()
        for t in tray._manager.threads:
            t.join(timeout=1.0)

    def test_stop_services_no_manager(self) -> None:
        """Cover _stop_services when manager is None (line 219)."""
        tray = self._make_tray()
        # Don't call _ensure_manager — manager is None
        tray._stop_services(None, None)
        time.sleep(0.3)  # Let background thread run

    def test_stop_services_exiting(self) -> None:
        """Cover _stop_services when _exiting is True (lines 207-209)."""
        tray = self._make_tray()
        tray._exiting = True
        tray._stop_services(None, None)
        time.sleep(0.3)

    def test_restart_services(self) -> None:
        """Cover _restart_services (lines 226-263)."""
        tray = self._make_tray()
        tray._ensure_manager()
        assert tray._manager is not None
        tray._manager.start()
        time.sleep(0.05)
        tray._restart_services(None, None)
        time.sleep(2.0)  # Wait for stop + restart
        # New manager should exist
        assert tray._manager is not None
        tray._manager.stop()
        for t in tray._manager.threads:
            t.join(timeout=1.0)

    def test_restart_services_no_manager(self) -> None:
        """Cover _restart_services when no manager (line 258)."""
        tray = self._make_tray()
        tray._restart_services(None, None)
        time.sleep(0.5)

    def test_restart_services_exiting(self) -> None:
        """Cover _restart_services when _exiting (lines 233-235)."""
        tray = self._make_tray()
        tray._exiting = True
        tray._restart_services(None, None)
        time.sleep(0.3)

    def test_exit_tray(self) -> None:
        """Cover _exit_tray (lines 265-289)."""
        tray = self._make_tray()
        tray._ensure_manager()
        assert tray._manager is not None
        tray._manager.start()
        time.sleep(0.05)

        # Mock icon stop
        class FakeIcon:
            stopped = False

            def stop(self):
                self.stopped = True

        tray._icon = FakeIcon()
        tray._exit_tray(None, None)
        time.sleep(1.0)
        assert tray._exiting
        assert tray._icon.stopped
        for t in tray._manager.threads:
            t.join(timeout=1.0)

    def test_exit_tray_no_manager(self) -> None:
        """Cover _exit_tray when no manager (branch at line 275)."""
        tray = self._make_tray()
        tray._exit_tray(None, None)
        time.sleep(0.5)
        assert tray._exiting


class TestTrayControllerRun:
    """Test TrayController.run() paths."""

    def test_run_no_pystray_keyboard_interrupt(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Cover run() when pystray fails (lines 333-341)."""

        def _wait_svc(e: threading.Event) -> None:
            e.wait()

        def factory() -> ServiceManager:
            return ServiceManager([ServiceSpec("d", _wait_svc)], shutdown_timeout=0.5)

        tray = TrayController(manager_factory=factory, log_path_provider=lambda: "test.log")

        # Make _create_pystray always fail
        monkeypatch.setattr(tray, "_create_pystray", lambda: False)

        # Make time.sleep raise KeyboardInterrupt on first call in the fallback loop
        call_count = 0
        original_sleep = time.sleep

        def interrupt_sleep(secs: float) -> None:
            nonlocal call_count
            call_count += 1
            # Let initial sleeps pass (service startup), then interrupt the fallback loop
            if call_count > 3:
                raise KeyboardInterrupt()
            original_sleep(min(secs, 0.05))

        monkeypatch.setattr("background_utils.services.manager.time.sleep", interrupt_sleep)

        # run() should return after KeyboardInterrupt
        tray.run()
        assert tray._manager is not None
        # Clean up
        tray._manager.stop()
        for t in tray._manager.threads:
            t.join(timeout=1.0)

    def test_run_with_pystray_then_exit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Cover run() with mock pystray (lines 343-390)."""

        def _wait_svc(e: threading.Event) -> None:
            e.wait()

        def factory() -> ServiceManager:
            return ServiceManager([ServiceSpec("d", _wait_svc)], shutdown_timeout=0.5)

        tray = TrayController(manager_factory=factory, log_path_provider=lambda: "test.log")

        # Mock _create_pystray to succeed
        class FakeIcon:
            visible = False

            def run(self, setup=None):
                if setup:
                    setup(self)
                # Simulate the tray event loop for a bit
                time.sleep(0.2)

            def stop(self):
                pass

        def fake_create_pystray() -> bool:
            tray._icon = FakeIcon()
            return True

        monkeypatch.setattr(tray, "_create_pystray", fake_create_pystray)

        # Set _exiting after a brief delay so the main loop exits
        def delayed_exit() -> None:
            time.sleep(0.5)
            tray._exiting = True

        threading.Thread(target=delayed_exit, daemon=True).start()

        # Patch time.sleep to be faster
        original_sleep = time.sleep

        def fast_sleep(secs: float) -> None:
            original_sleep(min(secs, 0.1))

        monkeypatch.setattr("background_utils.services.manager.time.sleep", fast_sleep)

        tray.run()
        assert tray._exiting
        # Clean up
        if tray._manager:
            tray._manager.stop()
            for t in tray._manager.threads:
                t.join(timeout=1.0)

    def test_run_keyboard_interrupt_in_main_loop(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Cover KeyboardInterrupt in main tray loop (lines 377-390)."""

        def _wait_svc(e: threading.Event) -> None:
            e.wait()

        def factory() -> ServiceManager:
            return ServiceManager([ServiceSpec("d", _wait_svc)], shutdown_timeout=0.5)

        tray = TrayController(manager_factory=factory, log_path_provider=lambda: "test.log")

        class FakeIcon:
            visible = False
            stopped = False

            def run(self, setup=None):
                if setup:
                    setup(self)
                time.sleep(0.3)

            def stop(self):
                self.stopped = True

        def fake_create_pystray() -> bool:
            tray._icon = FakeIcon()
            return True

        monkeypatch.setattr(tray, "_create_pystray", fake_create_pystray)

        # Make main loop raise KeyboardInterrupt after brief delay
        sleep_count = 0
        original_sleep = time.sleep

        def kbd_sleep(secs: float) -> None:
            nonlocal sleep_count
            sleep_count += 1
            if sleep_count > 5:
                raise KeyboardInterrupt()
            original_sleep(min(secs, 0.1))

        monkeypatch.setattr("background_utils.services.manager.time.sleep", kbd_sleep)

        tray.run()
        assert tray._exiting
        assert tray._icon.stopped
        # Clean up
        if tray._manager:
            tray._manager.stop()
            for t in tray._manager.threads:
                t.join(timeout=1.0)
