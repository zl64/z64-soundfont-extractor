import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.gui.main_window import MainWindow


QApplication.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)

app = QApplication(sys.argv)
win = MainWindow()

win.show()
app.exec()