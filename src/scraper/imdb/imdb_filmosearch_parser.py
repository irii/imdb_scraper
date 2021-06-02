from bs4 import BeautifulSoup
from numpy import mat
from scraper.scrape_container import ScrapeContainer
from scraper.scraper_source import ScraperParser

import scraper.imdb.imdb_utils as Utils
import re

class ImdbFilmoSearchParser(ScraperParser):
    name = "IMDB_FILMOSEARCH"

    def isSupported(self, link) -> str:
        match = Utils.FILMOSEARCH_ID_PARSER_PAGE.match(link)
        if match:
            page = match.group('Page')
            return match.group('Id') + '-' + page

        match = Utils.FILMOSEARCH_ID_PARSER.match(link)
        if match:
            return match.group('Id') + '-1'

        return super().isSupported(link)

    def parse(self, container: ScrapeContainer, link: str, priority: int, id: str, soup: BeautifulSoup):
        actorMatch = Utils.FILMOSEARCH_EXTRACT_ACTORID_PARSER.match(link)
        if not actorMatch:
            return []

        actorId = actorMatch.group('Id')

        lister_list = soup.findAll(
            "div", attrs={'class': 'lister-item mode-detail'})

        sortId = 1

        for entry in lister_list:
            h3 = entry.find('h3', attrs={'class': 'lister-item-header'})
            links = h3.findAll('a', {'href': Utils.MOVIE_ID_PARSER})
            
            for link in links:
                titleId = Utils.MOVIE_ID_PARSER.match(link["href"]).group('Id')

                container.dataContainer.insertActorMovie({
                    'ActorID': actorId,
                    'MovieID': titleId
                })

                title_name_a = h3.find('a')

                genres = []
                genre = entry.find('span', {'class': 'genre'})
                if genre:
                    genres = [x.strip() for x in genre.text.split(',')]

                year = None
                year_el = entry.find('span', {'class': 'lister-item-year text-muted unbold'})
                if year_el:
                    years = re.findall(r'\d+', year_el.text)
                    if len(years) > 0:
                        year = int(years[0])

                rating = None
                rating_el = entry.find('div', {'class': 'inline-block ratings-imdb-rating'})

                if rating_el:
                    rating = float(rating_el["data-value"])

                if title_name_a:
                    container.dataContainer.insertOrUpdateMovie({
                        'ID': titleId,
                        'Title': title_name_a.text.strip(),
                        'Completed': False,
                        'Release': year,
                        'AvgRating': rating,
                        'Genres': genres,
                        'SourceUrl': 'https://www.imdb.com/title/' + titleId
                    })

                sortId = sortId + 1
                
                container.queue.enqueue('https://www.imdb.com/title/' + titleId + '/fullcredits', priority + 1)

        next_page = soup.find('a', {'class': 'lister-page-next next-page'})
        if next_page:
            container.queue.enqueue('https://www.imdb.com/filmosearch/' + next_page['href'], priority)