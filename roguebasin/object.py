# Eryn Wells <eryn@erynwells.me>

from typing import TYPE_CHECKING, Optional, Tuple, Type

import tcod

from .components import Fighter
from .geometry import Point
from .monsters import Species

if TYPE_CHECKING:
    from .ai import AI

class Entity:
    '''A single-tile drawable entity with a symbol and position

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
    blocks_movement : bool
        True if this Entity blocks other Entities from moving through its position
    '''

    def __init__(self, symbol: str, *,
                 position: Optional[Point] = None,
                 blocks_movement: Optional[bool] = True,
                 fg: Optional[Tuple[int, int, int]] = None,
                 bg: Optional[Tuple[int, int, int]] = None):
        self.position = position if position else Point()
        self.foreground = fg if fg else (255, 255, 255)
        self.background = bg
        self.symbol = symbol
        self.blocks_movement = blocks_movement

    def print_to_console(self, console: tcod.Console) -> None:
        '''Render this Entity to the console'''
        console.print(x=self.position.x, y=self.position.y, string=self.symbol, fg=self.foreground, bg=self.background)

    def __str__(self) -> str:
        return f'{self.symbol}[{self.position}]'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.symbol!r}, position={self.position!r}, fg={self.foreground!r}, bg={self.background!r})'

class Actor(Entity):
    def __init__(self, symbol: str, *,
                 position: Optional[Point] = None,
                 blocks_movement: Optional[bool] = True,
                 ai: Optional[Type['AI']] = None,
                 fighter: Optional[Fighter] = None,
                 fg: Optional[Tuple[int, int, int]] = None,
                 bg: Optional[Tuple[int, int, int]] = None):
        super().__init__(symbol, position=position, blocks_movement=blocks_movement, fg=fg, bg=bg)

        # Components
        self.ai = ai
        self.fighter = fighter

    @property
    def name(self) -> str:
        return 'Actor'

    @property
    def sight_radius(self) -> int:
        '''The number of tiles this entity can see around itself'''
        return 0

    @property
    def yields_corpse_on_death(self) -> bool:
        '''True if this Actor should produce a corpse when it dies'''
        return False

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.symbol!r}, position={self.position!r}, fighter={self.fighter!r}, ai={self.ai!r}, fg={self.foreground!r}, bg={self.background!r})'

class Hero(Actor):
    '''The hero, the player character'''

    def __init__(self, position: Point):
        super().__init__('@',
             position=position,
             fighter=Fighter(maximum_hit_points=30, attack_power=5, defense=2),
             fg=tuple(tcod.white))

    @property
    def name(self) -> str:
        return 'Hero'

    @property
    def sight_radius(self) -> int:
        # TODO: Make this configurable
        return 8

    def __str__(self) -> str:
        return f'{self.symbol}[{self.position}][{self.fighter.hit_points}/{self.fighter.maximum_hit_points}]'


class Monster(Actor):
    '''An instance of a Species'''

    def __init__(self, species: Species, ai_class: Type['AI'], position: Point = None):
        fighter = Fighter(
            maximum_hit_points=species.maximum_hit_points,
            attack_power=species.attack_power,
            defense=species.defense)

        super().__init__(
            species.symbol,
            ai=ai_class(self),
            position=position,
            fighter=fighter,
            fg=species.foreground_color,
            bg=species.background_color)

        self.species = species

    @property
    def name(self) -> str:
        return self.species.name

    @property
    def sight_radius(self) -> int:
        return self.species.sight_radius

    @property
    def yields_corpse_on_death(self) -> bool:
        return True

    def __str__(self) -> str:
        return f'{self.name} with {self.fighter.hit_points}/{self.fighter.maximum_hit_points} hp at {self.position}'

