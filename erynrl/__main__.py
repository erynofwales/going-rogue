# Eryn Wells <eryn@erynwells.me>

'''Main module'''

import argparse
import sys
import tcod
from . import log
from .configuration import Configuration, FontConfiguration, FontConfigurationError
from .engine import Engine
from .geometry import Size
from .interface import Interface


TITLE = 'ErynRL'


def parse_args(argv, *a, **kw):
    parser = argparse.ArgumentParser(*a, **kw)
    parser.add_argument('--debug', action='store_true', default=True)
    parser.add_argument('--font')
    parser.add_argument('--sandbox', action='store_true', default=False)
    args = parser.parse_args(argv)
    return args


def main(argv):
    '''
    Beginning of the game

    Parameters
    ----------
    argv : List[str]
        A standard argument list, most likely you'll get this from sys.argv
    '''
    args = parse_args(argv[1:], prog=argv[0])

    log.init()

    try:
        font = args.font
        if font:
            font_config = FontConfiguration.with_filename(font)
        else:
            font_config = FontConfiguration.default_configuration()
    except FontConfigurationError as error:
        log.ROOT.error('Unable to create a font configuration: %s', error)
        return -1

    configuration = Configuration(
        console_font_configuration=font_config,
        map_size=Size(80, 40),
        sandbox=args.sandbox)

    engine = Engine(configuration)
    interface = Interface(configuration.console_size, engine)
    tileset = configuration.console_font_configuration.tileset

    with tcod.context.new(
            columns=interface.console.width,
            rows=interface.console.height,
            tileset=tileset,
            title=TITLE) as context:
        interface.run_event_loop(context)

    return 0


def run_until_exit():
    '''
    Run main() and call sys.exit when it finishes. In practice, this function will never return. The game engine has
    other mechanisms for exiting.
    '''
    result = main(sys.argv)
    sys.exit(0 if not result else result)


run_until_exit()
