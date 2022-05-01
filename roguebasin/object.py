#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

import tcod
from .geometry import Point, Vector

class Object:
    '''A drawable object with a symbol and (x, y) position.'''

    def __init__(self, symbol: str, color: tcod.Color = (255, 255, 255), x: int = 0, y: int = 0):
        self.__x = int(x)
        self.__y = int(y)
        self.__color = color
        self.__symbol = symbol

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        self.__x = int(value)

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        self.__y = int(value)

    def move(self, delta: Vector):
        '''Move this object by (dx, dy).'''
        self.__x += delta.dx
        self.__y += delta.dy

    def move_to(self, point: Point) -> None:
        '''Move this object directly to the given position.'''
        self.__x = point.x
        self.__y = point.y

    def print(self, console: tcod.Console) -> None:
        console.print(x=self.__x, y=self.__y, string=self.__symbol, fg=self.__color)
