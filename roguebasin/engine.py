#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

import logging
import random
import tcod
from .actions import ExitAction, MovePlayerAction, RegenerateRoomsAction
from .events import EventHandler
from .geometry import Direction, Point, Size
from .map import Map
from .object import Entity
from dataclasses import dataclass
from typing import MutableSet

LOG = logging.getLogger('engine')
EVENT_LOG = logging.getLogger('events')

@dataclass
class Configuration:
    map_size: Size

class Engine:
    def __init__(self, event_handler: EventHandler, configuration: Configuration):
        self.event_handler = event_handler
        self.configuration = configuration

        self.rng = tcod.random.Random()

        map_size = configuration.map_size
        self.map = Map(map_size)

        first_room = self.map.generator.rooms[0]
        player_start_position = first_room.center
        self.player = Entity('@', position=player_start_position, fg=tcod.white)

        self.entities: MutableSet[Entity] = {self.player}
        for _ in range(self.rng.randint(5, 15)):
            position = self.map.random_walkable_position()
            self.entities.add(Entity('@', position=position, fg=tcod.yellow))

        self.update_field_of_view()

    def handle_event(self, event: tcod.event.Event):
        action = self.event_handler.dispatch(event)

        if not action:
            return

        action.perform(self, self.player)

        directions = list(Direction.all())
        moved_entities: MutableSet[Entity] = {self.player}

        for ent in self.entities:
            if ent == self.player:
                continue

            while True:
                new_position = ent.position + random.choice(directions)
                overlaps_with_previously_moved_entity = any(new_position == moved_ent.position for moved_ent in moved_entities)
                if not overlaps_with_previously_moved_entity and self.map.tile_is_walkable(new_position):
                    ent.position = new_position
                    moved_entities.add(ent)
                    break

        self.update_field_of_view()

    def print_to_console(self, console):
        self.map.print_to_console(console)

        for ent in self.entities:
            # Only print entities that are in the field of view
            if not self.map.visible[tuple(ent.position)]:
                continue
            ent.print_to_console(console)

    def update_field_of_view(self) -> None:
        '''Compute visible area of the map based on the player's position and point of view.'''
        self.map.visible[:] = tcod.map.compute_fov(
            self.map.tiles['transparent'],
            tuple(self.player.position),
            radius=8)

        # Visible tiles should be added to the explored list
        self.map.explored |= self.map.visible
