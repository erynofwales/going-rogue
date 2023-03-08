# Eryn Wells <eryn@erynwells.me>

'''
Declares the MessageLogWindow.
'''

from . import Window
from ...geometry import Rect
from ...messages import MessageLog


class MessageLogWindow(Window):
    '''A window that displays a list of messages'''

    def __init__(self, bounds: Rect, message_log: MessageLog):
        super().__init__(bounds, framed=True)
        self.message_log = message_log

    def draw(self, console):
        super().draw(console)
        self.message_log.render_to_console(console, self.drawable_bounds)
