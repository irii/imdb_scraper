from scraper.scraper import ScraperEventListener
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

# QT UI Adapter
class QtScraperEventListener(QObject, ScraperEventListener):
    onFinished = pyqtSignal()
    onProccessing = pyqtSignal(str, str, int, int)
    onCanceld = pyqtSignal()
    onError = pyqtSignal(str, str, str)

    def processing(self, type: str, item: str, current: int, total: int):
        self.onProccessing.emit(type, item, current, total)
        
    def finished(self):
        self.onFinished.emit()
        
    def canceld(self):
        self.onCanceld.emit()
        
    def error(self, type: str, item: str):
        self.onError.emit(type, item)
