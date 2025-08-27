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

    # Mock the Windows check
    monkeypatch.setattr("os.name", "nt")
    
    # Create simple mock profile with expected structure
    def mock_gather_profiles() -> tuple[list[wifi.WifiProfile], int]:
        return [wifi.WifiProfile(name="SSID1", password="pass")], 0
    
    def mock_list_networks() -> list[dict[str, str]]:
        return [{"ssid": "SSID2", "type": "Infrastructure", "authentication": "WPA2", "encryption": "CCMP"}]

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
    tray = TrayController(
        manager_factory=manager_factory, 
        log_path_provider=log_path_provider
    )
    
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