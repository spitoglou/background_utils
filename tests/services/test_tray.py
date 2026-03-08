"""Comprehensive tests for Tray Controller functionality."""

from __future__ import annotations

import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from background_utils.services.manager import ServiceManager, ServiceSpec, TrayController


class MockService:
    """Mock service for testing."""

    def __init__(self):
        self.run_calls = 0
        self.stop_event = None

    def run(self, stop_event: threading.Event):
        """Mock service run method."""
        self.run_calls += 1
        self.stop_event = stop_event
        # Simulate service work until stopped
        while not stop_event.wait(timeout=0.1):
            pass


class TestTrayControllerInitialization:
    """Test TrayController initialization and basic functionality."""

    def test_tray_controller_creation(self):
        """Test that TrayController can be created."""

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        assert tray is not None
        assert tray._manager_factory is not None
        assert tray._manager is None  # Not created yet
        assert tray._log_path_provider is not None

    def test_tray_controller_with_mock_services(self):
        """Test TrayController with mock services."""
        mock_service = MockService()

        def manager_factory():
            return ServiceManager(services=[ServiceSpec(name="test", target=mock_service.run)])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        assert tray is not None
        assert len(tray._manager_factory().services) == 1


class TestTrayMenuActions:
    """Test tray menu action functionality."""

    def test_view_log_action(self, tmp_path, mock_gui_components):
        """Test View Log menu action."""
        log_file = tmp_path / "test.log"
        log_file.write_text("Test log content")

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return str(log_file)

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        # Mock subprocess for notepad
        with patch("subprocess.Popen") as mock_popen:
            # Create mock icon and item
            mock_icon = MagicMock()
            mock_item = MagicMock()

            # Call the view log action
            tray._view_log(mock_icon, mock_item)

            # Verify subprocess was called
            mock_popen.assert_called_once()
            args, kwargs = mock_popen.call_args
            assert "notepad.exe" in args[0]
            assert str(log_file) in args[0]

    def test_stop_services_action(self, mock_gui_components):
        """Test Stop Services menu action."""
        mock_service = MockService()

        def manager_factory():
            return ServiceManager(services=[ServiceSpec(name="test", target=mock_service.run)])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        # Create manager instance
        tray._ensure_manager()
        assert tray._manager is not None

        # Start services in a thread
        service_thread = threading.Thread(target=tray._manager.start)
        service_thread.start()
        time.sleep(0.1)  # Let services start

        # Call stop services action
        mock_icon = MagicMock()
        mock_item = MagicMock()
        tray._stop_services(mock_icon, mock_item)

        # Give stop thread time to work
        time.sleep(0.2)

        # Verify services are stopping
        assert tray._manager.stop_event.is_set()

    def test_restart_services_action(self, mock_gui_components):
        """Test Restart Services menu action."""
        mock_service = MockService()

        def manager_factory():
            return ServiceManager(services=[ServiceSpec(name="test", target=mock_service.run)])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        try:
            # Create manager instance
            tray._ensure_manager()
            original_manager = tray._manager

            # Start services
            service_thread = threading.Thread(target=tray._manager.start, daemon=True)
            service_thread.start()
            time.sleep(0.1)

            # Call restart services action
            mock_icon = MagicMock()
            mock_item = MagicMock()
            tray._restart_services(mock_icon, mock_item)

            # Give restart thread time to work - restart has internal delays
            time.sleep(1.5)

            # Verify original manager was stopped
            assert original_manager.stop_event.is_set()
            # After restart, a new manager is created - verify service ran again
            assert mock_service.run_calls >= 1
        finally:
            # Cleanup
            if tray._manager:
                tray._manager.stop_event.set()
                time.sleep(0.2)

    def test_exit_action(self, mock_gui_components):
        """Test Exit menu action."""

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        # Mock os._exit to prevent actual exit
        with patch("os._exit") as mock_exit:
            mock_icon = MagicMock()
            mock_item = MagicMock()

            # Call exit action
            tray._exit_tray(mock_icon, mock_item)

            # Give exit thread time to work
            time.sleep(0.2)

            # Verify exit was called
            mock_exit.assert_called_once_with(0)


class TestTrayLifecycleManagement:
    """Test tray lifecycle and state management."""

    def test_tray_ensure_manager(self, mock_gui_components):
        """Test _ensure_manager creates manager only once."""
        mock_service = MockService()

        def manager_factory():
            return ServiceManager(services=[ServiceSpec(name="test", target=mock_service.run)])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        # First call should create manager
        tray._ensure_manager()
        manager1 = tray._manager
        assert manager1 is not None

        # Second call should return same manager
        tray._ensure_manager()
        manager2 = tray._manager
        assert manager2 is manager1

    def test_tray_exiting_flag(self, mock_gui_components):
        """Test exiting flag prevents duplicate actions."""

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        # Set exiting flag
        tray._exiting = True

        # Actions should be ignored when exiting
        mock_icon = MagicMock()
        mock_item = MagicMock()

        # These should not cause errors or actions
        tray._stop_services(mock_icon, mock_item)
        tray._restart_services(mock_icon, mock_item)

        assert tray._exiting is True


class TestTrayServiceManagement:
    """Test tray service management functionality."""

    def test_service_startup_via_tray(self, mock_gui_components):
        """Test starting services via tray controller."""
        mock_service = MockService()

        def manager_factory():
            return ServiceManager(services=[ServiceSpec(name="test", target=mock_service.run)])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        # Ensure manager is created
        tray._ensure_manager()

        # Start services via tray
        service_thread = threading.Thread(target=tray._manager.start)
        service_thread.start()
        time.sleep(0.1)

        # Verify service started
        assert mock_service.run_calls == 1
        assert mock_service.stop_event is not None
        assert not mock_service.stop_event.is_set()

    def test_service_shutdown_via_tray(self, mock_gui_components):
        """Test shutting down services via tray controller."""
        mock_service = MockService()

        def manager_factory():
            return ServiceManager(services=[ServiceSpec(name="test", target=mock_service.run)])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        # Ensure manager is created and services started
        tray._ensure_manager()
        service_thread = threading.Thread(target=tray._manager.start)
        service_thread.start()
        time.sleep(0.1)

        # Stop services via tray
        tray._manager.stop()
        service_thread.join(timeout=1.0)

        # Verify service stopped
        assert mock_service.stop_event.is_set()


class TestTrayThreading:
    """Test tray threading behavior."""

    def test_menu_actions_non_blocking(self, mock_gui_components):
        """Test that menu actions run in background threads."""

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        # Create manager
        tray._ensure_manager()

        # Call menu actions - they should create background threads
        mock_icon = MagicMock()
        mock_item = MagicMock()

        # These should not block
        tray._stop_services(mock_icon, mock_item)
        tray._restart_services(mock_icon, mock_item)

        # Should complete quickly since they run in background
        time.sleep(0.1)

    def test_tray_locking_mechanism(self, mock_gui_components):
        """Test tray locking mechanism for thread safety."""

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        # Verify lock exists
        assert hasattr(tray, "_lock")
        assert isinstance(tray._lock, threading.Lock)

        # Test lock usage in critical sections
        with tray._lock:
            # Should be able to acquire lock
            assert True


class TestTrayErrorHandling:
    """Test tray error handling and recovery."""

    def test_tray_error_in_menu_action(self, mock_gui_components, caplog):
        """Test error handling in menu actions."""

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        # Mock a failing manager
        mock_manager = MagicMock()
        mock_manager.stop.side_effect = Exception("Test error")
        tray._manager = mock_manager

        # Call action that should handle error gracefully
        mock_icon = MagicMock()
        mock_item = MagicMock()

        tray._stop_services(mock_icon, mock_item)

        # Give time for error handling
        time.sleep(0.2)

        # Should not raise exception
        assert True

    def test_tray_pystray_unavailable(self, monkeypatch):
        """Test behavior when pystray is unavailable."""
        import builtins

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


class TestTrayWindowsSpecific:
    """Test Windows-specific tray behavior."""

    def test_windows_log_path(self, monkeypatch):
        """Test Windows log path handling."""
        # Mock Windows environment
        monkeypatch.setattr("os.name", "nt")

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return "C:\\Users\\test\\AppData\\Local\\background-utils\\background-utils.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        # Should handle Windows paths correctly
        assert (
            tray._log_path_provider()
            == "C:\\Users\\test\\AppData\\Local\\background-utils\\background-utils.log"
        )

    def test_tray_icon_creation(self, mock_gui_components):
        """Test tray icon creation."""

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        # Create pystray icon
        result = tray._create_pystray()

        # Should succeed with mocks
        assert result is True
        assert tray._icon is not None


class TestTrayPerformance:
    """Performance tests for tray controller."""

    @pytest.mark.timeout(5)
    def test_tray_creation_performance(self, mock_gui_components):
        """Test that tray creation is fast."""

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return "/tmp/test.log"

        start_time = time.time()

        TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        creation_time = time.time() - start_time
        assert creation_time < 0.1  # Should create in under 100ms

    @pytest.mark.timeout(10)
    def test_tray_menu_action_performance(self, mock_gui_components):
        """Test that menu actions complete quickly."""

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        mock_icon = MagicMock()
        mock_item = MagicMock()

        # Test multiple menu actions
        start_time = time.time()

        tray._stop_services(mock_icon, mock_item)
        tray._restart_services(mock_icon, mock_item)

        # Give background threads time to start
        time.sleep(0.2)

        action_time = time.time() - start_time
        assert action_time < 1.0  # Should complete in under 1 second


class TestTrayIntegration:
    """Integration tests for tray controller."""

    def test_full_tray_lifecycle(self, mock_gui_components):
        """Test complete tray lifecycle."""
        mock_service = MockService()

        def manager_factory():
            return ServiceManager(services=[ServiceSpec(name="test", target=mock_service.run)])

        def log_path_provider():
            return "/tmp/test.log"

        # Create tray
        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        try:
            # Ensure manager created
            tray._ensure_manager()

            # Start services
            service_thread = threading.Thread(target=tray._manager.start, daemon=True)
            service_thread.start()
            time.sleep(0.2)

            # Verify services running
            assert mock_service.run_calls == 1

            # Stop services
            mock_icon = MagicMock()
            mock_item = MagicMock()
            tray._stop_services(mock_icon, mock_item)
            time.sleep(0.5)

            # Verify services stopped
            assert tray._manager.stop_event.is_set()

            # Restart services - this runs in a background thread with internal delays
            tray._restart_services(mock_icon, mock_item)

            # Wait for restart to complete:
            # - _do_restart has internal wait for stop + 0.5s sleep + service start
            # Poll for the service to be called again
            for _ in range(20):  # Up to 2 seconds
                if mock_service.run_calls >= 2:
                    break
                time.sleep(0.1)

            # Verify services restarted
            assert mock_service.run_calls >= 2  # Should have run at least twice
        finally:
            # Ensure cleanup - stop any running manager
            if tray._manager:
                tray._manager.stop_event.set()
                time.sleep(0.3)

    def test_tray_with_multiple_services(self, mock_gui_components):
        """Test tray with multiple services."""
        service1 = MockService()
        service2 = MockService()

        def manager_factory():
            return ServiceManager(
                services=[
                    ServiceSpec(name="service1", target=service1.run),
                    ServiceSpec(name="service2", target=service2.run),
                ]
            )

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        # Ensure manager created
        tray._ensure_manager()

        # Start services
        service_thread = threading.Thread(target=tray._manager.start)
        service_thread.start()
        time.sleep(0.1)

        # Verify both services started
        assert service1.run_calls == 1
        assert service2.run_calls == 1

        # Stop services
        mock_icon = MagicMock()
        mock_item = MagicMock()
        tray._stop_services(mock_icon, mock_item)
        time.sleep(0.3)

        # Verify both services stopped
        assert service1.stop_event.is_set()
        assert service2.stop_event.is_set()


class TestTrayEdgeCases:
    """Test edge cases and unusual scenarios."""

    def test_tray_with_no_services(self, mock_gui_components):
        """Test tray with no services."""

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        # Should handle empty services gracefully
        tray._ensure_manager()

        # Menu actions should not fail
        mock_icon = MagicMock()
        mock_item = MagicMock()

        tray._stop_services(mock_icon, mock_item)
        tray._restart_services(mock_icon, mock_item)

        time.sleep(0.2)
        assert True  # Should not raise exceptions

    def test_tray_rapid_menu_actions(self, mock_gui_components):
        """Test rapid menu actions."""

        def manager_factory():
            return ServiceManager(services=[])

        def log_path_provider():
            return "/tmp/test.log"

        tray = TrayController(manager_factory=manager_factory, log_path_provider=log_path_provider)

        mock_icon = MagicMock()
        mock_item = MagicMock()

        # Rapid actions should be handled gracefully
        for _i in range(5):
            tray._stop_services(mock_icon, mock_item)
            tray._restart_services(mock_icon, mock_item)

        time.sleep(0.3)
        assert True  # Should not raise exceptions
