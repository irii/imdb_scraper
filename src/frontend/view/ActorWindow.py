import sys
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QDialog
from .generated.Ui_ActorWindow import Ui_ActorWindow
import urllib

from frontend.model.ActorModel import ActorModel
from frontend.controller.ActorController import ActorController
from frontend.BaseWindow import BaseChildWindow

class ActorWindow(BaseChildWindow):
    def __init__(self, model: ActorModel, ctrl: ActorController):
        super().__init__()

        self.ui = Ui_ActorWindow()
        self.ui.setupUi(self)

        self.model = model
        self.controller = ctrl

        self.model.data_updated.connect(self.data_updated)

    def data_updated(self):
        if not self.model.actor:
            self.close()
            return

        if(self.model.imagePath):
            pixmap = QPixmap(self.model.imagePath)            
            self.ui.label_image.setPixmap(pixmap)
            self.ui.label_image.resize(pixmap.width(), pixmap.height())

        self.setWindowTitle("Actor - " + self.model.actor["Name"] + "(" + self.model.actor["ID"] + ")")
        self.ui.label_name.setText(self.model.actor["Name"])
        self.ui.label_dateOfBirth.setText(self.model.actor["DateOfBirth"])
        self.ui.label_born_in.setText(self.model.actor["BornIn"])
        #self.ui.label_biography.setText(actorDataFrame["Biography"])

        