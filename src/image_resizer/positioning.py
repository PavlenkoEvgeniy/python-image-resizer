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


def choose_monitor(
    monitors: list[tuple[int, int, int, int]], pointer: tuple[int, int]
) -> Optional[tuple[int, int, int, int]]:
    """Pick the monitor that contains the given point.

    Args:
        monitors: Monitor rectangles as (x, y, width, height).
        pointer: Global (x, y) point, e.g. the current mouse position.

    Returns:
        The containing monitor rectangle, or None when the point is
        outside every monitor (or the list is empty).
    """
    px, py = pointer
    for x, y, width, height in monitors:
        if x <= px < x + width and y <= py < y + height:
            return x, y, width, height
    return None


def detect_monitors() -> list[tuple[int, int, int, int]]:
    """Best-effort monitor detection.

    Returns:
        Monitor rectangles as (x, y, width, height); empty when
        monitor detection is unavailable (screeninfo missing, native
        Wayland, etc.) and callers should fall back to the whole screen.
    """
    try:
        from screeninfo import get_monitors

        return [(m.x, m.y, m.width, m.height) for m in get_monitors()]
    except Exception:
        return []


def center_on_screen(
    window: tk.Wm,
    width: int,
    height: int,
    monitors: Optional[list[tuple[int, int, int, int]]] = None,
) -> None:
    """Position and size a window centered inside a monitor.

    The window is centered on the monitor that currently holds the mouse
    pointer, so on multi-monitor setups the window opens where the user
    is working instead of straddling the seam between monitors (Tk
    reports all monitors as one combined virtual screen). When monitor
    detection is unavailable or the pointer is outside every monitor,
    the window falls back to centering on the whole virtual screen.

    Args:
        window: Window to position.
        width: Window width.
        height: Window height.
        monitors: Monitor rectangles to use instead of detecting them.
    """
    if monitors is None:
        monitors = detect_monitors()
    monitor = choose_monitor(
        monitors, (window.winfo_pointerx(), window.winfo_pointery())
    )

    if monitor is not None:
        mx, my, mw, mh = monitor
        dx, dy = centered_origin((mw, mh), (width, height))
        x = mx + max(0, min(dx, max(0, mw - width)))
        y = my + max(0, min(dy, max(0, mh - height)))
    else:
        screen_size = (window.winfo_screenwidth(), window.winfo_screenheight())
        x, y = centered_origin(screen_size, (width, height))
        x = max(0, x)
        y = max(0, y)

    window.geometry(f"{width}x{height}+{x}+{y}")
    _align_client(window, x, y, width, height)


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
    x += parent.winfo_rootx()
    y += parent.winfo_rooty()
    window.geometry(f"{w}x{h}+{x}+{y}")
    _align_client(window, x, y, w, h)


def _align_client(
    window: tk.Wm, x: int, y: int, width: int, height: int
) -> None:
    """Move a mapped window so its client area lands at the requested point.

    Some window managers treat a geometry position as the position of the
    window frame, shifting the client area down by the title bar height.
    Measure the actual placement once the window is mapped and re-apply
    the difference.
    """
    window.update()
    if not window.winfo_ismapped():
        return
    error_x = x - window.winfo_rootx()
    error_y = y - window.winfo_rooty()
    if error_x or error_y:
        window.geometry(f"{width}x{height}+{x + error_x}+{y + error_y}")
        window.update()