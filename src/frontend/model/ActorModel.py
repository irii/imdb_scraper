from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

class ActorModel(QObject):
    data_updated = pyqtSignal()
    data_processing = pyqtSignal(int) # Progress

    actor: dict = None
    awards: dict = None
    movies = None
    imagePath: str = None

    genres = None

    def setDataFrame(self, actor, awards, movies, genres, imagePath=None):
        self.actor = actor
        self.awards = awards
        self.movies = movies
        self.genres = genres
        self.imagePath = imagePath

        self.data_updated.emit()