from pathlib import Path
from PySide6.QtWidgets import QFileDialog
from qfluentwidgets import (
    FluentIcon,
    InfoBar,
    MessageBox,
    PushSettingCard,
)

from app.gui.components import PageSection, ScrollPage
from app.gui.components import ExtractSoundfontExpandCard
from app.gui.viewmodels import SoundfontExtractorViewmodel


class SoundfontExtractorView(ScrollPage):
    def __init__(self, parent=None):
        super().__init__('Soundfont Extractor', parent=parent)

        self.setObjectName('soundfontExtractorView')

        self._setup_ui()
        self._setup_viewmodel()

        self._on_state_changed(False)

    def _setup_ui(self):
        self._init_rom_section()
        self._init_soundfont_section()

        self.addWidget(self.rom_section)
        self.addWidget(self.soundfont_section)

    def _setup_viewmodel(self):
        self.view_model = SoundfontExtractorViewmodel(self)
        self._bind_viewmodel()

    def _init_rom_section(self):
        self.rom_section = PageSection('ROM')

        self.load_rom_card = PushSettingCard(
            text='Load ROM',
            icon=FluentIcon.FOLDER,
            title='ROM file',
            content=''
        )
        self.load_rom_card.setMinimumHeight(64)

        self.load_rom_card.button.clicked.connect(self._select_file_dialog)

        self.rom_section.addWidget(self.load_rom_card)

    def _init_soundfont_section(self):
        self.soundfont_section = PageSection('Soundfont')

        self.output_dir_card = PushSettingCard(
            text='Choose folder',
            icon=FluentIcon.FOLDER,
            title='Output directory',
            content='',
        )
        self.output_dir_card.setMinimumHeight(64)

        self.output_dir_card.button.clicked.connect(self._select_folder_dialog)

        self.extract_card = ExtractSoundfontExpandCard(
            icon=FluentIcon.SAVE,
            title='Extract soundfont',
            content='Extract the selected soundfont to the specified folder',
        )

        self.extract_card.filter_switch.checkedChanged.connect(self._on_filter_changed)
        self.extract_card.soundfont_list.currentIndexChanged.connect(self._on_soundfont_selected)
        self.extract_card.extract_button.clicked.connect(self._on_extract_clicked)

        self.soundfont_section.addWidget(self.output_dir_card)
        self.soundfont_section.addWidget(self.extract_card)

    def _bind_viewmodel(self):
        self.view_model.rom_loaded.connect(self._on_rom_loaded)
        self.view_model.output_dir_changed.connect(self._on_output_dir_changed)
        self.view_model.operation_succeeded.connect(self._on_operation_succeeded)
        self.view_model.operation_failed.connect(self._on_operation_failed)
        self.view_model.soundfonts_reset.connect(self._on_soundfonts_reset)
        self.view_model.state_changed.connect(self._on_state_changed)
        self.view_model.soundfonts_reset.connect(self._on_soundfonts_reset)
        self.view_model.overwrite_requested.connect(self._on_overwrite_requested)

    def _on_state_changed(self, enabled: bool):
        card = self.extract_card
        card.setEnabled(enabled)
        card.setExpand(enabled)

        card.soundfont_list.setEnabled(enabled)
        card.filter_switch.setEnabled(enabled)
        card.extract_button.setEnabled(enabled)

        if not enabled:
            card.soundfont_list_combobox.clear()
            self.load_rom_card.setContent(None)

    def _on_rom_loaded(self, path: str):
        self.load_rom_card.setContent(path)

    def _on_output_dir_changed(self, path: str):
        self.output_dir_card.setContent(path)

    def _on_soundfont_selected(self, index: int):
        combo = self.extract_card.soundfont_list_combobox
        soundfont = combo.itemData(index)

        self.view_model.set_selected_soundfont(soundfont)

    def _on_filter_changed(self, checked: bool):
        self.view_model.set_filter_modified(checked)

    def _on_soundfonts_reset(self, soundfonts: list):
        combo = self.extract_card.soundfont_list
        combo.clear()

        for sf in soundfonts:
            combo.addItem(
                f'0x{sf.index:02X}',
                userData=sf
            )

        if combo.count() > 0:
            combo.setCurrentIndex(0)

        # self.soundfont_model.set_items(soundfonts)

    def _on_extract_clicked(self):
        self.view_model.extract_selected_soundfont()

    def _on_overwrite_requested(self, path: Path, callback):
        dialog = MessageBox(
            title='Replace or skip files',
            content=f'The destination already has a file named\n"{path.name}"',
            parent=self,
        )
        dialog.yesButton.setText('Replace')
        dialog.cancelButton.setText('Skip')

        result = dialog.exec()

        callback(result)

    def _select_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Load ROM',
            '',
            'ROM Files (*.z64 *.n64 *.v64);;All Files (*.*)'
        )

        if file_path:
            self.view_model.load_rom(file_path)

    def _select_folder_dialog(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            'Select Folder',
            '',
        )

        if dir_path:
            self.view_model.set_output_dir(dir_path)

    def _on_operation_succeeded(self, content: str):
        InfoBar.success(
            title='Success',
            content=content,
            duration=10000, # ms
            parent=self,
        )

    def _on_operation_failed(self, content: str):
        InfoBar.error(
            title='Error',
            content=content,
            duration=10000, # ms
            parent=self,
        )
