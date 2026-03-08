"""Tests for the Wi-Fi CLI commands."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from background_utils.cli.commands.wifi import (
    WifiProfile,
    _check_service_error,
    _gather_profiles,
    _get_profile_key,
    _list_networks,
    _list_profiles,
    app,
)

runner = CliRunner()


class TestCheckServiceError:
    """Tests for _check_service_error helper function."""

    def test_wireless_autoconfig_not_running(self):
        """Test detection of wlansvc not running."""
        error = "The Wireless AutoConfig Service (wlansvc) is not running"
        is_error, message = _check_service_error(error)
        assert is_error is True
        assert message is not None
        assert "net start wlansvc" in message

    def test_wlan_autoconfig_unavailable(self):
        """Test detection of WLAN autoconfig unavailable."""
        error = "wlan autoconfig service is not available"
        is_error, message = _check_service_error(error)
        assert is_error is True
        assert message is not None
        assert "virtual machine" in message.lower() or "not available" in message.lower()

    def test_wlansvc_generic_error(self):
        """Test detection of wlansvc generic error."""
        error = "wlansvc service error"
        is_error, message = _check_service_error(error)
        assert is_error is True
        assert message is not None

    def test_no_service_error(self):
        """Test non-service error returns False."""
        error = "Some other error occurred"
        is_error, message = _check_service_error(error)
        assert is_error is False
        assert message is None


class TestListProfiles:
    """Tests for _list_profiles function."""

    def test_list_profiles_success(self):
        """Test successful profile listing."""
        mock_output = """
Profiles on interface Wi-Fi:

Group policy profiles (read only)
---------------------------------

User profiles
-------------
    All User Profile     : HomeNetwork
    All User Profile     : WorkNetwork
    All User Profile     : CafeWifi
"""
        with patch(
            "background_utils.cli.commands.wifi._run",
            return_value=(0, mock_output, ""),
        ):
            profiles = _list_profiles()
            assert profiles == ["HomeNetwork", "WorkNetwork", "CafeWifi"]

    def test_list_profiles_empty(self):
        """Test listing when no profiles exist."""
        mock_output = """
Profiles on interface Wi-Fi:

User profiles
-------------
"""
        with patch(
            "background_utils.cli.commands.wifi._run",
            return_value=(0, mock_output, ""),
        ):
            profiles = _list_profiles()
            assert profiles == []

    def test_list_profiles_service_error(self):
        """Test error when service is not running."""
        with patch(
            "background_utils.cli.commands.wifi._run",
            return_value=(1, "", "The Wireless AutoConfig Service (wlansvc) is not running"),
        ):
            with pytest.raises(RuntimeError) as exc_info:
                _list_profiles()
            assert "net start wlansvc" in str(exc_info.value)

    def test_list_profiles_generic_error(self):
        """Test generic error handling."""
        with patch(
            "background_utils.cli.commands.wifi._run",
            return_value=(1, "", "Unknown error occurred"),
        ):
            with pytest.raises(RuntimeError) as exc_info:
                _list_profiles()
            assert "Unknown error occurred" in str(exc_info.value)


class TestGetProfileKey:
    """Tests for _get_profile_key function."""

    def test_get_key_success(self):
        """Test successful password retrieval."""
        mock_output = """
Profile MyNetwork on interface Wi-Fi:

Applied: All User Profile

Profile information
-------------------
    Version                : 1
    Type                   : Wireless LAN
    Name                   : MyNetwork
    Control options        :
        Connection mode    : Connect automatically

Key Content            : MySecretPassword123
"""
        with patch(
            "background_utils.cli.commands.wifi._run",
            return_value=(0, mock_output, ""),
        ):
            password, is_error = _get_profile_key("MyNetwork")
            assert password == "MySecretPassword123"
            assert is_error is False

    def test_get_key_no_password(self):
        """Test when profile has no password (open network)."""
        mock_output = """
Profile OpenNetwork on interface Wi-Fi:

Profile information
-------------------
    Type                   : Wireless LAN
    Name                   : OpenNetwork
"""
        with patch(
            "background_utils.cli.commands.wifi._run",
            return_value=(0, mock_output, ""),
        ):
            password, is_error = _get_profile_key("OpenNetwork")
            assert password is None
            assert is_error is False

    def test_get_key_permission_error(self):
        """Test handling of permission errors."""
        with patch(
            "background_utils.cli.commands.wifi._run",
            return_value=(1, "", "Access is denied"),
        ):
            password, is_error = _get_profile_key("ProtectedNetwork")
            assert password is None
            assert is_error is True


class TestListNetworks:
    """Tests for _list_networks function."""

    def test_list_networks_success(self):
        """Test successful network listing."""
        mock_output = """
Interface name : Wi-Fi
There are 2 networks currently visible.

SSID 1 : HomeNetwork
    Network type            : Infrastructure
    Authentication          : WPA2-Personal
    Encryption              : CCMP

SSID 2 : WorkNetwork
    Network type            : Infrastructure
    Authentication          : WPA2-Enterprise
    Encryption              : CCMP
"""
        with patch(
            "background_utils.cli.commands.wifi._run",
            return_value=(0, mock_output, ""),
        ):
            networks = _list_networks()
            assert len(networks) == 2
            assert networks[0]["ssid"] == "HomeNetwork"
            assert networks[0]["authentication"] == "WPA2-Personal"
            assert networks[1]["ssid"] == "WorkNetwork"
            assert networks[1]["authentication"] == "WPA2-Enterprise"

    def test_list_networks_empty(self):
        """Test listing when no networks are visible."""
        mock_output = """
Interface name : Wi-Fi
There are 0 networks currently visible.
"""
        with patch(
            "background_utils.cli.commands.wifi._run",
            return_value=(0, mock_output, ""),
        ):
            networks = _list_networks()
            assert networks == []

    def test_list_networks_service_error(self):
        """Test error when service is not running."""
        with patch(
            "background_utils.cli.commands.wifi._run",
            return_value=(1, "", "The Wireless AutoConfig Service (wlansvc) is not running"),
        ):
            with pytest.raises(RuntimeError) as exc_info:
                _list_networks()
            assert "net start wlansvc" in str(exc_info.value)


class TestGatherProfiles:
    """Tests for _gather_profiles function."""

    def test_gather_profiles_all_with_passwords(self):
        """Test gathering profiles all with passwords."""
        with (
            patch(
                "background_utils.cli.commands.wifi._list_profiles",
                return_value=["Network1", "Network2"],
            ),
            patch(
                "background_utils.cli.commands.wifi._get_profile_key",
                side_effect=[("pass1", False), ("pass2", False)],
            ),
        ):
            profiles, errors = _gather_profiles()
            assert len(profiles) == 2
            assert profiles[0].name == "Network1"
            assert profiles[0].password == "pass1"
            assert errors == 0

    def test_gather_profiles_with_permission_errors(self):
        """Test gathering profiles with permission errors."""
        with (
            patch(
                "background_utils.cli.commands.wifi._list_profiles",
                return_value=["Network1", "Network2"],
            ),
            patch(
                "background_utils.cli.commands.wifi._get_profile_key",
                side_effect=[("pass1", False), (None, True)],
            ),
        ):
            profiles, errors = _gather_profiles()
            assert len(profiles) == 2
            assert profiles[1].password is None
            assert errors == 1


class TestShowPasswordsCommand:
    """Tests for show-passwords CLI command."""

    def test_show_passwords_table(self):
        """Test table output format."""
        mock_profiles = [
            WifiProfile(name="Network1", password="pass1"),
            WifiProfile(name="Network2", password="pass2"),
        ]
        with patch(
            "background_utils.cli.commands.wifi._gather_profiles",
            return_value=(mock_profiles, 0),
        ):
            result = runner.invoke(app, ["show-passwords"])
            assert result.exit_code == 0
            assert "Network1" in result.output
            assert "pass1" in result.output

    def test_show_passwords_json(self):
        """Test JSON output format."""
        mock_profiles = [
            WifiProfile(name="Network1", password="pass1"),
        ]
        with patch(
            "background_utils.cli.commands.wifi._gather_profiles",
            return_value=(mock_profiles, 0),
        ):
            result = runner.invoke(app, ["show-passwords", "-o", "json"])
            assert result.exit_code == 0
            assert '"name": "Network1"' in result.output
            assert '"password": "pass1"' in result.output

    def test_show_passwords_error(self):
        """Test error handling."""
        with patch(
            "background_utils.cli.commands.wifi._gather_profiles",
            side_effect=RuntimeError("Test error"),
        ):
            result = runner.invoke(app, ["show-passwords"])
            assert result.exit_code == 1


class TestListNetworksCommand:
    """Tests for list-networks CLI command."""

    def test_list_networks_table(self):
        """Test table output format."""
        mock_networks = [
            {
                "ssid": "Network1",
                "type": "Infrastructure",
                "authentication": "WPA2",
                "encryption": "CCMP",
            },
        ]
        with patch(
            "background_utils.cli.commands.wifi._list_networks",
            return_value=mock_networks,
        ):
            result = runner.invoke(app, ["list-networks"])
            assert result.exit_code == 0
            assert "Network1" in result.output

    def test_list_networks_json(self):
        """Test JSON output format."""
        mock_networks = [
            {
                "ssid": "Network1",
                "type": "Infrastructure",
                "authentication": "WPA2",
                "encryption": "CCMP",
            },
        ]
        with patch(
            "background_utils.cli.commands.wifi._list_networks",
            return_value=mock_networks,
        ):
            result = runner.invoke(app, ["list-networks", "-o", "json"])
            assert result.exit_code == 0
            assert '"ssid": "Network1"' in result.output

    def test_list_networks_error(self):
        """Test error handling."""
        with patch(
            "background_utils.cli.commands.wifi._list_networks",
            side_effect=RuntimeError("Test error"),
        ):
            result = runner.invoke(app, ["list-networks"])
            assert result.exit_code == 1
