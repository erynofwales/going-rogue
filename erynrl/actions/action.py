# Eryn Wells <eryn@erynwells.me>

from typing import TYPE_CHECKING, Optional

from ..object import Actor
from .result import ActionResult

if TYPE_CHECKING:
    from ..engine import Engine

class Action:
    '''An action that an Entity should perform.'''

    def __init__(self, actor: Optional[Actor] = None):
        self.actor = actor

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
        raise NotImplementedError()

    def failure(self) -> ActionResult:
        '''Create an ActionResult indicating failure with no follow-up'''
        return ActionResult(self, success=False)

    def success(self) -> ActionResult:
        '''Create an ActionResult indicating success with no follow-up'''
        return ActionResult(self, success=True)

    def __str__(self) -> str:
        return f'{self.__class__.__name__} for {self.actor!s}'

    def __repr__(self):
        return f'{self.__class__.__name__}({self.actor!r})'
