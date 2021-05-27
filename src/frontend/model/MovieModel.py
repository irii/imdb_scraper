from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

class MovieModel(QObject):
    data_updated = pyqtSignal()
    data_proccessing = pyqtSignal()

    actors = None
    movie: dict = None
    imagePath: str = None

    def setDataFrame(self, movie, actors, imagePath=None):
        self.movie = movie
        self.actors = actors
        self.imagePath = imagePath

        self.data_updated.emit()