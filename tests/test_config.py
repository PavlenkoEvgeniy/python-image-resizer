"""Tests for config module."""

import pytest

from image_resizer.config import AppConfig


class TestAppConfig:
    """Tests for AppConfig class."""

    def test_defaults(self):
        config = AppConfig()
        assert config.default_width == 800
        assert config.default_height == 600
        assert config.default_output_format == "JPEG"
        assert config.default_output_dir == "resized_images"
        assert config.maintain_aspect_ratio is True
        assert config.add_dimensions_to_filename is True
        assert config.jpeg_quality == 95

    def test_custom_config(self):
        config = AppConfig(
            default_width=1024,
            default_height=768,
            default_output_format="PNG",
            default_output_dir="custom_output",
            maintain_aspect_ratio=False,
            add_dimensions_to_filename=False,
            jpeg_quality=80,
        )
        assert config.default_width == 1024
        assert config.default_height == 768
        assert config.default_output_format == "PNG"
        assert config.default_output_dir == "custom_output"
        assert config.maintain_aspect_ratio is False
        assert config.add_dimensions_to_filename is False
        assert config.jpeg_quality == 80

    def test_presets(self):
        config = AppConfig()
        assert len(config.presets) > 0
        assert config.presets[0] == ("Custom", 0, 0)
        assert ("1920x1080", 1920, 1080) in config.presets
        assert ("1280x720", 1280, 720) in config.presets

    def test_get_preset_dimensions(self):
        config = AppConfig()

        w, h = config.get_preset_dimensions("1920x1080")
        assert w == 1920
        assert h == 1080

        w, h = config.get_preset_dimensions("640x480")
        assert w == 640
        assert h == 480

    def test_get_preset_dimensions_custom(self):
        config = AppConfig()
        w, h = config.get_preset_dimensions("Custom")
        assert w == 0
        assert h == 0

    def test_get_preset_dimensions_unknown(self):
        config = AppConfig()
        w, h = config.get_preset_dimensions("Unknown")
        assert w == 0
        assert h == 0

    def test_from_dict(self):
        data = {
            "default_width": 640,
            "default_height": 480,
        }
        config = AppConfig.from_dict(data)
        assert config.default_width == 640
        assert config.default_height == 480
        # Other fields should use defaults
        assert config.jpeg_quality == 95

    def test_from_dict_unknown_fields_ignored(self):
        data = {
            "default_width": 640,
            "unknown_field": "ignored",
        }
        config = AppConfig.from_dict(data)
        assert config.default_width == 640
        # Should not raise