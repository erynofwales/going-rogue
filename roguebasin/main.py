#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

'''
New script.
'''

import argparse
import logging
import os.path
import random
import tcod
from .events import EventHandler, ExitAction, MovePlayerAction, RegenerateRoomsAction
from .geometry import Point, Rect, Size, Vector
from .object import Object
from .tile import Tile
from typing import List

CONSOLE_WIDTH, CONSOLE_HEIGHT = 80, 50
FONT = 'terminal16x16_gs_ro.png'

LOG = logging.getLogger('roguebasin')

MAP_WIDTH, MAP_HEIGHT = 80, 45

PLAYER = Object('@', x=MAP_WIDTH // 2, y=MAP_HEIGHT // 2)
NPC = Object('@', color=tcod.yellow, x=random.randint(0, MAP_WIDTH), y=random.randint(0, MAP_HEIGHT))

def parse_args(argv, *a, **kw):
    parser = argparse.ArgumentParser(*a, **kw)
    # TODO: Configure arguments here.
    args = parser.parse_args(argv)
    return args

def init_logging():
    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.DEBUG)

    stderr_handler = logging.StreamHandler()
    stderr_handler.setFormatter(logging.Formatter("%(asctime)s %(name)s: %(message)s"))

    root_logger.addHandler(stderr_handler)

def find_fonts_directory():
    '''
    Walk up the filesystem tree from this script to find a fonts/ directory.
    '''
    parent_dir = os.path.dirname(__file__)
    while parent_dir and parent_dir != '/':
        possible_fonts_dir = os.path.join(parent_dir, 'fonts')
        LOG.debug(f'Checking for fonts dir at {possible_fonts_dir}')
        if os.path.isdir(possible_fonts_dir):
            LOG.info(f'Found fonts dir: {possible_fonts_dir}')
            return possible_fonts_dir

        parent_dir = os.path.dirname(parent_dir)
    else:
        return None

def main(argv):
    args = parse_args(argv[1:], prog=argv[0])

    init_logging()

    fonts_directory = find_fonts_directory()
    if not fonts_directory:
        return -1

    font = os.path.join(fonts_directory, FONT)
    if not os.path.isfile(font):
        return -1

    tileset = tcod.tileset.load_tilesheet(font, 16, 16, tcod.tileset.CHARMAP_CP437)
    console = tcod.Console(CONSOLE_WIDTH, CONSOLE_HEIGHT, order='F')

    level = [[Tile(False) for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]

    random = tcod.random.Random()
    partitions, rooms = generate_rooms(random)

    objects = [PLAYER, NPC]

    event_handler = EventHandler()

    with tcod.context.new(columns=console.width, rows=console.height, tileset=tileset) as context:
        while True:
            #
            # Draw
            #

            console.clear()

            for part in partitions:
                console.draw_frame(part.x, part.y, part.width, part.height, bg=(40, 40, 80), clear=True, decoration="···· ····")

            for room in rooms:
                console.draw_frame(room.origin.x, room.origin.y, room.size.width, room.size.height,
                    fg=(255, 255, 255), bg=(80, 40, 40), clear=True)

            for obj in objects:
                obj.print(console)

            context.present(console)

            #
            # Handle Events
            #

            for event in tcod.event.wait():
                action = event_handler.dispatch(event)

                if not action:
                    continue

                if isinstance(action, MovePlayerAction):
                    new_player_position = Point(max(0, min(CONSOLE_WIDTH, PLAYER.x + action.direction[0])),
                                                max(0, min(CONSOLE_HEIGHT, PLAYER.y + action.direction[1])))
                    can_move_to_level_position = not level[new_player_position.x][new_player_position.y].blocks_movement
                    overlaps_an_object = any(new_player_position.x == obj.x and new_player_position.y == obj.y for obj in objects)
                    if can_move_to_level_position and not overlaps_an_object:
                        LOG.debug(f'Moving player to {new_player_position}; can_move:{can_move_to_level_position} overlaps:{overlaps_an_object}')
                        PLAYER.move_to(new_player_position)

                if isinstance(action, ExitAction):
                    raise SystemExit()

                if isinstance(action, RegenerateRoomsAction):
                    partitions, rooms = generate_rooms(random)

def generate_rooms(random: tcod.random.Random) -> List[Rect]:
    bsp = tcod.bsp.BSP(x=0, y=0, width=MAP_WIDTH, height=MAP_HEIGHT)
    bsp.split_recursive(
        depth=4,
        min_width=8, min_height=8,
        max_horizontal_ratio=1.5, max_vertical_ratio=1.5)

    partitions = []
    rooms = []
    indent = 0
    for node in bsp.pre_order():
        if node.children:
            LOG.debug(f'{" " * indent}{Rect(node.x, node.y, node.width, node.height)}')
            indent += 2
            # TODO: Connect the two child rooms
        else:
            LOG.debug(f'{" " * indent}{Rect(node.x, node.y, node.width, node.height)} (room)')
            size = Size(random.randint(5, min(15, max(5, node.width - 2))),
                        random.randint(5, min(15, max(5, node.height - 2))))
            origin = Point(node.x + random.randint(1, max(1, node.width - size.width - 1)),
                           node.y + random.randint(1, max(1, node.height - size.height - 1)))
            room = Rect(origin.x, origin.y, size.width, size.height)
            LOG.debug(f'{" " * indent}`-> {room}')
            partitions.append(node)
            rooms.append(room)
            indent -= 2

    return partitions, rooms