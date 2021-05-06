import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QDialog
from .generated.Ui_ScrapeDialog import Ui_ScrapeDialog

from frontend.model.ScrapeModel import ScrapeModel
from frontend.controller.ScrapeController import ScrapeController

from frontend.BaseWindow import BaseDialog


class ScrapeDialog(BaseDialog):
    def __init__(self, model: ScrapeModel, ctrl: ScrapeController):
        super().__init__()
        self.ui = Ui_ScrapeDialog()
        self.ui.setupUi(self)

        self.model = model
        self.controller = ctrl

        self.ui.pushButton_begin.clicked.connect(lambda: self.controller.startScraping(
            not self.ui.checkBox_merge.isChecked(),
            self.ui.plainTextEdit.toPlainText().split(sep='\n'))
        )

        self.model.progress_changed.connect(self.setProgress)
        self.model.started.connect(lambda: [
            self.ui.pushButton_begin.setEnabled(False),
            self.ui.plainTextEdit.setEnabled(False)
        ])

        self.model.finished.connect(lambda: [
            self.ui.pushButton_begin.setEnabled(True),
            self.ui.plainTextEdit.setEnabled(True)
        ])

    @QtCore.pyqtSlot(int, int)
    def setProgress(self, value, max):
        self.ui.progressBar.setValue(value)
        self.ui.progressBar.setMaximum(max)
        self.ui.label_progress.setText(str(value) + ' / ' + str(max))
