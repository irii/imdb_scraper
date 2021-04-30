import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget
from .generated.Ui_AboutDialog import Ui_AboutDialog

class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)
        