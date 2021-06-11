import re

from bs4 import BeautifulSoup
from scraper.scrape_container import ScrapeContainer
from scraper.scraper_source import ScraperSource

import scraper.imdb.imdb_utils as Utils

_AWARD_ID_IDENTIFIER = "ACTOR_AWARD:"
_AWARD_ID_IDENTIFIER_LEN = len(_AWARD_ID_IDENTIFIER)

_BIO_ID_IDENTIFIER = "ACTOR_BIO:"
_BIO_ID_IDENTIFIER_LEN = len(_BIO_ID_IDENTIFIER)

_HEIGHT_PARSER = re.compile(r".*\((?P<Height>[0-9|,|\.]*).*m\).*", re.IGNORECASE)

class ImdbActorParser(ScraperSource):
    """This ScraperSource handels all actor releated extraction processes.
    """
    name = "IMDB_ACTOR"

    def getBioLink(self, id: str) -> str:
        """Returns the biography link based on the given actor id.

        Args:
            id (str): ActorId

        Returns:
            str: Actor biography link
        """
        return self.getLink(_BIO_ID_IDENTIFIER + id)

    def getLink(self, id: str) -> str:
        """Returns the actor link given by the requested id.

        Args:
            id (str): Generated actor id

        Returns:
            str: Actor link
        """
        if id.startswith(_AWARD_ID_IDENTIFIER):
            return "https://www.imdb.com/name/" + id[_AWARD_ID_IDENTIFIER_LEN:] + "/awards"

        if id.startswith(_BIO_ID_IDENTIFIER):
            return "https://www.imdb.com/name/" + id[_BIO_ID_IDENTIFIER_LEN:] + "/bio"

        return "https://www.imdb.com/name/" + id

    def isSupported(self, link: str) -> str:
        """Returns a id if the link is supported this scraper.

        Args:
            link (str): Requested link

        Returns:
            str: Unique id
        """

        # This scraper supports multiple sites, so we have to identify each site with it's own prefix.

        match = Utils.ACTOR_AWARD_ID_PARSER.match(link)
        if match:
            return _AWARD_ID_IDENTIFIER + match.group('Id') 

        match = Utils.ACTOR_BIO_ID_PARSER.match(link)
        if match:
            return _BIO_ID_IDENTIFIER + match.group('Id') 

        match = Utils.ACTOR_ID_PARSER.match(link)
        if match:
            return match.group('Id')

        return super().isSupported(link)


    def parse(self, container: ScrapeContainer, link: str, priority: int, id: str, soup: BeautifulSoup):
        """Parses all informations based on the given data.

        Args:
            container (ScrapeContainer): A ScrapeContainer instance
            link (str): The scrape link
            priority (int): The scrape priority
            id (str): The generated unique id
            soup (BeautifulSoup): The content
        """
        
        # This scraper supports multiple sites, so we have to check which prefix was added and call the correct parser.

        if id.startswith(_AWARD_ID_IDENTIFIER):
            return self._parse_actor_awards(container, link, priority, id[_AWARD_ID_IDENTIFIER_LEN:], soup)

        if id.startswith(_BIO_ID_IDENTIFIER):
            return self._parse_actor_bio(container, link, priority, id[_BIO_ID_IDENTIFIER_LEN:], soup)

        return self._parse_actor(container, link, priority, id, soup)

    def _parse_actor(self, container: ScrapeContainer, link: str, priority: int, id: str, soup: BeautifulSoup):
        """This method redirects to the biography page.

        Args:
            container (ScrapeContainer): A ScrapeContainer instance
            link (str): The scrape link
            priority (int): The scrape priority
            id (str): The generated unique id
            soup (BeautifulSoup): The content
        """
        container.queue.enqueue("https://www.imdb.com/name/" + id + "/bio", priority)

    def _parse_actor_bio(self, container: ScrapeContainer, link: str, priority: int, id: str, soup: BeautifulSoup):
        """Parses all biograhpy informations.

        Args:
            container (ScrapeContainer): A ScrapeContainer instance
            link (str): The scrape link
            priority (int): The scrape priority
            id (str): The generated unique id
            soup (BeautifulSoup): The content
        """

        name = soup.find("h3").text.strip()

        nickname_td = soup.find('td', {'class': 'label'}, text="Nickname")
        nickname = None
        if nickname_td:
            nickname_sibling_td = nickname_td.find_next_sibling('td')
            if nickname_sibling_td:
                nickname = nickname_sibling_td.text.strip()

        height_td = soup.find('td', {'class': 'label'}, text="Height")
        if height_td:
            height_sibling_td = height_td.find_next_sibling('td')
            if height_sibling_td:
                match = _HEIGHT_PARSER.match(height_sibling_td.text.strip())
                if match:
                    height = float(match.group('Height').replace(',', '.'))

        bornInfo = soup.find("time")
        imageUrlEl = soup.find('img', {'class': 'poster'}) or soup.find('img', {'id': 'name-poster'})

        dateOfBirth = None
        bornIn = None

        if(bornInfo):
            dateOfBirth = bornInfo["datetime"].strip()
            bornInEl = bornInfo.parent.find('a', {'href': Utils.ACTOR_FIND_BIRTH_LOCATION_PARSER})
            if(bornInEl):
                bornIn = bornInEl.text.strip()

        if(imageUrlEl):
            image_link = Utils.prepareImageLink(imageUrlEl['src'])
            if image_link:
                container.images['actor_' + id + "." + image_link[1]] = image_link[0]


        biography = ''
        bio_title = soup.find('a', {'name': 'mini_bio'})
        if bio_title:
            bio_content = bio_title.find_next_sibling('div', {'class': 'soda odd'})
            if bio_content:
                biography = bio_content.text.strip()

        container.dataContainer.insertOrUpdateActor({
            'ID': id,
            'Name': name,
            'Nickname': nickname,
            'Height': height,
            'DateOfBirth': dateOfBirth,
            'BornIn': bornIn,
            'Biography': biography,
            'SourceUrl': link,
            'Completed': True
        })

        container.queue.enqueue('https://www.imdb.com/name/' + id + '/awards', priority)
        container.queue.enqueue('https://www.imdb.com/filmosearch/?explore=title_type&role=' + id + '&ref_=filmo_ref_typ&sort=user_rating,desc&mode=detail&page=1&title_type=movie%2CtvMovie', priority)

    def _parse_actor_awards(self, container: ScrapeContainer, link: str, priority: int, id: str, soup: BeautifulSoup):
        """Parses all awards based on the given data.

        Args:
            container (ScrapeContainer): A ScrapeContainer instance
            link (str): The scrape link
            priority (int): The scrape priority
            id (str): The generated unique id
            soup (BeautifulSoup): The content
        """

        alist = soup.find('div', class_="article listo")

        award_name = None

        for el in alist:
            if(el.name == 'h3'):
                award_name = el.text.strip()
            if (el.name == 'table'):
                rows = el.findAll('tr')

                year = 0
                winner = False
                category = ''

                for a in rows:
                    year_el = a.find('td', attrs={'class': 'award_year'})
                    if(year_el):
                        year = int(year_el.text.strip(), base=10)

                    winner_el = a.find('td', attrs={'class': 'award_outcome'})
                    if(winner_el):
                        winner = winner_el.find('b').text.strip() == 'Winner'
                        category = a.find(
                            'span', attrs={'class': 'award_category'}).text

                    movie_id = None
                    movie_link = a.find('td', class_="award_description")

                    if(movie_link):
                        movie_link = movie_link.find('a')
                        if(movie_link):
                            movie_link_match = Utils.MOVIE_ID_PARSER.match(
                                movie_link['href'])
                            if(movie_link_match):
                                movie_id = movie_link_match.group('Id')
                                container.queue.enqueue('https://www.imdb.com/title/' + movie_id, priority + 1)

                    award_description = a.find('td', class_="award_description").next_element.strip() or ''

                    container.dataContainer.insertOrUpdateActorAward({
                        'ActorID': id,
                        'Name': award_name,
                        'Year': year,
                        'Category': category,
                        'Description': award_description,
                        'Winner': winner,
                        'MovieId': movie_id,
                        'SourceUrl': link
                    })