from bs4 import BeautifulSoup
from scraper.scrape_container import ScrapeContainer
from scraper.scraper_source import ScraperParser

import scraper.imdb.imdb_utils as Utils

class ImdbListParser(ScraperParser):
    name = "IMDB_LIST"

    def getLink(self, id) -> str:        
        return "https://www.imdb.com/list/" + id

    def isSupported(self, link) -> str:
        match = Utils.LIST_ID_PARSER.match(link)
        if match:
            return match.group('Id')

        return super().isSupported(link)

    def parse(self, container: ScrapeContainer, list_link: str, priority: int, id: str, soup: BeautifulSoup):
        title = soup.find("h1").text
        lister_list = soup.findAll(
            "div", attrs={'class': 'lister-item mode-detail'})

        sortId = 1

        for entry in lister_list:
            h3 = entry.find('h3', attrs={'class': 'lister-item-header'})
            a = h3.find('a')
            link = a['href']

            match = Utils.ACTOR_ID_PARSER.match(link)
            if(match):
                container.queue.enqueue('https://www.imdb.com/name/' + match.group('Id') + '/bio', priority + 1) # Queue entry

                # Add scrape result
                container.lists.append({
                    'ID': id,
                    'Title': title,
                    'SortId': sortId,
                    'Type': 'Actor',
                    'ItemId': match.group('Id'),
                    'SourceUrl': link
                })

                container.actors.append({
                    'ID': match.group('Id'),
                    'Name': a.text.strip(),
                    'Completed': False,
                    'SourceUrl': 'https://www.imdb.com/name/' + match.group('Id') + '/bio'
                })

            match = Utils.MOVIE_ID_PARSER.match(link)
            if(match):
                container.queue.enqueue('https://www.imdb.com/title/' + match.group('Id'), priority + 1) # Queue entry

                # Add scrape result
                container.lists.append({
                    'ID': id,
                    'Title': title,
                    'SortId': sortId,
                    'Type': 'Movie',
                    'ItemId': match.group('Id'),
                    'SourceUrl': link,
                })

                container.movies.append({
                    'ID': match.group('Id'),
                    'Title': a.text.strip(),
                    'Completed': False,
                    'Genres': [],
                    'SourceUrl': 'https://www.imdb.com/title/' + match.group('Id')
                })

            sortId = sortId + 1