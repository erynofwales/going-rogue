# Eryn Wells <eryn@erynwells.me>

'''Defines event handling mechanisms.'''

import logging
from typing import Optional, TYPE_CHECKING

import tcod

from .actions import Action, ActionResult, ExitAction, RegenerateRoomsAction, BumpAction, WaitAction
from .geometry import Direction
from .object import Actor

if TYPE_CHECKING:
    from .engine import Engine

LOG = logging.getLogger('events')
ACTIONS_TREE_LOG = logging.getLogger('actions.tree')

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

        # Unhandled event. Ignore it.
        if not action:
            LOG.debug('Unhandled event: %s', event)
            return

        ACTIONS_TREE_LOG.info('Processing Hero Actions')
        ACTIONS_TREE_LOG.info('|-> %s', action.actor)

        result = self.perform_action_until_done(action)

        # Player's action failed, don't proceed with turn.
        if not result.success and result.done:
            return

        # Copy the list so we only act on the entities that exist at the start of this turn. Sort it by Euclidean
        # distance to the Hero, so entities closer to the hero act first.
        hero_position = self.engine.hero.position
        entities = sorted(
            self.engine.entities,
            key=lambda e: e.position.euclidean_distance_to(hero_position))

        ACTIONS_TREE_LOG.info('Processing Entity Actions')

        for i, ent in enumerate(entities):
            if not isinstance(ent, Actor):
                continue

            ent_ai = ent.ai
            if not ent_ai:
                continue

            if self.engine.map.visible[tuple(ent.position)]:
                ACTIONS_TREE_LOG.info('%s-> %s', '|' if i < len(entities) - 1 else '`', ent)

            action = ent_ai.act(self.engine)
            self.perform_action_until_done(action)

        self.engine.update_field_of_view()

    def perform_action_until_done(self, action: Action) -> ActionResult:
        '''Perform the given action and any alternate follow-up actions until the action chain is done.'''
        result = action.perform(self.engine)

        if ACTIONS_TREE_LOG.isEnabledFor(logging.INFO) and self.engine.map.visible[tuple(action.actor.position)]:
            if result.alternate:
                alternate_string = f'{result.alternate.__class__.__name__}[{result.alternate.actor.symbol}]'
            else:
                alternate_string = str(result.alternate)
            ACTIONS_TREE_LOG.info('|   %s-> %s => success=%s done=%s alternate=%s',
                '|' if not result.success or not result.done else '`',
                action,
                result.success,
                result.done,
                alternate_string)

        while not result.done:
            action = result.alternate
            assert action is not None, f'Action {result.action} incomplete but no alternate action given'

            result = action.perform(self.engine)

            if ACTIONS_TREE_LOG.isEnabledFor(logging.INFO) and self.engine.map.visible[tuple(action.actor.position)]:
                if result.alternate:
                    alternate_string = f'{result.alternate.__class__.__name__}[{result.alternate.actor.symbol}]'
                else:
                    alternate_string = str(result.alternate)
                ACTIONS_TREE_LOG.info('|   %s-> %s => success=%s done=%s alternate=%s',
                    '|' if not result.success or not result.done else '`',
                    action,
                    result.success,
                    result.done,
                    alternate_string)

            if result.success:
                break

        return result

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        return ExitAction(self.engine.hero)

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
                action = RegenerateRoomsAction(hero)
            case tcod.event.KeySym.PERIOD:
                action = WaitAction(hero)

        return action
