class ScrapeContainer:
    _scraped_ids = []

    actors = []
    awards = []
    movies = []
    lists = []
    actorsMovies = []
    images = {}

    def markIdAsSet(self, data_type, id):
        self._scraped_ids.append(data_type + '::' + id)

    def isIdSet(self, data_type, id):
        return (data_type + '::' + id) in self._scraped_ids