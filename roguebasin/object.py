#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

import tcod

class Object:
    '''
    A drawable object with a symbol and (x, y) position.
    '''

    def __init__(self, symbol, x=0, y=0):
        self.__x = int(x)
        self.__y = int(y)
        self.symbol = symbol

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

    def print(self, console: tcod.Console) -> None:
        console.print(x=self.__x, y=self.__y, string=self.symbol)
