import os
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from qfluentwidgets import Theme, setTheme, setThemeColor
from qframelesswindow.utils import getSystemAccentColor

from app.gui.main_window import MainWindow


QApplication.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)

if sys.platform in {'win32', 'darwin'}:
    setThemeColor(getSystemAccentColor(), save=True)

setTheme(Theme.AUTO)

os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'
os.environ['QT_SCALE_FACTOR'] = '1.0'

app = QApplication(sys.argv)
win = MainWindow()

app.exec()