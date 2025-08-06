# from future import annotations
import os
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw
import pystray

def log(msg: str) -> None:
    log_dir = Path(os.getenv("LOCALAPPDATA") or ".") / "background-utils"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "tray-test.log"
    with log_file.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")

def create_image() -> Image.Image:
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((8, 8, size - 8, size - 8), fill=(30, 144, 255, 255))
    return img

def on_quit(icon, item):  # type: ignore[no-untyped-def]
    try:
        icon.visible = False
    except Exception:
        pass
    log("Quit clicked; stopping icon")
    icon.stop()

def main() -> None:
    log(f"Starting tray_test with {sys.executable}")
    image = create_image()
    icon = pystray.Icon("tray-test", image, "Tray Test",
    pystray.Menu(pystray.MenuItem("Quit", on_quit)))
    try:
        # Try visibility toggle to prompt shell refresh
        icon.visible = False
        icon.visible = True
        log("Icon created and visibility toggled True")
    except Exception as exc:
        log(f"Error toggling visibility: {exc!r}")

    try:
        icon.run()
        log("icon.run() returned")
    finally:
        try:
            icon.visible = False
        except Exception:
            pass
        log("Exiting tray_test")


if __name__ == "__main__":
    main()