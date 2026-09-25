"""UI dialogs for the Image Resizer application."""

import tkinter as tk
from tkinter import ttk

from image_resizer import __version__, __author__, __email__
from image_resizer.positioning import center_over_parent

# Fixed About dialog size, the single source of truth.
ABOUT_WIDTH = 420
ABOUT_HEIGHT = 380


class AboutDialog:
    """About dialog window."""

    def __init__(self, parent: tk.Wm):
        """Create the about dialog.

        Args:
            parent: Parent window.
        """
        self.window = tk.Toplevel(parent)
        self.window.title("About Image Resizer Pro")
        self.window.resizable(False, False)
        self.window.transient(parent)

        self._create_content()
        center_over_parent(self.window, parent, ABOUT_WIDTH, ABOUT_HEIGHT)

        self.window.wait_visibility()
        self.window.grab_set()
        self.window.focus_set()

    def _create_content(self) -> None:
        """Create the dialog content."""
        frame = ttk.Frame(self.window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # Title with emoji
        title_label = tk.Label(
            frame,
            text="📷 Image Resizer Pro",
            font=("Arial", 16, "bold"),
        )
        title_label.pack(pady=(0, 10))

        # Version
        version_label = ttk.Label(frame, text=f"Version {__version__}")
        version_label.pack(pady=(0, 15))

        ttk.Separator(frame, orient="horizontal").pack(fill=tk.X, pady=(0, 15))

        # License info
        license_label = ttk.Label(frame, text="License: Freeware")
        license_label.pack(anchor=tk.W, pady=2)

        copyright_label = ttk.Label(frame, text="Copyright © 2026")
        copyright_label.pack(anchor=tk.W, pady=2)

        author_label = ttk.Label(frame, text=f"Author: {__author__}")
        author_label.pack(anchor=tk.W, pady=2)

        email_label = ttk.Label(frame, text=f"Email: {__email__}")
        email_label.pack(anchor=tk.W, pady=2)

        ttk.Separator(frame, orient="horizontal").pack(fill=tk.X, pady=(0, 15))

        # Description
        desc_text = (
            "A simple and powerful tool for batch resizing images.\n"
            "Supports drag & drop, multiple formats, and aspect ratio preservation."
        )
        desc_label = tk.Label(
            frame,
            text=desc_text,
            font=("Arial", 9),
            wraplength=360,
            justify=tk.CENTER,
        )
        desc_label.pack(pady=(0, 15))

        # Close button
        close_btn = ttk.Button(frame, text="Close", command=self.window.destroy)
        close_btn.pack()


class MessageDialog:
    """Modal message dialog centered over its parent window.

    Auto-sized to its content, shown as error, warning or info depending
    on the level.
    """

    _STYLES = {
        "error": ("✖", "#b3261e"),
        "warning": ("⚠", "#b36b00"),
        "info": ("ℹ", "#1b6ec2"),
    }

    def __init__(self, parent: tk.Wm, level: str, title: str, message: str):
        """Create the message dialog.

        Args:
            parent: Parent window to center over.
            level: One of "error", "warning", "info".
            title: Dialog title.
            message: Message text.
        """
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.resizable(False, False)
        self.window.transient(parent)

        icon_text, color = self._STYLES[level]
        frame = ttk.Frame(self.window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        body = ttk.Frame(frame)
        body.pack()
        icon_label = tk.Label(body, text=icon_text, fg=color, font=("Arial", 24))
        icon_label.pack(side=tk.LEFT, padx=(0, 12))
        message_label = ttk.Label(
            body, text=message, wraplength=320, justify=tk.LEFT
        )
        message_label.pack(side=tk.LEFT)

        self.ok_button = ttk.Button(
            frame, text="OK", command=self.window.destroy, width=10
        )
        self.ok_button.pack(pady=(16, 0))

        center_over_parent(self.window, parent)

        self.window.bind("<Return>", lambda event: self.window.destroy())
        self.window.bind("<Escape>", lambda event: self.window.destroy())
        self.window.wait_visibility()
        self.window.grab_set()
        self.ok_button.focus_set()


class ErrorDialog:
    """Helper class for showing message dialogs centered over the main window."""

    @staticmethod
    def show_error(title: str, message: str, parent: tk.Wm) -> None:
        """Show an error message box.

        Args:
            title: Dialog title.
            message: Error message.
            parent: Window to center over.
        """
        MessageDialog(parent, "error", title, message)

    @staticmethod
    def show_warning(title: str, message: str, parent: tk.Wm) -> None:
        """Show a warning message box.

        Args:
            title: Dialog title.
            message: Warning message.
            parent: Window to center over.
        """
        MessageDialog(parent, "warning", title, message)

    @staticmethod
    def show_info(title: str, message: str, parent: tk.Wm) -> None:
        """Show an info message box.

        Args:
            title: Dialog title.
            message: Info message.
            parent: Window to center over.
        """
        MessageDialog(parent, "info", title, message)