# Eryn Wells <eryn@erynwells.me>

'''
Defines the classes the support the in-game message log. Messages are recorded to the log as game actions are handled. A
short buffer of messages is displayed in the game's HUD, and a full list of messages can be viewed by the player at any
time.
'''

import textwrap
from typing import List, Optional, Reversible, Tuple

import tcod

from .geometry import Rect


class Message:
    '''A message in the message log

    Attributes
    ----------
    text : str
        The text of the message
    foreground : Tuple[int, int, int]
        The foreground color to render the message with
    count : int
        The number of times this message has stacked
    '''

    def __init__(self, text: str, fg: Optional[Tuple[int, int, int]] = None):
        self.text = text
        self.foreground = fg
        self.count = 1

    @property
    def full_text(self) -> str:
        '''The full text of the message, including a count of repeats, if present'''
        if self.count == 1:
            return self.text
        return f'{self.text} (x{self.count})'

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({repr(self.text)}, fg={self.foreground})'


class MessageLog:
    '''A buffer of messages sent to the player by the game'''

    def __init__(self):
        self.messages: List[Message] = []

    def add_message(self, text: str, fg: Optional[Tuple[int, int, int]] = None, stack: bool = True):
        '''
        Add a message to the buffer

        Parameters
        ----------
        text : str
            The text of the message
        fg : Tuple[int, int, int], optional
            A foreground color to render the text
        stack : bool
            If True and the previous message in the buffer is the same as the text given, increment the count of that
            message rather than adding a new message to the buffer
        '''
        if stack and self.messages and self.messages[-1].text == text:
            self.messages[-1].count += 1
        else:
            self.messages.append(Message(text, fg))

    def render_to_console(self, console: tcod.console.Console, rect: Rect):
        '''Render this message log to the given console in the given rect'''
        self.render_messages(console, rect, self.messages)

    @staticmethod
    def render_messages(console: tcod.console.Console, rect: Rect, messages: Reversible[Message]):
        '''Render a list of messages to the console in the given rect'''
        y_offset = min(rect.size.height, len(messages)) - 1

        for message in reversed(messages):
            wrapped_text = textwrap.wrap(message.full_text, rect.size.width)
            for line in wrapped_text:
                console.print(x=rect.min_x, y=rect.min_y + y_offset, string=line, fg=message.foreground)
                y_offset -= 1

                if y_offset < 0:
                    break

            if y_offset < 0:
                break
