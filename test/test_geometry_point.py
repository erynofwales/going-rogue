# Eryn Wells <eryn@erynwells.me>

from erynrl.geometry import Point


def test_point_neighbors():
    '''Check that Point.neighbors returns all neighbors'''
    test_point = Point(5, 5)

    expected_neighbors = set([
        Point(4, 4),
        Point(5, 4),
        Point(6, 4),
        Point(4, 5),
        # Point(5, 5),
        Point(6, 5),
        Point(4, 6),
        Point(5, 6),
        Point(6, 6),
    ])

    neighbors = set(test_point.neighbors)
    for pt in expected_neighbors:
        assert pt in neighbors

    assert expected_neighbors - neighbors == set(), \
        f"Found some points that didn't belong in the set of neighbors of {test_point}"


def test_point_manhattan_distance():
    '''Check that the Manhattan Distance calculation on Points is correct'''
    point_a = Point(3, 2)
    point_b = Point(8, 5)

    assert point_a.manhattan_distance_to(point_b) == 8
