from typing import Callable, List

from bs4 import BeautifulSoup
import requests
import pandas as pd
from scraper.imdb.imdb_actor_parser import ImdbActorParser
from scraper.imdb.imdb_filmosearch_parser import ImdbFilmoSearchParser

from scraper.imdb.imdb_movie_parser import ImdbMovieParser

from .scraper_source import ScrapeContainer, ScraperParser
from data.data_container import DataContainer

import scraper.imdb as IMDB

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept-language": "en-US"
}

TYPE_PROGRESS_SCRAPING = 'SCRAPING'
TYPE_PROGRESS_DOWNLOADING_IMAGES = 'DOWNLOADING-IMAGES'

class ScraperEventListener:
    def processing(self, type: str, item: str, current: int, total: int):
        pass

    def finished(self):
        pass

    def canceld(self):
        pass

    def error(self, type: str, item: str, message: str):
        pass

# Optional based lambda event listener, allows easier "chaining"
class LambdaScraperEventListener(ScraperEventListener):
    def __init__(self, processing:Callable[[str, str, int, int], None]=None, finished:Callable[[], None]=None, canceld:Callable[[], None]=None, error:Callable[[str, str], None]=None):
        super().__init__()

        self._processing = processing
        self._finished = finished
        self._canceld = canceld
        self._error = error

    def processing(self, type: str, item: str, current: int, total: int):
        if self._processing:
            self._processing(type, item, current, total)

    def finished(self):
        if self._finished:
            self._finished()

    def canceld(self):
        if self._canceld:
            self._canceld()

    def error(self, type: str, item: str, message: str):
        if self._error:
            self._error(type, item, message)

_PARSER_IMDB_ACTOR = IMDB.ImdbActorParser()
_PARSER_IMDB_MOVIE = IMDB.ImdbMovieParser()
_PARSER_IMDB_LIST = IMDB.ImdbListParser()
_PARSER_IMDB_FILMOSEARCH = IMDB.ImdbFilmoSearchParser()

class Scraper:
    parsers: List[ScraperParser] = [_PARSER_IMDB_ACTOR, _PARSER_IMDB_MOVIE, _PARSER_IMDB_LIST, _PARSER_IMDB_FILMOSEARCH]

    def __init__(self, dataContainer: DataContainer):
        self.dataContainer = dataContainer

    def _downloadImages(self, images, listener:ScraperEventListener=None):
        counter = 0      
        for k in images.keys():
            counter = counter + 1

            if self.dataContainer.imageExists(k):
                continue

            if listener:
                listener.processing(TYPE_PROGRESS_DOWNLOADING_IMAGES, images[k], counter, len(images.keys()))

            try:
                r = requests.get(images[k])
                if r.status_code == 200:
                    self.dataContainer.saveImage(k, r.content)
            except Exception as e:
                if listener:
                    listener.error(TYPE_PROGRESS_DOWNLOADING_IMAGES, images[k], e)


    def _process_handle_link(self, container, link, priority, parsers):
        for x in parsers:
            id = x.isSupported(link)
            if id:
                if container.isIdSet(x.name, id):
                    return []

                container.markIdAsSet(x.name, id)

                page = requests.get(link, headers=_HEADERS)
                soup = BeautifulSoup(page.text, 'html.parser')

                return x.parse(container, link, priority, id, soup)

    def _process(self, startLinks, parsers, listener: ScraperEventListener=None, maxScrapeLevel: int = 1) -> ScrapeContainer:
        container = ScrapeContainer(self.dataContainer)

        for sl in startLinks:
            container.queue.enqueue(sl, 1)

        scrapedCount = 0

        while(container.queue.getLength() > 0):
            (url, level) = container.queue.dequeue()

            if level > maxScrapeLevel:
                break

            if listener:
                listener.processing(TYPE_PROGRESS_SCRAPING, url, scrapedCount, container.queue.getTotalCount(maxScrapeLevel))

            scrapedCount = scrapedCount + 1

            try:
                self._process_handle_link(container, url, level, parsers)
            except Exception as e:
                if listener:
                    listener.error(TYPE_PROGRESS_SCRAPING, url, e)

        return container
        
    def _synchronize(self, urls, parsers, listener: ScraperEventListener=None, maxScrapeLevel: int = 1):
        result = self._process(urls, parsers, listener, maxScrapeLevel)

        self._downloadImages(result.images, listener)

        if listener:
            listener.finished()

    def synchronize(self, urls, listener: ScraperEventListener=None, maxScrapeLevel: int = 1):
        return self._synchronize(urls, self.parsers, listener, maxScrapeLevel)


    # This method gets called, if an actor is requested. If it was not fully scraped in the previous process, then this will be also done her.
    # This will start a small scrape process and merge it into the current database
    def fetchActor(self, actorId, listener: ScraperEventListener):
        df = self.dataContainer.actors
        partialActorData = df[(df["ID"] == actorId)]

        if len(partialActorData) > 0 and partialActorData.loc[partialActorData.index[0], 'Completed'] == True:
            listener.finished()
            return

        link = _PARSER_IMDB_ACTOR.getBioLink(actorId)

        self._synchronize([link], [_PARSER_IMDB_ACTOR, ImdbFilmoSearchParser()], listener)


    # This method gets called, if an movie is requested. If it was not fully scraped in the previous process, then this will be also done her.
    # This will start a small scrape process and merge it into the current database
    def fetchMovie(self, movieId, listener: ScraperEventListener):
        df = self.dataContainer.movies
        partialMovieData = df[(df["ID"] == movieId)]

        if len(partialMovieData) > 0 and partialMovieData.loc[partialMovieData.index[0], 'Completed'] == True:
            listener.finished()
            return

        link = _PARSER_IMDB_MOVIE.getLink(movieId)

        self._synchronize([link], [_PARSER_IMDB_MOVIE], listener)