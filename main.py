"""Main entry point for Image Resizer Pro application."""

import os
import sys
from pathlib import Path

# Add src to path for local development
if getattr(sys, "frozen", False):
    # Running as compiled executable
    os.chdir(Path(sys.executable).parent)
else:
    # Running as script
    src_path = Path(__file__).parent / "src"
    if src_path.exists():
        sys.path.insert(0, str(Path(__file__).parent))

from tkinterdnd2 import TkinterDnD  # noqa: E402

from image_resizer.config import AppConfig  # noqa: E402
from image_resizer.main_window import ImageResizerWindow  # noqa: E402


def main():
    """Main entry point."""
    root = TkinterDnD.Tk()
    config = AppConfig()
    app = ImageResizerWindow(root, config)

    # Create menu bar
    menubar = __import__("tkinter").Menu(root)
    root.config(menu=menubar)
    menubar.add_command(label="About", command=app.show_about)

    root.mainloop()


if __name__ == "__main__":
    main()