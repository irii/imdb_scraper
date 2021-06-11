import sys
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QModelIndex
from PyQt5.QtGui import QPixmap
import numpy as np
from .generated.Ui_ActorWindow import Ui_ActorWindow

from frontend.model.ActorModel import ActorModel
from frontend.controller.ActorController import ActorController
from frontend.BaseWindow import BaseChildWindow

from frontend.PandasTable import PandasModel

class ActorWindow(BaseChildWindow):
    """Actor Window - QT Window View
    """
    current_pixmap: QPixmap = None


    def __init__(self, model: ActorModel, ctrl: ActorController):
        """Constructor
        Args:
            model (ActorModel): A actor model instance
            ctrl (ActorController): A actor controller instance
        """
        super().__init__()

        self.ui = Ui_ActorWindow()
        self.ui.setupUi(self)

        self.model = model
        self.controller = ctrl

        self.model.data_updated.connect(self.data_updated)
        self.model.data_processing.connect(lambda progress: [self.setEnabled(False), self.ui.progressBar_scraping.setVisible(True), self.ui.progressBar_scraping.setValue(progress)])
        
        self.ui.tableView_awards.doubleClicked.connect(self.table_awards_double_click)
        self.ui.tableView_movies.doubleClicked.connect(self.table_movies_double_click)
        self.ui.checkBox_top_five.stateChanged.connect(self.checkbox_top_five_changed)

    def checkbox_top_five_changed(self, *args):
        """Get's triggered when the top five checkbox has changed and updates the ui data
        """
        self.data_updated()

    def resizeEvent(self, event):
        """Get's triggered when the window size changes and scales the actor image
        """

        if self.current_pixmap:
            self.ui.label_image.setPixmap(self.current_pixmap.scaled(self.ui.label_image.size(), aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio, transformMode=QtCore.Qt.TransformationMode.SmoothTransformation))

    def data_updated(self):
        """Updates all ui elements with the current model data
        """

        if not self.model.actor:
            self.close()
            return

        if self.model.imagePath:
            self.current_pixmap = QPixmap(self.model.imagePath)
            self.ui.label_image.setPixmap(self.current_pixmap.scaled(self.ui.label_image.size(), aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio, transformMode=QtCore.Qt.TransformationMode.SmoothTransformation))

        self.setWindowTitle("Actor - " + self.model.actor["Name"] + " (" + self.model.actor["ID"] + ")")

        info_content_items = [
            "Name: " + self.model.actor['Name']
        ]

        if self.model.actor['Nickname'] is not None and len(self.model.actor['Nickname']) > 0:
            info_content_items.append("Nickname: " + self.model.actor['Nickname'])
        
        if self.model.actor['DateOfBirth'] is not None and len(self.model.actor['DateOfBirth']) > 0:
            info_content_items.append("Date of birth: " + self.model.actor['DateOfBirth'])

        if self.model.actor['BornIn'] is not None and len(self.model.actor['BornIn']) > 0:
            info_content_items.append("Born in: " + self.model.actor['BornIn'])
        
        if self.model.actor['Height'] is not None and self.model.actor['Height'] != np.nan:
            info_content_items.append("Height: " + str(self.model.actor['Height']))

        if self.model.actor['OverallRating'] is not None and self.model.actor['OverallRating'] != np.nan:
            info_content_items.append("Overall Rating: " + str(self.model.actor['OverallRating']))
        

        self.ui.label_info.setText('\n'.join(info_content_items))
    
        self.ui.tableView_awards.setModel(PandasModel(self.model.awards, displayIndex=False))

        movies = self.model.movies
        if self.ui.checkBox_top_five.isChecked():
            movies = movies.head(5)

        self.ui.tableView_movies.setModel(PandasModel(movies))
        self.ui.tableView_genres.setModel(PandasModel(self.model.genres, displayIndex=False))
        self.ui.tableView_rating_per_year.setModel(PandasModel(self.model.avgRatingPerYear, displayIndex=False))
        self.ui.label_biography.setText(self.model.actor["Biography"])

        self.ui.progressBar_scraping.setVisible(False)
        self.setEnabled(True)

        

    @pyqtSlot(QModelIndex)
    def table_awards_double_click(self, index):
        """Get's called when an double click on an award happens. Opens a new actor if available.
        """
        data = self.model.awards.iloc[index.row()]
        self.controller.display_movie(data['ID'])
        
    @pyqtSlot(QModelIndex)
    def table_movies_double_click(self, index):
        """Get's called when an double click on an movie happens. Opens a new movie if available.
        """
        data = self.model.movies.iloc[index.row()]
        self.controller.display_movie(data['MovieID'])