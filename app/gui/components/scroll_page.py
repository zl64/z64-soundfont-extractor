from PySide6.QtGui import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import SmoothScrollArea

from app.gui.components.page_header import PageHeader


class ScrollPage(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)

        self.setObjectName('scrollPage')
        self.setStyleSheet('''
        #view {
            background: transparent;
        }

        QScrollArea {
            border: none;
            background: transparent;
        }
        ''')

        self.__init_view()
        self.__init_page_header(title)
        self.__init_scroll_area()
        self.__init_view_layout()
        self.__init_root_layout()

    def __init_view(self):
        self.view = QWidget()
        self.view.setObjectName('view')

    def __init_page_header(self, title: str):
        self.page_header = PageHeader(title)

    def __init_scroll_area(self):
        self.scroll_area = SmoothScrollArea(self)
        self.scroll_area.setWidget(self.view)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

    def __init_view_layout(self):
        self.view_layout = QVBoxLayout(self.view)
        self.view_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.view_layout.setContentsMargins(36, 0, 36, 36)
        self.view_layout.setSpacing(30)

    def __init_root_layout(self):
        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        self.root_layout.addWidget(self.page_header)
        self.root_layout.addWidget(self.scroll_area)

    def addWidget(self, widget):
        self.view_layout.addWidget(widget, 0, Qt.AlignmentFlag.AlignTop)
        return widget