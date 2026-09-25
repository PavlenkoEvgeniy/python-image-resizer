"""Utilities for positioning tkinter windows."""

import tkinter as tk


def center_on_parent(parent: tk.Wm, window: tk.Wm) -> None:
    """Center window on its parent's area.

    The window keeps its current size; a not-yet-mapped window is sized
    to its requested size. The position is clamped so the window stays
    fully visible on the parent's screen.
    """
    window.update_idletasks()
    width, height = _window_size(window)
    x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
    y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
    x, y = _clamped_origin(
        x, y, width, height,
        parent.winfo_screenwidth(), parent.winfo_screenheight(),
    )
    _move_window(window, x, y, width, height)


def _move_window(window: tk.Wm, x: int, y: int, width: int, height: int) -> None:
    """Move window to the given position, correcting for window-manager offsets.

    Some window managers treat a geometry position as the position of the
    window frame, shifting the client area down by the title bar height.
    Measure the actual placement and re-apply the difference.
    """
    window.geometry(f"{width}x{height}+{x}+{y}")
    window.update()
    error_x = x - window.winfo_rootx()
    error_y = y - window.winfo_rooty()
    if error_x or error_y:
        window.geometry(f"{width}x{height}+{x + error_x}+{y + error_y}")
        window.update()


def _window_size(window: tk.Wm) -> tuple[int, int]:
    """Actual size of a mapped window, or requested size before mapping."""
    width = window.winfo_width()
    height = window.winfo_height()
    if width <= 1 or height <= 1:
        width = window.winfo_reqwidth()
        height = window.winfo_reqheight()
    return width, height


def _clamped_origin(
    x: int, y: int,
    width: int, height: int,
    screen_width: int, screen_height: int,
) -> tuple[int, int]:
    """Keep the window fully inside the given screen bounds."""
    return (
        max(0, min(x, screen_width - width)),
        max(0, min(y, screen_height - height)),
    )