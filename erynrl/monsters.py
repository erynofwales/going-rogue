# Eryn Wells <eryn@erynwells.me>

'''Defines the Species type, which represents a class of monsters, and all the monster types the hero can encounter in
the dungeon.'''

from dataclasses import dataclass
from typing import Optional, Tuple

# pylint: disable=too-many-instance-attributes


@dataclass(frozen=True)
class Species:
    '''A kind of monster.

    Attributes
    ----------
    name : str
        A friendly, user-visiable name for the monster
    symbol : str
        The symbol used to render the monster on the map
    maximum_hit_points : int
        The maximum number of hit points the monster can be spawned with
    sight_radius : int
        The number of tiles this monster can see
    foreground_color : Tuple[int, int, int]
        The foreground color used to render the monster on the map
    background_color : Tuple[int, int, int], optional
        The background color used to render the monster on the map; if none is given, the tile color specified by the
        map will be used.
    '''
    name: str
    symbol: str
    maximum_hit_points: int
    sight_radius: int
    # TODO: Rename these two attributes something better
    attack_power: int
    defense: int
    foreground_color: Tuple[int, int, int]
    background_color: Optional[Tuple[int, int, int]] = None


Orc = Species(name='Orc', symbol='o',
              foreground_color=(63, 127, 63),
              maximum_hit_points=10,
              sight_radius=4,
              attack_power=4, defense=1)
Troll = Species(name='Troll', symbol='T',
                foreground_color=(0, 127, 0),
                maximum_hit_points=16,
                sight_radius=4,
                attack_power=3, defense=0)
