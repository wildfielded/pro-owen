#!/usr/bin/python3

import sys
from os.path import abspath
from time import sleep
from configparser import ConfigParser, ExtendedInterpolation

from PyQt5.QtCore import QCoreApplication, QThread, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDesktopWidget, QWidget, QPushButton
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView

import ConfiGranit as c_
import HTMLCreator as h_


#####=====----- Константы -----=====#####

INI_FILE = 'owen.ini'
CFG = ConfigParser(interpolation=ExtendedInterpolation())


#####=====----- Классы -----=====#####

class BgCreator(QThread):
    ''' Фоновое периодическое обновление HTML-файла для показа в главном окне
    '''
    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            h_.create(CFG)
            sleep(25)


class OwenWindow(QWidget):
    ''' Основное окно
    '''
    def __init__(self):
        super().__init__()
        self.setup_main_win()
        self.html = BgCreator()
        self.html.start()

    def move_to_center(self):
        ''' Центрирует окно программы на дисплее
        '''
        win_geom_ = self.frameGeometry()
        win_center_ = QDesktopWidget().availableGeometry().center()
        win_geom_.moveCenter(win_center_)
        self.move(win_geom_.topLeft())

    def tune_to(self, server):
        ''' Для переключения по кнопкам URL в окне "браузера"
        '''
        if server == 0:
            self.HtmlWidget.load(QUrl().fromLocalFile(abspath('index.html')))
        if server == 1:
            self.HtmlWidget.load(QUrl(CFG.get('NETWORK', 'srv1_url')))
        if server == 2:
            self.HtmlWidget.load(QUrl(CFG.get('NETWORK', 'srv2_url')))

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
        self.HtmlWidget.load(QUrl().fromLocalFile(abspath('index.html')))

        main_layout = QVBoxLayout()
        main_layout.addLayout(ToolbarLayout)
        main_layout.addWidget(self.HtmlWidget)
        self.setLayout(main_layout)


#####=====----- Функции -----=====#####

def ini_setup():
    ''' Считывает настройки из INI-файла и парсит в объект CFG. Если не удаётся
        (неважно, по какой причине), то считывает дефолтные настройки из залитого
        гранитом словаря в configranit, парсит в CFG и заодно создаёт INI-файл.
    '''
    try:
        with open(INI_FILE, 'r', encoding='utf-8') as f_:
            CFG.read_file(f_)
    except:
        CFG.read_dict(c_.DEFAULT_CFG)
        with open(INI_FILE, 'w', encoding='utf-8') as f_:
            CFG.write(f_)


#####=====----- Собственно, сама программа -----=====#####

if __name__ == '__main__':
    ini_setup()
    app_ = QApplication([])
    main_window_ = OwenWindow()
    main_window_.show()
    sys.exit(app_.exec_())

#####=====----- THE END -----=====########################################