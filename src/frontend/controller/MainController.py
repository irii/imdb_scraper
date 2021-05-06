from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

from data.data_container import DataContainer

from frontend.controller.AboutController import AboutController
from frontend.view.AboutWindow import AboutWindow

from frontend.controller.ActorController import ActorController
from frontend.view.ActorWindow import ActorWindow
from frontend.model.ActorModel import ActorModel

from frontend.controller.ScrapeController import ScrapeController
from frontend.view.ScrapeDialog import ScrapeDialog
from frontend.model.ScrapeModel import ScrapeModel

from frontend.model.MainModel import MainModel

class MainController(QObject):
    _child_view_sessions = {}
    _dataContainer = DataContainer()

    _current_database_folder: str

    def __init__(self, model: MainModel):
        super().__init__()
        self.model = model

    def loadDatabase(self, folder):
        self._current_database_folder = folder
        self._dataContainer.load(folder)
        self.model.setData(self._dataContainer.actors, self._dataContainer.movies, self._dataContainer.lists)

    def saveDatabase(self, folder=None):
        self._dataContainer.save(folder or self._current_database_folder)


    def change_selected_item(self, content_type, identifier):
        self.model.set_selected_item(content_type, identifier)

    def _get_or_register_view(self, id, factory):
        if id not in self._child_view_sessions.keys():
            view = factory()
            view.closed.connect(lambda: self._child_view_sessions.pop(id, None))
            self._child_view_sessions[id] = view       

        return self._child_view_sessions[id]

    def _create_scrape_view(self):
        model = ScrapeModel()
        ctrl = ScrapeController(self._dataContainer, model, self.scrape_finished)
        w = ScrapeDialog(model, ctrl)
        return w

    def display_scrape(self):
        if not self._dataContainer.database_loaded:
            return False

        view = self._get_or_register_view('scrape_view', self._create_scrape_view)
        view.show()
        return True

    def _create_about_view(self):
        ctrl = AboutController()
        w = AboutWindow(ctrl)
        return w

    def scrape_finished(self):
        self.model.setData(self._dataContainer.actors, self._dataContainer.movies, self._dataContainer.lists)

    def display_about(self):
        view = self._get_or_register_view('about_view', self._create_about_view)
        view.show()

    def _create_actor_view(self, actorId):
        model = ActorModel()
        ctrl = ActorController(model, actorId, self._dataContainer, None)
        w = ActorWindow(model, ctrl)

        ctrl.setActor(actorId)

        return w

    def display_actor(self, actorId):
        view = self._get_or_register_view('actor_' + actorId, lambda: self._create_actor_view(actorId))
        view.show()