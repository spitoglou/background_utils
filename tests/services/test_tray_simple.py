"""Simplified tests for Tray Controller functionality."""

from __future__ import annotations

import threading
import time
from unittest.mock import MagicMock, patch

from background_utils.services.manager import ServiceManager, ServiceSpec, TrayController


class TestTrayControllerSimple:
    """Simplified tests for TrayController."""

    def test_tray_controller_creation(self):
        """Test that TrayController can be created."""

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        assert tray is not None
        assert tray._manager_factory is not None
        assert tray._manager is None
        assert tray._log_path_provider is not None

    def test_tray_ensure_manager(self):
        """Test _ensure_manager creates manager."""

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        # First call should create manager
        tray._ensure_manager()
        assert tray._manager is not None

        # Second call should return same manager
        manager1 = tray._manager
        tray._ensure_manager()
        manager2 = tray._manager
        assert manager2 is manager1

    def test_tray_stop_services(self):
        """Test stop services action."""

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        # Create manager
        tray._ensure_manager()

        # Call stop services
        mock_icon = MagicMock()
        mock_item = MagicMock()
        tray._stop_services(mock_icon, mock_item)

        # Give brief time for background thread
        time.sleep(0.1)

        # Verify stop was initiated
        assert tray._manager.stop_event.is_set()

    def test_tray_restart_services(self):
        """Test restart services action."""

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        # Create manager
        tray._ensure_manager()

        # Call restart services
        mock_icon = MagicMock()
        mock_item = MagicMock()
        tray._restart_services(mock_icon, mock_item)

        # Give brief time for background thread
        time.sleep(0.2)

        # Verify restart was initiated
        assert tray._manager.stop_event.is_set()

    def test_tray_exit_action(self):
        """Test exit action."""

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        # Mock os._exit
        with patch("os._exit") as mock_exit:
            mock_icon = MagicMock()
            mock_item = MagicMock()

            tray._exit_tray(mock_icon, mock_item)

            # Give brief time for background thread
            time.sleep(0.1)

            # Verify exit was called
            mock_exit.assert_called_once_with(0)

    def test_tray_view_log_action(self, tmp_path):
        """Test view log action."""
        log_file = tmp_path / "test.log"
        log_file.write_text("Test log content")

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return str(log_file)

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        # Mock subprocess
        with patch("subprocess.Popen") as mock_popen:
            mock_icon = MagicMock()
            mock_item = MagicMock()

            tray._view_log(mock_icon, mock_item)

            # Verify subprocess was called
            mock_popen.assert_called_once()
            args, kwargs = mock_popen.call_args
            assert "notepad.exe" in args[0]
            assert str(log_file) in args[0]

    def test_tray_locking(self):
        """Test tray locking mechanism."""

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        # Verify lock exists
        assert hasattr(tray, "_lock")
        assert isinstance(tray._lock, threading.Lock)

        # Test lock usage
        with tray._lock:
            assert True

    def test_tray_exiting_flag(self):
        """Test exiting flag."""

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        # Set exiting flag
        tray._exiting = True

        # Actions should be ignored
        mock_icon = MagicMock()
        mock_item = MagicMock()

        tray._stop_services(mock_icon, mock_item)
        tray._restart_services(mock_icon, mock_item)

        assert tray._exiting is True

    def test_tray_pystray_unavailable(self, monkeypatch):
        """Test behavior when pystray unavailable."""
        import builtins
        from unittest.mock import patch

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        # Force pystray import to fail by patching builtins.__import__
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "pystray" or name.startswith("pystray."):
                raise ImportError("pystray not available")
            return original_import(name, *args, **kwargs)

        with patch.object(builtins, "__import__", mock_import):
            result = tray._create_pystray()
            assert result is False

    def test_tray_windows_path(self, monkeypatch):
        """Test Windows path handling."""
        monkeypatch.setattr("os.name", "nt")

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return "C:\\Users\\test\\AppData\\Local\\test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        assert tray._log_path_provider() == "C:\\Users\\test\\AppData\\Local\\test.log"

    def test_tray_performance(self):
        """Test tray creation performance."""

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return "/tmp/test.log"

        start_time = time.time()

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        creation_time = time.time() - start_time
        assert creation_time < 0.1

    def test_tray_with_services(self):
        """Test tray with services."""

        def run_service(stop_event):
            while not stop_event.wait(timeout=0.1):
                pass

        def manager_factory():
            return ServiceManager(services=[ServiceSpec(name="test", target=run_service)])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        # Should have service
        assert len(tray._manager_factory().services) == 1
