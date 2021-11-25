#!/usr/bin/python3

import sys

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import (QDesktopWidget, QWidget, QPushButton, QGroupBox)
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout)
from PyQt5.QtWebEngineWidgets import QWebEngineView


class OwenWindow(QWidget):
    ''' Основное окно
    '''
    def __init__(self):
        super().__init__()
        self.setup_main_win()

    def move_to_center(self):
        win_query_ = self.frameGeometry()
        center_point_ = QDesktopWidget().availableGeometry().center()
        win_query_.moveCenter(center_point_)
        self.move(win_query_.topLeft())

    def setup_main_win(self):
        self.setWindowTitle('OWEN')
        self.setWindowIcon(QIcon('icon-owen.ico'))
        self.resize(700, 800)
        #####self.resize(self.sizeHint())
        self.move_to_center()

        ToolbarLayout = QHBoxLayout()
        ToolbarLayout.addWidget(QPushButton(QIcon('icon-config.svg'), u'Настройки'))
        ToolbarLayout.addWidget(QPushButton(QIcon('icon-pc.svg'), u'АРМ'))
        ToolbarLayout.addWidget(QPushButton(QIcon('icon-downld.svg'), u'Сервер-1'))
        ToolbarLayout.addWidget(QPushButton(QIcon('icon-downld.svg'), u'Сервер-2'))
        ToolbarLayout.addWidget(QPushButton(QIcon('icon-exit.svg'), u'Выход'))

        HtmlWidget = QWebEngineView()
        HtmlWidget.load(QUrl('http://10.30.40.122/owen/'))
        WebLayout = QVBoxLayout()
        WebLayout.addWidget(HtmlWidget)

        main_layout = QVBoxLayout()
        main_layout.addLayout(ToolbarLayout)
        #####main_layout.addLayout(WebLayout)
        main_layout.addWidget(HtmlWidget)
        self.setLayout(main_layout)


if __name__ == '__main__':
    app_ = QApplication([])
    main_window_ = OwenWindow()
    main_window_.show()
    sys.exit(app_.exec_())

##########################################################################