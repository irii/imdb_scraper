class ScrapeResult:    
    _scraped_ids = []

    actors = []
    awards = []
    movies = []
    lists = []
    casts = []
    images = []

    def markIdAsSet(self, data_type, id):
        self._scraped_ids.append(data_type + '::' + id)

    def isIdSet(self, data_type, id):
        return (data_type + '::' + id) in self._scraped_ids


class ScraperSource:
    name: str

    def scrape(self, container: ScrapeResult, startLinks, notify):
        pass