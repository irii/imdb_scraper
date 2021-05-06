import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget
from .generated.Ui_AboutDialog import Ui_AboutDialog

from frontend.BaseWindow import BaseChildWindow

class AboutWindow(BaseChildWindow):
    def __init__(self, controller):
        super().__init__()
        
        self.controller = controller
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)
        