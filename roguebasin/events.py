# Eryn Wells <eryn@erynwells.me>

'''Defines event handling mechanisms.'''

import logging
import random
from typing import MutableSet, Optional, TYPE_CHECKING

import tcod

from .actions import Action, ActionResult, ExitAction, RegenerateRoomsAction, BumpAction
from .geometry import Direction
from .object import Entity

if TYPE_CHECKING:
    from .engine import Engine

LOG = logging.getLogger('events')

class EventHandler(tcod.event.EventDispatch[Action]):
    '''Handler of `tcod` events'''

    def __init__(self, engine: 'Engine'):
        super().__init__()
        self.engine = engine

    def wait_for_events(self):
        '''Wait for events and handle them.'''
        for event in tcod.event.wait():
            self.handle_event(event)

    def handle_event(self, event: tcod.event.Event) -> None:
        '''Handle the given event. Transform that event into an Action via an EventHandler and perform it.'''
        action = self.dispatch(event)

        if not action:
            return

        result = self.perform_action_until_done(action)

        # Action failed, so do nothing further.
        if not result.success and result.done:
            return

        directions = list(Direction.all())

        hero = self.engine.hero
        moved_entities: MutableSet[Entity] = {self.engine.hero}

        for ent in self.engine.entities:
            if ent == hero:
                continue

            while True:
                new_position = ent.position + random.choice(directions)
                overlaps_with_previously_moved_entity = any(new_position == moved_ent.position for moved_ent in moved_entities)
                tile_is_walkable = self.engine.map.tile_is_walkable(new_position)
                if not overlaps_with_previously_moved_entity and tile_is_walkable:
                    ent.position = new_position
                    moved_entities.add(ent)
                    break

        self.engine.update_field_of_view()

    def perform_action_until_done(self, action: Action) -> ActionResult:
        '''Perform the given action and any alternate follow-up actions until the action chain is done.'''
        result = action.perform(self.engine)
        LOG.debug('Performed action success=%s done=%s alternate=%s', result.success, result.done, result.alternate)

        while not result.done:
            alternate = result.alternate
            assert alternate is not None, f'Action {result.action} incomplete but no alternate action given'

            result = alternate.perform(self.engine)
            LOG.debug('Performed action success=%s done=%s alternate=%s', result.success, result.done, result.alternate)

            if result.success:
                LOG.info('Action succeded!')
                break
        else:
            LOG.info('Action failed!')

        return result

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        return ExitAction()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        hero = self.engine.hero

        sym = event.sym
        match sym:
            case tcod.event.KeySym.b:
                action = BumpAction(hero, Direction.SouthWest)
            case tcod.event.KeySym.h:
                action = BumpAction(hero, Direction.West)
            case tcod.event.KeySym.j:
                action = BumpAction(hero, Direction.South)
            case tcod.event.KeySym.k:
                action = BumpAction(hero, Direction.North)
            case tcod.event.KeySym.l:
                action = BumpAction(hero, Direction.East)
            case tcod.event.KeySym.n:
                action = BumpAction(hero, Direction.SouthEast)
            case tcod.event.KeySym.u:
                action = BumpAction(hero, Direction.NorthEast)
            case tcod.event.KeySym.y:
                action = BumpAction(hero, Direction.NorthWest)
            case tcod.event.KeySym.SPACE:
                action = RegenerateRoomsAction()

        return action
