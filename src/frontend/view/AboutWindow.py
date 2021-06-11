import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget

from frontend.controller.AboutController import AboutController
from .generated.Ui_AboutDialog import Ui_AboutDialog

from frontend.BaseWindow import BaseChildWindow

class AboutWindow(BaseChildWindow):
    """About Window - QT Window View
    """
    def __init__(self, controller: AboutController):
        """Constructor

        Args:
            controller (AboutController): A controller instance
        """
        super().__init__()
        
        self.controller = controller
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)
        