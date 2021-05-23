from bs4 import BeautifulSoup
from scraper.scrape_container import ScrapeContainer
from scraper.scraper_source import ScraperParser

import scraper.imdb.imdb_utils as Utils

class ImdbFilmoSearchParser(ScraperParser):
    name = "IMDB_FILMOSEARCH"

    def isSupported(self, link) -> str:
        match = Utils.FILMOSEARCH_ID_PARSER.match(link)
        if match:
            return match.group('Id')

        return super().isSupported(link)


    def parse(self, container: ScrapeContainer, link: str, priority: int, id: str, soup: BeautifulSoup):
        actorMatch = Utils.FILMOSEARCH_EXTRACT_ACTORID_PARSER.match(link)
        if not actorMatch:
            return []

        actorId = actorMatch.group('Id')

        lister_list = soup.findAll(
            "div", attrs={'class': 'lister-item mode-detail'})

        sort_type = soup.find('select', {'class' : 'lister-sort-by'}).find('option', {'selected': 'selected'}).text

        sortId = 1

        for entry in lister_list:
            h3 = entry.find('h3', attrs={'class': 'lister-item-header'})
            links = h3.findAll('a', {'href': Utils.MOVIE_ID_PARSER})
            
            for link in links:
                titleId = Utils.MOVIE_ID_PARSER.match(link["href"]).group('Id')

                container.actorsMovies.append({
                    'ActorID': actorId,
                    'MovieID': titleId,
                    'SortId': sortId,
                    'Type': sort_type,
                    'Value': 0
                })

                sortId = sortId + 1
                
                container.queue.enqueue('https://www.imdb.com/title/' + titleId, priority + 1)

        next_page = soup.find('a', {'class': 'lister-page-next next-page'})
        if next_page:
            container.queue.enqueue('https://www.imdb.com/filmosearch/' + next_page['href'], priority)