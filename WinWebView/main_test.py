#!/usr/bin/python3

from os.path import abspath
import sys
import time

from PyQt5.QtCore import (QCoreApplication, QThread, QUrl)
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import (QDesktopWidget, QWidget, QPushButton)
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout)
from PyQt5.QtWebEngineWidgets import QWebEngineView

import configowen as c_


class BGecho(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            print('Test')
            time.sleep(5)


class OwenWindow(QWidget):
    ''' Основное окно
    '''
    def __init__(self):
        super().__init__()
        self.setup_main_win()
        self.t_ = BGecho()
        self.t_.start()

    def move_to_center(self):
        win_query_ = self.frameGeometry()
        center_point_ = QDesktopWidget().availableGeometry().center()
        win_query_.moveCenter(center_point_)
        self.move(win_query_.topLeft())

    def tune_to(self, server):
        if server == 0:
            self.HtmlWidget.load(QUrl().fromLocalFile(abspath('index.html')))
        if server == 1:
            self.HtmlWidget.load(QUrl(c_.URL_SRV1))
        if server == 2:
            self.HtmlWidget.load(QUrl(c_.URL_SRV2))

    def setup_main_win(self):
        self.setWindowTitle('OWEN')
        self.setWindowIcon(QIcon('icon-owen.ico'))
        self.resize(700, 800)
        self.move_to_center()

        button_conf_ = QPushButton(QIcon('icon-config.svg'), u'Настройки')
        button_conf_.setToolTip(u'Настройки программы')
        button_armd_ = QPushButton(QIcon('icon-pc.svg'), u'АРМ')
        button_armd_.setToolTip(u'Работа без вэб-сервера')
        button_armd_.clicked.connect(lambda: self.tune_to(0))
        button_srv1_ = QPushButton(QIcon('icon-downld.svg'), u'Сервер-1')
        button_srv1_.setToolTip(u'Соединение с основным вэб-сервером')
        button_srv1_.clicked.connect(lambda: self.tune_to(1))
        button_srv2_ = QPushButton(QIcon('icon-downld.svg'), u'Сервер-2')
        button_srv2_.setToolTip(u'Соединение с резервным вэб-сервером')
        button_srv2_.clicked.connect(lambda: self.tune_to(2))
        button_exit_ = QPushButton(QIcon('icon-exit.svg'), u'Выход')
        button_exit_.setToolTip(u'Выход из программы')
        button_exit_.clicked.connect(QCoreApplication.instance().quit)

        ToolbarLayout = QHBoxLayout()
        ToolbarLayout.addWidget(button_conf_)
        ToolbarLayout.addWidget(button_armd_)
        ToolbarLayout.addWidget(button_srv1_)
        ToolbarLayout.addWidget(button_srv2_)
        ToolbarLayout.addWidget(button_exit_)

        self.HtmlWidget = QWebEngineView()
        self.HtmlWidget.load(QUrl('http://10.30.40.122/owen/'))

        main_layout = QVBoxLayout()
        main_layout.addLayout(ToolbarLayout)
        main_layout.addWidget(self.HtmlWidget)
        self.setLayout(main_layout)


if __name__ == '__main__':
    app_ = QApplication([])
    main_window_ = OwenWindow()
    main_window_.show()
    sys.exit(app_.exec_())

#####=====----- THE END -----=====########################################