from PyQt5.QtCore import QModelIndex, pyqtSlot, QVariant
from PyQt5.QtWidgets import QLabel, QMainWindow, QFileDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import pandas as pd


from .generated.Ui_MainWindow import Ui_MainWindow
from .AboutWindow import AboutWindow

from frontend.controller.MainController import MainController
from frontend.model.MainModel import MainModel, CONTENT_TYPE_MOVIE, CONTENT_TYPE_ACTOR, CONTENT_TYPE_LIST

from frontend.PandasTable import PandasModel

class MainWindow(QMainWindow):
    """The Main-Ui - QT MainWindow view
    """

    aboutWindow: AboutWindow = None
    ui: Ui_MainWindow

    combobox_model = QStandardItemModel()
    data_model = PandasModel(pd.DataFrame([]))

    statusBarWidget = None

    def closeEvent(self, event):
        """Get's called when the is getting closed. This method closes all child windows to execute the application
        """
        event.accept()
        self.controller.closeAll()

    def __init__(self, model: MainModel, controller: MainController):
        """Constructor

        Args:
            model (MainModel): A main model instance
            controller (MainController): A main controller instance
        """
        super().__init__()

        self.model = model
        self.controller = controller

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)        
        self.connectUi()

        self.statusBarWidget = QLabel(text="Database not loaded")
        self.statusBar().addWidget(self.statusBarWidget)

        self.database_updated() # Initial view state initialization

        self.model.database_updated.connect(self.database_updated)
        self.model.selection_changed.connect(self.selection_changed)

      
    def connectUi(self):
        """Connects all ui elements with a function
        """

        self.ui.actionExit.triggered.connect(lambda:self.close())
        self.ui.actionAbout.triggered.connect(self.displayAbout)        
        self.ui.actionOpen_Database.triggered.connect(self.openOrNewDatabase)
        self.ui.actionSave_Database.triggered.connect(self.saveDatabase)

        self.ui.pushButton_scrape.clicked.connect(lambda: self.controller.display_scrape())        
        self.ui.comboBox_select_type.currentIndexChanged.connect(self.comboBox_index_changed)
        self.ui.tableView_items.doubleClicked.connect(self.table_double_click)
        self.ui.tableView_items.setModel(self.data_model)

    def comboBox_index_changed(self, index):
        """Get's triggered when the category combobox is changed and updates the selected item.
        Args:
            index (object): Current index
        """
        if index >= 0 and index < len(self.model.selection_items):
            item = self.model.selection_items[index]
            self.controller.change_selected_item(item[0], item[2])
        else:
            self.controller.change_selected_item(None, None)

    def displayAbout(self):
        """Display the about window
        """
        self.controller.display_about()   

    def openOrNewDatabase(self):
        """Get's called when the menu action OpenDatabase is triggerd.
        This method displays a folder dialog and loads the database if selected.
        """
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

        if not file:
            return

        self.controller.loadDatabase(file)
        
    def saveDatabase(self):
        """Get's called when the menu action SaveDatabase is triggered.
        This method saves the current database.
        """
        self.controller.saveDatabase()

    def selection_changed(self):
        """This method get's called when the MainModel instance notfies a selection change event.
        """
        data = self.model.content
        if data is None:
            self.data_model.updateDataFrame(pd.DataFrame([]))
            return

        self.data_model.updateDataFrame(self.model.content)

    def database_updated(self):
        """This method get's called when the MainModel instance notfies a data change event.
        """

        if self.model.database_loaded:
            self.statusBarWidget.setText('Database loaded')
        else:
            self.statusBarWidget.setText('Database not loaded')

        self.combobox_model.clear()
        for item in self.model.selection_items:
            row = QStandardItem(item[1])
            row.setData(QVariant(item))
            self.combobox_model.appendRow(row)
        
        self.ui.comboBox_select_type.setModel(self.combobox_model)        
        self.ui.pushButton_scrape.setEnabled(self.model.database_loaded)
        self.ui.tableView_items.setEnabled(self.model.database_loaded)
        self.ui.actionSave_Database.setEnabled(self.model.database_loaded)

        
    @pyqtSlot(QModelIndex)
    def table_double_click(self, index):
        """Displays the corresponding window when a double click happens on the table view.

        Args:
            index (object): Selection index
        """
        data = self.model.content.iloc[index.row()]

        if self.model.content_type == CONTENT_TYPE_ACTOR:
            self.controller.display_actor(data['ID'])
            
        elif self.model.content_type == CONTENT_TYPE_MOVIE:
            self.controller.display_movie(data['ID'])

        elif self.model.content_type == CONTENT_TYPE_LIST:
            if data['Type'] == 'Actor':
                self.controller.display_actor(data['ItemId'])
            elif data['Type'] == 'Movie':
                self.controller.display_movie(data['ItemId'])