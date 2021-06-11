import pandas as pd
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

class ActorModel(QObject):
    """This model class contains all actor releated data for thie ui from the controller
    """
    
    data_updated = pyqtSignal()
    data_processing = pyqtSignal(int) # Progress

    actor: dict = None
    awards: pd.DataFrame = None
    movies: pd.DataFrame = None
    avgRatingPerYear: pd.DataFrame = None
    imagePath: str = None

    genres = None

    def setDataFrame(self, actor, awards, movies, genres, avgRatingPerYear, imagePath=None):
        """Updates the current data and notifies all listeners

        Args:
            actor ([type]): A actor info dictionary
            awards ([type]): A list of all actor awards
            movies ([type]): A list of all actor movies
            genres ([type]): A list of all generes the actor was releated
            avgRatingPerYear ([type]): Calcualted avg rating per year
            imagePath (str, optional): The actor image if available. Defaults to None.
        """
        self.actor = actor
        self.awards = awards
        self.movies = movies
        self.genres = genres
        self.avgRatingPerYear = avgRatingPerYear
        self.imagePath = imagePath

        self.data_updated.emit()