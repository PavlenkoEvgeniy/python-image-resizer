"""Smoke tests for the main window module.

The app once crashed at startup because the merged code referenced
undefined window-size constants. These tests import the module so that
a regression fails here, not at first app launch.
"""


def test_main_window_module_imports():
    from image_resizer import main_window  # noqa: F401


def test_main_window_size_constants_exist():
    from image_resizer.main_window import WINDOW_HEIGHT, WINDOW_WIDTH

    assert WINDOW_WIDTH > 0
    assert WINDOW_HEIGHT > 0