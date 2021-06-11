from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
import pandas as pd

class MovieModel(QObject):
    """This model class contains all actor releated data for thie ui from the controller
    """
    
    data_updated = pyqtSignal()
    data_processing = pyqtSignal(int)

    actors: pd.DataFrame = None
    movie: dict = None
    imagePath: str = None

    def setDataFrame(self, movie: dict, actors: pd.DataFrame, imagePath: str=None):
        """Updates the current data and notifies all listeners

        Args:
            movie (dict): A movie info dictionary
            actors (pd.DataFrame): A list of all actors in this movie
            imagePath (str, optional): A image of this movie if available. Defaults to None.
        """
        self.movie = movie
        self.actors = actors
        self.imagePath = imagePath

        self.data_updated.emit()