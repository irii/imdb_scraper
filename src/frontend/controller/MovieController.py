import pandas as pd
from data.data_container import DataContainer
from frontend.WindowManager import WindowManager
from frontend.model.MovieModel import MovieModel
from scraper.scraper import Scraper, LambdaScraperEventListener
from PyQt5 import QtCore

class MovieBackgroundTask(QtCore.QThread):
    """This class handles the ondemand background scraping task

    Args:
        scraper (Scraper): The scraper instance
        movieId (str): The requested movie which should be fetched if required
    """

    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(int)

    def __init__(self, scraper: Scraper, movieId: str):
        """Constructor
        Args:
            scraper (Scraper): A scraper instance
            movieId (str): The requested movie id
        """
        super().__init__()

        self.scraper = scraper
        self.movieId = movieId

    def run(self):
        """Overwritten method, executes the async process.
        """
        self.scraper.fetchMovie(self.movieId, LambdaScraperEventListener(finished=lambda: self.finished.emit(), processing=self._report_progress))

    def _report_progress(self, type: str, link: str, count: int, totalCount: int):
        """Calculates the current progress based on already scraped urls in relation with total count of urls which where queued.

        Args:
            type (str): [description]
            link (str): [description]
            count (int): [description]
            totalCount (int): [description]
        """
        if totalCount == 0:
            self.progress.emit(0)
            return    

        self.progress.emit(count / totalCount * 100)

class MovieController:
    """This controller handles all movie releated processes also it allows to fetch on demand an movie and map it to the model
    """

    _background_task: MovieBackgroundTask = None

    def __init__(self, model: MovieModel, dataContainer: DataContainer, windowManager: WindowManager, scraper: Scraper):
        """Constructor
        Args:
            model (MovieModel): A movie model instance
            dataContainer (DataContainer): A data container instance
            windowManager (WindowManager): A window manager instance
            scraper (Scraper): A scraper instance
        """

        self.model = model
        self._dataContainer = dataContainer
        self._windowManager = windowManager
        self._scraper = scraper

    def set_movie(self, id: str) -> bool():
        """Tries to load a movie and assign it to the model.
        If required a scrape processes happens.

        Args:
            id (str): The requested movie (id)

        Returns:
            [bool]: Returns true if operation was executed successfully.
        """
        self._background_task = MovieBackgroundTask(self._scraper, id)
        self._background_task.progress.connect(lambda progress: self.model.data_processing.emit(progress))
        self._background_task.finished.connect(lambda: self._apply_data(id))
        
        self._background_task.start()

        return True


    def _apply_data(self, id: str):
        """This methods load the movie data from the datacontainer and assigns it to the model.
        Args:
            id (str): Movie Id
        """

        df = self._dataContainer.movies
        movie = df.loc[(df['ID'] == id)].to_dict('records')[0]

        actors_df = self._dataContainer.actors[['ID', 'Name']]
        actors_movies_df = self._dataContainer.actors_movies[(self._dataContainer.actors_movies["MovieID"] == id)][["ActorID"]]
        
        actors = actors_movies_df.merge(actors_df, how='left', left_on='ActorID', right_on='ID')

        self.model.setDataFrame(movie, actors, self._dataContainer.getImage('movie_' + id))

    def display_actor(self, actorId):
        """Opens a actor window by the given actorId

        Args:
            actorId (str): Unique identifier of an actor
        """

        if actorId is None or pd.isnull(actorId) or actorId.strip() == '':
            return

        self._windowManager.get_or_create_view('ACTOR', actorId).show()