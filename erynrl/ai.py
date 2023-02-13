# Eryn Wells <eryn@erynwells.me>

import random
from typing import TYPE_CHECKING, List, Optional

import numpy as np
import tcod

from . import log
from .actions.action import ActionWithActor
from .actions.game import BumpAction, WaitAction
from .components import Component
from .geometry import Direction, Point
from .object import Entity

if TYPE_CHECKING:
    from .engine import Engine

# pylint: disable=too-few-public-methods


class AI(Component):
    '''An abstract class providing AI for an entity.'''

    def __init__(self, entity: Entity) -> None:
        super().__init__()
        self.entity = entity

    def act(self, engine: 'Engine') -> Optional[ActionWithActor]:
        '''Produce an action to perform'''
        raise NotImplementedError()


class HostileEnemy(AI):
    '''Entity AI for a hostile enemy.

    The entity will wander around until it sees the hero, at which point it will
    beeline for her.
    '''

    def act(self, engine: 'Engine') -> Optional[ActionWithActor]:
        visible_tiles = tcod.map.compute_fov(
            engine.map.tiles['transparent'],
            pov=tuple(self.entity.position),
            radius=self.entity.sight_radius)

        if engine.map.visible[tuple(self.entity.position)]:
            log.AI.debug("AI for %s", self.entity)

        hero_position = engine.hero.position
        hero_is_visible = visible_tiles[hero_position.x, hero_position.y]

        if hero_is_visible:
            path_to_hero = self.get_path_to(hero_position, engine)
            assert len(path_to_hero) > 0, f'{self.entity} attempting to find a path to hero while on top of the hero!'

            entity_position = self.entity.position

            if engine.map.visible[tuple(self.entity.position)]:
                log.AI.debug('|-> Path to hero %s', path_to_hero)

            next_position = path_to_hero.pop(0) if len(path_to_hero) > 1 else hero_position
            direction_to_next_position = entity_position.direction_to_adjacent_point(next_position)

            if engine.map.visible[tuple(self.entity.position)]:
                log.AI.info('`-> Hero is visible to %s, bumping %s (%s)',
                            self.entity, direction_to_next_position, next_position)

            return BumpAction(self.entity, direction_to_next_position)
        else:
            move_or_wait_chance = random.random()
            if move_or_wait_chance <= 0.7:
                # Pick a random adjacent tile to move to
                directions = list(Direction.all())
                while len(directions) > 0:
                    direction = random.choice(directions)
                    directions.remove(direction)
                    new_position = self.entity.position + direction
                    overlaps_existing_entity = any(new_position == ent.position for ent in engine.entities)
                    tile_is_walkable = engine.map.tile_is_walkable(new_position)
                    if not overlaps_existing_entity and tile_is_walkable:
                        if engine.map.visible[tuple(self.entity.position)]:
                            log.AI.info('Hero is NOT visible to %s, bumping %s randomly', self.entity, direction)
                        action = BumpAction(self.entity, direction)
                        break
                else:
                    # If this entity somehow can't move anywhere, just wait
                    if engine.map.visible[tuple(self.entity.position)]:
                        log.AI.info("Hero is NOT visible to %s and it can't move anywhere, waiting", self.entity)
                    action = WaitAction(self.entity)

                return action
            else:
                return WaitAction(self.entity)

    def get_path_to(self, point: Point, engine: 'Engine') -> List[Point]:
        '''Compute a path to the given position.

        Copied from the Roguelike tutorial. :)

        Arguments
        ---------
        point : Point
            The target point
        engine : Engine
            The game engine

        Returns
        -------
        List[Point]
            An array of Points representing a path from the Entity's position to the target point
        '''
        # Copy the walkable array
        cost = np.array(engine.map.tiles['walkable'], dtype=np.int8)

        for ent in engine.entities:
            # Check that an entity blocks movement and the cost isn't zero (blocking)
            position = ent.position
            if ent.blocks_movement and cost[position.x, position.y]:
                # Add to the cost of a blocked position. A lower number means more enemies will crowd behind each other
                # in hallways. A higher number means enemies will take longer paths in order to surround the player.
                cost[position.x, position.y] += 10

        # Create a graph from the cost array and pass that graph to a new pathfinder.
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        # Set the starting position
        pathfinder.add_root(tuple(self.entity.position))

        # Compute the path to the destination and remove the starting point.
        path: List[List[int]] = pathfinder.path_to(tuple(point))[1:].tolist()

        # Convert from List[List[int]] to List[Tuple[int, int]].
        return [Point(index[0], index[1]) for index in path]
