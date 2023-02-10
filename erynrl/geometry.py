# Eryn Wells <eryn@erynwells.me>

'''A bunch of geometric primitives'''

import math
from dataclasses import dataclass
from typing import Any, Iterator, Optional, overload


@dataclass(frozen=True)
class Point:
    '''A two-dimensional point, with coordinates in X and Y axes'''

    x: int = 0
    y: int = 0

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
        return (self.x in (other.x - 1, other.x + 1)) and (self.y in (other.y - 1, other.y + 1))

    def direction_to_adjacent_point(self, other: 'Point') -> Optional['Vector']:
        for direction in Direction.all():
            if (self + direction) != other:
                continue
            return direction

        return None

    def euclidean_distance_to(self, other: 'Point') -> float:
        '''Compute the Euclidean distance to another Point'''
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    @overload
    def __add__(self, other: 'Vector') -> 'Point':
        ...

    def __add__(self, other: Any) -> 'Point':
        if not isinstance(other, Vector):
            raise TypeError('Only Vector can be added to a Point')
        return Point(self.x + other.dx, self.y + other.dy)

    def __iter__(self):
        yield self.x
        yield self.y

    def __str__(self):
        return f'(x:{self.x}, y:{self.y})'


@dataclass(frozen=True)
class Vector:
    '''A two-dimensional vector, representing change in position in X and Y axes'''

    dx: int = 0
    dy: int = 0

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


@dataclass(frozen=True)
class Size:
    '''A two-dimensional size, representing size in X (width) and Y (height) axes'''

    width: int = 0
    height: int = 0

    def __iter__(self):
        yield self.width
        yield self.height

    def __str__(self):
        return f'(w:{self.width}, h:{self.height})'


@dataclass(frozen=True)
class Rect:
    '''A two-dimensional rectangle, defined by an origin point and size'''

    origin: Point
    size: Size

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
        return int(self.origin.x + self.size.width / 2)

    @property
    def mid_y(self) -> int:
        '''The y-value of the center point of this rectangle.'''
        return int(self.origin.y + self.size.height / 2)

    @property
    def max_x(self) -> int:
        '''Maximum x-value that is still within the bounds of this rectangle.'''
        return self.origin.x + self.size.width - 1

    @property
    def max_y(self) -> int:
        '''Maximum y-value that is still within the bounds of this rectangle.'''
        return self.origin.y + self.size.height - 1

    @property
    def midpoint(self) -> Point:
        '''A Point in the middle of the Rect'''
        return Point(self.mid_x, self.mid_y)

    def inset_rect(self, top: int = 0, right: int = 0, bottom: int = 0, left: int = 0) -> 'Rect':
        '''
        Return a new Rect inset from this rect by the specified values. Arguments are listed in clockwise order around
        the permeter. This method doesn't validate the returned Rect, or transform it to a canonical representation with
        the origin at the top-left.

        Parameters
        ----------
        top : int
            Amount to inset from the top
        right : int
            Amount to inset from the right
        bottom : int
            Amount to inset from the bottom
        left : int
            Amount to inset from the left

        Returns
        -------
        Rect
            A new Rect, inset from `self` by the given amount on each side
        '''
        return Rect(Point(self.origin.x + left, self.origin.y + top),
                    Size(self.size.width - right - left, self.size.height - top - bottom))

    def __iter__(self):
        yield tuple(self.origin)
        yield tuple(self.size)

    def __str__(self):
        return f'[{self.origin}, {self.size}]'
