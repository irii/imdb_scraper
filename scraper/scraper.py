import requests
import pandas as pd
from .scraper_source import ScraperSource, ScrapeResult
from data.data_container import DataContainer

from .sources.imdb import ImdbSource

TYPE_PROGRESS_SCRAPING = 'SCRAPING'
TYPE_PROGRESS_DOWNLOADING_IMAGES = 'DOWNLOADING-IMAGES'


class Scraper:
    sources: list[ScraperSource] = [ImdbSource()]

    def __init__(self, dataContainer: DataContainer):
        self.dataContainer = dataContainer

    def _downloadImages(self, images, delete_orphanded_items, progress_callback=None):
        for k in images.keys():
            r = requests.get(images[k])
            if r.status_code == 200:
                self.dataContainer.saveImage(k, r.content)
           
    def synchronize(self, urls, progress_callback=None, delete_orphanded_items=False):
        result = ScrapeResult()

        for scraper in self.sources:
            scraper.scrape(urls, result, progress_callback)

        self.dataContainer.migrateMovies(result.movies, delete_orphanded_items)
        self.dataContainer.migrateActors(result.actors, delete_orphanded_items)
        self.dataContainer.migrateLists(result.lists, delete_orphanded_items)
        self.dataContainer.migrateAwards(result.awards, delete_orphanded_items)

        self._downloadImages(result.images, delete_orphanded_items, progress_callback)
