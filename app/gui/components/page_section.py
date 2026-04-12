from PySide6.QtGui import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import StrongBodyLabel


class PageSection(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)

        self.setObjectName('pageSection')

        self.__init_title_label(title)
        self.__init_widget_layout()
        self.__init_root_layout()

    def __init_title_label(self, title: str):
        self.title_label = StrongBodyLabel(title)
        self.title_label.setContentsMargins(0, 0, 0, 8)

    def __init_widget_layout(self):
        self.widget_layout = QVBoxLayout()
        self.widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)
        self.widget_layout.setSpacing(4)

    def __init_root_layout(self):
        self.root_layout = QVBoxLayout(self)
        self.root_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        self.root_layout.addWidget(self.title_label)
        self.root_layout.addLayout(self.widget_layout)

    def addWidget(self, widget):
        self.widget_layout.addWidget(widget, 0, Qt.AlignmentFlag.AlignTop)
        return widget