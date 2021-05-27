import sys
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QModelIndex
from PyQt5.QtGui import QPixmap
from .generated.Ui_MovieWindow import Ui_MovieWindow

from frontend.model.MovieModel import MovieModel
from frontend.controller.MovieController import MovieController
from frontend.BaseWindow import BaseChildWindow

from frontend.PandasTable import PandasModel

class MovieWindow(BaseChildWindow):
    def __init__(self, model: MovieModel, ctrl: MovieController):
        super().__init__()

        self.ui = Ui_MovieWindow()
        self.ui.setupUi(self)

        self.model = model
        self.controller = ctrl

        self.model.data_updated.connect(self.data_updated)
        self.ui.tableView_cast.doubleClicked.connect(self.table_cast_double_click)

        self.model.data_proccessing.connect(self.data_processing)

    def data_processing(self):
        pass

    def data_updated(self):
        self.setWindowTitle("Movie - " + self.model.movie["Title"] + " (" + self.model.movie["ID"] + ")")

        if self.model.imagePath:
            pixmap = QPixmap(self.model.imagePath)
            pixmap = pixmap.scaled(self.ui.label_image.parentWidget().width(), self.ui.label_image.parentWidget().height(), aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            self.ui.label_image.setPixmap(pixmap)
            
        self.ui.label_name.setText(self.model.movie['Title'])
        self.ui.label_release_year.setText(str(int(self.model.movie['Release'])))
        self.ui.label_description.setText(str(self.model.movie['Description']))

        self.ui.tableView_cast.setModel(PandasModel(self.model.actors[['Name']]))

    @pyqtSlot(QModelIndex)
    def table_cast_double_click(self, index):
        data = self.model.actors.iloc[index.row()]
        self.controller.display_actor(data['ID'])