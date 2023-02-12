# Eryn Wells <eryn@erynwells.me>

'''Defines the core game engine.'''

import random
from typing import TYPE_CHECKING, List, MutableSet, NoReturn, Optional

import tcod

from . import log
from . import monsters
from .actions.action import Action
from .actions.result import ActionResult
from .ai import HostileEnemy
from .configuration import Configuration
from .events import GameOverEventHandler, MainGameEventHandler
from .geometry import Point, Size
from .interface import Interface
from .map import Map
from .map.generator import RoomsAndCorridorsGenerator
from .map.generator.room import BSPRoomGenerator
from .map.generator.corridor import ElbowCorridorGenerator
from .messages import MessageLog
from .object import Actor, Entity, Hero, Monster

if TYPE_CHECKING:
    from .events import EventHandler


class Engine:
    '''The main game engine.

    This class provides the event handling, map drawing, and maintains the list of entities.

    Attributes
    ----------
    configuration : Configuration
        Defines the basic configuration for the game
    entities : MutableSet[Entity]
        A set of all the entities on the current map, including the Hero
    hero : Hero
        The hero, the Entity controlled by the player
    map : Map
        A map of the current level
    rng : tcod.random.Random
        A random number generator
    '''

    def __init__(self, config: Configuration):
        self.configuration = config

        self.current_turn = 1
        self.did_begin_turn = False
        self.did_successfully_process_actions_for_turn = False

        self.rng = tcod.random.Random()
        self.message_log = MessageLog()

        map_size = config.map_size
        self.map = Map(config, map_generator)

        self.event_handler: 'EventHandler' = MainGameEventHandler(self)

        self.__current_mouse_point: Optional[Point] = None
        self.__mouse_path_points: Optional[List[Point]] = None

        self.entities: MutableSet[Entity] = set()

        try:
            hero_start_position = self.map.up_stairs[0]
        except IndexError:
            hero_start_position = self.map.random_walkable_position()
        self.hero = Hero(position=hero_start_position)

        self.entities.add(self.hero)

        while len(self.entities) < 25:
            should_spawn_monster_chance = random.random()
            if should_spawn_monster_chance < 0.1:
                continue

            while True:
                random_start_position = self.map.random_walkable_position()
                if not any(ent.position == random_start_position for ent in self.entities):
                    break

            spawn_monster_chance = random.random()
            if spawn_monster_chance > 0.8:
                monster = Monster(monsters.Troll, ai_class=HostileEnemy, position=random_start_position)
            else:
                monster = Monster(monsters.Orc, ai_class=HostileEnemy, position=random_start_position)

            log.ENGINE.info('Spawning %s', monster)
            self.entities.add(monster)

        self.update_field_of_view()

        # Interface elements
        self.interface = Interface(Size(80, 50), self.map, self.message_log)
        self.message_log.add_message('Greetings adventurer!', fg=(127, 127, 255), stack=False)

    def print_to_console(self, console):
        '''Print the whole game to the given console.'''
        self.map.highlight_points(self.__mouse_path_points or [])

        self.interface.update(self.hero, self.current_turn)
        self.interface.draw(console)

        entities_at_mouse_position = []
        for ent in sorted(self.entities, key=lambda e: e.render_order.value):
            # Only process entities that are in the field of view
            if not self.map.visible[tuple(ent.position)]:
                continue

            ent.print_to_console(console)

            if ent.position == self.__current_mouse_point:
                entities_at_mouse_position.append(ent)

        if len(entities_at_mouse_position) > 0:
            console.print(x=1, y=43, string=', '.join(e.name for e in entities_at_mouse_position))

    def run_event_loop(self, context: tcod.context.Context, console: tcod.Console) -> NoReturn:
        '''Run the event loop forever. This method never returns.'''
        while True:
            console.clear()
            self.print_to_console(console)
            context.present(console)

            self.begin_turn()
            self.event_handler.handle_events(context)
            self.finish_turn()

    def process_input_action(self, action: Action):
        '''Process an Action from player input'''

        log.ACTIONS_TREE.info('Processing Hero Actions')
        log.ACTIONS_TREE.info('|-> %s', action.actor)

        # Clear the mouse path highlight before handling actions.
        self.__mouse_path_points = None

        result = self._perform_action_until_done(action)

        # Player's action failed, don't proceed with turn.
        if not result.success and result.done:
            self.did_successfully_process_actions_for_turn = False
            return

        self.did_successfully_process_actions_for_turn = True
        self.process_entity_actions()
        self.update_field_of_view()

    def process_entity_actions(self):
        '''Run AI for entities that have them, and process actions from those AIs'''
        hero_position = self.hero.position

        # Copy the list so we only act on the entities that exist at the start of this turn. Sort it by Euclidean
        # distance to the Hero, so entities closer to the hero act first.
        entities = sorted(
            self.entities,
            key=lambda e: e.position.euclidean_distance_to(hero_position))

        log.ACTIONS_TREE.info('Processing Entity Actions')

        for i, ent in enumerate(entities):
            if not isinstance(ent, Actor):
                continue

            ent_ai = ent.ai
            if not ent_ai:
                continue

            if self.map.visible[tuple(ent.position)]:
                log.ACTIONS_TREE.info('%s-> %s', '|' if i < len(entities) - 1 else '`', ent)

            action = ent_ai.act(self)
            self._perform_action_until_done(action)

    def _perform_action_until_done(self, action: Action) -> ActionResult:
        '''Perform the given action and any alternate follow-up actions until the action chain is done.'''
        result = action.perform(self)

        if log.ACTIONS_TREE.isEnabledFor(log.INFO) and self.map.visible[tuple(action.actor.position)]:
            if result.alternate:
                alternate_string = f'{result.alternate.__class__.__name__}[{result.alternate.actor.symbol}]'
            else:
                alternate_string = str(result.alternate)
            log.ACTIONS_TREE.info(
                '|   %s-> %s => success=%s done=%s alternate=%s',
                '|' if not result.success or not result.done else '`',
                action,
                result.success,
                result.done,
                alternate_string)

        while not result.done:
            action = result.alternate
            assert action is not None, f'Action {result.action} incomplete but no alternate action given'

            result = action.perform(self)

            if log.ACTIONS_TREE.isEnabledFor(log.INFO) and self.map.visible[tuple(action.actor.position)]:
                if result.alternate:
                    alternate_string = f'{result.alternate.__class__.__name__}[{result.alternate.actor.symbol}]'
                else:
                    alternate_string = str(result.alternate)
                log.ACTIONS_TREE.info(
                    '|   %s-> %s => success=%s done=%s alternate=%s',
                    '|' if not result.success or not result.done else '`',
                    action,
                    result.success,
                    result.done,
                    alternate_string)

            if result.success:
                break

        return result

    def update_field_of_view(self):
        '''Compute visible area of the map based on the player's position and point of view.'''
        # FIXME: Move this to the Map class
        self.map.visible[:] = tcod.map.compute_fov(
            self.map.tiles['transparent'],
            tuple(self.hero.position),
            radius=8)

        # Add visible tiles to the explored grid
        self.map.explored |= self.map.visible

    def update_mouse_point(self, mouse_point: Optional[Point]):
        if mouse_point == self.__current_mouse_point:
            return

        should_render_mouse_path = (
            mouse_point
            and self.map.tile_is_in_bounds(mouse_point)
            and self.map.tile_is_walkable(mouse_point))

        if not should_render_mouse_path:
            self.__current_mouse_point = None
            self.__mouse_path_points = None
            return

        self.__current_mouse_point = mouse_point

        path_from_hero_to_mouse_point = tcod.los.bresenham(tuple(self.hero.position), tuple(self.__current_mouse_point))
        mouse_path_points = [Point(x, y) for x, y in path_from_hero_to_mouse_point.tolist()]

        all_mouse_path_points_are_walkable = all(
            self.map.tile_is_walkable(pt) and self.map.point_is_explored(pt) for pt in mouse_path_points)
        if not all_mouse_path_points_are_walkable:
            self.__current_mouse_point = None
            self.__mouse_path_points = None
            return

        self.__mouse_path_points = mouse_path_points

    def begin_turn(self) -> None:
        '''Begin the current turn'''
        if self.did_begin_turn:
            return

        if log.ROOT.isEnabledFor(log.INFO):
            dashes = '-' * 20
            log.ROOT.info('%s Turn %d %s', dashes, self.current_turn, dashes)

        self.did_begin_turn = True

    def finish_turn(self) -> None:
        '''Finish the current turn and prepare for the next turn'''
        if not self.did_successfully_process_actions_for_turn:
            return

        log.ROOT.info('Completed turn %d successfully', self.current_turn)
        self._prepare_for_next_turn()

    def _prepare_for_next_turn(self) -> None:
        self.current_turn += 1
        self.did_begin_turn = False
        self.did_successfully_process_actions_for_turn = False

    def kill_actor(self, actor: Actor) -> None:
        '''Kill an entity. Remove it from the game.'''
        if actor == self.hero:
            # When the hero dies, the game is over.
            log.ACTIONS.info('Time to die.')
            self.event_handler = GameOverEventHandler(self)
        else:
            log.ACTIONS.info('%s dies', actor)
            self.entities.remove(actor)
