from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Tuple

import typer
from rich.console import Console
from rich.table import Table

from background_utils.logging import setup_logging, logger

# Force UTF-8 on Windows consoles to avoid cp1252 encoding issues (e.g., for dashes)
if os.name == "nt":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    os.environ.setdefault("PYTHONUTF8", "1")

console = Console(soft_wrap=False, force_terminal=False, legacy_windows=True)
app = typer.Typer(no_args_is_help=True, add_completion=False, help="Wi-Fi utilities (Windows)")


@dataclass(frozen=True)
class WifiProfile:
    name: str
    password: Optional[str]


def _run(cmd: List[str]) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, shell=False)
    return proc.returncode, proc.stdout, proc.stderr


def _list_profiles() -> List[str]:
    # Windows: netsh wlan show profiles
    code, out, err = _run(["netsh", "wlan", "show", "profiles"])
    if code != 0:
        raise RuntimeError(f"Failed to list profiles: {err or out}")
    profiles: List[str] = []
    for line in out.splitlines():
        # Lines like: "    All User Profile     : MyWifi"
        if ":" in line and "Profile" in line:
            parts = line.split(":", 1)
            if len(parts) == 2:
                name = parts[1].strip()
                if name:
                    profiles.append(name)
    return profiles


def _get_profile_key(name: str) -> Optional[str]:
    # netsh wlan show profile name="SSID" key=clear
    code, out, err = _run(["netsh", "wlan", "show", "profile", f'name="{name}"', "key=clear"])
    if code != 0:
        logger.warning(f"Failed to get key for profile {name}: {err or out}")
        return None
    key_line_prefix = "Key Content"
    for line in out.splitlines():
        if key_line_prefix in line and ":" in line:
            return line.split(":", 1)[1].strip() or None
    return None


def _list_networks() -> List[dict]:
    # Windows: netsh wlan show networks
    code, out, err = _run(["netsh", "wlan", "show", "networks"])
    if code != 0:
        raise RuntimeError(f"Failed to list networks: {err or out}")
    
    networks = []
    current_network = {}
    
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


def _gather_profiles() -> List[WifiProfile]:
    profiles = []
    for name in _list_profiles():
        pwd = _get_profile_key(name)
        profiles.append(WifiProfile(name=name, password=pwd))
    return profiles


@app.command("show-passwords")
def show_passwords(
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Optional output format: 'table' (default) or 'json'",
        metavar="FORMAT",
    )
) -> None:
    """
    Show saved Wi-Fi profiles and their passwords (Windows only).
    Requires administrative privileges to reveal passwords.
    """
    setup_logging()

    try:
        profiles = _gather_profiles()
    except Exception as exc:  # noqa: BLE001
        logger.exception(f"Failed to fetch Wi-Fi profiles: {exc}")
        raise typer.Exit(code=1)

    if output == "json":
        data = [{"name": p.name, "password": p.password} for p in profiles]
        console.print_json(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # Avoid non-ASCII characters in title for legacy Windows consoles
    table = Table(title="Wi-Fi Passwords (Windows)")
    table.add_column("SSID", style="cyan", no_wrap=True)
    table.add_column("Password", style="green")

    for p in profiles:
        table.add_row(p.name, p.password or "N/A")

    # Ensure printing doesn't trigger cp1252 encoding errors
    console.print(table, overflow="ignore", soft_wrap=False)


@app.command("list-networks")
def list_networks(
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Optional output format: 'table' (default) or 'json'",
        metavar="FORMAT",
    )
) -> None:
    """
    List available Wi-Fi networks (Windows only).
    """
    setup_logging()

    try:
        networks = _list_networks()
    except Exception as exc:  # noqa: BLE001
        logger.exception(f"Failed to fetch Wi-Fi networks: {exc}")
        raise typer.Exit(code=1)

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
            network.get("encryption", "N/A")
        )

    # Ensure printing doesn't trigger cp1252 encoding errors
    console.print(table, overflow="ignore", soft_wrap=False)