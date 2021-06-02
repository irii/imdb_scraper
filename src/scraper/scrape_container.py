from data.data_container import DataContainer
from .scraper_queue import ScraperQueue

class ScrapeContainer:
    _scraped_ids = []

    def __init__(self, dataContainer: DataContainer):
        self.dataContainer = dataContainer

    images = {}
    queue: ScraperQueue = ScraperQueue()

    def markIdAsSet(self, data_type, id):
        self._scraped_ids.append(data_type + '::' + id)

    def isIdSet(self, data_type, id):
        return (data_type + '::' + id) in self._scraped_ids