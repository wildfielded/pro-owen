#!/usr/bin/python3

import sys

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication,
                             QWidget, QDesktopWidget, QPushButton,
                             QTableView, QHBoxLayout, QVBoxLayout)

#####=====----- Классы -----=====#####

class OwenWindow(QWidget):
    ''' Основное окно
    '''
    def __init__(self):
        super().__init__()
        self.setup_main_win()

    def setup_geom(self):
        ''' Задаёт размер и центрирует окно
        '''
        self.resize(800, 800)
        win_geom_ = self.frameGeometry()
        win_center_ = QDesktopWidget().availableGeometry().center()
        win_geom_.moveCenter(win_center_)
        self.move(win_geom_.topLeft())

    def setup_main_win(self):
        self.setWindowTitle('OWEN')
        self.setWindowIcon(QIcon('icon-owen.ico'))
        self.setup_geom()

        button_exit_ = QPushButton(QIcon('icon-exit.svg'), u'Выход')
        button_exit_.setToolTip(u'Выход из программы')
        button_exit_.clicked.connect(QCoreApplication.instance().quit)

        toolbar_layout_ = QHBoxLayout()
        toolbar_layout_.addWidget(button_exit_)

        datafield_layout_ = QTableView()

        main_layout_ = QVBoxLayout()
        main_layout_.addLayout(toolbar_layout_)
        main_layout_.addWidget(datafield_layout_)
        self.setLayout(main_layout_)


#####=====----- Функции -----=====#####

#####=====----- Собственно, сама программа -----=====#####

if __name__ == '__main__':
    app_ = QApplication([])
    prog_window_ = OwenWindow()
    prog_window_.show()
    sys.exit(app_.exec_())

#####=====----- THE END -----=====########################################