#!/usr/bin/python3

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data
    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
    def rowCount(self, index):
        return len(self._data)
    def columnCount(self, index):
        return len(self._data[0])

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.table = QtWidgets.QTableView()
        data = [
            [4,'One Two',2,2.71828],
            [1,'3,14',0,'state'],
            [3,'Проверка',0,'report'],
            [3,3,u'Трали-вали', 0.34],
            ['',8,9,'ffas']
            ]
        self.model = TableModel(data)
        self.table.setModel(self.model)
        self.setCentralWidget(self.table)

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()

##########################################################################