# Eryn Wells <eryn@erynwells.me>

from typing import TYPE_CHECKING

from ..object import Actor
from .result import ActionResult

if TYPE_CHECKING:
    from ..engine import Engine


class Action:
    '''An action with no specific actor'''

    def __init__(self, actor: Actor):
        super().__init__()
        self.actor = actor

    # pylint: disable=unused-argument
    def perform(self, engine: 'Engine') -> ActionResult:
        '''Perform this action.

        Parameters
        ----------
        engine : Engine
            The game engine

        Returns
        -------
        ActionResult
            A result object reflecting how the action was handled, and what follow-up actions, if any, are needed to
            complete the action.
        '''
        return self.success()

    def failure(self) -> ActionResult:
        '''Create an ActionResult indicating failure with no follow-up'''
        return ActionResult(self, success=False)

    def success(self) -> ActionResult:
        '''Create an ActionResult indicating success with no follow-up'''
        return ActionResult(self, success=True)

    def __str__(self) -> str:
        return self.__class__.__name__

    def __repr__(self):
        return f'{self.__class__.__name__}()'
