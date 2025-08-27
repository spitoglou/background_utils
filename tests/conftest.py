"""Test configuration and fixtures for background_utils tests."""
from __future__ import annotations

import os
import sys
import threading
import time
from typing import Generator

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
            if hasattr(thread, '_stop_event'):
                thread._stop_event.set()  # type: ignore
            # Give threads a chance to stop gracefully
    
    # Wait briefly for threads to stop
    time.sleep(0.1)
    
    # Force join any remaining daemon threads
    for thread in current_threads:
        if (thread != threading.main_thread() and 
            thread.is_alive() and 
            thread.daemon):
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
    mock_pystray = type('MockPystray', (), {
        'Icon': MockIcon,
        'Menu': MockMenu,
        'MenuItem': MockMenuItem,
    })()
    
    monkeypatch.setattr('sys.modules', {
        **sys.modules, 
        'pystray': mock_pystray
    })


@pytest.fixture
def quick_intervals(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set fast intervals for service testing."""
    monkeypatch.setenv("BGU_SERVICE_INTERVAL_SECONDS", "0.05")


# Timeout configuration for individual tests
pytest_plugins = ["timeout"]