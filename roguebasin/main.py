#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

'''
New script.
'''

import argparse
from curses import KEY_DOWN
import logging
import math
import os.path
import tcod

CONSOLE_WIDTH, CONSOLE_HEIGHT = 50, 50
FONT = 'terminal16x16_gs_ro.png'

LOG = logging.getLogger('roguebasin')

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

    root_logger.addHandler(logging.StreamHandler())

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

    with tcod.context.new(columns=console.width, rows=console.height, tileset=tileset) as context:
        player_x, player_y = math.floor(CONSOLE_WIDTH / 2), math.floor(CONSOLE_HEIGHT / 2)
        while True:
            console.clear()
            console.print(x=player_x, y=player_y, string='@')
            context.present(console)

            for event in tcod.event.wait():
                # Sets tile coordinates for mouse events.
                context.convert_event(event)

                handled = True
                if isinstance(event, tcod.event.Quit):
                    raise SystemExit()
                elif isinstance(event, tcod.event.KeyDown):
                    sym = event.sym
                    if sym == tcod.event.KeySym.h:
                        player_x = max([0, player_x - 1])
                    elif sym == tcod.event.KeySym.j:
                        player_y = min([CONSOLE_HEIGHT - 1, player_y + 1])
                    elif sym == tcod.event.KeySym.k:
                        player_y = max([0, player_y - 1])
                    elif sym == tcod.event.KeySym.l:
                        player_x = min([CONSOLE_WIDTH - 1, player_x + 1])
                    else:
                        handled = False
                else:
                    handled = False

                if not handled:
                    LOG.info(f'Unhandled event: {event}')

if __name__ == '__main__':
    import sys
    result = main(sys.argv)
    sys.exit(0 if not result else result)