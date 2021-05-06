from frontend.model.ScrapeModel import ScrapeModel
from PyQt5 import QtCore

from scraper.scraper import Scraper


class ScrapeBackgroundTask(QtCore.QThread):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(str, int, int)

    def __init__(self, scraper: Scraper, startUrls, delete_orphanded_items: bool):
        super().__init__()

        self.scraper = scraper
        self.startUrls = startUrls
        self.delete_orphanded_items = delete_orphanded_items

    def run(self):
        self.scraper.synchronize(self.startUrls, lambda url, current, totalCount: self.progress.emit(url, current, totalCount), self.delete_orphanded_items)
        self.finished.emit()


class ScrapeController:
    _background_task: ScrapeBackgroundTask = None

    def __init__(self, dataContainer, model: ScrapeModel, scrapeFinished):
        self.dataContainer = dataContainer
        self.model = model
        self.scrapeFinished = scrapeFinished
        

    def startScraping(self, delete_orphanded_items: bool, scrapeLinks=[]) -> bool():
        if(len(scrapeLinks) == 0):
            return False

        if self._background_task:
            return False  # Task is still runing

        scraper = Scraper(self.dataContainer)

        self._background_task = ScrapeBackgroundTask(scraper, scrapeLinks, delete_orphanded_items)
        self._background_task.finished.connect(self._finish_callback)
        self._background_task.progress.connect(lambda url, current, total: self.model.progress_changed.emit(current, total))

        self._background_task.start()

        self.model.started.emit()

        if self.scrapeFinished:
            self._background_task.finished.connect(lambda: self.scrapeFinished())

        return True

    def _finish_callback(self):
        self._background_task = None
        self.model.finished.emit()
