#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

import tcod
from .actions import Action, ExitAction, MovePlayerAction, RegenerateRoomsAction
from typing import Optional

class EventHandler(tcod.event.EventDispatch[Action]):
    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        return ExitAction()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        sym = event.sym

        if sym == tcod.event.KeySym.h:
            action = MovePlayerAction(MovePlayerAction.Direction.West)
        elif sym == tcod.event.KeySym.j:
            action = MovePlayerAction(MovePlayerAction.Direction.South)
        elif sym == tcod.event.KeySym.k:
            action = MovePlayerAction(MovePlayerAction.Direction.North)
        elif sym == tcod.event.KeySym.l:
            action = MovePlayerAction(MovePlayerAction.Direction.East)
        elif sym == tcod.event.KeySym.SPACE:
            action = RegenerateRoomsAction()

        return action
