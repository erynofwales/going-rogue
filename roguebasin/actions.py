#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

import logging
from .geometry import Vector

LOG = logging.getLogger('events')

class Action:
    def perform(self, engine: 'Engine', entity: 'Entity') -> None:
        '''
        Perform this action. This is an abstract method that all subclasses
        should implement.
        '''
        raise NotImplementedError()

    def __repr__(self):
        return f'{self.__class__.__name__}()'

class ExitAction(Action):
    def perform(self, engine: 'Engine', entity: 'Entity') -> None:
        raise SystemExit()

class RegenerateRoomsAction(Action):
    def perform(self, engine: 'Engine', entity: 'Entity') -> None:
        ...

class MovePlayerAction(Action):
    class Direction:
        North = Vector(0, -1)
        NorthEast = Vector(1, -1)
        East = Vector(1, 0)
        SouthEast = Vector(1, 1)
        South = Vector(0, 1)
        SouthWest = Vector(-1, 1)
        West = Vector(-1, 0)
        NorthWest = Vector(-1, -1)

    def __init__(self, direction: Direction):
        self.direction = direction

    def perform(self, engine: 'Engine', entity: 'Entity') -> None:
        new_player_position = entity.position + self.direction

        position_is_in_bounds = engine.map.tile_is_in_bounds(new_player_position)
        position_is_walkable = engine.map.tile_is_walkable(new_player_position)
        overlaps_another_entity = any(new_player_position == ent.position for ent in engine.entities if ent is not entity)

        LOG.debug(f'Attempting to move player to {new_player_position} (in_bounds:{position_is_in_bounds} walkable:{position_is_walkable} overlaps:{overlaps_another_entity})')
        if position_is_in_bounds and position_is_walkable and not overlaps_another_entity:
            entity.position = new_player_position
