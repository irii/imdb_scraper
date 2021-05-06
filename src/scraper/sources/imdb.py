import re
import requests
from bs4 import BeautifulSoup, Tag

from scraper.scraper_source import ScraperSource, ScrapeResult

_LIST_ID_PARSER = re.compile(r".*list/(?P<Id>[A-Z0-9]*).*", re.IGNORECASE)
_AWARD_ID_PARSER = re.compile(
    r".*name/(?P<Id>[A-Z0-9]*)/awards.*", re.IGNORECASE)
_ACTOR_ID_PARSER = re.compile(r".*name/(?P<Id>nm[A-Z0-9]*).*", re.IGNORECASE)
_CAST_ID_PARSER = re.compile(
    r".*title/(?P<Id>tt[A-Z0-9]*)/fullcredits.*", re.IGNORECASE)
_MOVIE_ID_PARSER = re.compile(r".*title/(?P<Id>tt[A-Z0-9]*).*", re.IGNORECASE)
_ACTOR_FIND_BIRTH_LOCATION_PARSER = re.compile(
    r'.*\/search\/name\?birth\_place\=.*')


class ImdbSource(ScraperSource):
    def __init__(self):
        self.name = 'IMDB'

        self.scrapers = [
            {'matcher': _LIST_ID_PARSER, 'parser': self._parse_list, 'type': 'list'},
            {'matcher': _AWARD_ID_PARSER,
                'parser': self._parse_actor_awards, 'type': 'awards'},
            {'matcher': _ACTOR_ID_PARSER, 'parser': self._parse_actor, 'type': 'actor'},
            {'matcher': _CAST_ID_PARSER, 'parser': self._parse_movie_credits,
                'type': 'movie_credits'},
            {'matcher': _MOVIE_ID_PARSER, 'parser': self._parse_movie, 'type': 'movie'}
        ]

    def _parse_list(self, container: ScrapeResult, link: str, id: str, soup: BeautifulSoup):
        title = soup.find("h1").text
        lister_list = soup.findAll(
            "div", attrs={'class': 'lister-item mode-detail'})

        queue = []
        items = []

        sortId = 1

        for entry in lister_list:
            h3 = entry.find('h3', attrs={'class': 'lister-item-header'})
            link = h3.find('a')['href']

            match = _ACTOR_ID_PARSER.match(link)
            if(match):
                queue.append(f'https://www.imdb.com/name/' +
                             match.group('Id') + '/bio')     # Queue entry

                # Add scrape result
                items.append({
                    'ID': id,
                    'Title': title,
                    'SortId': sortId,
                    'Type': 'Actor',
                    'ItemId': match.group('Id')
                })

            match = _MOVIE_ID_PARSER.match(link)
            if(match):
                queue.append('https://www.imdb.com/title/' +
                             match.group('Id'))  # Queue entry

                # Add scrape result
                container.lists.append({
                    'ID': id,
                    'Title': title,
                    'SortId': sortId,
                    'Type': 'Movie',
                    'ItemId': match.group('Id')
                })

            sortId = sortId + 1
        return queue

    def _parse_actor(self, container: ScrapeResult, link: str, id: str, soup: BeautifulSoup):
        name = soup.find("h3").text.strip()
        bornInfo = soup.find("time")
        imageUrlEl = soup.find('img', {'class': 'poster'})

        dateOfBirth = None
        bornIn = None
        imageUrl = None

        if(bornInfo):
            dateOfBirth = bornInfo["datetime"].strip()
            # bornInfo.find_next_sibling('a').text.strip()
            bornInEl = bornInfo.parent.find(
                'a', {'href': _ACTOR_FIND_BIRTH_LOCATION_PARSER})
            if(bornInEl):
                bornIn = bornInEl.text.strip()
        else:
            born = ''

        if(imageUrlEl):
            container.images['actor_' + id] = imageUrlEl['src']

        container.actors.append({
            'ID': id,
            'Name': name,
            'DateOfBirth': dateOfBirth,
            'BornIn': bornIn
        })

        return ['https://www.imdb.com/name/' + id + '/awards']

    def _parse_actor_awards(self, container: ScrapeResult, link: str, id: str, soup: BeautifulSoup):
        alist = soup.find('div', class_="article listo")

        award_name = None

        queue = []

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
                            movie_link_match = _MOVIE_ID_PARSER.match(
                                movie_link['href'])
                            if(movie_link_match):
                                movie_id = movie_link_match.group('Id')
                                queue.append(
                                    'https://www.imdb.com/title/' + movie_id)

                    award_description_list = list(
                        a.find('td', class_="award_description").children)
                    award_description = ''
                    if len(award_description_list) > 0:
                        award_description = award_description_list[0]

                    container.awards.append({
                        'ActorID': id,
                        'Name': award_name,
                        'Year': year,
                        'Category': category,
                        'Reason': award_description,
                        'Winner': winner,
                        'MovieId': movie_id
                    })

        return queue

    def _parse_movie(self, container: ScrapeResult, link: str, id: str, soup: BeautifulSoup):
        title = soup.find('h1').find(text=True, recursive=False).strip()
        rating_el = soup.find('span', attrs={'itemprop': 'ratingValue'})

        year = None
        year_el = soup.find('span', attrs={'id': 'titleYear'})
        if(year_el):
            year = int(year_el.find('a').text.strip(), base=10)

        posterEl = soup.find('div', {'class': 'poster'})
        if(posterEl):
            container.images['movie_' + id] = posterEl.find('img')['src']

        container.movies.append({
            'ID': id,
            'Title': title,
            'AvgRating': float(rating_el.text.strip()),
            'Release': year
        })

        return ['https://www.imdb.com/title/' + id + '/fullcredits']

    def _parse_movie_credits(self, container: ScrapeResult, link: str, id: str, soup: BeautifulSoup):
        actorIds = []

        actor_urls = soup.find_all('a', {'href': _ACTOR_ID_PARSER})
        for x in actor_urls:
            actorIds.append(_ACTOR_ID_PARSER.match(x).group('id'))

        return actorIds

    def _handle_link(self, container: ScrapeResult, link):
        for x in self.scrapers:
            match = x['matcher'].match(link)
            if(match):
                id = match.group('Id')

                if container.isIdSet(x['type'], id):
                    return []

                container.markIdAsSet(x['type'], id)

                page = requests.get(link)
                soup = BeautifulSoup(page.text, 'html.parser')

                return x['parser'](container, link, match.group('Id'), soup) or []

        return []

    def scrape(self, container: ScrapeResult, startLinks, notify):
        queue = [] + startLinks
        scrapedCount = 0

        total_count = len(startLinks)

        while((len(queue) > 0) and (scrapedCount < 100)):
            work = queue.pop(0)

            if(notify):
                notify(work, len(queue), total_count)

            try:
                scrapedCount = scrapedCount + 1
                new_queue_items = self._handle_link(container, work)
            except:
                pass

            total_count = total_count + len(new_queue_items)

            queue = queue + new_queue_items

        return container
