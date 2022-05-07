# Eryn Wells <eryn@erynwells.me>

import argparse
import logging
import os.path
import sys
import tcod
from .engine import Configuration, Engine
from .events import EventHandler
from .geometry import Size

LOG = logging.getLogger('main')

CONSOLE_WIDTH, CONSOLE_HEIGHT = 80, 50
MAP_WIDTH, MAP_HEIGHT = 80, 45

FONT = 'terminal16x16_gs_ro.png'

def parse_args(argv, *a, **kw):
    parser = argparse.ArgumentParser(*a, **kw)
    parser.add_argument('--debug', action='store_true', default=True)
    args = parser.parse_args(argv)
    return args

def init_logging(args):
    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    stderr_handler = logging.StreamHandler()
    stderr_handler.setFormatter(logging.Formatter("%(asctime)s %(name)s: %(message)s"))

    root_logger.addHandler(stderr_handler)

def find_fonts_directory():
    '''Walk up the filesystem tree from this script to find a fonts/ directory.'''
    parent_dir = os.path.dirname(__file__)
    while parent_dir and parent_dir != '/':
        possible_fonts_dir = os.path.join(parent_dir, 'fonts')
        LOG.debug('Checking for fonts dir at %s', possible_fonts_dir)
        if os.path.isdir(possible_fonts_dir):
            LOG.info('Found fonts dir %s', possible_fonts_dir)
            break
        parent_dir = os.path.dirname(parent_dir)
    else:
        return None

    return possible_fonts_dir

def main(argv):
    args = parse_args(argv[1:], prog=argv[0])

    init_logging(args)

    fonts_directory = find_fonts_directory()
    if not fonts_directory:
        LOG.error("Couldn't find a fonts/ directory")
        return -1

    font = os.path.join(fonts_directory, FONT)
    if not os.path.isfile(font):
        LOG.error("Font file %s doesn't exist", font)
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

def run_until_exit():
    '''Run the package's main() and call sys.exit when it finishes.'''
    result = main(sys.argv)
    sys.exit(0 if not result else result)

run_until_exit()
