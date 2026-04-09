import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.gui.views.main_window_view import MainWindowView
from app.gui.viewmodels.main_window_viewmodel import MainWindowViewModel


QApplication.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)

app = QApplication(sys.argv)

view_model = MainWindowViewModel()
view = MainWindowView(view_model)

view.show()
app.exec()