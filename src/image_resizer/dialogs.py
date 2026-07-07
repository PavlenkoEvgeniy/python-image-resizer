"""UI dialogs for the Image Resizer application."""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from image_resizer import __version__, __author__, __email__


class AboutDialog:
    """About dialog window."""

    def __init__(self, parent: tk.Tk):
        """Create the about dialog.

        Args:
            parent: Parent window.
        """
        self.window = tk.Toplevel(parent)
        self.window.title("About Image Resizer Pro")
        self.window.geometry("420x380")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        self.window.focus_set()

        # Center dialog on screen
        self.window.update()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = 420
        window_height = 380
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self._create_content()

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

        ttk.Separator(frame, orient="horizontal").pack(fill=tk.X, pady=(15, 15))

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


class ErrorDialog:
    """Helper class for showing error dialogs."""

    @staticmethod
    def show_error(title: str, message: str) -> None:
        """Show an error message box.

        Args:
            title: Dialog title.
            message: Error message.
        """
        from tkinter import messagebox
        messagebox.showerror(title, message)

    @staticmethod
    def show_warning(title: str, message: str) -> None:
        """Show a warning message box.

        Args:
            title: Dialog title.
            message: Warning message.
        """
        from tkinter import messagebox
        messagebox.showwarning(title, message)

    @staticmethod
    def show_info(title: str, message: str) -> None:
        """Show an info message box.

        Args:
            title: Dialog title.
            message: Info message.
        """
        from tkinter import messagebox
        messagebox.showinfo(title, message)