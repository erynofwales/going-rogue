#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

import tcod
from .geometry import Point
from typing import Optional, Tuple

class Entity:
    '''A single-tile drawable entity with a symbol and position.'''

    def __init__(self, symbol: str, *,
                 position: Optional[Point] = None,
                 fg: Optional[Tuple[int, int, int]] = None,
                 bg: Optional[Tuple[int, int, int]] = None):
        self.position = position if position else Point()
        self.foreground = fg if fg else (255, 255, 255)
        self.background = bg
        self.symbol = symbol

    def print_to_console(self, console: tcod.Console) -> None:
        console.print(x=self.position.x, y=self.position.y, string=self.symbol, fg=self.foreground, bg=self.background)

    def __str__(self):
        return f'{self.symbol}[{self.position}]'

    def __repr__(self):
        return f'{self.__class__.__name__}({self.symbol}, position={self.position}, fg={self.foreground}, bg={self.background})'

class Hero(Entity):
    def __init__(self, position: Point):
        super().__init__('@', position=position, fg=tuple(tcod.white))