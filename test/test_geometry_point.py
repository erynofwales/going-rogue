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


def test_point_is_adjacent_to():
    '''Check that Point.is_adjacent_to correctly computes adjacency'''
    test_point = Point(5, 5)

    assert not test_point.is_adjacent_to(test_point), \
        f"{test_point!s} should not be considered adjacent to itself"

    for neighbor in test_point.neighbors:
        assert test_point.is_adjacent_to(neighbor), \
            f"Neighbor {neighbor!s} that was not considered adjacent to {test_point!s}"

    assert not test_point.is_adjacent_to(Point(3, 5))
    assert not test_point.is_adjacent_to(Point(7, 5))
    assert not test_point.is_adjacent_to(Point(5, 3))
    assert not test_point.is_adjacent_to(Point(5, 7))
