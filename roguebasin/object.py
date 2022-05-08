# Eryn Wells <eryn@erynwells.me>

from typing import TYPE_CHECKING, Optional, Tuple, Type

import tcod

from .components import Fighter
from .geometry import Point
from .monsters import Species

if TYPE_CHECKING:
    from .ai import AI

class Entity:
    '''A single-tile drawable entity with a symbol and position.

    Attributes
    ----------
    position : Point
        The Entity's location on the map
    foreground : Tuple[int, int, int]
        The foreground color used to render this Entity
    background : Tuple[int, int, int], optional
        The background color used to render this Entity
    symbol : str
        A single character string that represents this character on the map
    ai : Type[AI], optional
        If an entity can act on its own behalf, an instance of an AI class
    '''

    def __init__(self, symbol: str, *,
                 position: Optional[Point] = None,
                 ai: Optional[Type['AI']] = None,
                 fg: Optional[Tuple[int, int, int]] = None,
                 bg: Optional[Tuple[int, int, int]] = None):
        self.position = position if position else Point()
        self.foreground = fg if fg else (255, 255, 255)
        self.background = bg
        self.symbol = symbol
        self.ai = ai

    def print_to_console(self, console: tcod.Console) -> None:
        '''Render this Entity to the console'''
        console.print(x=self.position.x, y=self.position.y, string=self.symbol, fg=self.foreground, bg=self.background)

    def __str__(self) -> str:
        return f'{self.symbol}[{self.position}]'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.symbol}, position={self.position}, fg={self.foreground}, bg={self.background})'

class Hero(Entity):
    '''The hero, the player character'''

    def __init__(self, position: Point):
        super().__init__('@', position=position, fg=tuple(tcod.white))
        self.fighter = Fighter(maximum_hit_points=30, attack_power=5, defense=2)

    def __str__(self) -> str:
        return f'{self.symbol}[{self.position}][{self.fighter.hit_points}/{self.fighter.maximum_hit_points}]'


class Monster(Entity):
    '''An instance of a Species.'''

    def __init__(self, species: Species, ai_class: Type['AI'], position: Point = None):
        super().__init__(species.symbol, ai=ai_class(self), position=position, fg=species.foreground_color, bg=species.background_color)
        self.species = species
        self.fighter = Fighter(maximum_hit_points=species.maximum_hit_points,
                               attack_power=species.attack_power,
                               defense=species.defense)

    def __str__(self) -> str:
        return f'{self.symbol}[{self.species.name}][{self.position}][{self.fighter.hit_points}/{self.fighter.maximum_hit_points}]'
