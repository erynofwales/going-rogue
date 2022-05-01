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
        North = Vector(0, -1)
        NorthEast = Vector(1, -1)
        East = Vector(1, 0)
        SouthEast = Vector(1, 1)
        South = Vector(0, 1)
        SouthWest = Vector(-1, 1)
        West = Vector(-1, 0)
        NorthWest = Vector(-1, -1)

    def __init__(self, direction: Direction):
        self.direction = direction