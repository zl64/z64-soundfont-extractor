from PySide6.QtGui import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import TitleLabel


class PageHeader(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)

        self.setObjectName('pageHeader')

        self.__init_title_label(title)
        self.__init_layout()

    def __init_title_label(self, title: str):
        self.title_label = TitleLabel(title, self)

    def __init_layout(self):
        self.vbox_layout = QVBoxLayout(self)
        self.vbox_layout.addWidget(self.title_label)
        self.vbox_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vbox_layout.setContentsMargins(36, 24, 36, 12)
        self.vbox_layout.setSpacing(0)
