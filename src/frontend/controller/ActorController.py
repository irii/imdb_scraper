import pandas as pd
import numpy as np
from data.data_container import DataContainer
from frontend.WindowManager import WindowManager
from frontend.model.ActorModel import ActorModel
from scraper.scraper import Scraper, LambdaScraperEventListener
from PyQt5 import QtCore

class ActorBackgroundTask(QtCore.QThread):
    '''This class handles the ondemand background scraping task'''

    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(int)

    def __init__(self, scraper: Scraper, actorId):
        super().__init__()

        self.scraper = scraper
        self.actorId = actorId

    def run(self):
        """Overwritten method, executes the async process.
        """
        self.scraper.fetchActor(self.actorId, LambdaScraperEventListener(finished=lambda: self.finished.emit(), processing=self._report_progress))

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


class ActorController:
    """This controller handles all movie releated processes. This controller allows the fetch on demand an actor and map it to the model

    Returns:
        [type]: [description]
    """

    _background_task: ActorBackgroundTask = None

    def __init__(self, model: ActorModel, dataContainer: DataContainer, windowManager: WindowManager, scraper: Scraper):
        """Constructor

        Args:
            model (ActorModel): A actor model instance
            dataContainer (DataContainer): A data container instance
            windowManager (WindowManager): A window manager instance
            scraper (Scraper): A scraper instance
        """
        self.model = model
        self._dataContainer = dataContainer
        self._windowManager = windowManager
        self._scraper = scraper

    def set_actor(self, id: str) -> bool():
        """Tries to load a actor and assign it to the model.
        If required a scrape processes happens.

        Args:
            id (str): The requested actor id

        Returns:
            [bool]: Returns true if operation was executed successfully.
        """

        self._background_task = ActorBackgroundTask(self._scraper, id)
        self._background_task.progress.connect(lambda progress: self.model.data_processing.emit(progress))
        self._background_task.finished.connect(lambda: self._apply_data(id))
        
        self._background_task.start()
        return True


    def _apply_data(self, id):
        """This methods load the actor data from the datacontainer and assigns it to the model.
        Args:
            id (str): Movie Id
        """

        df = self._dataContainer.actors
        actor = df.loc[(df['ID'] == id)].to_dict('records')[0]

        awardsDf = self._dataContainer.awards
        awardsFiltered = awardsDf.loc[(awardsDf['ActorID'] == id)]

        moviesReduced = self._dataContainer.movies[['ID', 'Title', 'Genres', 'AvgRating', 'Release']]
        awardsMoivesJoined = awardsFiltered.merge(moviesReduced, how='left', left_on='MovieId', right_on='ID')
        awardsMoivesJoined['Title'] = awardsMoivesJoined['Title'].fillna('')
        awardsMoivesJoined['ID'] = awardsMoivesJoined['ID'].fillna('')

        awards = awardsMoivesJoined[['Year', 'Name', 'Category', 'Winner', 'Description', 'Title', 'ID']].sort_values(by=['Year', 'Name'], ascending=False)

        filtered_actor_movies = self._dataContainer.actors_movies[(self._dataContainer.actors_movies['ActorID'] == id)]

        movies = filtered_actor_movies.merge(moviesReduced, how='left', left_on='MovieID', right_on='ID')

        # Generes are a collection per row, which have to be merge into one list and grouped
        genres = [item for sublist in  movies[(pd.isnull(movies['Genres']) == False)]['Genres'].tolist() for item in sublist]
        genres_pd = pd.DataFrame(genres, columns=['Genres'])
        
        grouped_genres = genres_pd.groupby(['Genres'], as_index=False).agg(count_col=pd.NamedAgg('Genres', "count")).rename(columns={'count_col': 'Count'})

        movies_sorted = movies.sort_values(by='AvgRating', ascending=False)

        movies_grouped_year = movies[['Release', 'AvgRating']].groupby(['Release'], as_index=False).mean("AvgRating").round({'AvgRating': 2}).sort_values(by='AvgRating', ascending=False)

        overall_rating = movies_sorted["AvgRating"].mean()
        if np.isnan(overall_rating):
            overall_rating = np.float64(0.0)

        actor["OverallRating"] = overall_rating.round(2)

        self.model.setDataFrame(actor, awards, movies_sorted[['Title', 'Release', 'AvgRating', 'MovieID']], grouped_genres, movies_grouped_year, self._dataContainer.getImage('actor_' + id))

    def display_movie(self, movieId):
        """Opens a movie window by the given movieId

        Args:
            movieId (str): Unique identifier of an movie
        """

        if movieId is None or pd.isnull(movieId) or movieId.strip() == '':
            return

        self._windowManager.get_or_create_view('MOVIE', movieId).show()