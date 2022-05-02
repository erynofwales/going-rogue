#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

from dataclasses import dataclass
from typing import Any, Tuple, overload

@dataclass(frozen=True)
class Point:
    x: int = 0
    y: int = 0

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
    dx: int = 0
    dy: int = 0

    def __iter__(self):
        yield self.dx
        yield self.dy

    def __str__(self):
        return f'(δx:{self.x}, δy:{self.y})'

@dataclass(frozen=True)
class Size:
    width: int = 0
    height: int = 0

    def __iter__(self):
        yield self.width
        yield self.height

    def __str__(self):
        return f'(w:{self.width}, h:{self.height})'

@dataclass(frozen=True)
class Rect:
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
        return Point(self.mid_x, self.mid_y)

    def __iter__(self):
        yield tuple(self.origin)
        yield tuple(self.size)

    def __str__(self):
        return f'[{self.origin}, {self.size}]'