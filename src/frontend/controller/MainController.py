from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

from data.data_container import DataContainer
from frontend.model.MainModel import MainModel
from frontend.WindowManager import WindowManager

import pandas as pd

class MainController(QObject):
    _windowManager: WindowManager
    _dataContainer: DataContainer

    _current_database_folder: str

    def __init__(self, windowManager: WindowManager, model: MainModel, dataContainer: DataContainer):
        super().__init__()
        self._windowManager = windowManager
        self.model = model
        self._dataContainer = dataContainer

    def closeAll(self):
        self._windowManager.destroy_all()

    def loadDatabase(self, folder):
        self._current_database_folder = folder
        self._dataContainer.load(folder)

        moviesReduced = self._dataContainer.movies[['ID', 'Title']]
        moviesReduced['Type'] = 'Movie'

        moviesReduced.rename(columns={'ID': 'ID_Movie', 'Title': 'Name_Movie'}, inplace=True)

        actorsReduced = self._dataContainer.actors[['ID', 'Name']]
        actorsReduced['Type'] = 'Actor'

        actorsReduced.rename(columns={'ID': 'ID_Actor', 'Name': 'Name_Actor'}, inplace=True)

        enriched_list = self._dataContainer.lists.merge(moviesReduced, how='left', left_on=['Type', 'ItemId'], right_on=['Type', 'ID_Movie'])
        enriched_list = enriched_list.merge(actorsReduced, how='left', left_on=['Type', 'ItemId'], right_on=['Type', 'ID_Actor'])
        enriched_list['Name'] = None
        enriched_list['Name'] = enriched_list.apply(lambda row: row['Name_Movie'] if pd.isnull(row['Name_Actor']) else row['Name_Actor'], axis=1)

        enriched_list = enriched_list[['ID', 'SortId', 'Title', 'Type', 'ItemId', 'Name']]

        self.model.setData(self._dataContainer.actors, self._dataContainer.movies, enriched_list)

    def saveDatabase(self, folder=None):
        self._dataContainer.save(folder or self._current_database_folder)


    def change_selected_item(self, content_type, identifier):
        self.model.set_selected_item(content_type, identifier)

    def display_scrape(self):
        if not self._dataContainer.database_loaded:
            return False

        self._windowManager.get_or_create_view('SCRAPE', self.scrape_finished).show()
        return True

    def scrape_finished(self):
        self.model.setData(self._dataContainer.actors, self._dataContainer.movies, self._dataContainer.lists)

    def display_about(self):
        self._windowManager.get_or_create_view('ABOUT').show()

    def display_actor(self, actorId):
        if pd.isnull(actorId):
            return

        self._windowManager.get_or_create_view('ACTOR', actorId).show()
        
    def display_movie(self, movieId):
        if pd.isnull(movieId):
            return

        self._windowManager.get_or_create_view('MOVIE', movieId).show()