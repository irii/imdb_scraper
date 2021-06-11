from typing import Callable, List

from bs4 import BeautifulSoup
import requests
from .scraper_source import ScrapeContainer, ScraperSource
from data.data_container import DataContainer

import scraper.imdb as IMDB

# Default headers
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept-language": "en-US"
}

TYPE_PROGRESS_SCRAPING = 'SCRAPING'
TYPE_PROGRESS_DOWNLOADING_IMAGES = 'DOWNLOADING-IMAGES'

class ScraperEventListener:
    """This abstract Class synchronizies receives all scrape events. The following methods can be overwritten.
    """

    def processing(self, type: str, item: str, current: int, total: int):
        """Get's called when process changes

        Args:
            type (str): Progress type
            item (str): Url
            current (int): Scraped items count
            total (int): Total items count
        """
        pass

    def finished(self):
        """Get's called when the scraper has finished
        """
        pass

    def canceld(self):
        """Get's called when the scraper was canceld.
        """
        pass

    def error(self, type: str, item: str, message: str):
        """Get's called when an error occured.

        Args:
            type (str): Progress type
            item (str): Url
            message (str): Error message
        """
        pass

# Optional based lambda event listener, allows easier "chaining"
class LambdaScraperEventListener(ScraperEventListener):
    """This class is a proxy for the ScraperEventListener. Which accepts matching callback functions

    Args:
        ScraperEventListener ([type]): [description]
    """
    def __init__(self, processing:Callable[[str, str, int, int], None]=None, finished:Callable[[], None]=None, canceld:Callable[[], None]=None, error:Callable[[str, str], None]=None):
        """Constructor

        Args:
            processing (Callable[[str, str, int, int], None], optional): Processing event callback. Defaults to None.
            finished (Callable[[], None], optional): Finished event callback. Defaults to None.
            canceld (Callable[[], None], optional): Canceld event callback. Defaults to None.
            error (Callable[[str, str], None], optional): Error event callback. Defaults to None.
        """
        super().__init__()

        self._processing = processing
        self._finished = finished
        self._canceld = canceld
        self._error = error

    def processing(self, type: str, item: str, current: int, total: int):
        """Get's called when process changes

        Args:
            type (str): Progress type
            item (str): Url
            current (int): Scraped items count
            total (int): Total items count
        """
        if self._processing:
            self._processing(type, item, current, total)

    def finished(self):
        """Get's called when the scraper has finished
        """
        if self._finished:
            self._finished()

    def canceld(self):
        """Get's called when the scraper was canceld.
        """
        if self._canceld:
            self._canceld()

    def error(self, type: str, item: str, message: str):
        """Get's called when an error occured.

        Args:
            type (str): Progress type
            item (str): Url
            message (str): Error message
        """
        if self._error:
            self._error(type, item, message)

_PARSER_IMDB_ACTOR = IMDB.ImdbActorParser()
_PARSER_IMDB_MOVIE = IMDB.ImdbMovieParser()
_PARSER_IMDB_LIST = IMDB.ImdbListParser()
_PARSER_IMDB_FILMOSEARCH = IMDB.ImdbFilmoSearchParser()

class Scraper:
    """Scraper Class. This class is the maim class for handling scraping processes.
    This class is responsible for downloading, parsing and scraping the data.
    """

    # TODO: Remove hardcoding of imdb specific scrapers
    parsers: List[ScraperSource] = [_PARSER_IMDB_ACTOR, _PARSER_IMDB_MOVIE, _PARSER_IMDB_LIST, _PARSER_IMDB_FILMOSEARCH]

    def __init__(self, dataContainer: DataContainer):
        """Constructor

        Args:
            dataContainer (DataContainer): A data container instance
        """
        self.dataContainer = dataContainer

    def _downloadImages(self, images, listener:ScraperEventListener=None):
        """Downloads all enqueued images and reports progress.

        Args:
            images (list of tuples): List of all images
            listener (ScraperEventListener, optional): Callback handler. Defaults to None.
        """
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


    def _process_handle_link(self, container: ScrapeContainer, link: str, priority: int, parsers):
        """Searchs for a matching scraper source and begins the scraping process for the given url.

        Args:
            container (ScrapeContainer): A scraper container
            link (str): Scrape url
            priority (int): Current priority
            parsers ([list]): List of all parsers which should be used.
        """
        for x in parsers:
            id = x.isSupported(link)
            if id:
                if container.isIdSet(x.name, id):
                    return []

                container.markIdAsSet(x.name, id)

                page = requests.get(link, headers=_HEADERS)
                soup = BeautifulSoup(page.text, 'html.parser')

                return x.parse(container, link, priority, id, soup)

    def _process(self, startLinks, parsers, listener: ScraperEventListener=None, maxScrapeLevel: int = 1, canContinue=None) -> ScrapeContainer:
        """ Internal

        Args:
            startLinks ([list]): List of urls which should be scraped.
            parsers ([list]): List of all parsers which should be used.
            listener (ScraperEventListener, optional): A scraper event listener. Defaults to None.
            maxScrapeLevel (int, optional): Max allowed scrape depth. Defaults to 1.
            canContinue ([type], optional): A function which determines on each dequeue process if the scraping process can continue. Defaults to None.

        Returns:
            ScrapeContainer: [description]
        """
        container = ScrapeContainer(self.dataContainer)

        for sl in startLinks:
            container.queue.enqueue(sl, 1)

        scrapedCount = 0

        while(container.queue.getLength() > 0 and (not canContinue or canContinue())):
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
        
    def _synchronize(self, urls, parsers, listener: ScraperEventListener=None, maxScrapeLevel: int = 1, canContinue=None):
        result = self._process(urls, parsers, listener, maxScrapeLevel, canContinue)

        self._downloadImages(result.images, listener)

        if listener:
            listener.finished()

    # Used for thread interrupt request, which allows aborting the scrape process on the next url.

    def synchronize(self, urls, listener: ScraperEventListener=None, maxScrapeLevel: int = 1, canContinue=None):
        """ Scrapes all urls with the help of the currently assigned default scraper sources.

        Args:
            urls ([list]): List of urls which should be scraped.
            listener (ScraperEventListener, optional): A scraper event listener. Defaults to None.
            maxScrapeLevel (int, optional): Max allowed scrape depth. Defaults to 1.
            canContinue ([type], optional): A function which determines on each dequeue process if the scraping process can continue. Defaults to None.
        """
        return self._synchronize(urls, self.parsers, listener, maxScrapeLevel, canContinue)


    def fetchActor(self, actorId: str, listener: ScraperEventListener):
        """This method gets called, if an actor is requested. If it was not fully scraped in the previous process, then this will be also done her.
        This will start a small scrape process and merge it into the current database

        Args:
            actorId (str): The requested actor id
            listener (ScraperEventListener): [description]
        """
        df = self.dataContainer.actors
        partialActorData = df[(df["ID"] == actorId)]

        if len(partialActorData) > 0 and partialActorData.loc[partialActorData.index[0], 'Completed'] == True:
            listener.finished()
            return

        # TODO: Remove hardcoding of imdb specific scrapers
        link = _PARSER_IMDB_ACTOR.getBioLink(actorId)

        self._synchronize([link], [_PARSER_IMDB_ACTOR, _PARSER_IMDB_FILMOSEARCH], listener)

    def fetchMovie(self, movieId: str, listener: ScraperEventListener):
        """This method gets called, if an movie is requested. If it was not fully scraped in the previous process, then this will be also done her.
        This will start a small scrape process and merge it into the current database

        Args:
            movieId (str): The requested movie id
            listener (ScraperEventListener): [description]
        """
        df = self.dataContainer.movies
        partialMovieData = df[(df["ID"] == movieId)]

        if len(partialMovieData) > 0 and partialMovieData.loc[partialMovieData.index[0], 'Completed'] == True:
            listener.finished()
            return

        # TODO: Remove hardcoding of imdb specific scrapers
        link = _PARSER_IMDB_MOVIE.getLink(movieId)

        self._synchronize([link], [_PARSER_IMDB_MOVIE], listener)