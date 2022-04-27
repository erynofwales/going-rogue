#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

from . import object
from . import main

if __name__ == '__main__':
    import sys
    result = main.main(sys.argv)
    sys.exit(0 if not result else result)