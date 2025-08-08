from __future__ import annotations

import importlib
import os
import threading
import time
from types import SimpleNamespace
from typing import Any, Callable

import pytest
from typer.testing import CliRunner

# CLI imports
from background_utils.cli.app import app as cli_app

# Modules under test
import background_utils.config as cfg
import background_utils.logging as blog
import background_utils.services.example_service as example_service
import background_utils.services.my_service as my_service
import background_utils.services.battery_monitor as battery_monitor
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

    monkeypatch.setattr(wifi, "_gather_profiles", lambda: [wifi.WifiProfile(name="SSID1", password="pass")])
    monkeypatch.setattr(wifi, "_list_networks", lambda: [{"ssid": "SSID2", "type": "Infrastructure", "authentication": "WPA2", "encryption": "CCMP"}])

    res1 = runner.invoke(cli_app, ["wifi", "show-passwords", "--output", "json"])
    assert res1.exit_code == 0
    assert "SSID1" in res1.stdout
    assert "pass" in res1.stdout

    res2 = runner.invoke(cli_app, ["wifi", "list-networks", "--output", "json"])
    assert res2.exit_code == 0
    assert "SSID2" in res2.stdout


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
    # Let it tick once
    time.sleep(0.12)
    stop.set()
    t.join(timeout=2.0)
    assert not t.is_alive()


def test_my_service_runs_and_stops_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BGU_SERVICE_INTERVAL_SECONDS", "0.1")
    stop = threading.Event()
    t = threading.Thread(target=my_service.run, args=(stop,), daemon=True)
    t.start()
    time.sleep(0.12)
    stop.set()
    t.join(timeout=2.0)
    assert not t.is_alive()


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
    time.sleep(0.06)
    stop.set()
    t.join(timeout=1.0)
    assert not t.is_alive()


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
    # After stop, threads should not be alive (or at least stop requested)
    time.sleep(0.05)
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

def test_tray_controller_runs_without_pystray(monkeypatch: pytest.MonkeyPatch) -> None:
    # Simulate pystray import failure to execute headless path
    def boom_import(*_a: Any, **_kw: Any) -> Any:
        raise RuntimeError("pystray missing")

    # Monkeypatch the import inside manager module by replacing pystray modules in sys.modules
    import sys
    sys.modules.pop("pystray", None)
    sys.modules["pystray"] = None  # type: ignore[assignment]

    # Manager factory producing a manager with a dummy service that waits for stop
    def manager_factory() -> ServiceManager:
        def target(e: threading.Event) -> None:
            e.wait()
        return ServiceManager([ServiceSpec("dummy", target)], shutdown_timeout=0.2)

    # Provide a dummy log path
    def log_path_provider() -> str:
        return os.path.join(".", "background-utils.log")

    tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

    # Run tray in a thread; it should detect pystray unavailability and enter a loop we can interrupt
    t = threading.Thread(target=tray.run, daemon=True)
    t.start()
    # Let it initialize
    time.sleep(0.2)
    # Trigger exit by setting internal flag via manager stop and setting exiting flag
    # Accessing protected members in tests is acceptable to control lifecycle
    tray._exiting = True  # type: ignore[attr-defined]
    # Give it time to exit loop
    time.sleep(0.2)
    # Best-effort join
    t.join(timeout=1.0)


# ---------------------------
# Import smoke tests
# ---------------------------

def test_cli_entry_importable() -> None:
    mod = importlib.import_module("background_utils.cli.app")
    assert hasattr(mod, "app")


def test_service_entry_importable() -> None:
    mod = importlib.import_module("background_utils.services.example_service")
    assert hasattr(mod, "main")