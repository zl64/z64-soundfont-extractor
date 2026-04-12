from pathlib import Path
from PySide6.QtCore import QObject, Signal
import traceback

from app.core.constants import OUT_DIR, VANILLA_SOUNDFONT_MD5_HASHES
from app.core.models import LoadedROM
from app.core.n64_rom import Soundfont
from app.core.services import ROMLoaderService
from app.gui.services import SoundfontExtractionService


class SoundfontExtractorViewmodel(QObject):
    rom_loaded = Signal(str)
    output_dir_changed = Signal(str)
    soundfonts_reset = Signal(list)
    operation_failed = Signal(str)
    operation_succeeded = Signal(str)
    state_changed = Signal(bool)
    overwrite_requested = Signal(Path, object)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.rom_loader: ROMLoaderService = ROMLoaderService()
        self.loaded_rom: LoadedROM | None = None
        self.output_dir: Path | None = None
        self.selected_soundfont: Soundfont | None = None
        self.filter_modified: bool = False

    def load_rom(self, file_path: str) -> None:
        try:
            self.loaded_rom = self.rom_loader.load(file_path)

            self.rom_loaded.emit(file_path)
            self.state_changed.emit(self.loaded_rom is not None)
            self._emit_soundfonts()

        except Exception as ex:
            traceback.print_exc()
            self.loaded_rom = None
            self.operation_failed.emit(str(ex))
            self.state_changed.emit(False)

    def set_output_dir(self, dir_path: str) -> None:
        self.output_dir = Path(dir_path).resolve()
        self.output_dir_changed.emit(dir_path)

    def set_filter_modified(self, enabled: bool) -> None:
        self.filter_modified = enabled
        self._emit_soundfonts()

    def set_selected_soundfont(self, soundfont: Soundfont | None) -> None:
        if self.selected_soundfont == soundfont:
            return

        self.selected_soundfont = soundfont

    def _emit_soundfonts(self) -> None:
        if not self.loaded_rom:
            self.soundfonts_reset.emit([])
            return

        items = self.loaded_rom.soundfonts

        if self.filter_modified:
            vanilla = set(self.get_vanilla_hashes())
            items = [sf for sf in items if sf.hash not in vanilla]

        self.soundfonts_reset.emit(items)

    def get_vanilla_hashes(self) -> list[str]:
        if not self.loaded_rom:
            return []
        return VANILLA_SOUNDFONT_MD5_HASHES.get(self.loaded_rom.game, [])

    def extract_selected_soundfont(self) -> None:
        if not self.loaded_rom:
            return

        if not isinstance(self.selected_soundfont, Soundfont):
            self.operation_failed.emit('No valid soundfont selected')
            return

        if self.output_dir is None or not self.output_dir.exists():
            self.output_dir = OUT_DIR / self.loaded_rom.game.name
            self.output_dir.mkdir(parents=True, exist_ok=True)

        extract_service = SoundfontExtractionService(
            soundfont=self.selected_soundfont,
            output_dir=self.output_dir,
            view_model=self,
        )

        extract_service.prepare()
        extract_service.start()
