from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
import pandas as pd

CONTENT_TYPE_ACTOR = 'ACTOR'
CONTENT_TYPE_MOVIE = 'MOVIE'
CONTENT_TYPE_LIST = 'LIST'

DEFAULT_SELECTION_ITEMS = [(None, 'Choose', None), (CONTENT_TYPE_ACTOR, 'Actors', None), (CONTENT_TYPE_MOVIE, 'Movies', None)]

class MainModel(QObject):
    database_loaded = False

    _lists = None
    _actors = None
    _movies = None

    _content = None
    _content_type = None

    _selection_items = DEFAULT_SELECTION_ITEMS

    data_updated = pyqtSignal()

    @property
    def content(self):
        return self._content

    @property
    def content_type(self):
        return self._content_type

    @property
    def selection_items(self):
        return self._selection_items


    def setData(self, actors, movies, lists):
        self._actors = actors
        self._movies = movies
        self._lists = lists

        list_titles = []
        for x in lists.groupby(['Title', 'ID']).groups.keys():
            list_titles.append((CONTENT_TYPE_LIST, x[0], x[1]))

        self._selection_items = DEFAULT_SELECTION_ITEMS + list_titles

        self.database_loaded = True

        self.data_updated.emit()

    def set_selected_item(self, content_type, identifier):
        self._content_type = content_type

        if(content_type == CONTENT_TYPE_ACTOR):
            self._content = self._actors
        elif(content_type == CONTENT_TYPE_MOVIE):
            self._content = self._movies
        elif(content_type == CONTENT_TYPE_LIST):
            self._content = self._lists[(self._lists.ID == identifier)][['Name', 'Type', 'ItemId', 'SortId']]
        else:
            self._content_type = None
            self._content = None            

        self.data_updated.emit()
