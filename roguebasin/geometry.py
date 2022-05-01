#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

from typing import Tuple, overload

class Point:
    __slots__ = ('x', 'y')

    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y

    @overload
    def __add__(self, other: Vector) -> Point:
        ...

    @overload
    def __add__(self, other) -> Point:
        if not isinstance(other, Vector):
            raise TypeError('Only Vector can be added to a Point')
        return Point(self.x + other.dx, self.y + other.dy)

    def __str__(self):
        return f'(x:{self.x}, y:{self.y})'

    def __repr__(self):
        return f'Point({self.x}, {self.y})'

class Vector:
    __slots__ = ('dx', 'dy')

    def __init__(self, dx: int = 0, dy: int = 0):
        self.dx = dx
        self.dy = dy

    def __str__(self):
        return f'(δx:{self.x}, δy:{self.y})'

    def __repr__(self):
        return f'Vector({self.x}, {self.y})'

class Size:
    __slots__ = ('width', 'height')

    def __init__(self, width: int = 0, height: int = 0):
        self.width = width
        self.height = height

    @property
    def as_tuple(self) -> Tuple[int, int]:
        return (self.width, self.height)

    def __str__(self):
        return f'(w:{self.width}, h:{self.height})'

    def __repr__(self):
        return f'Size({self.width}, {self.height})'

class Rect:
    __slots__ = ('origin', 'size')

    def __init__(self, x: int = 0, y: int = 0, w: int = 0, h: int = 0):
        '''
        Construct a new rectangle.
        '''
        self.origin = Point(x, y)
        self.size = Size(w, h)

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

    def __str__(self):
        return f'[{self.origin}, {self.size}]'

    def __repr__(self):
        return f'{self.__class__.__name__}({self.origin.x}, {self.origin.y}, {self.size.width}, {self.size.height})'