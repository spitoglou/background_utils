from __future__ import annotations

import importlib


def test_cli_entry_importable() -> None:
    mod = importlib.import_module("background_utils.cli.app")
    assert hasattr(mod, "app")


def test_service_entry_importable() -> None:
    mod = importlib.import_module("background_utils.services.example_service")
    assert hasattr(mod, "main")