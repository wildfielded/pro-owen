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

from PyQt5.QtMultimedia import QSound

import ConfiGranit as c_
import HTMLCreator as h_


#####=====----- Фундаментальные константы -----=====#####

INI_FILE = 'owen.ini'
CFG = ConfigParser(interpolation=ExtendedInterpolation())


#####=====----- Классы -----=====#####

class SirenaSound():
    def __init__(self):
        self.sound_file = QSound('sirena.wav')
        self.sound_file.setLoops(3)
    def playsirena(self):
        self.sound_file.play('sirena.wav')

class OwenWindow(QWidget):
    ''' Основное окно
    '''
    def __init__(self):
        super().__init__()
        self.setup_main_win()

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
            self.HtmlWidget.load(QUrl().fromLocalFile(abspath(CFG['FILES']['html_output'])))
        if server == 1:
            self.HtmlWidget.load(QUrl(CFG.get('NETWORK', 'srv1_url')))
        if server == 2:
            self.HtmlWidget.load(QUrl(CFG.get('NETWORK', 'srv2_url')))

    def play_sirena(self):
        sirena = SirenaSound()
        sirena.playsirena()

    def setup_main_win(self):
        self.setWindowTitle('OWEN')
        self.setWindowIcon(QIcon('icon-owen.ico'))
        self.resize(800, 800)
        self.move_to_center()

        button_armd_ = QPushButton(QIcon('icon-pc.svg'), u'Сирена')
        button_armd_.setToolTip(u'Орать сиреной')
        button_armd_.clicked.connect(lambda: self.play_sirena())
        button_exit_ = QPushButton(QIcon('icon-exit.svg'), u'Выход')
        button_exit_.setToolTip(u'Выход из программы')
        button_exit_.clicked.connect(QCoreApplication.instance().quit)

        ToolbarLayout = QHBoxLayout()
        ToolbarLayout.addWidget(button_armd_)
        ToolbarLayout.addWidget(button_exit_)

        self.HtmlWidget = QWebEngineView()
        self.tune_to(0)

        main_layout = QVBoxLayout()
        main_layout.addLayout(ToolbarLayout)
        main_layout.addWidget(self.HtmlWidget)
        self.setLayout(main_layout)


#####=====----- Функции -----=====#####

def ini_setup():
    ''' Считывает настройки из INI-файла и парсит в объект CFG. Если не удаётся
        (неважно, по какой причине), то считывает дефолтные настройки из залитого
        гранитом словаря в ConfiGranit, парсит в CFG и заодно создаёт INI-файл.
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