from typing import List

from bs4 import BeautifulSoup
import requests
import pandas as pd

from .scraper_source import ScrapeContainer, ScraperParser
from data.data_container import DataContainer

import scraper.imdb as IMDB

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept-language": "en-US"
}

TYPE_PROGRESS_SCRAPING = 'SCRAPING'
TYPE_PROGRESS_DOWNLOADING_IMAGES = 'DOWNLOADING-IMAGES'


class Scraper:
    parsers: List[ScraperParser] = [IMDB.ImdbActorParser(), IMDB.ImdbMovieParser(), IMDB.ImdbListParser(), IMDB.ImdbFilmoSearchParser()]

    def __init__(self, dataContainer: DataContainer):
        self.dataContainer = dataContainer

    def _downloadImages(self, images, delete_orphanded_items, progress_callback=None):
        for k in images.keys():
            r = requests.get(images[k])
            if r.status_code == 200:
                self.dataContainer.saveImage(k, r.content)

    def _process_handle_link(self, container, link, priority):
        for x in self.parsers:
            id = x.isSupported(link)
            if id:
                if container.isIdSet(x.name, id):
                    return []

                container.markIdAsSet(x.name, id)

                page = requests.get(link, headers=_HEADERS)
                soup = BeautifulSoup(page.text, 'html.parser')

                return x.parse(container, link, priority, id, soup) or []

        return []

    def _process(self, startLinks, notify=None, maxScrapeCount: int = None) -> ScrapeContainer:
        container = ScrapeContainer()
        for sl in startLinks:
            container.queue.enqueue(sl, 1)

        scrapedCount = 0

        while(container.queue.getLength() > 0 and (maxScrapeCount is None or scrapedCount < maxScrapeCount)):
            work = container.queue.dequeue()

            if work is None:
                break

            if(notify):
                notify(work[0], scrapedCount, container.queue.getTotalCount())

            scrapedCount = scrapedCount + 1
            self._process_handle_link(container, work[0], work[1])

        return container

           
    def synchronize(self, urls, progress_callback=None, delete_orphanded_items=False, maxScrapeCount: int = None):
        result = self._process(urls, progress_callback)

        self.dataContainer.migrateMovies(result.movies, delete_orphanded_items)
        self.dataContainer.migrateActors(result.actors, delete_orphanded_items)
        self.dataContainer.migrateLists(result.lists, delete_orphanded_items)
        self.dataContainer.migrateAwards(result.awards, delete_orphanded_items)
        self.dataContainer.migrateActorsMovies(result.actorsMovies, delete_orphanded_items)

        self._downloadImages(result.images, delete_orphanded_items, progress_callback)
