# Eryn Wells <eryn@erynwells.me>

from erynrl.geometry import Point, Rect, Size


def test_rect_corners():
    rect = Rect(Point(5, 5), Size(5, 5))

    corners = set(rect.corners)

    expected_corners = set([
        Point(5, 5),
        Point(9, 5),
        Point(5, 9),
        Point(9, 9)
    ])

    assert corners == expected_corners
