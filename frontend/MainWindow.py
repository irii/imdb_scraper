import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QDialog
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QListView
from PyQt5.QtWidgets import QTableView


from .generated.Ui_MainWindow import Ui_MainWindow
from .AboutWindow import AboutWindow

class MainWindow(QMainWindow):
    aboutWindow: AboutWindow = None

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.connectUi()
      
    def connectUi(self):
        self.ui.actionExit.triggered.connect(lambda:self.close())
        self.ui.actionAbout.triggered.connect(self.displayAbout)

    def displayAbout(self):
        if(self.aboutWindow == None):
            self.aboutWindow = AboutWindow()

        self.aboutWindow.show()        