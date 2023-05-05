#!/usr/bin/python3

#####!!!!! TEMPORAL for VENV working in Windows !!!!!#####
import sys
sys.path.append('../VENVemul/Lib/site-packages')
#####!!!!!

# from time import time

from smb.SMBConnection import SMBConnection


def setup_logger():
    ''' Функция-декоратор для настройки функций лог-сообщений
    '''
    pass

def pull_current_files(login: str, passwd: str, domain: str,
                       cli_name: str, srv_name: str,
                       srv_ip: str, srv_port: int,
                       share_name: str, data_path: str, cfg_path: str,
                       last_cfgfile: str) -> str:
    ''' Забирает файл с последними измерениями и на всякий случай (если
    есть) текущий файл с пороговыми значениями с сервера OWEN и
    записывает себе локально. Проверяет наличие и свежесть файла с
    измерениями (чтобы не старше двух минут), иначе возвращает
    соответственно строку "ERR_missing_data" или "ERR_rancid_data".
    Arguments:
        login [str] -- Имя учётной записи, под которой идёт обращение на
            сетевой ресурс сервера OWEN
        passwd [str] -- Пароль учётной записи
        domain [str] -- AD-домен учётной записи
        cli_name [str] -- Имя локальной машины, где выполняется данная
            программа (можно назвать от балды)
        srv_name [str] -- NetBIOS/AD-имя сервера OWEN
        srv_ip [str] -- IP-адрес сервера OWEN
        srv_port [int] -- Номер TCP-порта для подключения к серверу OWEN
        share_name [str] -- Имя сетевого ресурса на сервере OWEN
        data_path [str] -- Путь к текущему файлу данных от корня
            сетевого ресурса на сервере OWEN
        cfg_path [str] -- Путь к текущему конфигурационному файлу от
            корня сетевого ресурса на сервере OWEN
        last_cfgfile [str] -- Путь к локальной копии конфигурационного
            файла
    Returns:
        [str] -- "ERR_missing_data" или "ERR_rancid_data"
    '''
    with SMBConnection(login, passwd, cli_name, srv_name, domain,
                       use_ntlm_v2=True, is_direct_tcp=True) as s_:
        s_.connect(srv_ip, srv_port)

        if s_.listPath(share_name, '/', pattern=cfg_path):
            with open(last_cfgfile, 'wb') as g_:
                s_.retrieveFile(share_name, cfg_path, g_)

        s_.close()


def push_current_files():
    '''
    '''
    pass

#####=====----- THE END -----=====#########################################