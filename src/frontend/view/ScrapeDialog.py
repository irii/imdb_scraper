import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QDialog

from scraper.scraper import TYPE_PROGRESS_DOWNLOADING_IMAGES, TYPE_PROGRESS_SCRAPING
from .generated.Ui_ScrapeDialog import Ui_ScrapeDialog

from frontend.model.ScrapeModel import ScrapeModel
from frontend.controller.ScrapeController import ScrapeController

from frontend.BaseWindow import BaseDialog


class ScrapeDialog(BaseDialog):
    """Scrape Dialog - Qt Window View
    """
    can_close = True

    def setCanClose(self, canClose: bool):
        """Set's the can_close field, which determines if the window can be closed.

        Args:
            canClose (bool): Can be closed true/false
        """

        self.can_close = canClose

    def __init__(self, model: ScrapeModel, ctrl: ScrapeController):
        """Constructor

        Args:
            model (ScrapeModel): A scrape model instance
            ctrl (ScrapeController): A scrape controller instance
        """
        super().__init__()
        self.ui = Ui_ScrapeDialog()
        self.ui.setupUi(self)

        self.model = model
        self.controller = ctrl

        self.ui.pushButton_begin.clicked.connect(lambda: self.controller.startOrAbortScraping(
            self.ui.spinBox_max_scrape_depth.value(),
            self.ui.plainTextEdit.toPlainText().split(sep='\n')
            )
        )

        self.model.progress_changed.connect(self.setProgress)
        self.model.started.connect(lambda: [
            self.ui.pushButton_begin.setText("Abort"),
            self.ui.plainTextEdit.setEnabled(False),
            self.ui.spinBox_max_scrape_depth.setEnabled(False),
            self.setCanClose(False)
        ])

        self.model.finished.connect(lambda: [
            self.ui.pushButton_begin.setText("Start"),
            self.ui.plainTextEdit.setEnabled(True),
            self.ui.spinBox_max_scrape_depth.setEnabled(True),
            self.setCanClose(True)
        ])

    def closeEvent(self, event):
        if self.can_close:
            event.accept()
        else:
            event.ignore()

    @QtCore.pyqtSlot(str, str, int, int)
    def setProgress(self, type: str, link: str, value: int, max: int):
        """Get's triggered when the scraper notifies a new progress value.

        Args:
            type ([type]): [description]
            link ([type]): [description]
            value ([type]): [description]
            max ([type]): [description]
        """
        text = "Step 1/2 (Scraping pages): "
        if type == TYPE_PROGRESS_DOWNLOADING_IMAGES:
            text = "Step 2/2 (Downloading images): "

        self.ui.label_progress.setText(text + link)
        self.ui.progressBar.setValue(value / max * 100)
