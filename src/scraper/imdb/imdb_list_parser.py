from bs4 import BeautifulSoup
from scraper.scrape_container import ScrapeContainer
from scraper.scraper_source import ScraperParser

import scraper.imdb.imdb_utils as Utils

class ImdbListParser(ScraperParser):
    name = "IMDB_LIST"

    def isSupported(self, link) -> str:
        match = Utils.LIST_ID_PARSER.match(link)
        if match:
            return match.group('Id')

        return super().isSupported(link)

    def parse(self, container: ScrapeContainer, link: str, priority: int, id: str, soup: BeautifulSoup):
        title = soup.find("h1").text
        lister_list = soup.findAll(
            "div", attrs={'class': 'lister-item mode-detail'})

        sortId = 1

        for entry in lister_list:
            h3 = entry.find('h3', attrs={'class': 'lister-item-header'})
            link = h3.find('a')['href']

            match = Utils.ACTOR_ID_PARSER.match(link)
            if(match):
                container.queue.enqueue('https://www.imdb.com/name/' + match.group('Id') + '/bio', priority) # Queue entry

                # Add scrape result
                container.lists.append({
                    'ID': id,
                    'Title': title,
                    'SortId': sortId,
                    'Type': 'Actor',
                    'ItemId': match.group('Id')
                })

            match = Utils.MOVIE_ID_PARSER.match(link)
            if(match):
                container.queue.enqueue('https://www.imdb.com/title/' + match.group('Id') + '', priority) # Queue entry

                # Add scrape result
                container.lists.append({
                    'ID': id,
                    'Title': title,
                    'SortId': sortId,
                    'Type': 'Movie',
                    'ItemId': match.group('Id')
                })

            sortId = sortId + 1