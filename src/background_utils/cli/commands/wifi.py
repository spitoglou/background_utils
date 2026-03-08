from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass

import typer
from rich.console import Console
from rich.table import Table

from background_utils.logging import logger

# Force UTF-8 on Windows consoles to avoid cp1252 encoding issues (e.g., for dashes)
if os.name == "nt":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    os.environ.setdefault("PYTHONUTF8", "1")

console = Console(soft_wrap=False, force_terminal=False, legacy_windows=True)
app = typer.Typer(no_args_is_help=True, add_completion=False, help="Wi-Fi utilities (Windows)")


@dataclass(frozen=True)
class WifiProfile:
    name: str
    password: str | None


def _run(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, shell=False)
    return proc.returncode, proc.stdout, proc.stderr


def _check_service_error(error_text: str) -> tuple[bool, str | None]:
    """Check if error is due to Windows service issues and provide helpful message."""
    error_lower = error_text.lower()

    if "wireless autoconfig service" in error_lower and "not running" in error_lower:
        return True, (
            "The Wireless AutoConfig Service (wlansvc) is not running.\n"
            "To fix this, run as Administrator:\n"
            "  net start wlansvc\n"
            "Or enable it permanently:\n"
            "  sc config wlansvc start= auto\n"
            "  net start wlansvc"
        )

    if "wlan autoconfig service" in error_lower:
        return True, (
            "Windows WLAN AutoConfig service is not available.\n"
            "This might be a virtual machine or system without Wi-Fi support."
        )

    if "wireless lan service" in error_lower or "wlansvc" in error_lower:
        return True, (
            "Windows Wi-Fi service is not available or not running.\n"
            "Try starting the service: net start wlansvc"
        )

    return False, None


def _list_profiles() -> list[str]:
    # Windows: netsh wlan show profiles
    code, out, err = _run(["netsh", "wlan", "show", "profiles"])
    if code != 0:
        error_text = err or out
        is_service_error, service_message = _check_service_error(error_text)

        if is_service_error:
            raise RuntimeError(f"Windows Wi-Fi service issue:\n{service_message}")
        else:
            raise RuntimeError(f"Failed to list profiles: {error_text}")

    profiles: list[str] = []
    for line in out.splitlines():
        # Lines like: "    All User Profile     : MyWifi"
        if ":" in line and "Profile" in line:
            parts = line.split(":", 1)
            if len(parts) == 2:
                name = parts[1].strip()
                if name:
                    profiles.append(name)
    return profiles


def _get_profile_key(name: str) -> tuple[str | None, bool]:
    """
    Get profile key for a Wi-Fi network.
    Returns (password, is_permission_error)
    """
    # Sanitize SSID: strip quotes and control characters to prevent netsh parsing issues
    sanitized = name.replace('"', "").replace("'", "")
    if not sanitized or sanitized != sanitized.strip():
        logger.warning(f"Skipping suspicious SSID: {name!r}")
        return None, False
    # netsh wlan show profile name="SSID" key=clear
    code, out, err = _run(["netsh", "wlan", "show", "profile", f'name="{sanitized}"', "key=clear"])
    if code != 0:
        # Check if it's a permission/privilege error
        error_text = (err or out).lower()
        is_permission_error = any(
            phrase in error_text
            for phrase in [
                "one or more parameters for the command are not correct",
                "access is denied",
                "privilege",
                "administrator",
            ]
        )
        return None, is_permission_error

    key_line_prefix = "Key Content"
    for line in out.splitlines():
        if key_line_prefix in line and ":" in line:
            password = line.split(":", 1)[1].strip() or None
            return password, False
    return None, False


def _list_networks() -> list[dict[str, str]]:
    # Windows: netsh wlan show networks
    code, out, err = _run(["netsh", "wlan", "show", "networks"])
    if code != 0:
        error_text = err or out
        is_service_error, service_message = _check_service_error(error_text)

        if is_service_error:
            raise RuntimeError(f"Windows Wi-Fi service issue:\n{service_message}")
        else:
            raise RuntimeError(f"Failed to list networks: {error_text}")

    networks = []
    current_network: dict[str, str] = {}

    for line in out.splitlines():
        line = line.strip()
        if line.startswith("SSID"):
            if current_network:
                networks.append(current_network)
                current_network = {}
            # Line like: "SSID 1 : MyNetwork"
            parts = line.split(":", 1)
            if len(parts) == 2:
                current_network["ssid"] = parts[1].strip()
        elif line.startswith("Network type"):
            # Line like: "Network type            : Infrastructure"
            parts = line.split(":", 1)
            if len(parts) == 2:
                current_network["type"] = parts[1].strip()
        elif line.startswith("Authentication"):
            # Line like: "Authentication          : WPA2-Personal"
            parts = line.split(":", 1)
            if len(parts) == 2:
                current_network["authentication"] = parts[1].strip()
        elif line.startswith("Encryption"):
            # Line like: "Encryption              : CCMP"
            parts = line.split(":", 1)
            if len(parts) == 2:
                current_network["encryption"] = parts[1].strip()

    # Add last network if exists
    if current_network:
        networks.append(current_network)

    return networks


def _gather_profiles() -> tuple[list[WifiProfile], int]:
    """
    Gather Wi-Fi profiles with passwords.
    Returns (profiles, permission_error_count)
    """
    profiles = []
    permission_errors = 0

    for name in _list_profiles():
        pwd, is_permission_error = _get_profile_key(name)
        if is_permission_error:
            permission_errors += 1
        profiles.append(WifiProfile(name=name, password=pwd))

    return profiles, permission_errors


@app.command("show-passwords")
def show_passwords(
    output: str | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Optional output format: 'table' (default) or 'json'",
        metavar="FORMAT",
    ),
) -> None:
    """
    Show saved Wi-Fi profiles and their passwords (Windows only).
    Requires administrative privileges to reveal passwords.
    """

    try:
        profiles, permission_errors = _gather_profiles()
    except Exception as exc:  # noqa: BLE001
        error_msg = str(exc)

        # Check if it's a service-related error and provide cleaner output
        if "Windows Wi-Fi service issue:" in error_msg:
            # Extract just the helpful message without the prefix
            clean_msg = error_msg.replace("Windows Wi-Fi service issue:\n", "")
            console.print("[red]❌ Wi-Fi Service Issue[/red]")
            console.print(f"[yellow]{clean_msg}[/yellow]")
        else:
            logger.exception(f"Failed to fetch Wi-Fi profiles: {exc}")
            console.print(f"[red]❌ Error:[/red] {error_msg}")

        raise typer.Exit(code=1) from exc

    if output == "json":
        data = [{"name": p.name, "password": p.password} for p in profiles]
        console.print_json(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # Avoid non-ASCII characters in title for legacy Windows consoles
    table = Table(title="Wi-Fi Passwords (Windows)")
    table.add_column("SSID", style="cyan", no_wrap=True)
    table.add_column("Password", style="green")

    for p in profiles:
        if p.password is None:
            password_display = "[yellow]Insufficient privileges[/yellow]"
        else:
            password_display = p.password
        table.add_row(p.name, password_display)

    # Ensure printing doesn't trigger cp1252 encoding errors
    console.print(table, overflow="ignore", soft_wrap=False)

    # Add informational message if there were permission errors
    if permission_errors > 0:
        console.print()
        console.print(
            f"[yellow]![/yellow]  {permission_errors} network(s) require"
            " administrator privileges to reveal passwords."
        )
        console.print("[dim]Run this command as Administrator to see all Wi-Fi passwords.[/dim]")


@app.command("list-networks")
def list_networks(
    output: str | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Optional output format: 'table' (default) or 'json'",
        metavar="FORMAT",
    ),
) -> None:
    """
    List available Wi-Fi networks (Windows only).
    """

    try:
        networks = _list_networks()
    except Exception as exc:  # noqa: BLE001
        error_msg = str(exc)

        # Check if it's a service-related error and provide cleaner output
        if "Windows Wi-Fi service issue:" in error_msg:
            # Extract just the helpful message without the prefix
            clean_msg = error_msg.replace("Windows Wi-Fi service issue:\n", "")
            console.print("[red]❌ Wi-Fi Service Issue[/red]")
            console.print(f"[yellow]{clean_msg}[/yellow]")
        else:
            logger.exception(f"Failed to fetch Wi-Fi networks: {exc}")
            console.print(f"[red]❌ Error:[/red] {error_msg}")

        raise typer.Exit(code=1) from exc

    if output == "json":
        console.print_json(json.dumps(networks, ensure_ascii=False, indent=2))
        return

    # Avoid non-ASCII characters in title for legacy Windows consoles
    table = Table(title="Available Wi-Fi Networks (Windows)")
    table.add_column("SSID", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta")
    table.add_column("Authentication", style="yellow")
    table.add_column("Encryption", style="blue")

    for network in networks:
        table.add_row(
            network.get("ssid", "N/A"),
            network.get("type", "N/A"),
            network.get("authentication", "N/A"),
            network.get("encryption", "N/A"),
        )

    # Ensure printing doesn't trigger cp1252 encoding errors
    console.print(table, overflow="ignore", soft_wrap=False)
