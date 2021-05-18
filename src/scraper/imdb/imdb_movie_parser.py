import re

from bs4 import BeautifulSoup
from scraper.scrape_container import ScrapeContainer
from scraper.scraper_source import ScraperParser

import scraper.imdb.imdb_utils as Utils

_CAST_ID_IDENTIFIER = "MOVIE_CAST:"
_CAST_ID_IDENTIFIER_LEN = len(_CAST_ID_IDENTIFIER)

class ImdbMovieParser(ScraperParser):
    name = "IMDB_MOVIE"

    def isSupported(self, link) -> str:
        match = Utils.MOVIE_CAST_ID_PARSER.match(link)
        if match:
            return _CAST_ID_IDENTIFIER + match.group('Id')

        match = Utils.MOVIE_ID_PARSER.match(link)
        if match:
            return match.group('Id')

        return super().isSupported(link)

    def parse(self, container: ScrapeContainer, link: str, id: str, soup: BeautifulSoup):
        if id.startswith(_CAST_ID_IDENTIFIER):
            return self._parse_movie_credits(container, link, id[_CAST_ID_IDENTIFIER_LEN:], soup)

        return self._parse_movie(container, link, id, soup)

    def _parse_movie(self, container: ScrapeContainer, link: str, id: str, soup: BeautifulSoup):
        title = soup.find('h1').find(text=True, recursive=False).strip()
        rating_el = soup.find('span', attrs={'itemprop': 'ratingValue'})

        year = None
        year_el = soup.find('span', attrs={'id': 'titleYear'})
        if(year_el):
            year = int(year_el.find('a').text.strip(), base=10)

        posterEl = soup.find('div', {'class': 'poster'})
        if(posterEl):
            link = Utils.prepareImageLink(posterEl.find('img')['src'])
            if link:
                container.images['movie_' + id + "." + link[1]] = link[0]

        container.movies.append({
            'ID': id,
            'Title': title,
            'AvgRating': float(rating_el.text.strip()),
            'Release': year
        })

        return ['https://www.imdb.com/title/' + id + '/fullcredits']


    def _parse_movie_credits(self, container: ScrapeContainer, link: str, id: str, soup: BeautifulSoup):
        actorIds = []

        actor_urls = soup.find_all('a', {'href': Utils.ACTOR_ID_PARSER})
        for x in actor_urls:
            actorIds.append(Utils.ACTOR_ID_PARSER.match(x).group('id'))

        return actorIds