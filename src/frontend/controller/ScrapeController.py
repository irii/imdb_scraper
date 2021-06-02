from frontend.model.ScrapeModel import ScrapeModel
from PyQt5 import QtCore

from scraper.scraper import Scraper, LambdaScraperEventListener


class ScrapeBackgroundTask(QtCore.QThread):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(str, str, int, int)

    def __init__(self, scraper: Scraper, startUrls, depth):
        super().__init__()

        self.scraper = scraper
        self.startUrls = startUrls
        self.depth = depth

    def run(self):
        self.scraper.synchronize(self.startUrls, maxScrapeLevel=self.depth, listener=LambdaScraperEventListener(processing=lambda type, url, count, totalCount: self.progress.emit(type, url, count, totalCount)))
        self.finished.emit()


class ScrapeController:
    _background_task: ScrapeBackgroundTask = None

    def __init__(self, dataContainer, model: ScrapeModel, scrapeFinished):
        self.dataContainer = dataContainer
        self.model = model
        self.scrapeFinished = scrapeFinished
        

    def startScraping(self, depth, scrapeLinks=[]) -> bool():
        if(len(scrapeLinks) == 0):
            return False

        if self._background_task:
            return False  # Task is still runing

        scraper = Scraper(self.dataContainer)

        self._background_task = ScrapeBackgroundTask(scraper, scrapeLinks, depth)
        self._background_task.finished.connect(self._finish_callback)
        self._background_task.progress.connect(lambda type, url, current, total: self.model.progress_changed.emit(type, url, current, total))

        self._background_task.start()

        self.model.started.emit()

        return True

    def _finish_callback(self):
        self._background_task = None
        self.model.finished.emit()
        if self.scrapeFinished:
            self.scrapeFinished()
