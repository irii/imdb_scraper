import re

from bs4 import BeautifulSoup
from scraper.scrape_container import ScrapeContainer
from scraper.scraper_source import ScraperParser

import scraper.imdb.imdb_utils as Utils

_AWARD_ID_IDENTIFIER = "ACTOR_AWARD:"
_AWARD_ID_IDENTIFIER_LEN = len(_AWARD_ID_IDENTIFIER)

_BIO_ID_IDENTIFIER = "ACTOR_BIO:"
_BIO_ID_IDENTIFIER_LEN = len(_BIO_ID_IDENTIFIER)

class ImdbActorParser(ScraperParser):
    name = "IMDB_ACTOR"

    def getBioLink(self, id) -> str:
        return self.getLink(_BIO_ID_IDENTIFIER + id)

    def getLink(self, id) -> str:        
        if id.startswith(_AWARD_ID_IDENTIFIER):
            return "https://www.imdb.com/name/" + id[_AWARD_ID_IDENTIFIER_LEN:] + "/awards"

        if id.startswith(_BIO_ID_IDENTIFIER):
            return "https://www.imdb.com/name/" + id[_BIO_ID_IDENTIFIER_LEN:] + "/bio"

        return "https://www.imdb.com/name/" + id

    def isSupported(self, link) -> str:
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
        if id.startswith(_AWARD_ID_IDENTIFIER):
            return self._parse_actor_awards(container, link, priority, id[_AWARD_ID_IDENTIFIER_LEN:], soup)

        if id.startswith(_BIO_ID_IDENTIFIER):
            return self._parse_actor_bio(container, link, priority, id[_BIO_ID_IDENTIFIER_LEN:], soup)

        return self._parse_actor(container, link, priority, id, soup)

    def _parse_actor(self, container: ScrapeContainer, link: str, priority: int, id: str, soup: BeautifulSoup):
        container.queue.enqueue("https://www.imdb.com/name/" + id + "/bio", priority)

    def _parse_actor_bio(self, container: ScrapeContainer, link: str, priority: int, id: str, soup: BeautifulSoup):
        name = soup.find("h3").text.strip()
        bornInfo = soup.find("time")
        imageUrlEl = soup.find('img', {'class': 'poster'}) or soup.find('img', {'id': 'name-poster'})

        dateOfBirth = None
        bornIn = None

        if(bornInfo):
            dateOfBirth = bornInfo["datetime"].strip()
            # bornInfo.find_next_sibling('a').text.strip()
            bornInEl = bornInfo.parent.find(
                'a', {'href': Utils.ACTOR_FIND_BIRTH_LOCATION_PARSER})
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
            'DateOfBirth': dateOfBirth,
            'BornIn': bornIn,
            'Biography': biography,
            'SourceUrl': link,
            'Completed': True
        })

        container.queue.enqueue('https://www.imdb.com/name/' + id + '/awards', priority)
        container.queue.enqueue('https://www.imdb.com/filmosearch/?explore=title_type&role=' + id + '&ref_=filmo_ref_typ&sort=user_rating,desc&mode=detail&page=1&title_type=movie%2CtvMovie', priority)

    def _parse_actor_awards(self, container: ScrapeContainer, link: str, priority: int, id: str, soup: BeautifulSoup):
        alist = soup.find('div', class_="article listo")

        award_name = None

        for el in alist:
            if(el.name == 'h3'):
                award_name = el.text.strip()
            if (el.name == 'table'):
                rows = el.findAll('tr')

                year = 0
                winner = False
                category = None

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

                    award_description = a.find('td', class_="award_description").next_element.strip()

                    container.dataContainer.insertOrUpdateActorAward({
                        'ActorID': id,
                        'Name': award_name,
                        'Year': year,
                        'Category': category,
                        'Description': award_description,
                        'Winner': winner,
                        'MovieId': movie_id
                    })