import sys
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QModelIndex
from PyQt5.QtGui import QPixmap
from .generated.Ui_ActorWindow import Ui_ActorWindow

from frontend.model.ActorModel import ActorModel
from frontend.controller.ActorController import ActorController
from frontend.BaseWindow import BaseChildWindow

from frontend.PandasTable import PandasModel

class ActorWindow(BaseChildWindow):
    def __init__(self, model: ActorModel, ctrl: ActorController):
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
        self.data_updated()

    def data_updated(self):
        if not self.model.actor:
            self.close()
            return

        if self.model.imagePath:
            pixmap = QPixmap(self.model.imagePath)
            pixmap = pixmap.scaledToWidth(self.ui.label_image.parentWidget().width() * 0.25)
            self.ui.label_image.setPixmap(pixmap)
            

        self.setWindowTitle("Actor - " + self.model.actor["Name"] + " (" + self.model.actor["ID"] + ")")

        info_content = self.model.actor['Name'] + "\nDate of birth: " + str(self.model.actor['DateOfBirth']) + "\nBorn in: " + str(self.model.actor['BornIn'])

        self.ui.label_info.setText(info_content)
    
        self.ui.tableView_awards.setModel(PandasModel(self.model.awards[['Name', 'Year', 'Winner', 'Description', 'Title']]))

        movies = self.model.movies
        if self.ui.checkBox_top_five.isChecked():
            movies = movies.head(5)

        self.ui.tableView_movies.setModel(PandasModel(movies))
        self.ui.tableView_genres.setModel(PandasModel(self.model.genres))
        self.ui.label_biography.setText(self.model.actor["Biography"])

        self.ui.progressBar_scraping.setVisible(False)
        self.setEnabled(True)

        

    @pyqtSlot(QModelIndex)
    def table_awards_double_click(self, index):
        data = self.model.awards.iloc[index.row()]
        self.controller.display_movie(data['ID'])
        
    @pyqtSlot(QModelIndex)
    def table_movies_double_click(self, index):
        data = self.model.movies.iloc[index.row()]
        self.controller.display_movie(data['MovieID'])