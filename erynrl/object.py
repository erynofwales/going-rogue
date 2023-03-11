# Eryn Wells <eryn@erynwells.me>

'''Defines a number of high-level game objects. The parent class of all game objects is the Entity class.'''

from typing import TYPE_CHECKING, Optional, Type

import tcod

from . import items
from .components import Fighter, Renderable
from .geometry import Point
from .monsters import Species

if TYPE_CHECKING:
    from .ai import AI


class Entity:
    '''A single-tile drawable entity with a symbol and position

    ### Attributes

    identifier : int
        A numerical value that uniquely identifies this entity across the entire
        game
    position : Point
        The Entity's location on the map
    blocks_movement : bool
        True if this Entity blocks other Entities from moving through its
        position
    '''

    # A monotonically increasing identifier to help differentiate between
    # entities that otherwise look identical
    __next_identifier = 1

    def __init__(
            self,
            *,
            position: Optional[Point] = None,
            blocks_movement: Optional[bool] = True,
            renderable: Optional[Renderable] = None):
        self.identifier = Entity.__next_identifier
        self.position = position if position else Point()
        self.renderable = renderable
        self.blocks_movement = blocks_movement

        Entity.__next_identifier += 1

    def __str__(self):
        return f'{self.__class__.__name__}!{self.identifier}'

    def __repr__(self):
        return f'{self.__class__.__name__}(position={self.position!r}, blocks_movement={self.blocks_movement}, renderable={self.renderable!r})'


class Actor(Entity):
    '''
    An actor is an abstract class that defines an object that can act in the
    game world. Entities that are actors will be allowed an opportunity to
    perform an action during each game turn.

    ### Attributes

    ai : AI, optional
        If an entity can act on its own behalf, an instance of an AI class
    fighter : Fighter, optional
        If an entity can fight or take damage, an instance of the Fighter class.
        This is where hit points, attack power, defense power, etc live.
    '''

    def __init__(
            self,
            *,
            position: Optional[Point] = None,
            blocks_movement: Optional[bool] = True,
            renderable: Optional[Renderable] = None,
            ai: Optional['AI'] = None,
            fighter: Optional[Fighter] = None):
        super().__init__(
            position=position,
            blocks_movement=blocks_movement,
            renderable=renderable)

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
        return f'{self.__class__.__name__}(position={self.position!r}, fighter={self.fighter!r}, ai={self.ai!r}, renderable={self.renderable!r})'


class Hero(Actor):
    '''The hero, the player character'''

    def __init__(self, position: Point):
        super().__init__(
            position=position,
            fighter=Fighter(maximum_hit_points=30, attack_power=5, defense=2),
            renderable=Renderable('@', Renderable.Order.HERO, tuple(tcod.white)))

    @property
    def name(self) -> str:
        return 'Hero'

    @property
    def sight_radius(self) -> int:
        # TODO: Make this configurable
        return 0

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
            ai=ai_class(self),
            position=position,
            fighter=fighter,
            renderable=Renderable(
                symbol=species.symbol,
                fg=species.foreground_color,
                bg=species.background_color))

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
        super().__init__(position=position,
                         blocks_movement=False,
                         renderable=Renderable(
                             symbol=kind.symbol,
                             order=Renderable.Order.ITEM,
                             fg=kind.foreground_color,
                             bg=kind.background_color))
        self.kind = kind
        self._name = name

    @property
    def name(self) -> str:
        '''The name of the item'''
        if self._name:
            return self._name
        return self.kind.name
