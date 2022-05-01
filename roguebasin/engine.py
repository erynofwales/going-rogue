#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

import logging
import tcod
from .actions import ExitAction, MovePlayerAction, RegenerateRoomsAction
from .events import EventHandler
from .geometry import Point, Size
from .map import Map
from .object import Entity
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

        first_room = self.map.rooms[0]
        player_start_position = first_room.midpoint
        self.player = Entity('@', position=player_start_position, fg=tcod.white)
        self.entities: AbstractSet[Entity] = {self.player}
        for _ in range(self.rng.randint(1, 15)):
            position = Point(self.rng.randint(0, map_size.width), self.rng.randint(0, map_size.height))
            self.entities.add(Entity('@', position=position, fg=tcod.yellow))

    def handle_event(self, event: tcod.event.Event):
        action = self.event_handler.dispatch(event)

        if not action:
            return

        action.perform(self, self.player)

    def print_to_console(self, console):
        self.map.print_to_console(console)

        for ent in self.entities:
            ent.print_to_console(console)
