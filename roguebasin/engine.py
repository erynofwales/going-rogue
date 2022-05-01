#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

import logging
import tcod
from .actions import ExitAction, MovePlayerAction, RegenerateRoomsAction
from .events import EventHandler
from .geometry import Point, Size
from .map import Map
from .object import Object
from typing import AbstractSet

LOG = logging.getLogger('engine')
EVENT_LOG = logging.getLogger('events')

class Configuration:
    def __init__(self, map_size: Size):
        self.map_size = map_size
        self.random_seed = None

class Engine:
    def __init__(self, event_handler: EventHandler, configuration: Configuration):
        self.event_handler = event_handler
        self.configuration = configuration

        self.rng = tcod.random.Random(seed=configuration.random_seed)

        map_size = configuration.map_size
        self.map = Map(map_size)

        self.player = Object('@', tcod.white, x=int(map_size.width / 2), y=int(map_size.height / 2))
        self.objects: AbstractSet[Object] = {self.player}
        for _ in range(self.rng.randint(1, 15)):
            self.objects.add(Object('@', color=tcod.yellow, x=self.rng.randint(0, map_size.width), y=self.rng.randint(0, map_size.height)))

    def handle_event(self, event: tcod.event.Event):
        action = self.event_handler.dispatch(event)

        if not action:
            return

        if isinstance(action, MovePlayerAction):
            map_size = self.configuration.map_size
            new_player_position = Point(self.player.x + action.direction[0],
                                        self.player.y + action.direction[1])
            can_move_to_map_position = self.map.tile_is_in_bounds(new_player_position) and self.map.tile_is_walkable(new_player_position)
            overlaps_an_object = any(new_player_position.x == obj.x and new_player_position.y == obj.y for obj in self.objects)
            EVENT_LOG.debug(f'Attempting to move player to {new_player_position}; can_move:{can_move_to_map_position} overlaps:{overlaps_an_object}')
            if can_move_to_map_position and not overlaps_an_object:
                self.player.move_to(new_player_position)

        if isinstance(action, ExitAction):
            raise SystemExit()

        # if isinstance(action, RegenerateRoomsAction):
        #     partitions, rooms = generate_rooms(random)

    def print_to_console(self, console):
        self.map.print_to_console(console)

        for obj in self.objects:
            obj.print_to_console(console)
