from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

class ScrapeModel(QObject):
    started = pyqtSignal()
    finished = pyqtSignal()
    progress_changed = pyqtSignal(str, str, int, int)