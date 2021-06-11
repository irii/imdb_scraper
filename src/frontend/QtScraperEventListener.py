from scraper.scraper import ScraperEventListener
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

class QtScraperEventListener(QObject, ScraperEventListener):
    """This Class synchronizies scrape events to the UI layer. This class is primary used for async scrape processes.
    
    Attributes:
        onFinished (pyqtSignal):  get's emitted after the scraper has finished
        onProcessing (pyqtSignal):    get's emitted after the scraper begins with a new url
        onCanceld (pyqtSignal):   get's called if the user has aborted the scraping process
        onError (pyqtSignal): get's called when an error occured, the scrape process will continue
    """

    onFinished = pyqtSignal()
    onProccessing = pyqtSignal(str, str, int, int)
    onCanceld = pyqtSignal()
    onError = pyqtSignal(str, str, str)

    def processing(self, type: str, item: str, current: int, total: int):
        """Processing event
        """
        self.onProccessing.emit(type, item, current, total)
        
    def finished(self):
        """Finish event
        """
        self.onFinished.emit()
        
    def canceld(self):
        """Cancel event
        """
        self.onCanceld.emit()
        
    def error(self, type: str, item: str):
        """Error event
        """
        self.onError.emit(type, item)
