# Eryn Wells <eryn@erynwells.me>

'''
Run the cellular atomaton from ErynRL and print the results.
'''

import argparse

from erynrl import log
from erynrl.geometry import Point, Rect, Size
from erynrl.map.generator.cellular_atomata import CellularAtomataMapGenerator


def parse_args(argv, *a, **kw):
    '''Parse command line arguments'''
    parser = argparse.ArgumentParser(*a, **kw)
    parser.add_argument('--rounds', type=int, default=5)
    args = parser.parse_args(argv)
    return args


def main(argv):
    '''The script'''

    args = parse_args(argv[1:], prog=argv[0])

    log.init()

    bounds = Rect(Point(), Size(20, 20))

    config = CellularAtomataMapGenerator.Configuration()
    config.number_of_rounds = args.rounds

    gen = CellularAtomataMapGenerator(bounds, config)

    gen.generate()

    print(gen)


if __name__ == '__main__':
    import sys
    result = main(sys.argv)
    sys.exit(0 if not result else result)
