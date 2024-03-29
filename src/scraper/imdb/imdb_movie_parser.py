import re

from bs4 import BeautifulSoup
from requests.api import post
from scraper.scrape_container import ScrapeContainer
from scraper.scraper_source import ScraperSource

import scraper.imdb.imdb_utils as Utils
import re

# Classic Design Regex Patterns
_CAST_ID_IDENTIFIER = "MOVIE_CAST:"
_CAST_ID_IDENTIFIER_LEN = len(_CAST_ID_IDENTIFIER)
_CLASSIC_GENRE_HREF = re.compile(r".*\/search\/title\?genres\=.*", re.IGNORECASE)

# New Design Regex Patterns
_DESIGN_2_RATING = re.compile(r".*AggregateRatingButton\_\_RatingScore.*", re.IGNORECASE)
_DESIGN_2_YEAR_HREF = re.compile(r"^.*\/title\/.*\/releaseinfo\?.*#releases.*", re.IGNORECASE)
_DESIGN_2_IPC_POSTER_CLASS = re.compile(r".*ipc-media--poster.*", re.IGNORECASE)

class ImdbMovieParser(ScraperSource):
    """This ScraperSource handels all movie releated extraction processes.
    """
    name = "IMDB_MOVIE"

    def getLink(self, id) -> str:
        """Returns the movie link given by the requested id.

        Args:
            id (str): Generated movie id

        Returns:
            str: Actor link
        """
        if id.startswith(_CAST_ID_IDENTIFIER):
            return "https://www.imdb.com/title/" + id[_CAST_ID_IDENTIFIER_LEN:] + "/fullcredits"

        return "https://www.imdb.com/title/" + id

    def isSupported(self, link: str) -> str:
        """Returns a id if the link is supported this scraper.

        Args:
            link (str): Requested link

        Returns:
            str: Unique id
        """

        # This scraper supports different pages, so we have to identify each site with it's own prefix.

        match = Utils.MOVIE_CAST_ID_PARSER.match(link)
        if match:
            return _CAST_ID_IDENTIFIER + match.group('Id')

        match = Utils.MOVIE_ID_PARSER.match(link)
        if match:
            return match.group('Id')

        return super().isSupported(link)

    def parse(self, container: ScrapeContainer, link: str, priority: int, id: str, soup: BeautifulSoup):
        """ Extracts all data based on the given content.

        Args:
            container (ScrapeContainer): A ScrapeContainer instance
            link (str): The scrape link
            priority (int): The scrape priority
            id (str): The generated unique id
            soup (BeautifulSoup): The content
        """

        if id.startswith(_CAST_ID_IDENTIFIER):
            return self._parse_movie_credits(container, link, priority, id[_CAST_ID_IDENTIFIER_LEN:], soup)

        # Check if we got the new or classic layout
        if soup.find('body', {'id': 'styleguide-v2'}):
            # Still the classic layout
            return self._parse_movie(container, link, priority, id, soup)
        else:
            # New layout
            return self._parse_movie_2(container, link, priority, id, soup)

    def _parse_movie_2(self, container: ScrapeContainer, link: str, priority: int, id: str, soup: BeautifulSoup):
        """Extracts all movie informations by the new imdb design

        Args:
            container (ScrapeContainer): A ScrapeContainer instance
            link (str): The scrape link
            priority (int): The scrape priority
            id (str): The generated unique id
            soup (BeautifulSoup): The content
        """
        title = soup.find('h1').find(text=True, recursive=False).strip()
        rating_el = soup.find('span', {'class': _DESIGN_2_RATING})

        year = None
        year_el = soup.find('a', {'href': _DESIGN_2_YEAR_HREF})
        if(year_el):
            year = int(year_el.text.strip(), base=10)

        posterEl = soup.find('div', { 'class': _DESIGN_2_IPC_POSTER_CLASS })
        if posterEl:
            posterEl = posterEl.find('img', {'class': 'ipc-image'})
            
        if posterEl:
            link = Utils.prepareImageLink(posterEl['src'])
            if link:
                container.images['movie_' + id + "." + link[1]] = link[0]

        rating = None
        if rating_el:
            rating = float(rating_el.text.strip())


        genres = []
        genres_container = soup.find('li', {'data-testid': 'storyline-genres'})
        if genres_container:
            genres = list(dict.fromkeys([x.text.strip() for x in genres_container.find_all('li', {'role': 'presentation'})]))

        container.dataContainer.insertOrUpdateMovie({
            'ID': id,
            'Title': title,
            'AvgRating': rating,
            'Release': year,
            'Genres': genres,
            'SourceUrl': link,
            'Completed': True
        })

        container.queue.enqueue('https://www.imdb.com/title/' + id + '/fullcredits', priority)

    def _parse_movie(self, container: ScrapeContainer, link: str, priority: int, id: str, soup: BeautifulSoup):
        """Extracts all movie informations by the classic imdb design

        Args:
            container (ScrapeContainer): A ScrapeContainer instance
            link (str): The scrape link
            priority (int): The scrape priority
            id (str): The generated unique id
            soup (BeautifulSoup): The content
        """
        title = soup.find('h1').find(text=True, recursive=False).strip()
        rating_el = soup.find('span', attrs={'itemprop': 'ratingValue'})

        year = None
        year_el = soup.find('span', attrs={'id': 'titleYear'})
        if(year_el):
            year = int(year_el.find('a').text.strip(), base=10)

        posterEl = soup.find('div', {'class': 'poster'})
        if posterEl:
            posterEl = posterEl.find('img')
            

        if posterEl:
            link = Utils.prepareImageLink(posterEl['src'])
            if link:
                container.images['movie_' + id + "." + link[1]] = link[0]

        rating = None
        if rating_el:
            rating = float(rating_el.text.strip())


        genres_els = soup.find_all('a', {'href': _CLASSIC_GENRE_HREF})
        genres = list(dict.fromkeys([x.text.strip() for x in genres_els]))

        container.dataContainer.insertOrUpdateMovie({
            'ID': id,
            'Title': title,
            'AvgRating': rating,
            'Release': year,
            'Genres': genres,
            'SourceUrl': link,
            'Completed': True
        })

        container.queue.enqueue('https://www.imdb.com/title/' + id + '/fullcredits', priority)


    def _parse_movie_credits(self, container: ScrapeContainer, link: str, priority: int, id: str, soup: BeautifulSoup):
        """Extracts all actors which where in this movie and enqueues them to the database

        Args:
            container (ScrapeContainer): A ScrapeContainer instance
            link (str): The scrape link
            priority (int): The scrape priority
            id (str): The generated unique id
            soup (BeautifulSoup): The content
        """

        actor_urls = soup.find_all('a', {'href': Utils.ACTOR_ID_PARSER})
        for x in actor_urls:
            actorId = Utils.ACTOR_ID_PARSER.match(x['href']).group('Id')

            container.dataContainer.insertActorMovie({
                'ActorID': actorId,
                'MovieID': id,
                'SourceUrl': link
            })

            container.dataContainer.insertOrUpdateActor({
                'ID': actorId,
                'Name': x.text.strip(),
                'Completed': False,
                'SourceUrl': 'https://www.imdb.com/' + x['href']
            })

            container.queue.enqueue('https://www.imdb.com/' + x['href'], priority + 1)