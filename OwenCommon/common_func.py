#!/usr/bin/python3

from time import time

from smb.SMBConnection import SMBConnection

##### import configowen as c_

def setup_logger():
    ''' Функция-декоратор для настройки функций лог-сообщений
    '''
    pass

def pull_current_files():
    ''' Забирает файл с последними измерениями и на всякий случай (если
    есть) текущий файл с пороговыми значениями с сервера OWEN и
    записывает себе локально. Проверяет наличие и свежесть файла с
    измерениями (чтобы не старше двух минут), иначе возвращает
    соответственно строку "ERR_missing_data" или "ERR_rancid_data".
    '''
    pass

def push_current_files():
    '''
    '''
    pass

#####=====----- THE END -----=====#########################################