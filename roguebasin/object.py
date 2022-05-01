#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

import tcod
from .geometry import Point
from typing import Optional

class Entity:
    '''A single-tile drawable entity with a symbol and position.'''

    def __init__(self, symbol: str, *, position: Optional[Point] = None, color: Optional[tcod.Color] = None):
        self.position = position if position else Point()
        self.color = color if color else tcod.white
        self.symbol = symbol

    def print_to_console(self, console: tcod.Console) -> None:
        console.print(x=self.__x, y=self.__y, string=self.__symbol, fg=self.__color)
