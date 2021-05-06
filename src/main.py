import sys
import threading
from PyQt5.QtWidgets import QApplication, QWidget

from PyQt5.QtCore import QThread
from PyQt5 import QtCore

from frontend.view.MainWindow import MainWindow
from frontend.controller.MainController import MainController
from frontend.model.MainModel import MainModel

from scraper.scraper import Scraper
from data.data_container import DataContainer

def main():
    app = QApplication(sys.argv)


    mainModel = MainModel()
    mainController = MainController(mainModel)

    mainWindow = MainWindow(mainModel, mainController)
    mainWindow.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()