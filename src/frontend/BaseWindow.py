from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget, QDialog

class BaseDialog(QDialog):
    """Abstract BaseDialog which implements a closed window signal

    Args:
        QDialog ([type]): [description]
    """
    closed = pyqtSignal()

    def __init__(self):
        """Constructor
        """
        super().__init__()

    def closeEvent(self, event):
        """Triggers the close event, when the window is getting closed.
        """
        event.accept()
        self.closed.emit()

class BaseChildWindow(QWidget):
    """[summary]

    Args:
        QWidget ([type]): [description]
    """
    closed = pyqtSignal()

    def __init__(self):
        """Constructor
        """
        super().__init__()

    def closeEvent(self, event):
        """Triggers the close event, when the window is getting closed.
        """
        event.accept()
        self.closed.emit()