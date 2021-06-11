from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

class ScrapeModel(QObject):
    """Scrape model
    """
    
    started = pyqtSignal()
    finished = pyqtSignal()
    progress_changed = pyqtSignal(str, str, int, int)