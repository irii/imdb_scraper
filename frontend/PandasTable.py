from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class PandasModel(QAbstractTableModel):
    def __init__(self, data, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=DisplayRole):
        if index.isValid():
            if role == DisplayRole:
                return QVariant(str(
                    self._data.iloc[index.row()][index.column()]))

        return QVariant()