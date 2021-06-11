from frontend.model.ScrapeModel import ScrapeModel
from PyQt5 import QtCore

from scraper.scraper import Scraper, LambdaScraperEventListener
from data.data_container import DataContainer

class ScrapeBackgroundTask(QtCore.QThread):
    """Scraper background task
    """
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(str, str, int, int)

    def __init__(self, scraper: Scraper, startUrls, depth):
        """Constructor

        Args:
            scraper (Scraper): A scraper instance
            startUrls ([type]): Start urls (at least one has to be passed)
            depth ([type]): Max allowed level of nested links
        """
        super().__init__()

        self.scraper = scraper
        self.startUrls = startUrls
        self.depth = depth

    def run(self):
        """Async process
        """        
        self.scraper.synchronize(
            urls=self.startUrls,
            maxScrapeLevel=self.depth,
            listener=LambdaScraperEventListener(processing=lambda type, url, count, totalCount: self.progress.emit(type, url, count, totalCount)),
            canContinue=lambda: not self.isInterruptionRequested()
        )
        self.finished.emit()


class ScrapeController:
    """ Scrape controller for handling the scrape process dialog
    """

    _background_task: ScrapeBackgroundTask = None

    def __init__(self, dataContainer: DataContainer, model: ScrapeModel, scrapeFinished):
        """Constructor

        Args:
            dataContainer (DataContainer): A data container instance
            model (ScrapeModel): A scrape model instance
            scrapeFinished ([type]): A callback method when the scrape processed has finished or aborted or an error happend
        """
        self.dataContainer = dataContainer
        self.model = model
        self.scrapeFinished = scrapeFinished
        

    def startOrAbortScraping(self, depth: int, scrapeLinks=[]) -> bool():
        """Handles start and cancellation of the scrape process
        Returns:
            depth (int): Max allowed scrape depth
            scrapeLinks (str[]): A list of links which have to be scraped
        """

        if(len(scrapeLinks) == 0):
            return False

        if self._background_task:
            self._background_task.requestInterruption()
            return False  # Task is still runing

        scraper = Scraper(self.dataContainer)

        self._background_task = ScrapeBackgroundTask(scraper, scrapeLinks, depth)
        self._background_task.finished.connect(self._finish_callback)
        self._background_task.progress.connect(lambda type, url, current, total: self.model.progress_changed.emit(type, url, current, total))

        self._background_task.start()

        self.model.started.emit()

        return True

    def _finish_callback(self):
        """Finish callback - Clears all internal variable and notifies all listeners        
        """
        self._background_task = None
        self.model.finished.emit()
        if self.scrapeFinished:
            self.scrapeFinished()
