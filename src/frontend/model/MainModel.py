from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
import pandas as pd

CONTENT_TYPE_ACTOR = 'ACTOR'
CONTENT_TYPE_MOVIE = 'MOVIE'
CONTENT_TYPE_LIST = 'LIST'

# Default category values
DEFAULT_SELECTION_ITEMS = [(None, 'Choose', None), (CONTENT_TYPE_ACTOR, 'Actors', None), (CONTENT_TYPE_MOVIE, 'Movies', None)]

class MainModel(QObject):
    '''This model class contains all actor releated data for thie ui from the controller'''

    database_loaded = False

    _lists: pd.DataFrame = None
    _actors: pd.DataFrame = None
    _movies: pd.DataFrame = None

    _content: pd.DataFrame = None
    _content_type = None

    _selection_items = DEFAULT_SELECTION_ITEMS

    selection_changed = pyqtSignal()
    database_updated = pyqtSignal()

    @property
    def content(self):
        """Returns a pandas dataframe content, based on the selected category or list
        """
        return self._content

    @property
    def content_type(self):
        """Returns the current selected category or list
        """
        return self._content_type

    @property
    def selection_items(self):
        """Returns a list of all available categories and lists
        """
        return self._selection_items

    def setData(self, actors: pd.DataFrame, movies: pd.DataFrame, lists: pd.DataFrame):
        """Updates the current set data and notifies all listeners
        Args:
            actors (pd.DataFrame): Updated actors
            movies (pd.DataFrame): Updated movies
            lists (pd.DataFrame): Updated lists
        """

        self._actors = actors
        self._movies = movies
        self._lists = lists

        list_titles = []
        for x in lists.groupby(['Title', 'ID']).groups.keys():
            list_titles.append((CONTENT_TYPE_LIST, x[0], x[1]))

        self._selection_items = DEFAULT_SELECTION_ITEMS + list_titles

        self.database_loaded = True

        self.database_updated.emit()

    def set_selected_item(self, content_type: str, identifier: str):
        """Updates the current selection and notifies all listeners
        Args:
            content_type (str): Category type
            identifier (str): If category type is a list, the selected list id
        """
        if not self.database_loaded:
            return

        self._content_type = content_type

        if(content_type == CONTENT_TYPE_ACTOR):
            self._content = self._actors[['ID', 'Name']]
        elif(content_type == CONTENT_TYPE_MOVIE):
            self._content = self._movies[['ID', 'Title']]
        elif(content_type == CONTENT_TYPE_LIST):
            self._content = self._lists[(self._lists.ID == identifier)].sort_values('SortId', ascending=True)[['Name', 'Type', 'ItemId']]
        else:
            self._content_type = None
            self._content = None            

        self.selection_changed.emit()
