#!/usr/bin/python3

import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QPushButton, QVBoxLayout


class OwenWindow(QWidget):
    ''' Основное окно
    '''
    def __init__(self):
        super().__init__()
        self.setup_main_win()

    def move_to_center(self):
        win_query_ = self.frameGeometry()
        center_point_ = QDesktopWidget().availableGeometry().center()
        print(center_point_)
        win_query_.moveCenter(center_point_)
        print(win_query_)
        self.move(win_query_.topLeft())

    def setup_main_win(self):
        self.butt_widget = QGroupBox('Button Group')
        self.butt_layout = QHBoxLayout()
        self.butt_layout.addWidget(QPushButton('Start'))
        self.butt_layout.addWidget(QPushButton('Exit'))
        self.butt_layout.setObjectName('ButtonLayout')
        self.setWindowTitle('OWEN')
        self.setWindowIcon(QIcon('owenicon.svg'))
        self.resize(600, 300)
        self.move_to_center()
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(QPushButton('Exit'))
        self.main_layout.addWidget(self.butt_widget)
        self.setLayout(self.main_layout)


if __name__ == '__main__':
    app_ = QApplication([])
    main_window_ = OwenWindow()
    main_window_.show()
    sys.exit(app_.exec_())

##########################################################################