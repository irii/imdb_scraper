import sys
import threading
from PyQt5.QtWidgets import QApplication, QWidget

from PyQt5.QtCore import QThread
from PyQt5 import QtCore

from frontend.controller.ScrapeController import ScrapeController
from frontend.model.ScrapeModel import ScrapeModel
from frontend.view.ScrapeDialog import ScrapeDialog

from frontend.view.MainWindow import MainWindow
from frontend.controller.MainController import MainController
from frontend.model.MainModel import MainModel

from scraper.scraper import Scraper
from data.data_container import DataContainer

from frontend.WindowManager import WindowManager

from frontend.controller.AboutController import AboutController
from frontend.view.AboutWindow import AboutWindow


from frontend.controller.ActorController import ActorController
from frontend.view.ActorWindow import ActorWindow
from frontend.model.ActorModel import ActorModel

from frontend.controller.MovieController import MovieController
from frontend.view.MovieWindow import MovieWindow
from frontend.model.MovieModel import MovieModel

from scraper.scraper import Scraper

def scrapeViewFactory(windowManager, dataContainer, scraper, *args):
    model = ScrapeModel()
    ctrl = ScrapeController(dataContainer, model, args[0])
    w = ScrapeDialog(model, ctrl)
    return w

def actorViewFactory(windowManager, dataContainer, scraper, *args):
    model = ActorModel()
    ctrl = ActorController(model, dataContainer, windowManager, scraper)
    view = ActorWindow(model, ctrl)

    ctrl.set_actor(args[0])
    return view

def movieViewFactory(windowManager, dataContainer, scraper, *args):
    model = MovieModel()
    ctrl = MovieController(model, dataContainer, windowManager, scraper)
    view = MovieWindow(model, ctrl)

    ctrl.set_movie(args[0])
    return view

# Decouple view logic from controller logic
def configureWindowManager(windowManager: WindowManager):
    # Register View factories which can be called by an controller instance
    windowManager.register_view('ABOUT', lambda *a: 'ABOUT', lambda *a: AboutWindow(AboutController()))
    windowManager.register_view('ACTOR', lambda *a: 'ACTOR-' + a[0], actorViewFactory)
    windowManager.register_view('MOVIE', lambda *a: 'MOVIE-' + str(a[0]), movieViewFactory)
    windowManager.register_view('SCRAPE', lambda *a: 'SCRAPE', scrapeViewFactory)

def main():
    app = QApplication(sys.argv)
    # Default Arguments for every factory function
    # Currently: WindowManager, DataContainer
       
    dataContainer = DataContainer()
    scraper = Scraper(dataContainer)


    windowManager = WindowManager(dataContainer, scraper)
    configureWindowManager(windowManager)

    #dataContainer.load("./test")
    #s = Scraper(dataContainer)
    #s.synchronize(['https://www.imdb.com/list/ls053501318/'])
    #dataContainer.save()


    mainModel = MainModel()
    mainController = MainController(windowManager, mainModel, dataContainer)

    mainWindow = MainWindow(mainModel, mainController)
    mainWindow.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()