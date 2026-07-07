"""Application configuration management."""

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class AppConfig:
    """Application configuration settings."""

    default_width: int = 800
    default_height: int = 600
    default_output_format: str = "JPEG"
    default_output_dir: str = "resized_images"
    maintain_aspect_ratio: bool = True
    add_dimensions_to_filename: bool = True
    jpeg_quality: int = 95

    # Preset resolutions
    presets: tuple[tuple[str, int, int], ...] = (
        ("Custom", 0, 0),
        ("1920x1080", 1920, 1080),
        ("1280x720", 1280, 720),
        ("800x600", 800, 600),
        ("640x480", 640, 480),
        ("320x240", 320, 240),
    )

    @classmethod
    def from_dict(cls, data: dict) -> "AppConfig":
        """Create config from dictionary.

        Args:
            data: Dictionary with configuration values.

        Returns:
            AppConfig instance.
        """
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered)

    def get_preset_dimensions(self, preset_name: str) -> tuple[int, int]:
        """Get dimensions for a named preset.

        Args:
            preset_name: Name of the preset.

        Returns:
            Tuple of (width, height), or (0, 0) if not found.
        """
        for name, w, h in self.presets:
            if name == preset_name:
                return w, h
        return 0, 0


def get_resource_path(relative_path: str) -> Path:
    """Get absolute path to a resource, works for dev and PyInstaller.

    Args:
        relative_path: Relative path to the resource.

    Returns:
        Absolute path to the resource.
    """
    try:
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        base_path = Path(os.path.abspath("."))

    return base_path / relative_path


def get_app_dir() -> Path:
    """Get the application directory.

    Returns:
        Path to the application directory.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent