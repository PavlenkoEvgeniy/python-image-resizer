"""Tests for image_processor module."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from image_resizer.image_processor import (
    ImageProcessor,
    OutputFormat,
    ResizeResult,
)


class TestOutputFormat:
    """Tests for OutputFormat enum."""

    def test_jpeg_extension(self):
        assert OutputFormat.JPEG.extension == "jpg"


class TestResizeResult:
    """Tests for ResizeResult class."""

    def test_success_result(self):
        result = ResizeResult(success=True, output_path=Path("/output/test.jpg"))
        assert result.success is True
        assert result.output_path == Path("/output/test.jpg")
        assert result.error is None

    def test_failure_result(self):
        result = ResizeResult(success=False, error="Some error")
        assert result.success is False
        assert result.output_path is None
        assert result.error == "Some error"


class TestImageProcessor:
    """Tests for ImageProcessor class."""

    @pytest.fixture
    def processor(self):
        """Create an ImageProcessor instance."""
        return ImageProcessor(output_format=OutputFormat.JPEG, quality=95)

    @pytest.fixture
    def sample_image_path(self, tmp_path):
        """Create a sample image path."""
        return tmp_path / "test_image.jpg"

    def test_init_defaults(self):
        processor = ImageProcessor()
        assert processor.output_format == OutputFormat.JPEG
        assert processor.quality == 95

    def test_init_custom(self):
        processor = ImageProcessor(output_format=OutputFormat.PNG, quality=85)
        assert processor.output_format == OutputFormat.PNG
        assert processor.quality == 85

    def test_is_supported_jpeg(self, processor):
        assert processor.is_supported("test.jpg") is True
        assert processor.is_supported("test.jpeg") is True

    def test_is_supported_png(self, processor):
        assert processor.is_supported("test.png") is True

    def test_is_supported_webp(self, processor):
        assert processor.is_supported("test.webp") is True

    def test_is_supported_bmp(self, processor):
        assert processor.is_supported("test.bmp") is True

    def test_is_supported_gif(self, processor):
        assert processor.is_supported("test.gif") is True

    def test_is_supported_unsupported(self, processor):
        assert processor.is_supported("test.txt") is False
        assert processor.is_supported("test.pdf") is False

    def test_resize_nonexistent_file(self, processor, tmp_path):
        result = processor.resize(
            tmp_path / "nonexistent.jpg",
            tmp_path,
            800,
            600,
        )
        assert result.success is False
        assert "not found" in result.error.lower()

    @patch("image_resizer.image_processor.Image.open")
    def test_resize_without_aspect_ratio(self, mock_open, processor, tmp_path):
        # Create a file that exists
        test_file = tmp_path / "test.jpg"
        test_file.touch()
        
        mock_img = MagicMock()
        mock_img.size = (1000, 800)
        mock_img.mode = "RGB"
        
        mock_resized = MagicMock()
        mock_resized.mode = "RGB"
        mock_resized.save = MagicMock()
        
        mock_img.resize = MagicMock(return_value=mock_resized)
        mock_open.return_value.__enter__.return_value = mock_img

        result = processor.resize(
            test_file,
            tmp_path,
            400,
            300,
            maintain_aspect=False,
        )

        assert result.success is True

    @patch("image_resizer.image_processor.Image.open")
    def test_resize_with_aspect_ratio(self, mock_open, processor, tmp_path):
        test_file = tmp_path / "test.jpg"
        test_file.touch()
        
        mock_img = MagicMock()
        # Use actual integers for size
        mock_img.size = (1920, 1080)
        mock_img.width = 1920
        mock_img.height = 1080
        mock_img.mode = "RGB"
        
        mock_resized = MagicMock()
        mock_resized.mode = "RGB"
        mock_resized.save = MagicMock()
        
        mock_img.resize = MagicMock(return_value=mock_resized)
        mock_open.return_value.__enter__.return_value = mock_img

        result = processor.resize(
            test_file,
            tmp_path,
            800,
            600,
            maintain_aspect=True,
        )

        assert result.success is True
        call_args = mock_img.resize.call_args[0][0]
        assert call_args[0] <= 800
        assert call_args[1] <= 600

    @patch("image_resizer.image_processor.Image.open")
    def test_resize_adds_dimensions_to_filename(self, mock_open, processor, tmp_path):
        test_file = tmp_path / "photo.jpg"
        test_file.touch()
        
        mock_img = MagicMock()
        mock_img.size = (1000, 800)
        mock_img.width = 1000
        mock_img.height = 800
        mock_img.mode = "RGB"
        
        mock_resized = MagicMock()
        mock_resized.mode = "RGB"
        mock_resized.save = MagicMock()
        
        mock_img.resize = MagicMock(return_value=mock_resized)
        mock_open.return_value.__enter__.return_value = mock_img

        result = processor.resize(
            test_file,
            tmp_path,
            640,
            480,
            maintain_aspect=False,
            add_dimensions_to_filename=True,
        )

        assert result.success is True
        assert result.output_path is not None
        # With maintain_aspect=False, it uses exact target dimensions
        assert "640x480" in str(result.output_path)

    @patch("image_resizer.image_processor.Image.open")
    def test_resize_handles_rgba_for_jpeg(self, mock_open, processor, tmp_path):
        test_file = tmp_path / "transparent.png"
        test_file.touch()
        
        # Create a more complete mock that handles PIL operations
        mock_img = MagicMock()
        mock_img.size = (100, 100)
        mock_img.width = 100
        mock_img.height = 100
        mock_img.mode = "RGBA"

        # Mock the split method to return channels
        mock_channel = MagicMock()
        mock_img.split = MagicMock(return_value=[
            MagicMock(), MagicMock(), MagicMock(), mock_channel
        ])
        
        mock_resized = MagicMock()
        mock_resized.mode = "RGBA"
        mock_resized.size = (100, 100)
        mock_resized.width = 100
        mock_resized.height = 100
        mock_resized.split = MagicMock(return_value=[
            MagicMock(), MagicMock(), MagicMock(), mock_channel
        ])
        
        # Mock Image.new to return a proper background
        mock_background = MagicMock()
        mock_background.size = (100, 100)
        mock_background.paste = MagicMock()
        mock_background.split = MagicMock(return_value=[
            MagicMock(), MagicMock(), MagicMock()
        ])
        
        with patch("image_resizer.image_processor.Image.new", return_value=mock_background):
            mock_img.resize = MagicMock(return_value=mock_resized)
            mock_open.return_value.__enter__.return_value = mock_img

            # Use maintain_aspect=False for predictable dimensions
            result = processor.resize(
                test_file,
                tmp_path,
                100,
                100,
                maintain_aspect=False,
            )

            assert result.success is True


class TestImageProcessorCalculateAspectRatio:
    """Tests for aspect ratio calculation."""

    def test_wider_image(self):
        processor = ImageProcessor()
        w, h = processor._calculate_aspect_ratio(1920, 1080, 800, 600)
        assert w == 800
        assert h == 450

    def test_taller_image(self):
        processor = ImageProcessor()
        w, h = processor._calculate_aspect_ratio(600, 800, 800, 600)
        assert w == 450
        assert h == 600

    def test_exact_fit(self):
        processor = ImageProcessor()
        w, h = processor._calculate_aspect_ratio(800, 600, 800, 600)
        assert w == 800
        assert h == 600

    def test_larger_target(self):
        processor = ImageProcessor()
        w, h = processor._calculate_aspect_ratio(100, 100, 800, 600)
        # Since image is smaller, it gets upscaled to fit
        assert w == 600
        assert h == 600