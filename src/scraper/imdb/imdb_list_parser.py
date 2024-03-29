from bs4 import BeautifulSoup
from scraper.scrape_container import ScrapeContainer
from scraper.scraper_source import ScraperSource

import scraper.imdb.imdb_utils as Utils

class ImdbListParser(ScraperSource):
    name = "IMDB_LIST"

    def getLink(self, id: str) -> str:
        """Returns the list link given by it's id

        Args:
            id (str): List-Item Id

        Returns:
            str: List link
        """
        return "https://www.imdb.com/list/" + id

    def isSupported(self, link) -> str:
        """Returns a id if the link is supported this scraper.

        Args:
            link (str): Requested link

        Returns:
            str: Unique id
        """

        match = Utils.LIST_ID_PARSER.match(link)
        if match:
            return match.group('Id')

        return super().isSupported(link)

    def parse(self, container: ScrapeContainer, list_link: str, priority: int, id: str, soup: BeautifulSoup):
        """Parses and extracts a list items based on the given data.

        Args:
            container (ScrapeContainer): A ScrapeContainer instance
            link (str): The scrape link
            priority (int): The scrape priority
            id (str): The generated unique id
            soup (BeautifulSoup): The content
        """

        title = soup.find("h1").text
        lister_list = soup.findAll(
            "div", attrs={'class': 'lister-item mode-detail'})

        sortId = 1

        items = []

        for entry in lister_list:
            h3 = entry.find('h3', attrs={'class': 'lister-item-header'})
            a = h3.find('a')
            link = a['href']

            match = Utils.ACTOR_ID_PARSER.match(link)
            if(match):
                # Enqueue actor
                container.queue.enqueue('https://www.imdb.com/name/' + match.group('Id') + '/bio', priority + 1) # Queue entry

                # Add scrape result
                items.append({
                    'ID': id,
                    'Title': title,
                    'SortId': sortId,
                    'Type': 'Actor',
                    'ItemId': match.group('Id'),
                    'SourceUrl': link
                })

                # Add partial actor data
                container.dataContainer.insertOrUpdateActor({
                    'ID': match.group('Id'),
                    'Name': a.text.strip(),
                    'Completed': False,
                    'SourceUrl': 'https://www.imdb.com/name/' + match.group('Id') + '/bio'
                })

            match = Utils.MOVIE_ID_PARSER.match(link)
            if(match):
                # Enqueue movie
                container.queue.enqueue('https://www.imdb.com/title/' + match.group('Id'), priority + 1) # Queue entry

                # Add scrape result
                items.append({
                    'ID': id,
                    'Title': title,
                    'SortId': sortId,
                    'Type': 'Movie',
                    'ItemId': match.group('Id'),
                    'SourceUrl': link,
                })

                # Add partial movie data
                container.dataContainer.insertOrUpdateMovie({
                    'ID': match.group('Id'),
                    'Title': a.text.strip(),
                    'Completed': False,
                    'Genres': [],
                    'SourceUrl': 'https://www.imdb.com/title/' + match.group('Id')
                })

            sortId = sortId + 1
        container.dataContainer.insertOrUpdateList(id, items)