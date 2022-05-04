#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

import tcod
from .actions import Action, ExitAction, MovePlayerAction, RegenerateRoomsAction
from .geometry import Direction
from typing import Optional

class EventHandler(tcod.event.EventDispatch[Action]):
    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        return ExitAction()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        sym = event.sym

        if sym == tcod.event.KeySym.b:
            action = MovePlayerAction(Direction.SouthWest)
        elif sym == tcod.event.KeySym.h:
            action = MovePlayerAction(Direction.West)
        elif sym == tcod.event.KeySym.j:
            action = MovePlayerAction(Direction.South)
        elif sym == tcod.event.KeySym.k:
            action = MovePlayerAction(Direction.North)
        elif sym == tcod.event.KeySym.l:
            action = MovePlayerAction(Direction.East)
        elif sym == tcod.event.KeySym.n:
            action = MovePlayerAction(Direction.SouthEast)
        elif sym == tcod.event.KeySym.u:
            action = MovePlayerAction(Direction.NorthEast)
        elif sym == tcod.event.KeySym.y:
            action = MovePlayerAction(Direction.NorthWest)
        elif sym == tcod.event.KeySym.SPACE:
            action = RegenerateRoomsAction()

        return action
