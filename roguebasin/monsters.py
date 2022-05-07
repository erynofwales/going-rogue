#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

import tcod
from .geometry import Point
from .object import Entity
from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class Species:
    '''A kind of monster.'''
    name: str
    symbol: str
    maximum_hit_points: int
    foreground_color: Tuple[int, int, int]
    background_color: Tuple[int, int, int] = None

class Monster(Entity):
    '''An instance of a Species.'''

    def __init__(self, species: Species, position: Point = None):
        super().__init__(species.symbol, position=position, fg=species.foreground_color, bg=species.background_color)
        self.species: Species = species
        self.hit_points: int = species.maximum_hit_points

    def __str__(self) -> str:
        return f'{self.symbol}[{self.species.name}][{self.position}][{self.hit_points}/{self.species.maximum_hit_points}]'

Orc = Species(name='Orc', symbol='o', foreground_color=(63, 127, 63), maximum_hit_points=10)
Troll = Species(name='Troll', symbol='T', foreground_color=(0, 127, 0), maximum_hit_points=20)