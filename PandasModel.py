# from https://github.com/Axel-Erfurt/QTableView_pandas/blob/master/QTableView_pandas.py
import sys
import csv, codecs 
import os
import pandas as pd
from PyQt5.QtCore import Qt, QDir, QItemSelectionModel, QAbstractTableModel, QModelIndex, QVariant, QSize, QSettings
from PyQt5.QtWidgets import (QMainWindow, QTableView, QApplication, QToolBar, QLineEdit, QComboBox, QDialog, 
                                                            QAction, QMenu, QFileDialog, QAbstractItemView, QMessageBox, QWidget)
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QCursor, QIcon, QKeySequence, QTextDocument, QTextCursor, QTextTableFormat
from PyQt5 import QtPrintSupport

class PandasModel(QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), litoy=None, parent=None):
        QAbstractTableModel.__init__(self, parent=None)
        self.setChanged = False
        self.dataChanged.connect(self.setModified)

        self._df = df
        self.litoy = litoy

    def setModified(self):
        self.setChanged = True
        print("Changed something in PandasModel.")
        self.litoy.save_to_file(self.litoy.df)
        self.litoy._reload_df()
        print("Saved and reloaded LiTOY db.")

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            try:
                return self._df.columns.tolist()[section]
            except (IndexError, ):
                return QVariant()
        elif orientation == Qt.Vertical:
            try:
                return self._df.index.tolist()[section]
            except (IndexError, ):
                return QVariant()

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if (role == Qt.EditRole):
                return self._df.values[index.row()][index.column()]
            elif (role == Qt.DisplayRole):
                return self._df.values[index.row()][index.column()]
        return None

    def setData(self, index, new_value, role):
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        old_value = self._df.loc[row, col]
        self._df.at[row, col] = new_value
        self.litoy.df.loc[row, col] = new_value
        self.litoy.gui_log(f'Edited entry with ID {row}, field "{col}", {old_value} => {new_value}',
                         False)
        self.dataChanged.emit(index, index)
        return True

    def rowCount(self, parent=QModelIndex()): 
        return len(self._df.index)

    def columnCount(self, parent=QModelIndex()): 
        return len(self._df.columns)

    def sort(self, column, order):
        colname = self._df.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
#        self._df.sort_values(colname, ascending= order == Qt.AscendingOrder, inplace=True)
#        self._df.reset_index(inplace=True, drop=True)
        print("Stopped inplace commands!")
        self.layoutChanged.emit()
