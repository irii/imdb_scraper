import sys
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QModelIndex
from PyQt5.QtGui import QPixmap
from .generated.Ui_MovieWindow import Ui_MovieWindow

from frontend.model.MovieModel import MovieModel
from frontend.controller.MovieController import MovieController
from frontend.BaseWindow import BaseChildWindow

from frontend.PandasTable import PandasModel

import pandas as pd

class MovieWindow(BaseChildWindow):
    def __init__(self, model: MovieModel, ctrl: MovieController):
        super().__init__()

        self.ui = Ui_MovieWindow()
        self.ui.setupUi(self)

        self.model = model
        self.controller = ctrl

        self.model.data_updated.connect(self.data_updated)
        self.ui.tableView_cast.doubleClicked.connect(self.table_cast_double_click)
        self.model.data_processing.connect(lambda progress: [self.setEnabled(False), self.ui.progressBar_scraping.setVisible(True), self.ui.progressBar_scraping.setValue(progress)])

        self.model.data_processing.connect(self.data_processing)

    def data_processing(self):
        pass

    def data_updated(self):
        self.setWindowTitle("Movie - " + self.model.movie["Title"] + " (" + self.model.movie["ID"] + ")")

        if self.model.imagePath:
            pixmap = QPixmap(self.model.imagePath)
            pixmap = pixmap.scaledToWidth(self.ui.label_image.parentWidget().width() * 0.25)
            self.ui.label_image.setPixmap(pixmap)
            
        info_content = self.model.movie['Title']
        
        if not pd.isnull(self.model.movie['Release']):
            info_content = info_content + "\nRelease: " + str(int(self.model.movie['Release']))
        
        if not pd.isnull(self.model.movie['AvgRating']):
            info_content = info_content + "\nRating:" + str(float(self.model.movie['AvgRating']))

        info_content = info_content + "\nGenres: " + ', '.join(self.model.movie["Genres"])


        self.ui.label_info.setText(info_content)
        self.ui.tableView_cast.setModel(PandasModel(self.model.actors[['Name']]))
        self.ui.progressBar_scraping.setVisible(False)
        self.setEnabled(True)

    @pyqtSlot(QModelIndex)
    def table_cast_double_click(self, index):
        data = self.model.actors.iloc[index.row()]
        self.controller.display_actor(data['ID'])