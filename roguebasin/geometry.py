#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

class Point:
    __slots__ = ('x', 'y')

    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y

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
    def max_x(self) -> int:
        return self.origin.x + self.size.width

    @property
    def max_y(self) -> int:
        return self.origin.y + self.size.height

    def __str__(self):
        return f'({self.origin}, {self.size})'

    def __repr__(self):
        return f'Rect({self.origin.x}, {self.origin.y}, {self.size.width}, {self.size.height})'