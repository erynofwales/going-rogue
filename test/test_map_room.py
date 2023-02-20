# Eryn Wells <eryn@erynwells.me>

from erynrl.geometry import Point, Rect, Size
from erynrl.map.room import RectangularRoom


def test_rectangular_room_wall_points():
    '''Check that RectangularRoom.wall_points returns the correct set of points'''
    rect = Rect(Point(5, 5), Size(5, 5))
    room = RectangularRoom(rect)

    expected_points = set([
        Point(5, 5),
        Point(6, 5),
        Point(7, 5),
        Point(8, 5),
        Point(9, 5),
        Point(9, 6),
        Point(9, 7),
        Point(9, 8),
        Point(9, 9),
        Point(8, 9),
        Point(7, 9),
        Point(6, 9),
        Point(5, 9),
        Point(5, 8),
        Point(5, 7),
        Point(5, 6),
    ])

    for pt in room.wall_points:
        expected_points.remove(pt)

    assert len(expected_points) == 0
