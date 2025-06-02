from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from year import Year 
    from elf import Elf

from typing import Dict


# population object is a dictionary of all Elves - key is ID, value is Elf object

population: Dict [int, Elf] = {}

# history object is a dictionary of all Years = key is year, value is Year object

history: Dict [int, Year] = {}