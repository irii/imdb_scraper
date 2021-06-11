from PyQt5.QtCore import Qt, QAbstractTableModel

import pandas as pd
import numpy as np

_INT_TYPES = [pd.Int8Dtype, pd.Int16Dtype, pd.Int32Dtype, pd.Int64Dtype, pd.Int64Index, np.int0, np.intc, np.int8, np.int16, np.int32, np.uint, np.uint0, np.uint16, np.uint32, np.uint64, np.uintc, np.uintp]
_FLOAT_TYPES = [pd.Float64Index, np.float64, np.float32, np.float16, np.float_]

class PandasModel(QAbstractTableModel):
    """Pandas to Table model adapter
    This class provides a table view with requierd informations.

    Args:
        QAbstractTableModel ([type]): [description]
    """
    def __init__(self, data: pd.DataFrame, parent=None, displayIndex: bool = True):
        """Constructor

        Args:
            data (pd.DataFrame): [description]
            parent (object, optional): Parent instance. Defaults to None.
            displayIndex (bool, optional): Display index. Defaults to True.
        """
        QAbstractTableModel.__init__(self, parent)
        self._data = data
        self._displayIndex = displayIndex

    def updateDataFrame(self, df: pd.DataFrame, displayIndex: bool = True):
        """Replaces the current dataframe instance and notifies the bound ui for changes.

        Args:
            df (pd.DataFrame): New data frame
            displayIndex (bool, optional): Dispaly index. Defaults to True.
        """
        self.layoutAboutToBeChanged.emit()
        self._displayIndex = displayIndex
        self._data = df.reset_index(drop=True)        
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        """Returns the current row count

        Args:
            parent (object, optional): Parent instance. Defaults to None.

        Returns:
            int: Row count
        """
        return len(self._data.values)

    def columnCount(self, parent=None):
        """Returns the current column count

        Args:
            parent (object, optional): Parent instance. Defaults to None.

        Returns:
            int: Column count
        """
        return self._data.columns.size

    def data(self, index, role=Qt.DisplayRole):
        """Returns the for the requested row and column the value.

        Args:
            index (ModelIndex): Provides requested row and column
            role ([type], optional): Qt display role. Defaults to Qt.DisplayRole.

        Returns:
            any: The row/column value.
        """
        if index.isValid():
            if role == Qt.DisplayRole:
                ctype = self._data[self._data.columns[index.column()]].dtype
                value = self._data.iloc[index.row()][index.column()]
                return self._getValue(value, ctype)
        
        return None

    def _getValue(self, value, columnType):
        """Converts the value into a matching type based on the pandas type.

        Args:
            value (str): Value
            columnType (object): Pandas Column type

        Returns:
            any: The converted rturn type
        """
        if columnType == object:
            return value
        elif columnType in _INT_TYPES:
            return int(value)
        elif columnType in _FLOAT_TYPES:
            return float(value)
        elif columnType.name == 'bool':
            return bool(value)

        return str(value)

    def headerData(self, section, orientation, role):
        """Returns the header information from the pandas data frame.

        Args:
            section (int): Header index
            orientation (any): Vertical/Horizontal
            role (any): Dispaly type.

        Returns:
            [type]: [description]
        """
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical and self._displayIndex:
                return str(self._data.index[section])