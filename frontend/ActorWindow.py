import sys
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QDialog
from .generated.Ui_ActorWindow import Ui_ActorWindow
import urllib

class ActorWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ActorWindow()
        self.ui.setupUi(self)

    def setDataFrame(self, actorDataFrame, awards, movies, imageUrl=None):
        if(imageUrl):
            pixmap = QPixmap(imageUrl)            
            self.ui.label_image.setPixmap(pixmap)
            self.ui.label_image.resize(pixmap.width(), pixmap.height())

        self.setWindowTitle("Actor - " + actorDataFrame["Name"] + "(" + actorDataFrame["ID"] + ")")
        self.ui.label_name.setText(actorDataFrame["Name"])
        self.ui.label_dateOfBirth.setText(actorDataFrame["DateOfBirth"])
        self.ui.label_born_in.setText(actorDataFrame["BornIn"])
        #self.ui.label_biography.setText(actorDataFrame["Biography"])

        