#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

import tcod
from .actions import Action, ExitAction, RegenerateRoomsAction, BumpAction
from .geometry import Direction
from typing import Optional

class EventHandler(tcod.event.EventDispatch[Action]):
    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        return ExitAction()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        sym = event.sym

        if sym == tcod.event.KeySym.b:
            action = BumpAction(Direction.SouthWest)
        elif sym == tcod.event.KeySym.h:
            action = BumpAction(Direction.West)
        elif sym == tcod.event.KeySym.j:
            action = BumpAction(Direction.South)
        elif sym == tcod.event.KeySym.k:
            action = BumpAction(Direction.North)
        elif sym == tcod.event.KeySym.l:
            action = BumpAction(Direction.East)
        elif sym == tcod.event.KeySym.n:
            action = BumpAction(Direction.SouthEast)
        elif sym == tcod.event.KeySym.u:
            action = BumpAction(Direction.NorthEast)
        elif sym == tcod.event.KeySym.y:
            action = BumpAction(Direction.NorthWest)
        elif sym == tcod.event.KeySym.SPACE:
            action = RegenerateRoomsAction()

        return action
