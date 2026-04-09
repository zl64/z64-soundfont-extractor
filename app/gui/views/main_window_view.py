from pathlib import Path
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

from app.core.constants import ROM_EXTS
from app.gui.models.soundfont_list_filter_proxy import SoundfontListFilterProxy
from app.gui.models.soundfont_list_model import SoundfontListModel
from app.gui.viewmodels.main_window_viewmodel import MainWindowViewModel


class MainWindowView(QWidget):
    def __init__(self, view_model: MainWindowViewModel):
        super().__init__()
        self.view_model: MainWindowViewModel = view_model

        self.setWindowTitle('Zelda64 Soundfont Extractor')
        self.setFixedSize(500, 250)
        self.setAcceptDrops(True)

        # Create UI
        self._create_ui()

        # Bind signals
        self._bind_view_model()

    def _create_ui(self) -> None:
        # Create main window layout
        self.main_layout = QVBoxLayout()

        # Create widgets
        self._create_rom_group()
        self._create_soundfont_group()
        self._create_extract_soundfont_button()

        # Add widgets to layout
        self.main_layout.addWidget(self.rom_group)
        self.main_layout.addWidget(self.soundfont_group)
        self.main_layout.addWidget(self.extract_soundfont_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Set layout
        self.setLayout(self.main_layout)

    def _create_rom_group(self) -> None:
        self.rom_group = QGroupBox()
        self.rom_group.setTitle('ROM')

        self._create_rom_file_path_line_edit()
        self._create_open_rom_button()

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.rom_file_path_line_edit)
        h_layout.addWidget(self.open_rom_button)

        self.rom_group.setLayout(h_layout)

    def _create_rom_file_path_line_edit(self) -> None:
        self.rom_file_path_line_edit = QLineEdit()
        self.rom_file_path_line_edit.setMinimumWidth(200)
        self.rom_file_path_line_edit.setEnabled(True)
        self.rom_file_path_line_edit.setReadOnly(False)
        self.rom_file_path_line_edit.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.rom_file_path_line_edit.setAcceptDrops(True)

    def _create_open_rom_button(self) -> None:
        self.open_rom_button = QPushButton()
        self.open_rom_button.setText('Open ROM')
        self.open_rom_button.setFixedWidth(150)
        self.open_rom_button.setEnabled(True)
        self.open_rom_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.open_rom_button.clicked.connect(self._select_file_dialog)

    def _create_soundfont_group(self) -> None:
        self.soundfont_group = QGroupBox()
        self.soundfont_group.setTitle('Soundfont')

        self._create_soundfont_combobox()
        self._create_modified_only_checkbox()

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.soundfont_combobox)
        h_layout.addWidget(self.modified_only_checkbox)

        self.soundfont_group.setLayout(h_layout)

    def _create_soundfont_combobox(self) -> None:
        self.soundfont_combobox = QComboBox()
        self.soundfont_combobox.setFixedWidth(250)
        self.soundfont_combobox.setMaxVisibleItems(10)

        self.soundfont_model = SoundfontListModel()
        self.soundfont_proxy = SoundfontListFilterProxy()

        self.soundfont_proxy.setSourceModel(self.soundfont_model)
        self.soundfont_combobox.setModel(self.soundfont_proxy)

        self.soundfont_combobox.currentIndexChanged.connect(self._on_selection_changed)

    def _create_modified_only_checkbox(self) -> None:
        self.modified_only_checkbox = QCheckBox()
        self.modified_only_checkbox.setText('Show modified soundfonts only')
        self.modified_only_checkbox.setEnabled(False)

        self.modified_only_checkbox.stateChanged.connect(self._on_filter_changed)

    def _create_extract_soundfont_button(self) -> None:
        self.extract_soundfont_button = QPushButton()
        self.extract_soundfont_button.setText('Extract Soundfont')
        self.extract_soundfont_button.setFixedWidth(200)
        self.extract_soundfont_button.setEnabled(False)
        self.extract_soundfont_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.extract_soundfont_button.clicked.connect(self._on_extract_clicked)

    def _bind_view_model(self) -> None:
        self.view_model.rom_loaded.connect(self._on_rom_loaded)
        self.view_model.soundfonts_reset.connect(self._on_soundfonts_reset)
        self.view_model.error_occured.connect(self._show_error)
        self.view_model.extraction_success.connect(self._show_success)
        self.view_model.state_changed.connect(self._update_ui_state)
        self.view_model.overwrite_requested.connect(self._on_overwrite_requested)

    def _select_file_dialog(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Select decompressed ROM file',
            '',
            'ROM Files (*.z64 *.n64 *.v64);;All Files (*.*)'
        )

        if file_path:
            self.view_model.load_rom(file_path)

    def _on_filter_changed(self, state: int):
        self.soundfont_proxy.set_filter(
            bool(state),
            self.view_model.get_vanilla_hashes()
        )

    def _on_selection_changed(self, proxy_index: int) -> None:
        if proxy_index < 0:
            self.view_model.set_selected_soundfont(None)
            return

        source_index = self.soundfont_proxy.mapToSource(
            self.soundfont_proxy.index(proxy_index, 0)
        )

        soundfont = source_index.data(Qt.ItemDataRole.UserRole)

        self.view_model.set_selected_soundfont(soundfont)

    def _on_extract_clicked(self) -> None:
        self.view_model.extract_selected_soundfont()

    def _on_overwrite_requested(self, path: str, callback) -> None:
        msg = QMessageBox(self)
        msg.setWindowTitle('Replace or Skip Files')
        msg.setText(f'The destination alread has a file named {path}')
        msg.setIcon(QMessageBox.Icon.Question)

        replace = msg.addButton('Replace file', QMessageBox.ButtonRole.AcceptRole)
        skip = msg.addButton('Skip file', QMessageBox.ButtonRole.RejectRole)

        msg.exec()

        callback(msg.clickedButton() == replace)

    def _on_rom_loaded(self, path: str) -> None:
        self.rom_file_path_line_edit.setText(path)

    def _on_soundfonts_reset(self, soundfonts: list) -> None:
        self.soundfont_model.set_items(soundfonts)

    def _update_ui_state(self, enabled: bool) -> None:
        self.extract_soundfont_button.setEnabled(enabled)
        self.modified_only_checkbox.setEnabled(enabled)

    def _show_error(self, message: str) -> None:
        QMessageBox.critical(self, 'Error', message)

    def _show_success(self, output_path: str) -> None:
        QMessageBox.information(self, 'Success', f'Soundfont data extracted to:\n{output_path}')

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            if any(url.toLocalFile().lower().endswith(ROM_EXTS) for url in event.mimeData().urls()):
                event.acceptProposedAction()
            else:
                event.ignore()

    def dropEvent(self, event) -> None:
        if not event.mimeData().hasUrls():
            return

        for url in event.mimeData().urls():
            file_path = url.toLocalFile()

            if file_path.lower().endswith(ROM_EXTS):
                self.view_model.load_rom(file_path)
                break
