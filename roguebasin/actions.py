#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

class Action:
    pass

class ExitAction(Action):
    pass

class RegenerateRoomsAction(Action):
    pass

class MovePlayerAction(Action):
    class Direction:
        North = (0, -1)
        NorthEast = (1, -1)
        East = (1, 0)
        SouthEast = (1, 1)
        South = (0, 1)
        SouthWest = (-1, 1)
        West = (-1, 0)
        NorthWest = (-1, -1)

    def __init__(self, direction: Direction):
        self.direction = direction