import sys
import threading
from PyQt5.QtWidgets import QApplication, QWidget

from PyQt5.QtCore import QThread
from PyQt5 import QtCore

from frontend.MainWindow import MainWindow
from frontend.ScrapeWindow import ScrapeWindow

from scraper.scraper import Scraper
from scraper.data_container import DataContainer


from frontend.ActorWindow import ActorWindow

class YourThreadName(QThread):
    progress = QtCore.pyqtSignal(str, int,int)

    def __init__(self):
        QThread.__init__(self)
    def run(self):
        dataContainer = DataContainer()
        dataContainer.load('.\example_database')
        instance = Scraper(dataContainer)  

        s = self.progress
        #instance.synchronize(['https://www.imdb.com/list/ls053501318/'], lambda url, current, totalCount: s.emit(url, current, totalCount))

        #dataContainer.save('.\example_database')

        aw = ActorWindow()
        aw.show()
        imageUrl = dataContainer.getImage(dataContainer.actors.iloc[2]['ID'])
        aw.setDataFrame(dataContainer.actors.iloc[2], [], [], imageUrl)
        sys.exit(app.exec_())

def main():
    app = QApplication(sys.argv)
   
    dataContainer = DataContainer()
    dataContainer.load('.\example_database')
    instance = Scraper(dataContainer)  

    #instance.synchronize(['https://www.imdb.com/list/ls053501318/'], lambda url, current, totalCount: s.emit(url, current, totalCount))

    #dataContainer.save('.\example_database')

    aw = ActorWindow()
    aw.show()
    imageUrl = dataContainer.getImage(dataContainer.actors.iloc[2]['ID'])
    aw.setDataFrame(dataContainer.actors.iloc[2], [], [], imageUrl)
    sys.exit(app.exec_())

def scrape(mw):
    dataContainer = DataContainer()
    dataContainer.initEmpty()
    instance = ImdbScraper(dataContainer)  
    result = instance.scrape(['https://www.imdb.com/list/ls053501318/'], lambda url, current, totalCount: mw.setProgress(current, totalCount))


if __name__ == "__main__":
    main()