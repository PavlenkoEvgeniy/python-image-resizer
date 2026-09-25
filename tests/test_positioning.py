"""Tests for window positioning helpers."""

from image_resizer.positioning import centered_origin


def test_centers_window_on_screen():
    assert centered_origin((1920, 1080), (800, 650)) == (560, 215)


def test_window_equal_to_container_starts_at_origin():
    assert centered_origin((800, 650), (800, 650)) == (0, 0)


def test_window_larger_than_container_gives_negative_origin():
    assert centered_origin((100, 100), (200, 300)) == (-50, -100)


def test_odd_difference_rounds_down():
    assert centered_origin((101, 101), (50, 50)) == (25, 25)