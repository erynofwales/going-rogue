#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

import logging
from .geometry import Direction
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .engine import Engine
    from .object import Entity

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
    def __init__(self, direction: Direction):
        self.direction = direction

    def perform(self, engine: 'Engine', entity: 'Entity') -> None:
        new_player_position = entity.position + self.direction

        position_is_in_bounds = engine.map.tile_is_in_bounds(new_player_position)
        position_is_walkable = engine.map.tile_is_walkable(new_player_position)
        overlaps_another_entity = any(new_player_position == ent.position for ent in engine.entities if ent is not entity)

        if position_is_in_bounds and position_is_walkable and not overlaps_another_entity:
            LOG.info('Moving hero to %s (in_bounds:%s walkable:%s overlaps:%s)',
                     new_player_position,
                     position_is_in_bounds,
                     position_is_walkable,
                     overlaps_another_entity)
            entity.position = new_player_position
