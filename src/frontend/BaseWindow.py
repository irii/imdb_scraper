from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget, QDialog

class BaseDialog(QDialog):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()

    def closeEvent(self, event):
        event.accept()
        self.closed.emit()

class BaseChildWindow(QWidget):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()

    def closeEvent(self, event):
        event.accept()
        self.closed.emit()