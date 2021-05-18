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

    def _process_handle_link(self, container, link):
        for x in self.parsers:
            id = x.isSupported(link)
            if id:
                if container.isIdSet(x.name, id):
                    return []

                container.markIdAsSet(x.name, id)

                page = requests.get(link, headers=_HEADERS)
                soup = BeautifulSoup(page.text, 'html.parser')

                return x.parse(container, link, id, soup) or []

        return []

    def _process(self, startLinks, notify=None) -> ScrapeContainer:
        container = ScrapeContainer()

        queue = [] + startLinks
        scrapedCount = 0

        total_count = len(startLinks)

        while((len(queue) > 0) and (scrapedCount < 400)):
            work = queue.pop(0)

            if(notify):
                notify(work, scrapedCount, total_count)

            
            scrapedCount = scrapedCount + 1
            new_queue_items = self._process_handle_link(container, work)


            total_count = total_count + len(new_queue_items)

            queue = queue + new_queue_items

        return container

           
    def synchronize(self, urls, progress_callback=None, delete_orphanded_items=False):
        result = self._process(urls, progress_callback)

        self.dataContainer.migrateMovies(result.movies, delete_orphanded_items)
        self.dataContainer.migrateActors(result.actors, delete_orphanded_items)
        self.dataContainer.migrateLists(result.lists, delete_orphanded_items)
        self.dataContainer.migrateAwards(result.awards, delete_orphanded_items)

        self._downloadImages(result.images, delete_orphanded_items, progress_callback)
