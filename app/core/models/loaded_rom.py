from dataclasses import dataclass

from app.core.enums import Game
from app.core.n64_rom import Soundfont


@dataclass
class LoadedROM:
    game: Game
    soundfonts: list[Soundfont]