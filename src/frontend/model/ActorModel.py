from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

class ActorModel(QObject):
    data_updated = pyqtSignal()

    actor: dict = None
    awards: dict = None
    movies = None
    imagePath: str = None

    def setDataFrame(self, actor, awards, movies, imagePath=None):
        self.actor = actor
        self.awards = awards
        self.movies = movies
        self.imagePath = imagePath

        self.data_updated.emit()