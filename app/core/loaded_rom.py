from dataclasses import dataclass

from app.core.enums import Game
from app.core.n64_rom import ROM, Soundfont


@dataclass
class LoadedROM:
    game: Game
    soundfonts: list[Soundfont]

    @staticmethod
    def load_rom_data(file_path: str) -> 'LoadedROM':
        rom = ROM(file_path)

        try:
            if not rom.is_valid:
                raise ValueError('Invalid ROM file')

            soundfonts = rom.get_soundfonts()
            game = rom.game

            return LoadedROM(
                game=game,
                soundfonts=soundfonts
            )
        finally:
            rom.close()