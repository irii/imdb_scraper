import pandas as pd
import numpy as np
from data.data_container import DataContainer
from frontend.WindowManager import WindowManager
from scraper.scraper import Scraper, LambdaScraperEventListener
from PyQt5 import QtCore

class ActorBackgroundTask(QtCore.QThread):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(int)

    def __init__(self, scraper: Scraper, actorId):
        super().__init__()

        self.scraper = scraper
        self.actorId = actorId

    def run(self):
        self.scraper.fetchActor(self.actorId, LambdaScraperEventListener(finished=lambda: self.finished.emit(), processing=self._report_progress))

    def _report_progress(self, type, link, count, totalCount):
        if totalCount == 0:
            self.progress.emit(0)
            return    

        self.progress.emit(count / totalCount * 100)


class ActorController:
    _background_task: ActorBackgroundTask = None

    def __init__(self, model, dataContainer: DataContainer, windowManager: WindowManager, scraper: Scraper):
        self.model = model
        self._dataContainer = dataContainer
        self._windowManager = windowManager
        self._scraper = scraper

    def set_actor(self, id) -> bool():
        self._background_task = ActorBackgroundTask(self._scraper, id)
        self._background_task.progress.connect(lambda progress: self.model.data_processing.emit(progress))
        self._background_task.finished.connect(lambda: self._apply_data(id))
        
        self._background_task.start()
        return True


    def _apply_data(self, id):
        df = self._dataContainer.actors
        actor = df.loc[(df['ID'] == id)].to_dict('records')[0]

        awardsDf = self._dataContainer.awards
        awardsFiltered = awardsDf.loc[(awardsDf['ActorID'] == id)]

        moviesReduced = self._dataContainer.movies[['ID', 'Title', 'Genres', 'AvgRating']]
        awardsMoivesJoined = awardsFiltered.merge(moviesReduced, how='left', left_on='MovieId', right_on='ID')
        awards = awardsMoivesJoined[['Name', 'Year', 'Winner', 'Description', 'Title', 'ID']]

        filtered_actor_movies = self._dataContainer.actors_movies[(self._dataContainer.actors_movies['ActorID'] == id)]

        movies = filtered_actor_movies.merge(moviesReduced, how='left', left_on='MovieID', right_on='ID')

        genres = [item for sublist in  movies[(pd.isnull(movies['Genres']) == False)]['Genres'].tolist() for item in sublist]
        genres_pd = pd.DataFrame(genres, columns=['Genres'])
        
        grouped_genres = genres_pd.groupby(['Genres'], as_index=False).agg(count_col=pd.NamedAgg('Genres', "count")).rename(columns={'count_col': 'Count'})

        movies_sorted = movies.sort_values(by='AvgRating', ascending=False)
        self.model.setDataFrame(actor, awards, movies_sorted[['Title', 'MovieID', 'AvgRating']], grouped_genres, self._dataContainer.getImage('actor_' + id))

    def display_movie(self, movieId):
        if pd.isnull(movieId):
            return

        self._windowManager.get_or_create_view('MOVIE', movieId).show()