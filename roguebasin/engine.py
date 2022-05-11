# Eryn Wells <eryn@erynwells.me>

'''Defines the core game engine.'''

import logging
import random
from dataclasses import dataclass
from typing import MutableSet

import tcod

from . import monsters
from .ai import HostileEnemy
from .geometry import Size
from .map import Map
from .object import Entity, Hero, Monster

LOG = logging.getLogger('engine')

@dataclass
class Configuration:
    map_size: Size

class Engine:
    '''The main game engine.

    This class provides the event handling, map drawing, and maintains the list of entities.

    Attributes
    ----------
    configuration : Configuration
        Defines the basic configuration for the game
    entities : MutableSet[Entity]
        A set of all the entities on the current map, including the Hero
    hero : Hero
        The hero, the Entity controlled by the player
    map : Map
        A map of the current level
    rng : tcod.random.Random
        A random number generator
    '''

    def __init__(self, configuration: Configuration):
        self.configuration = configuration

        self.rng = tcod.random.Random()
        self.map = Map(configuration.map_size)

        first_room = self.map.generator.rooms[0]
        hero_start_position = first_room.center
        self.hero = Hero(position=hero_start_position)

        self.entities: MutableSet[Entity] = {self.hero}
        for room in self.map.rooms:
            should_spawn_monster_chance = random.random()
            if should_spawn_monster_chance < 0.4:
                continue

            floor = list(room.walkable_tiles)
            for _ in range(2):
                while True:
                    random_start_position = random.choice(floor)
                    if not any(ent.position == random_start_position for ent in self.entities):
                        break

                spawn_monster_chance = random.random()
                if spawn_monster_chance > 0.8:
                    monster = Monster(monsters.Troll, ai_class=HostileEnemy, position=random_start_position)
                else:
                    monster = Monster(monsters.Orc, ai_class=HostileEnemy, position=random_start_position)

                LOG.info('Spawning %s', monster)
                self.entities.add(monster)

        self.update_field_of_view()

    def print_to_console(self, console):
        '''Print the whole game to the given console.'''
        self.map.print_to_console(console)

        hp, max_hp = self.hero.fighter.hit_points, self.hero.fighter.maximum_hit_points
        console.print(x=1, y=47, string=f'HP: {hp}/{max_hp}')

        for ent in sorted(self.entities, key=lambda e: e.render_order.value):
            # Only print entities that are in the field of view
            if not self.map.visible[tuple(ent.position)]:
                continue
            ent.print_to_console(console)

    def update_field_of_view(self) -> None:
        '''Compute visible area of the map based on the player's position and point of view.'''
        self.map.visible[:] = tcod.map.compute_fov(
            self.map.tiles['transparent'],
            tuple(self.hero.position),
            radius=8)

        # Visible tiles should be added to the explored list
        self.map.explored |= self.map.visible
