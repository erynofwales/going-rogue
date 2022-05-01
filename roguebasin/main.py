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
from .engine import Configuration, Engine
from .events import EventHandler
from .geometry import Size
from .object import Object

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

    event_handler = EventHandler()
    configuration = Configuration(map_size=Size(MAP_WIDTH, MAP_HEIGHT))
    engine = Engine(event_handler, configuration)

    with tcod.context.new(columns=console.width, rows=console.height, tileset=tileset) as context:
        while True:
            console.clear()
            engine.print_to_console(console)
            context.present(console)

            for event in tcod.event.wait():
                engine.handle_event(event)