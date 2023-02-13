# Eryn Wells <eryn@erynwells.me>

'''Defines a number of high-level game objects. The parent class of all game objects is the Entity class.'''

from enum import Enum
from typing import TYPE_CHECKING, Optional, Tuple, Type

import tcod

from . import items
from .components import Fighter
from .geometry import Point
from .monsters import Species

if TYPE_CHECKING:
    from .ai import AI


class RenderOrder(Enum):
    '''
    These values indicate the order that an Entity should be rendered. Higher values are rendered later and therefore on
    top of items with lower orderings.
    '''
    ITEM = 1000
    ACTOR = 2000
    HERO = 3000


class Entity:
    '''A single-tile drawable entity with a symbol and position

    Attributes
    ----------
    identifier : int
        A numerical value that uniquely identifies this entity across the entire game
    position : Point
        The Entity's location on the map
    foreground : Tuple[int, int, int]
        The foreground color used to render this Entity
    background : Tuple[int, int, int], optional
        The background color used to render this Entity
    symbol : str
        A single character string that represents this character on the map
    blocks_movement : bool
        True if this Entity blocks other Entities from moving through its position
    render_order : RenderOrder
        One of the RenderOrder values that specifies a layer at which this entity will be rendered. Higher values are
        rendered on top of lower values.
    '''

    # A monotonically increasing identifier to help differentiate between entities that otherwise look identical
    __next_identifier = 1

    def __init__(
            self,
            symbol: str,
            *,
            position: Optional[Point] = None,
            blocks_movement: Optional[bool] = True,
            render_order: RenderOrder = RenderOrder.ITEM,
            fg: Optional[Tuple[int, int, int]] = None,
            bg: Optional[Tuple[int, int, int]] = None):
        self.identifier = Entity.__next_identifier
        self.position = position if position else Point()
        self.foreground = fg if fg else (255, 255, 255)
        self.background = bg
        self.symbol = symbol
        self.blocks_movement = blocks_movement
        self.render_order = render_order

        Entity.__next_identifier += 1

    def print_to_console(self, console: tcod.Console) -> None:
        '''Render this Entity to the console'''
        console.print(x=self.position.x, y=self.position.y, string=self.symbol, fg=self.foreground, bg=self.background)

    def __str__(self) -> str:
        return f'{self.symbol}!{self.identifier} at {self.position}'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.symbol!r}, position={self.position!r}, fg={self.foreground!r}, bg={self.background!r})'


class Actor(Entity):
    '''
    An actor is an abstract class that defines an object that can act in the game world. Entities that are actors will
    be allowed an opportunity to perform an action during each game turn.

    Attributes
    ----------
    ai : AI, optional
        If an entity can act on its own behalf, an instance of an AI class
    fighter : Fighter, optional
        If an entity can fight or take damage, an instance of the Fighter class. This is where hit points, attack power,
        defense power, etc live.
    '''

    def __init__(
            self,
            symbol: str,
            *,
            position: Optional[Point] = None,
            blocks_movement: Optional[bool] = True,
            render_order: RenderOrder = RenderOrder.ACTOR,
            ai: Optional['AI'] = None,
            fighter: Optional[Fighter] = None,
            fg: Optional[Tuple[int, int, int]] = None,
            bg: Optional[Tuple[int, int, int]] = None):
        super().__init__(
            symbol,
            position=position,
            blocks_movement=blocks_movement,
            fg=fg,
            bg=bg,
            render_order=render_order)

        # Components
        self.ai = ai
        self.fighter = fighter

    @property
    def name(self) -> str:
        '''The name of this actor. This is a player-visible string.'''
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
        super().__init__(
            '@',
            position=position,
            fighter=Fighter(maximum_hit_points=30, attack_power=5, defense=2),
            render_order=RenderOrder.HERO,
            fg=tuple(tcod.white))

    @property
    def name(self) -> str:
        return 'Hero'

    @property
    def sight_radius(self) -> int:
        # TODO: Make this configurable
        return 8

    def __str__(self) -> str:
        assert self.fighter
        return f'Hero!{self.identifier} at {self.position} with {self.fighter.hit_points}/{self.fighter.maximum_hit_points} hp'


class Monster(Actor):
    '''An instance of a Species'''

    def __init__(self, species: Species, ai_class: Type['AI'], position: Optional[Point] = None):
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
        assert self.fighter
        return f'{self.name}!{self.identifier} with {self.fighter.hit_points}/{self.fighter.maximum_hit_points} hp at {self.position}'


class Item(Entity):
    '''An instance of an Item'''

    def __init__(self, kind: items.Item, position: Optional[Point] = None, name: Optional[str] = None):
        super().__init__(kind.symbol,
                         position=position,
                         blocks_movement=False,
                         render_order=RenderOrder.ITEM,
                         fg=kind.foreground_color,
                         bg=kind.background_color)
        self.kind = kind
        self._name = name

    @property
    def name(self) -> str:
        '''The name of the item'''
        if self._name:
            return self._name
        return self.kind.name
