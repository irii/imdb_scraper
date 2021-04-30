import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QDialog
from .generated.Ui_ScrapeWindow import Ui_Dialog

class ScrapeWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)


    @QtCore.pyqtSlot(str, int,int)
    def setProgress(self, url, value, max):
        self.ui.plainTextEdit.setPlainText(self.ui.plainTextEdit.toPlainText() + '\n' + url)
        self.ui.progressBar.setValue(value)
        self.ui.progressBar.setMaximum(max)
        
        