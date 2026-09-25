"""Window positioning helpers shared by the main window and dialogs."""

import tkinter as tk
from typing import Optional


def centered_origin(
    container_size: tuple[int, int], window_size: tuple[int, int]
) -> tuple[int, int]:
    """Compute the origin that centers a window inside a container.

    Args:
        container_size: (width, height) of the area to center within.
        window_size: (width, height) of the window to center.

    Returns:
        (x, y) offset relative to the container's top-left corner.
        Negative when the window is larger than the container.
    """
    x = (container_size[0] - window_size[0]) // 2
    y = (container_size[1] - window_size[1]) // 2
    return x, y


def center_on_screen(window: tk.Wm, width: int, height: int) -> None:
    """Position and size a window centered on the primary screen.

    Args:
        window: Window to position.
        width: Window width.
        height: Window height.
    """
    screen_size = (window.winfo_screenwidth(), window.winfo_screenheight())
    x, y = centered_origin(screen_size, (width, height))
    # Never let the window start off-screen.
    window.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")


def center_over_parent(
    window: tk.Wm,
    parent: tk.Wm,
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> None:
    """Position a window centered over its parent window.

    Centers over the parent's current on-screen rectangle, so the dialog
    lands on the same monitor as the parent. When width/height are omitted,
    the window's requested size is used.

    Args:
        window: Window to position.
        parent: Window to center over.
        width: Optional fixed window width.
        height: Optional fixed window height.
    """
    window.update_idletasks()
    w = width if width is not None else window.winfo_reqwidth()
    h = height if height is not None else window.winfo_reqheight()
    x, y = centered_origin((parent.winfo_width(), parent.winfo_height()), (w, h))
    window.geometry(f"{w}x{h}+{parent.winfo_rootx() + x}+{parent.winfo_rooty() + y}")