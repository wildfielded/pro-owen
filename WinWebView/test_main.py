#!/usr/bin/python3

import sys

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication, QPushButton, QToolTip, QWidget

class OwenWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_win()

    def init_win(self):
        QToolTip.setFont(QFont('SansSerif', 12))
        butt_ = QPushButton('Выход', self)
        butt_.setToolTip('Кнопка <B>завершения</B> программы')
        butt_.resize(butt_.sizeHint())
        butt_.move(50, 100)
        butt_.clicked.connect(QCoreApplication.instance().quit)
        self.setGeometry(200, 200, 600, 300)
        self.setWindowTitle('OWEN')
        self.setWindowIcon(QIcon('owenicon.svg'))
        self.show()


if __name__ == '__main__':
    app_ = QApplication(sys.argv)
    win_ = OwenWindow()
    sys.exit(app_.exec_())

##########################################################################