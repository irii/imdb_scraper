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
        
        self.ui.tableView_awards.doubleClicked.connect(self.table_awards_double_click)
        self.ui.tableView_movies.doubleClicked.connect(self.table_movies_double_click)

    def data_updated(self):
        if not self.model.actor:
            self.close()
            return

        if self.model.imagePath:
            pixmap = QPixmap(self.model.imagePath)
            pixmap = pixmap.scaled(self.ui.label_image.parentWidget().width(), self.ui.label_image.parentWidget().height(), aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            self.ui.label_image.setPixmap(pixmap)
            

        self.setWindowTitle("Actor - " + self.model.actor["Name"] + " (" + self.model.actor["ID"] + ")")
        self.ui.label_name.setText(self.model.actor["Name"])
        self.ui.label_dateOfBirth.setText(self.model.actor["DateOfBirth"])
        self.ui.label_born_in.setText(self.model.actor["BornIn"])

        self.ui.tableView_awards.setModel(PandasModel(self.model.awards[['Name', 'Year', 'Winner', 'Description', 'Title']]))
        self.ui.tableView_movies.setModel(PandasModel(self.model.movies))
        #self.ui.label_biography.setText(actorDataFrame["Biography"])

        

    @pyqtSlot(QModelIndex)
    def table_awards_double_click(self, index):
        data = self.model.awards.iloc[index.row()]
        self.controller.display_movie(data['ID'])
        
    @pyqtSlot(QModelIndex)
    def table_movies_double_click(self, index):
        data = self.model.movies.iloc[index.row()]
        self.controller.display_movie(data['ID'])