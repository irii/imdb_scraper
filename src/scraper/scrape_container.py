from data.data_container import DataContainer
from .scraper_queue import ScraperQueue

class ScrapeContainer:
    """Contains the scraping state while scraping the website.
    """
    _scraped_ids = []

    def __init__(self, dataContainer: DataContainer):
        self.dataContainer = dataContainer

    images = {}
    queue: ScraperQueue = ScraperQueue()

    def markIdAsSet(self, data_type: str, id: str):
        """Marks an url as scraped given by it's generated id from the scraper source.

        Args:
            data_type (str): Scraper Source type
            id (str): Unique id
        """
        self._scraped_ids.append(data_type + '::' + id)

    def isIdSet(self, data_type: str, id: str) -> bool:
        """[summary]

        Args:
            data_type (str): Scraper Source type
            id (str): Unique id

        Returns:
            bool: Already set true/false
        """
        return (data_type + '::' + id) in self._scraped_ids