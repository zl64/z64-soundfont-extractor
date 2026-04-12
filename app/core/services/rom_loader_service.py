from app.core.models import LoadedROM
from app.core.n64_rom import ROM


class ROMLoaderService:
    def load(self, file_path: str) -> LoadedROM:
        rom = ROM(file_path)

        try:
            if not rom.is_valid:
                raise ValueError('Invalid ROM file')

            return LoadedROM(
                game=rom.game,
                soundfonts=rom.get_soundfonts()
            )
        finally:
            rom.close()