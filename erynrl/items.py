# Eryn Wells <eryn@erynwells.me>

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class Item:
    '''A record of a kind of item

    This class follows the "type class" pattern. It represents a kind of item, not a specific instance of that item.
    (See `object.Item` for that.)

    Attributes
    ----------
    symbol : str
        The symbol used to render this item on the map
    foreground_color : Tuple[int, int, int]
        The foreground color used to render this item on the map
    background_color : Tuple[int, int, int], optional
        The background color used to render this item on the map
    name : str
        The name of this item
    description : str
        A description of this item
    '''
    symbol: str
    name: str
    description: str
    foreground_color: Tuple[int, int, int]
    background_color: Optional[Tuple[int, int, int]] = None


Corpse = Item(
    '%',
    name="Corpse",
    description="The corpse of a once-living being",
    foreground_color=(128, 128, 255))
