from PyQt5.QtCore import Qt, QVariant, QAbstractTableModel

import pandas as pd

_INT_TYPES = [pd.Int8Dtype, pd.Int16Dtype, pd.Int32Dtype, pd.Int64Dtype, pd.Int64Index]
_FLOAT_TYPES = [pd.Float64Index]

class PandasModel(QAbstractTableModel):
    def __init__(self, data, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                ctype = self._data[self._data.columns[index.column()]].dtype
                value = self._data.iloc[index.row()][index.column()]
                return self._getValue(value, ctype)
        
        return None

    def _getValue(self, value, columnType):
        if columnType == object:
            return value
        elif columnType in _INT_TYPES:
            return int(value)
        elif columnType in _FLOAT_TYPES:
            return float(value)

        return str(value)

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])