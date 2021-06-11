from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

from data.data_container import DataContainer
from scraper.scraper import Scraper
from frontend.model.MainModel import MainModel
from frontend.WindowManager import WindowManager

import pandas as pd

class MainController(QObject):
    """ The Main controller which handels all list interactions with the main ui.
    """

    _windowManager: WindowManager
    _dataContainer: DataContainer
    _current_database_folder: str

    def __init__(self, windowManager: WindowManager, model: MainModel, dataContainer: DataContainer):
        """Constructor

        Args:
            windowManager (WindowManager): A window manager instance
            model (MainModel): A main model instance
            dataContainer (DataContainer): A data container instance
        """
        super().__init__()
        self._windowManager = windowManager
        self.model = model
        self._dataContainer = dataContainer

        self._loadData()

    def closeAll(self):
        """Closes all windows"""
        self._windowManager.destroy_all()

    def loadDatabase(self, folder: str):
        """Loads a database with the given folder
        Args:
            folder (str): Database folder path
        """
        self._current_database_folder = folder
        self._dataContainer.load(folder)
        self._loadData()

    def _loadData(self):
        """Loads and calculates all based on the current set category in the model
        """

        if not self._dataContainer.database_loaded:
            return

        moviesReduced = self._dataContainer.movies[['ID', 'Title']]
        moviesReduced['Type'] = 'Movie'

        moviesReduced.rename(columns={'ID': 'ID_Movie', 'Title': 'Name_Movie'}, inplace=True)

        actorsReduced = self._dataContainer.actors[['ID', 'Name']]
        actorsReduced['Type'] = 'Actor'

        actorsReduced.rename(columns={'ID': 'ID_Actor', 'Name': 'Name_Actor'}, inplace=True)

        enriched_list = self._dataContainer.lists.merge(moviesReduced, how='left', left_on=['Type', 'ItemId'], right_on=['Type', 'ID_Movie'])
        enriched_list = enriched_list.merge(actorsReduced, how='left', left_on=['Type', 'ItemId'], right_on=['Type', 'ID_Actor'])
        enriched_list['Name'] = None

        if enriched_list['ID'].count() > 0:
            enriched_list['Name'] = enriched_list.apply(lambda row: row['Name_Movie'] if pd.isnull(row['Name_Actor']) else row['Name_Actor'], axis=1)

        enriched_list = enriched_list[['ID', 'SortId', 'Title', 'Type', 'ItemId', 'Name']]

        self.model.setData(self._dataContainer.actors, self._dataContainer.movies, enriched_list)


    def saveDatabase(self):
        """Saves the current database
        """
        self._dataContainer.save()


    def change_selected_item(self, content_type: str, identifier: str):
        """Get's called when the selected category item on the ui is changed

        Args:
            content_type ([type]): [description]
            identifier ([type]): [description]
        """
        self.model.set_selected_item(content_type, identifier)

    def display_scrape(self):
        if not self._dataContainer.database_loaded:
            return False

        self._windowManager.get_or_create_view('SCRAPE', self.scrape_finished).show()
        return True

    def scrape_finished(self):
        """Get's called when the scraper has finished the scraping processes, closes the scrape windows and updates the model data.
        """
        self._windowManager.close_view('SCRAPE')
        self._loadData()

    def display_about(self):
        """Displays the about window
        """
        self._windowManager.get_or_create_view('ABOUT').show()

    def display_actor(self, actorId: str):
        """Opens a actor window by the given actorId

        Args:
            actorId (str): Unique identifier of an actor
        """
        if pd.isnull(actorId):
            return

        self._windowManager.get_or_create_view('ACTOR', actorId).show()
        
    def display_movie(self, movieId):
        """Opens a movie window by the given movieId

        Args:
            movieId (str): Unique identifier of an movie
        """

        if pd.isnull(movieId):
            return

        self._windowManager.get_or_create_view('MOVIE', movieId).show()