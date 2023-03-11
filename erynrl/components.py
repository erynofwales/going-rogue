# Eryn Wells <eryn@erynwells.me>

import random
from enum import Enum
from typing import Optional, Tuple


class Component:
    '''A base, abstract Component that implement some aspect of an Entity's behavior.'''


class Fighter(Component):
    '''A Fighter is an Entity that can fight. That is, it has hit points (health), attack, and defense.

    Attributes
    ----------
    maximum_hit_points : int
        Maximum number of hit points the Fighter can have. In almost every case, a Fighter will be spawned with this
        many hit points.
    attack_power : int
        The amount of damage the Figher can do.
    defense : int
        The amount of damage the Fighter can deflect or resist.
    hit_points : int
        The current number of hit points remaining. When this reaches 0, the Fighter dies.
    '''

    def __init__(self, *, maximum_hit_points: int, attack_power: int, defense: int, hit_points: Optional[int] = None):
        self.maximum_hit_points = maximum_hit_points
        self.__hit_points = hit_points if hit_points else maximum_hit_points

        # TODO: Rename these two attributes something better
        self.attack_power = attack_power
        self.defense = defense

        # TODO: Factor this out into a dedicated Clock class
        self.__ticks_since_last_passive_heal = 0
        self.__ticks_for_next_passive_heal = 0
        self._reset_passive_heal_clock()

    @property
    def hit_points(self) -> int:
        '''Number of hit points remaining. When a Fighter reaches 0 hit points, they die.'''
        return self.__hit_points

    @hit_points.setter
    def hit_points(self, value: int) -> None:
        self.__hit_points = min(self.maximum_hit_points, max(0, value))

    @property
    def is_dead(self) -> bool:
        '''True if the Fighter has died, i.e. reached 0 hit points'''
        return self.__hit_points == 0

    def passively_recover_hit_points(self, number_of_ticks: int) -> bool:
        '''
        Check the passive healing clock to see if this fighter should recover hit points. If not, increment the
        counter.

        Arguments
        ---------
        number_of_ticks : int
            The number of ticks to increment the clock
        '''
        if self.hit_points == self.maximum_hit_points:
            self.__ticks_since_last_passive_heal = 0

        if self.__ticks_since_last_passive_heal < self.__ticks_for_next_passive_heal:
            self.__ticks_since_last_passive_heal += number_of_ticks
            return False

        self._reset_passive_heal_clock()

        return True

    def _reset_passive_heal_clock(self) -> None:
        self.__ticks_since_last_passive_heal = 0
        self.__ticks_for_next_passive_heal = random.randint(30, 70)


class Renderable(Component):
    class Order(Enum):
        '''
        These values indicate the order that an entity with a Renderable
        component should be rendered. Higher values are rendered later and
        therefore on top of items with lower orderings.
        '''
        ITEM = 1000
        ACTOR = 2000
        HERO = 3000

    def __init__(
            self,
            symbol: str,
            order: Order = Order.ACTOR,
            fg: Optional[Tuple[int, int, int]] = None,
            bg: Optional[Tuple[int, int, int]] = None):
        if len(symbol) != 1:
            raise ValueError(f'Symbol string "{symbol}" must be of length 1')

        self.symbol = symbol
        '''The symbol that represents this renderable on the map'''

        self.order = order
        '''
        Specifies the layer at which this entity is rendered. Higher values are
        rendered later, and thus on top of lower values.
        '''

        self.foreground = fg
        '''The foreground color of the entity'''

        self.background = bg
        '''The background color of the entity'''

    def __repr__(self):
        return f'{self.__class__.__name__}("{self.symbol}", {self.order}, {self.foreground}, {self.background})'
