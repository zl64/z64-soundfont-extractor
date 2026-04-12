from PySide6.QtGui import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLayout, QWidget
from qfluentwidgets import ComboBox, ExpandGroupSettingCard, PushButton, SwitchButton


class ExtractSoundfontExpandCard(ExpandGroupSettingCard):
    def __init__(self, icon, title: str, content=None, parent=None):
        super().__init__(icon, title, content, parent=parent)

        self.__init_soundfont_list_group()
        self.__init_soundfont_list_filter_group()
        self.__init_soundfont_extraction_group()
        self.__init_group()

        self.soundfont_list = self.soundfont_list_combobox
        self.filter_switch = self.soundfont_list_filter_switch_button
        self.extract_button = self.soundfont_extraction_button

    def __init_soundfont_list_group(self):
        self.soundfont_list_widget = QWidget(self.view)
        self.soundfont_list_label = QLabel('Selected soundfont', self.soundfont_list_widget)
        self.soundfont_list_combobox = ComboBox(self.soundfont_list_widget)
        self.soundfont_list_combobox.setMinimumWidth(120)
        self.soundfont_list_combobox.setMaxVisibleItems(8)

        self.soundfont_list_layout = QHBoxLayout(self.soundfont_list_widget)
        self.soundfont_list_layout.setContentsMargins(48, 16, 44, 16)
        self.soundfont_list_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.soundfont_list_layout.addWidget(self.soundfont_list_label, 0, Qt.AlignmentFlag.AlignLeft)
        self.soundfont_list_layout.addWidget(self.soundfont_list_combobox, 0, Qt.AlignmentFlag.AlignRight)

    def __init_soundfont_list_filter_group(self):
        self.soundfont_list_filter_widget = QWidget(self.view)
        self.soundfont_list_filter_label = QLabel('Show modified soundfonts only', self.soundfont_list_filter_widget)
        self.soundfont_list_filter_switch_button = SwitchButton('Off', self.soundfont_list_filter_widget)

        self.soundfont_list_filter_layout = QHBoxLayout(self.soundfont_list_filter_widget)
        self.soundfont_list_filter_layout.setContentsMargins(48, 16, 44, 16)
        self.soundfont_list_filter_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.soundfont_list_filter_layout.addWidget(self.soundfont_list_filter_label, 0, Qt.AlignmentFlag.AlignLeft)
        self.soundfont_list_filter_layout.addWidget(self.soundfont_list_filter_switch_button, 0, Qt.AlignmentFlag.AlignRight)

    def __init_soundfont_extraction_group(self):
        self.soundfont_extraction_widget = QWidget(self.view)
        self.soundfont_extraction_label = QLabel('Extract selected soundfont', self.soundfont_extraction_widget)
        self.soundfont_extraction_button = PushButton('Extract')
        self.soundfont_extraction_button.setMinimumWidth(120)

        self.soundfont_extraction_layout = QHBoxLayout(self.soundfont_extraction_widget)
        self.soundfont_extraction_layout.setContentsMargins(48, 16, 44, 16)
        self.soundfont_extraction_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.soundfont_extraction_layout.addWidget(self.soundfont_extraction_label, 0, Qt.AlignmentFlag.AlignLeft)
        self.soundfont_extraction_layout.addWidget(self.soundfont_extraction_button, 0, Qt.AlignmentFlag.AlignRight)

    def __init_group(self):
        self.viewLayout.setSpacing(0)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)

        self.addGroupWidget(self.soundfont_list_widget)
        self.addGroupWidget(self.soundfont_list_filter_widget)
        self.addGroupWidget(self.soundfont_extraction_widget)