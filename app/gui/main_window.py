import sys
from PySide6.QtCore import QPoint
from qfluentwidgets import (
    FluentIcon,
    FluentWindow,
    InfoBarManager,
    InfoBar,
)

from app.gui.views import SoundfontExtractorView


def is_win11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


@InfoBarManager.register('Custom')
class CustomInfoBarManager(InfoBarManager):
    def _pos(self, infoBar: InfoBar, parentSize=None) -> QPoint:
        p = infoBar.parent()
        parentSize = parentSize or p.size()

        x = (parentSize.width() - infoBar.width()) - 20
        y = 73

        index = self.infoBars[p].index(infoBar)
        for bar in self.infoBars[p][0:index]:
            y += (bar.height() + self.spacing)

        return QPoint(x, y)

    def _slideStartPos(self, infoBar: InfoBar) -> QPoint:
        pos = self._pos(infoBar)
        return QPoint(pos.x() + infoBar.width() + 16, pos.y())


class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Zelda64 Soundfont Extractor')
        self.navigationInterface.setDisabled(True)
        # self.navigationInterface.setVisible(False)

        self.setObjectName('mainWindow')
        self._init_window()
        self.show()

        self._init_views()
        self._init_navigation()

    def _init_window(self):
        self.setMinimumSize(720, 500)

        if is_win11():
            self.setMicaEffectEnabled(True)
        else:
            self.setMicaEffectEnabled(False)

    def _init_views(self):
        self.soundfont_extractor_view = SoundfontExtractorView(self)

    def _init_navigation(self):
        self.addSubInterface(
            self.soundfont_extractor_view,
            FluentIcon.FOLDER,
            'Soundfont Extractor'
        )