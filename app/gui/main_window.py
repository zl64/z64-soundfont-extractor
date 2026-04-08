from dataclasses import dataclass
from pathlib import Path
import traceback
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QComboBox,
    QCheckBox,
    QPushButton,
    QFileDialog,
    QHBoxLayout,
    QGroupBox,
    QLineEdit,
    QMessageBox,
)

from app.core.constants import GUI_DIR, OUT_DIR, ROM_EXTS, VANILLA_SOUNDFONT_MD5_HASHES
from app.core.enums import Game
from app.core.n64_rom import ROM, Soundfont


@dataclass(slots=True)
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


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Zelda64 Soundfont Extractor')
        self.setFixedSize(500, 250)
        self.setAcceptDrops(True)

        # Init ROM
        self.loaded_rom: LoadedROM | None = None

        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self._init_rom_group())
        main_layout.addWidget(self._init_soundfont_group())

        self.extract_button = create_push_button('Extract Soundfont', enabled=False)
        self.extract_button.clicked.connect(self._extract_soundfont)
        main_layout.addWidget(self.extract_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.setLayout(main_layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            if any(url.toLocalFile().lower().endswith(ROM_EXTS) for url in event.mimeData().urls()):
                event.acceptProposedAction()
            else:
                event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()

                if file_path.lower().endswith(ROM_EXTS):
                    self._load_rom(file_path=file_path)
                    break

    def _select_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f'Select decompressed ROM file',
            '',
            'ROM Files (*.z64 *.n64 *.v64);;All Files (*.*)'
        )

        if file_path:
            self._load_rom(file_path=file_path)

    def _init_rom_group(self) -> QGroupBox:
        group_box = QGroupBox('ROM')

        # ROM path line edit
        self.rom_file_path_edit = create_line_edit(min_width=200, read_only=False, focus_policy=Qt.FocusPolicy.NoFocus)
        self.rom_file_path_edit.setAcceptDrops(True)

        # ROM file dialog button
        self.rom_file_button = create_push_button('Open ROM File', fixed_width=150)
        self.rom_file_button.clicked.connect(self._select_file_dialog)

        # Horiz layout for the line edit and button
        layout = QHBoxLayout()
        layout.addWidget(self.rom_file_path_edit)
        layout.addWidget(self.rom_file_button)

        group_box.setLayout(layout)
        return group_box

    def _init_soundfont_group(self) -> QGroupBox:
        group_box = QGroupBox('Soundfont')

        # Soundfont combobox
        self.soundfont_combo = QComboBox()
        self.soundfont_combo.setFixedWidth(250)
        self.soundfont_combo.setMaxVisibleItems(10)

        # Checkbox to filter vanilla soundfonts out
        self.modified_soundfont_checkbox = QCheckBox('Show only modified soundfonts')
        self.modified_soundfont_checkbox.setEnabled(False)
        self.modified_soundfont_checkbox.stateChanged.connect(self._populate_soundfonts)

        # Horiz layout for the combobox and checkbox
        layout = QHBoxLayout()
        layout.addWidget(self.soundfont_combo)
        layout.addWidget(self.modified_soundfont_checkbox)

        group_box.setLayout(layout)
        return group_box

    def _make_file_row(self, line_edit, button) -> QHBoxLayout:
        row = QHBoxLayout()
        row.addWidget(line_edit)
        row.addWidget(button)

        return row

    def _load_rom(self, file_path: str):
        try:
            loaded = LoadedROM.load_rom_data(file_path)

            self.loaded_rom = loaded
            self.rom_file_path_edit.setText(file_path)
            self._populate_soundfonts()

            self.extract_button.setEnabled(True)
            self.modified_soundfont_checkbox.setEnabled(True)
        except Exception as ex:
            traceback.print_exc()
            QMessageBox.critical(self, 'Error', str(ex))
            self._reset_ui()

    def _reset_ui(self):
        self.loaded_rom = None
        self.extract_button.setEnabled(False)
        self.modified_soundfont_checkbox.setEnabled(False)
        self.soundfont_combo.clear()

    def _populate_soundfonts(self):
        self.soundfont_combo.clear()

        if not self.loaded_rom:
            return

        soundfonts = self.loaded_rom.soundfonts
        vanilla_hashes = VANILLA_SOUNDFONT_MD5_HASHES.get(self.loaded_rom.game, [])
        filter_modified = self.modified_soundfont_checkbox.isChecked()

        for sf in soundfonts:
            if filter_modified and sf.is_vanilla(vanilla_hashes):
                continue

            self.soundfont_combo.addItem(sf.display_name, sf)

    def _confirm_and_extract(self, path: Path, write_func):
        if path.exists():
            replace_button = QPushButton('Replace file')
            skip_button = QPushButton('Skip file')

            message_box = QMessageBox(self)
            message_box.setWindowTitle('Replace or Skip Files')
            message_box.setText(f'The destination already has a file named "{path.name}"')
            message_box.addButton(replace_button, QMessageBox.ButtonRole.AcceptRole)
            message_box.addButton(skip_button, QMessageBox.ButtonRole.RejectRole)
            message_box.setIcon(QMessageBox.Icon.Question)

            message_box.exec()

            if message_box.clickedButton() == skip_button:
                return

        write_func(path)

    def _extract_soundfont(self):
        if not self.loaded_rom:
            return

        soundfont: Soundfont | None = self.soundfont_combo.currentData()

        if not isinstance(soundfont, Soundfont):
            QMessageBox.warning(self, 'Warning', 'No valid soundfont selected')
            return

        output_dir = OUT_DIR / self.loaded_rom.game.name
        output_dir.mkdir(parents=True, exist_ok=True)

        base_path = output_dir / f'{soundfont.index:02X}'
        zbank_path = base_path.with_suffix('.zbank')
        bankmeta_path = base_path.with_suffix('.bankmeta')

        try:
            self._confirm_and_extract(zbank_path, soundfont.write_soundfont)
            self._confirm_and_extract(bankmeta_path, soundfont.write_table_entry)

            QMessageBox.information(self, 'Success', f'Soundfont data extracted to:\n{output_dir}')
        except Exception as ex:
            traceback.print_exc()
            QMessageBox.critical(self, 'Error', str(ex))


# GUI Helpers
def create_push_button(
    text: str,
    *,
    fixed_width: int = 200,
    enabled: bool = True,
    focus_policy=Qt.FocusPolicy.NoFocus
) -> QPushButton:
    push_button = QPushButton(text)
    push_button.setFixedWidth(fixed_width)
    push_button.setEnabled(enabled)
    push_button.setFocusPolicy(focus_policy)

    return push_button


def create_line_edit(
    *,
    min_width: int = 200,
    read_only: bool = False,
    enabled: bool = True,
    focus_policy=Qt.FocusPolicy.NoFocus
) -> QLineEdit:
    line_edit = QLineEdit()
    line_edit.setMinimumWidth(min_width)
    line_edit.setEnabled(enabled)
    line_edit.setReadOnly(read_only)
    line_edit.setFocusPolicy(focus_policy)

    return line_edit