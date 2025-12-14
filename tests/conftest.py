"""Test configuration and fixtures for background_utils tests."""

from __future__ import annotations

import os
import sys
import threading
import time
from collections.abc import Generator

import pytest


@pytest.fixture(autouse=True)
def cleanup_environment() -> Generator[None, None, None]:
    """Ensure clean test environment and proper cleanup."""
    # Store original state
    original_threads = threading.active_count()

    # Set environment for headless testing
    os.environ["PYTEST_RUNNING"] = "1"
    os.environ["HEADLESS"] = "1"

    # Remove GUI modules to prevent hanging
    gui_modules = ["pystray", "PIL", "tkinter"]
    removed_modules = {}
    for module in gui_modules:
        if module in sys.modules:
            removed_modules[module] = sys.modules[module]
            del sys.modules[module]

    yield

    # Cleanup after test
    # Force cleanup of any remaining threads
    current_threads = threading.enumerate()
    for thread in current_threads:
        if thread != threading.main_thread() and thread.is_alive():
            if hasattr(thread, "_stop_event"):
                thread._stop_event.set()  # type: ignore
            # Also check for stop_event on the thread's target if accessible
            if hasattr(thread, "_target") and hasattr(thread._target, "__self__"):
                obj = thread._target.__self__
                if hasattr(obj, "stop_event"):
                    obj.stop_event.set()

    # Wait briefly for threads to stop
    time.sleep(0.2)

    # Force join remaining threads with timeout
    for thread in threading.enumerate():
        if thread != threading.main_thread() and thread.is_alive():
            thread.join(timeout=0.5)

    # Restore modules
    for module, mod_obj in removed_modules.items():
        sys.modules[module] = mod_obj

    # Clean up environment
    os.environ.pop("PYTEST_RUNNING", None)
    os.environ.pop("HEADLESS", None)


@pytest.fixture(autouse=True)
def isolate_logging() -> Generator[None, None, None]:
    """Isolate logging configuration between tests."""
    # Remove loguru handlers before each test
    from loguru import logger

    logger.stop()  # Remove all handlers

    yield

    # Clean up after test
    logger.stop()  # Remove all handlers again


@pytest.fixture
def mock_gui_components(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock GUI components that can cause hanging."""

    # Mock pystray to prevent GUI initialization
    class MockIcon:
        def __init__(self, *args, **kwargs):
            pass

        def run(self, setup=None):
            if setup:
                setup(self)
            time.sleep(0.1)  # Brief delay to simulate initialization

        def stop(self):
            pass

        @property
        def visible(self):
            return True

        @visible.setter
        def visible(self, value):
            pass

    class MockMenu:
        def __init__(self, *args, **kwargs):
            pass

    class MockMenuItem:
        def __init__(self, *args, **kwargs):
            pass

    # Create mock pystray module
    mock_pystray = type(
        "MockPystray",
        (),
        {
            "Icon": MockIcon,
            "Menu": MockMenu,
            "MenuItem": MockMenuItem,
        },
    )()

    monkeypatch.setattr("sys.modules", {**sys.modules, "pystray": mock_pystray})


@pytest.fixture
def quick_intervals(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set fast intervals for service testing."""
    monkeypatch.setenv("BGU_SERVICE_INTERVAL_SECONDS", "0.05")


@pytest.fixture
def mock_imap_connection(monkeypatch: pytest.MonkeyPatch):
    """Mock IMAP connection for Gmail service testing."""

    class MockIMAP4_SSL:
        def __init__(self, *args, **kwargs):
            self.connected = True
            self.selected_folder = None
            self.search_results = []
            self.fetch_results = {}

        def login(self, user, password):
            return ("OK", [b"LOGIN completed"])

        def select(self, folder="INBOX"):
            self.selected_folder = folder
            return ("OK", [b"1"])

        def uid(self, command, *args):
            if command == "search":
                # Return mock UIDs
                return ("OK", [b"1 2 3"])
            return ("OK", [b""])

        def fetch(self, msg_id, data):
            # Return mock email data
            mock_email = (
                b"1 (UID 1 RFC822 {310}",
                b"From: test@example.com\r\n"
                b"Subject: Test Email\r\n"
                b"Date: Mon, 1 Jan 2024 12:00:00 +0000\r\n"
                b"\r\n"
                b"This is a test email body.\r\n"
                b")",
            )
            return ("OK", [mock_email])

        def close(self):
            return ("OK", [b"CLOSE completed"])

        def logout(self):
            self.connected = False
            return ("OK", [b"LOGOUT completed"])

    monkeypatch.setattr("imaplib.IMAP4_SSL", MockIMAP4_SSL)
    return MockIMAP4_SSL()


@pytest.fixture
def mock_notifications(monkeypatch: pytest.MonkeyPatch):
    """Mock notification system for testing."""

    class MockNotification:
        def __init__(self):
            self.notifications = []

        def notify(self, title, message, **kwargs):
            self.notifications.append({"title": title, "message": message, "kwargs": kwargs})
            return True

        def get_notifications(self):
            return self.notifications

        def clear(self):
            self.notifications.clear()

    mock_notify = MockNotification()

    # Mock plyer notification
    mock_plyer = type(
        "MockPlyer",
        (),
        {"notification": type("MockNotificationModule", (), {"notify": mock_notify.notify})()},
    )()

    monkeypatch.setattr(
        "sys.modules",
        {**sys.modules, "plyer": mock_plyer, "plyer.notification": mock_plyer.notification},
    )

    return mock_notify


@pytest.fixture
def mock_file_system(tmp_path, monkeypatch):
    """Mock file system operations for testing."""

    # Create mock cache directory
    cache_dir = tmp_path / "background-utils"
    cache_dir.mkdir(exist_ok=True)

    # Mock LOCALAPPDATA for Windows
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    return cache_dir


# Timeout configuration for individual tests
pytest_plugins = ["timeout"]
