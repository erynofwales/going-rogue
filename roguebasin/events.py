# Eryn Wells <eryn@erynwells.me>

'''Defines event handling mechanisms.'''

from typing import Optional

import tcod

from .actions import Action, ExitAction, RegenerateRoomsAction, BumpAction
from .geometry import Direction

class EventHandler(tcod.event.EventDispatch[Action]):
    '''Handler of `tcod` events'''

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        return ExitAction()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        sym = event.sym
        match sym:
            case tcod.event.KeySym.b:
                action = BumpAction(Direction.SouthWest)
            case tcod.event.KeySym.h:
                action = BumpAction(Direction.West)
            case tcod.event.KeySym.j:
                action = BumpAction(Direction.South)
            case tcod.event.KeySym.k:
                action = BumpAction(Direction.North)
            case tcod.event.KeySym.l:
                action = BumpAction(Direction.East)
            case tcod.event.KeySym.n:
                action = BumpAction(Direction.SouthEast)
            case tcod.event.KeySym.u:
                action = BumpAction(Direction.NorthEast)
            case tcod.event.KeySym.y:
                action = BumpAction(Direction.NorthWest)
            case tcod.event.KeySym.SPACE:
                action = RegenerateRoomsAction()

        return action
