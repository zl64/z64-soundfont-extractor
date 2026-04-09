from pathlib import Path
from PySide6.QtCore import QObject, Signal
import traceback

from app.core.constants import OUT_DIR, VANILLA_SOUNDFONT_MD5_HASHES
from app.core.loaded_rom import LoadedROM
from app.core.n64_rom import Soundfont


class MainWindowViewModel(QObject):
    rom_loaded = Signal(str)
    soundfonts_reset = Signal(list)
    error_occured = Signal(str)
    extraction_success = Signal(str)
    state_changed = Signal(bool)
    overwrite_requested = Signal(str, object)

    def __init__(self):
        super().__init__()
        self.loaded_rom: LoadedROM | None = None
        self.selected_soundfont: Soundfont | None = None
        self.filter_modified: bool = False

    def load_rom(self, file_path: str) -> None:
        try:
            self.loaded_rom = LoadedROM.load_rom_data(file_path)

            self.rom_loaded.emit(file_path)
            self.state_changed.emit(self.loaded_rom is not None)
            self._emit_soundfonts()

        except Exception as ex:
            traceback.print_exc()
            self.loaded_rom = None
            self.error_occured.emit(str(ex))
            self.state_changed.emit(False)

    def set_filter_modified(self, enabled: bool) -> None:
        self.filter_modified = enabled

        if self.selected_soundfont and self.loaded_rom:
            valid_indices = {sf.index for sf in self.loaded_rom.soundfonts}

            if self.selected_soundfont.index not in valid_indices:
                self.selected_soundfont = None

        self._emit_soundfonts()

    def set_selected_soundfont(self, soundfont: Soundfont | None) -> None:
        if self.selected_soundfont == soundfont:
            return

        self.selected_soundfont = soundfont

    def _emit_soundfonts(self) -> None:
        items = self.loaded_rom.soundfonts if self.loaded_rom else []
        self.soundfonts_reset.emit(items)

    def get_vanilla_hashes(self) -> list[str]:
        if not self.loaded_rom:
            return []
        return VANILLA_SOUNDFONT_MD5_HASHES.get(self.loaded_rom.game, [])

    def extract_selected_soundfont(self) -> None:
        if not self.loaded_rom:
            return

        soundfont = self.selected_soundfont

        if not isinstance(soundfont, Soundfont):
            self.error_occured.emit('No valid soundfont selected')
            return

        output_dir: Path = OUT_DIR / self.loaded_rom.game.name
        output_dir.mkdir(parents=True, exist_ok=True)

        base_path: Path = output_dir / f'{soundfont.index:02X}'
        targets = {
            'zbank': base_path.with_suffix('.zbank'),
            'bankmeta': base_path.with_suffix('.bankmeta')
        }

        try:
            for kind, path in targets.items():

                def proceed(should_write: bool, p=path, k=kind):
                    if not should_write:
                        return

                    if k == 'zbank':
                        soundfont.write_soundfont(p)
                    else:
                        soundfont.write_table_entry(p)

                if path.exists():
                    self.overwrite_requested.emit(str(path), proceed)
                else:
                    proceed(True)

            self.extraction_success.emit(str(output_dir))

        except Exception as ex:
            traceback.print_exc()
            self.error_occured.emit(str(ex))
