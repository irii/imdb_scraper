import sys
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, pyqtSlot, QVariant, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QDialog, QFileDialog
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QListView
from PyQt5.QtWidgets import QTableView


from .generated.Ui_MainWindow import Ui_MainWindow
from .AboutWindow import AboutWindow

from frontend.controller.MainController import MainController
from frontend.model.MainModel import MainModel, CONTENT_TYPE_MOVIE, CONTENT_TYPE_ACTOR, CONTENT_TYPE_LIST

from frontend.PandasTable import PandasModel

class ComboBoxModel(QAbstractItemModel):
    _parent = QModelIndex()

    def __init__(self, list):
        super().__init__(None)
        self._list = list

    def rowCount(self, parent):
        ret = len(self._list)
        return ret

    def columnCount(self, parent):
        return 1

    def index(self, row, column, parent):
        return self.createIndex(row, column)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._list[index.row()][1]
        else:
            return QVariant()

    def parent(self, index):
        return self._parent

class MainWindow(QMainWindow):
    aboutWindow: AboutWindow = None
    ui: Ui_MainWindow()

    combobox_model = ComboBoxModel([])

    def __init__(self, model: MainModel, controller: MainController = None):
        super().__init__()

        self.model = model
        self.controller = controller

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)        
        self.connectUi()

        self.data_updated() # Initial view state initialization
      
    def connectUi(self):
        self.ui.actionExit.triggered.connect(lambda:self.close())
        self.ui.actionAbout.triggered.connect(self.displayAbout)        
        self.ui.actionOpen_Database.triggered.connect(self.openOrNewDatabase)
        self.ui.actionSave_Database.triggered.connect(self.saveDatabase)
        self.ui.actionAbout.triggered.connect(lambda: self.controller.display_scrape())

        self.ui.pushButton_scrape.clicked.connect(lambda: self.controller.display_scrape())        
        self.model.data_updated.connect(self.data_updated)
        self.ui.tableView_items.setModel(self.combobox_model)
        self.ui.comboBox_select_type.currentIndexChanged.connect(self.comboBox_index_changed)
        self.ui.tableView_items.doubleClicked.connect(self.table_double_click)

    def comboBox_index_changed(self, index):
        item = self.model.selection_items[index]
        self.controller.change_selected_item(item[0], item[2])

    def displayAbout(self):
        self.controller.display_about()   

    def openOrNewDatabase(self):
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.controller.loadDatabase(file)
        
    def saveDatabase(self):
        self.controller.saveDatabase()

    def data_updated(self):
        self.combobox_model._list = self.model.selection_items
        self.ui.comboBox_select_type.setModel(self.combobox_model)
        self.ui.pushButton_scrape.setEnabled(self.model.database_loaded)
        self.ui.tableView_items.setEnabled(self.model.database_loaded)

        data = self.model.content
        if data is None:
            self.ui.tableView_items.setModel(None)
            return


        table_model = PandasModel(data)
        self.ui.tableView_items.setModel(table_model)
        
    @pyqtSlot(QModelIndex)
    def table_double_click(self, index):
        itemId = index.data()

        if self.model.content_type == CONTENT_TYPE_ACTOR:
            self.controller.display_actor(itemId)