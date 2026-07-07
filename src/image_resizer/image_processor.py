"""Image processing core functionality."""

import os
from pathlib import Path
from typing import Optional
from enum import Enum

from PIL import Image


class OutputFormat(Enum):
    """Supported output image formats."""

    JPEG = "JPEG"
    PNG = "PNG"
    WEBP = "WEBP"
    BMP = "BMP"

    @property
    def extension(self) -> str:
        """Get file extension for this format."""
        return "jpg" if self.value == "JPEG" else self.value.lower()


class ResizeResult:
    """Result of an image resize operation."""

    def __init__(
        self,
        success: bool,
        output_path: Optional[Path] = None,
        error: Optional[str] = None,
    ):
        self.success = success
        self.output_path = output_path
        self.error = error


class ImageProcessor:
    """Handles image resizing operations."""

    SUPPORTED_INPUT_FORMATS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}

    def __init__(self, output_format: OutputFormat = OutputFormat.JPEG, quality: int = 95):
        """Initialize the image processor.

        Args:
            output_format: The output format for resized images.
            quality: JPEG quality (1-100).
        """
        self.output_format = output_format
        self.quality = quality

    def is_supported(self, file_path: Path | str) -> bool:
        """Check if a file is a supported image format.

        Args:
            file_path: Path to the image file.

        Returns:
            True if the file format is supported.
        """
        return Path(file_path).suffix.lower() in self.SUPPORTED_INPUT_FORMATS

    def resize(
        self,
        input_path: Path | str,
        output_dir: Path | str,
        target_width: int,
        target_height: int,
        maintain_aspect: bool = True,
        add_dimensions_to_filename: bool = True,
    ) -> ResizeResult:
        """Resize an image to target dimensions.

        Args:
            input_path: Path to the input image.
            output_dir: Directory for the output image.
            target_width: Target width in pixels.
            target_height: Target height in pixels.
            maintain_aspect: Whether to maintain aspect ratio.
            add_dimensions_to_filename: Whether to add dimensions to output filename.

        Returns:
            ResizeResult indicating success or failure with details.
        """
        input_path = Path(input_path)
        output_dir = Path(output_dir)

        if not input_path.exists():
            return ResizeResult(
                success=False,
                error=f"Input file not found: {input_path}",
            )

        try:
            with Image.open(input_path) as img:
                if maintain_aspect:
                    new_width, new_height = self._calculate_aspect_ratio(
                        img.width, img.height, target_width, target_height
                    )
                else:
                    new_width, new_height = target_width, target_height

                resized = img.resize(
                    (new_width, new_height),
                    Image.Resampling.LANCZOS,
                )

                output_path = self._get_output_path(
                    input_path,
                    output_dir,
                    new_width,
                    new_height,
                    add_dimensions_to_filename,
                )

                self._save_image(resized, output_path)

                return ResizeResult(success=True, output_path=output_path)

        except Exception as e:
            return ResizeResult(
                success=False,
                error=f"Failed to process {input_path.name}: {str(e)}",
            )

    def _calculate_aspect_ratio(
        self,
        original_width: int,
        original_height: int,
        target_width: int,
        target_height: int,
    ) -> tuple[int, int]:
        """Calculate new dimensions maintaining aspect ratio.

        Args:
            original_width: Original image width.
            original_height: Original image height.
            target_width: Target width.
            target_height: Target height.

        Returns:
            Tuple of (new_width, new_height).
        """
        ratio = min(target_width / original_width, target_height / original_height)
        return (
            int(original_width * ratio),
            int(original_height * ratio),
        )

    def _get_output_path(
        self,
        input_path: Path,
        output_dir: Path,
        width: int,
        height: int,
        add_dimensions: bool,
    ) -> Path:
        """Determine the output file path.

        Args:
            input_path: Path to the input file.
            output_dir: Output directory.
            width: Resized width.
            height: Resized height.
            add_dimensions: Whether to add dimensions to filename.

        Returns:
            Path for the output file.
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        stem = input_path.stem
        if add_dimensions:
            stem = f"{stem}_{width}x{height}"

        if self.output_format == OutputFormat.JPEG:
            extension = "jpg"
        else:
            extension = self.output_format.extension

        return output_dir / f"{stem}.{extension}"

    def _save_image(self, img: Image.Image, output_path: Path) -> None:
        """Save the image with appropriate format handling.

        Args:
            img: The PIL Image to save.
            output_path: Path where the image will be saved.
        """
        save_kwargs = {}

        if self.output_format == OutputFormat.JPEG:
            # Handle transparency for JPEG
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(
                    img,
                    mask=img.split()[-1] if img.mode == "RGBA" else None,
                )
                img = background
            save_kwargs["quality"] = self.quality
            save_kwargs["optimize"] = True

        elif self.output_format == OutputFormat.PNG:
            save_kwargs["optimize"] = True

        img.save(output_path, format=self.output_format.value, **save_kwargs)