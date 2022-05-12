# Eryn Wells <eryn@erynwells.me>

from typing import Optional

# pylint: disable=too-few-public-methods
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
