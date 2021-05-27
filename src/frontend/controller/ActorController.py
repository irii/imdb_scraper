import pandas as pd
from data.data_container import DataContainer
from frontend.WindowManager import WindowManager
from scraper.scraper import Scraper, LambdaScraperEventListener

class ActorController:
    def __init__(self, model, dataContainer: DataContainer, windowManager: WindowManager, scraper: Scraper):
        self.model = model
        self._dataContainer = dataContainer
        self._windowManager = windowManager
        self._scraper = scraper

    def set_actor(self, id) -> bool():
        self.model.data_proccessing.emit()
        self._scraper.fetchActor(id, LambdaScraperEventListener(finished=lambda: self._apply_data(id)))
        return True

    def _apply_data(self, id):
        df = self._dataContainer.actors
        actor = df.loc[(df['ID'] == id)].to_dict('records')[0]

        awardsDf = self._dataContainer.awards
        awardsFiltered = awardsDf.loc[(awardsDf['ActorID'] == id)]

        moviesReduced = self._dataContainer.movies[['ID', 'Title']]
        awardsMoivesJoined = awardsFiltered.merge(moviesReduced, how='left', left_on='MovieId', right_on='ID')
        awards = awardsMoivesJoined[['Name', 'Year', 'Winner', 'Description', 'Title', 'ID']]

        movies = self._dataContainer.actors_movies[(self._dataContainer.actors_movies['ActorID'] == id)]
        movies = movies.merge(moviesReduced, how='left', left_on='MovieID', right_on='ID')
        movies = movies[['Title', 'MovieID']]

        self.model.setDataFrame(actor, awards, movies, self._dataContainer.getImage('actor_' + id))

    def display_movie(self, movieId):
        if pd.isnull(movieId):
            return

        self._windowManager.get_or_create_view('MOVIE', movieId).show()