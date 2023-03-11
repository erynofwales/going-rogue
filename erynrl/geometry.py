# Eryn Wells <eryn@erynwells.me>

'''A bunch of geometric primitives'''

import math
from dataclasses import dataclass
from typing import Iterator, Optional, overload, Tuple


@dataclass
class Point:
    '''A two-dimensional point, with coordinates in X and Y axes'''

    x: int = 0
    y: int = 0

    @property
    def numpy_index(self) -> Tuple[int, int]:
        '''Convert this Point into a tuple suitable for indexing into a numpy map array'''
        return (self.x, self.y)

    @property
    def neighbors(self) -> Iterator['Point']:
        '''Iterator over the neighboring points of `self` in all eight directions.'''
        for direction in Direction.all():
            yield self + direction

    def is_adjacent_to(self, other: 'Point') -> bool:
        '''Check if this point is adjacent to, but not overlapping the given point

        Parameters
        ----------
        other : Point
            The point to check

        Returns
        -------
        bool
            True if this point is adjacent to the other point
        '''
        if self == other:
            return False

        return (self.x - 1 <= other.x <= self.x + 1) and (self.y - 1 <= other.y <= self.y + 1)

    def direction_to_adjacent_point(self, other: 'Point') -> Optional['Vector']:
        '''
        Given a point directly adjacent to `self`, return a Vector indicating in
        which direction it is adjacent.
        '''
        for direction in Direction.all():
            if (self + direction) != other:
                continue
            return direction

        return None

    def euclidean_distance_to(self, other: 'Point') -> float:
        '''Compute the Euclidean distance to another Point'''
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def manhattan_distance_to(self, other: 'Point') -> int:
        '''Compute the Manhattan distance to another Point'''
        return abs(self.x - other.x) + abs(self.y - other.y)

    def __add__(self, other: 'Vector') -> 'Point':
        if not isinstance(other, Vector):
            raise TypeError('Only Vector can be added to a Point')
        return Point(self.x + other.dx, self.y + other.dy)

    def __sub__(self, other: 'Vector') -> 'Point':
        if not isinstance(other, Vector):
            raise TypeError('Only Vector can be added to a Point')
        return Point(self.x - other.dx, self.y - other.dy)

    def __lt__(self, other: 'Point') -> bool:
        return self.x < other.x and self.y < other.y

    def __le__(self, other: 'Point') -> bool:
        return self.x <= other.x and self.y <= other.y

    def __gt__(self, other: 'Point') -> bool:
        return self.x > other.x and self.y > other.y

    def __ge__(self, other: 'Point') -> bool:
        return self.x >= other.x and self.y >= other.y

    def __iter__(self):
        yield self.x
        yield self.y

    def __str__(self):
        return f'(x:{self.x}, y:{self.y})'


@dataclass
class Vector:
    '''A two-dimensional vector, representing change in position in X and Y axes'''

    dx: int = 0
    dy: int = 0

    @classmethod
    def from_point(cls, point: Point) -> 'Vector':
        '''Create a Vector from a Point'''
        return Vector(point.x, point.y)

    def __iter__(self):
        yield self.dx
        yield self.dy

    def __str__(self):
        return f'(δx:{self.dx}, δy:{self.dy})'


class Direction:
    '''
    A collection of simple uint vectors in each of the eight major compass
    directions. This is a namespace, not a class.
    '''

    North = Vector(0, -1)
    NorthEast = Vector(1, -1)
    East = Vector(1, 0)
    SouthEast = Vector(1, 1)
    South = Vector(0, 1)
    SouthWest = Vector(-1, 1)
    West = Vector(-1, 0)
    NorthWest = Vector(-1, -1)

    @classmethod
    def all(cls) -> Iterator[Vector]:
        '''Iterate through all directions, starting with North and proceeding clockwise'''
        yield Direction.North
        yield Direction.NorthEast
        yield Direction.East
        yield Direction.SouthEast
        yield Direction.South
        yield Direction.SouthWest
        yield Direction.West
        yield Direction.NorthWest


@dataclass
class Size:
    '''A two-dimensional size, representing size in X (width) and Y (height) axes'''

    width: int = 0
    height: int = 0

    @property
    def numpy_shape(self) -> Tuple[int, int]:
        '''Return a tuple suitable for passing into numpy array initializers for specifying the shape of the array.'''
        return (self.width, self.height)

    def __iter__(self):
        yield self.width
        yield self.height

    def __str__(self):
        return f'(w:{self.width}, h:{self.height})'


@dataclass
class Rect:
    '''
    A two-dimensional rectangle defined by an origin point and size
    '''

    origin: Point
    size: Size

    @staticmethod
    def from_raw_values(x: int, y: int, width: int, height: int):
        '''Create a rect from raw (unpacked from their struct) values'''
        return Rect(Point(x, y), Size(width, height))

    @property
    def min_x(self) -> int:
        '''Minimum x-value that is still within the bounds of this rectangle. This is the origin's x-value.'''
        return self.origin.x

    @property
    def min_y(self) -> int:
        '''Minimum y-value that is still within the bounds of this rectangle. This is the origin's y-value.'''
        return self.origin.y

    @property
    def mid_x(self) -> int:
        '''The x-value of the center point of this rectangle.'''
        return self.origin.x + self.size.width // 2

    @property
    def mid_y(self) -> int:
        '''The y-value of the center point of this rectangle.'''
        return self.origin.y + self.size.height // 2

    @property
    def max_x(self) -> int:
        '''Maximum x-value that is still within the bounds of this rectangle.'''
        return self.origin.x + self.size.width - 1

    @property
    def max_y(self) -> int:
        '''Maximum y-value that is still within the bounds of this rectangle.'''
        return self.origin.y + self.size.height - 1

    @property
    def end_x(self) -> int:
        '''X-value beyond the end of the rectangle.'''
        return self.origin.x + self.size.width

    @property
    def end_y(self) -> int:
        '''Y-value beyond the end of the rectangle.'''
        return self.origin.y + self.size.height

    @property
    def width(self) -> int:
        '''The width of the rectangle. A convenience property for accessing `self.size.width`.'''
        return self.size.width

    @property
    def height(self) -> int:
        '''The height of the rectangle. A convenience property for accessing `self.size.height`.'''
        return self.size.height

    @property
    def midpoint(self) -> Point:
        '''A Point in the middle of the Rect'''
        return Point(self.mid_x, self.mid_y)

    @property
    def corners(self) -> Iterator[Point]:
        '''An iterator over the corners of this rectangle'''
        yield self.origin
        yield Point(self.max_x, self.min_y)
        yield Point(self.min_x, self.max_y)
        yield Point(self.max_x, self.max_y)

    @property
    def edges(self) -> Iterator[int]:
        '''
        An iterator over the edges of this Rect in the order of: `min_x`, `max_x`, `min_y`, `max_y`.
        '''
        yield self.min_x
        yield self.max_x
        yield self.min_y
        yield self.max_y

    def intersects(self, other: 'Rect') -> bool:
        '''Returns `True` if `other` intersects this Rect.'''
        if other.min_x > self.max_x:
            return False

        if other.max_x < self.min_x:
            return False

        if other.min_y > self.max_y:
            return False

        if other.max_y < self.min_y:
            return False

        return True

    def inset_rect(self, top: int = 0, right: int = 0, bottom: int = 0, left: int = 0) -> 'Rect':
        '''
        Create a new Rect inset from this rect by the specified values.

        Arguments are listed in clockwise order around the permeter. This method
        doesn't validate the returned Rect, or transform it to a canonical
        representation with the origin at the top-left.

        ### Parameters

        `top`: int
            Amount to inset from the top
        `right`: int
            Amount to inset from the right
        `bottom`: int
            Amount to inset from the bottom
        `left`: int
            Amount to inset from the left

        ### Returns

        Rect
            A new Rect, inset from `self` by the given amount on each side
        '''
        return Rect(Point(self.origin.x + left, self.origin.y + top),
                    Size(self.size.width - right - left, self.size.height - top - bottom))

    @overload
    def __contains__(self, other: Point) -> bool:
        ...

    @overload
    def __contains__(self, other: 'Rect') -> bool:
        ...

    def __contains__(self, other: 'Point | Rect') -> bool:
        if isinstance(other, Point):
            return self.__contains_point(other)

        if isinstance(other, Rect):
            return self.__contains_rect(other)

        raise TypeError(f'{self.__class__.__name__} cannot contain value of type {other.__class__.__name__}')

    def __contains_point(self, pt: Point) -> bool:
        return self.min_x <= pt.x <= self.max_x and self.min_y <= pt.y <= self.max_y

    def __contains_rect(self, other: 'Rect') -> bool:
        return (self.min_x <= other.min_x
                and self.max_x >= other.max_x
                and self.min_y <= other.min_y
                and self.max_y >= other.max_y)

    def __iter__(self):
        yield tuple(self.origin)
        yield tuple(self.size)

    def __str__(self):
        return f'[{self.origin}, {self.size}]'
