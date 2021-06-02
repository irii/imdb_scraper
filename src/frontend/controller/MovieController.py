import pandas as pd
from data.data_container import DataContainer
from frontend.WindowManager import WindowManager
from scraper.scraper import Scraper, LambdaScraperEventListener
from PyQt5 import QtCore

class MovieBackgroundTask(QtCore.QThread):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(int)

    def __init__(self, scraper: Scraper, movieId):
        super().__init__()

        self.scraper = scraper
        self.movieId = movieId

    def run(self):
        self.scraper.fetchMovie(self.movieId, LambdaScraperEventListener(finished=lambda: self.finished.emit(), processing=self._report_progress))

    def _report_progress(self, type, link, count, totalCount):
        if totalCount == 0:
            self.progress.emit(0)
            return    

        self.progress.emit(count / totalCount * 100)

class MovieController:
    _background_task: MovieBackgroundTask = None

    def __init__(self, model, dataContainer: DataContainer, windowManager: WindowManager, scraper: Scraper):
        self.model = model
        self._dataContainer = dataContainer
        self._windowManager = windowManager
        self._scraper = scraper

    def set_movie(self, id) -> bool():
        self._background_task = MovieBackgroundTask(self._scraper, id)
        self._background_task.progress.connect(lambda progress: self.model.data_processing.emit(progress))
        self._background_task.finished.connect(lambda: self._apply_data(id))
        
        self._background_task.run()

        return True


    def _apply_data(self, id):  
        df = self._dataContainer.movies
        movie = df.loc[(df['ID'] == id)].to_dict('records')[0]

        actors_df = self._dataContainer.actors[['ID', 'Name']]
        actors_movies_df = self._dataContainer.actors_movies[(self._dataContainer.actors_movies["MovieID"] == id)][["ActorID"]]
        
        actors = actors_movies_df.merge(actors_df, how='left', left_on='ActorID', right_on='ID')

        self.model.setDataFrame(movie, actors, self._dataContainer.getImage('movie_' + id))

    def display_actor(self, actorId):
        if pd.isnull(actorId):
            return

        self._windowManager.get_or_create_view('ACTOR', actorId).show()