#!/usr/bin/python3

from time import strftime
from random import uniform

import sys
sys.path.append('..')
#####!!!!! TEMPORAL for VENV working in Windows !!!!!#####
import sys                                           #####
sys.path.append('../VENVemul/Lib/site-packages')     #####
#####!!!!! ------------------------------------ !!!!!#####
from smb.SMBConnection import SMBConnection

from OwenCommon.common_func import (inject_config, log_inf, log_err,
                                    get_current_files, read_json, write_json,
                                    parse_lastcfg, parse_lastdata)


''' =====----- Переменные и константы -----===== '''

CFG_CSV = 'cfg.csv'

''' =====----- Функции -----===== '''

def generate_measure(low_edge: float, high_edge: float) -> float:
    ''' Генерирует одно значение температуры для сенсора некоторым
    случайным способом. Сейчас просто берётся случайное число из данного
    диапазона, но можно прикрутить более продвинутую генерацию.
    Arguments:
        low_edge [float] -- Нижний предел диапазона температуры
        high_edge [float] -- Верхний предел диапазона температуры
    Returns:
        [float] -- Значение температуры
    '''
    return round(uniform(low_edge, high_edge), 1)


@inject_config()
def write_measures(login: str, passwd: str, domain: str, cli_name: str,
                   srv_name: str, srv_ip: str, srv_port: int, **kwargs):
    ''' Записывает файл с новыми измерениями на сетевой ресурс
    Arguments:
        Может принимать весь словарь именованных аргументов.
        Из них использует:
        login [str] -- Имя учётной записи, под которой идёт обращение на
            сетевой ресурс сервера OWEN
        passwd [str] -- Пароль учётной записи
        domain [str] -- AD-домен учётной записи
        cli_name [str] -- Имя локальной машины, где выполняется данная
            программа (можно назвать от балды)
        srv_name [str] -- NetBIOS/AD-имя сервера OWEN
        srv_ip [str] -- IP-адрес сервера OWEN
        srv_port [int] -- Номер TCP-порта для подключения к серверу OWEN
    Returns:
        None
    '''
    try:
        with SMBConnection(login, passwd, cli_name, srv_name, domain,
                        use_ntlm_v2=True, is_direct_tcp=True) as s_:
            s_.connect(srv_ip, srv_port)
            log_inf('Connecting to OWEN server.')
    except:
        log_err('Unable to write new data on OWEN server!')


@inject_config()
def put_current_files(login: str, passwd: str, domain: str,
                      cli_name: str, srv_name: str,
                      srv_ip: str, srv_port: int,
                      share_name: str, data_path: str, last_datafile: str,
                      **kwargs):
    ''' Записывает файл с генерированными измерениями на сетевой ресурс
    Arguments:
        Может принимать весь словарь именованных аргументов.
        Из них использует:
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
        last_datafile [str] -- Путь к локальной копии файла данных
    Returns:
        None
    '''
    try:
        with SMBConnection(login, passwd, cli_name, srv_name, domain,
                           use_ntlm_v2=True, is_direct_tcp=True) as s_:
            s_.connect(srv_ip, srv_port)
            with open(last_datafile, 'rb') as f_:
                s_.storeFile(share_name, data_path, f_)
            log_inf('Generated data file stored in OWEN server')
    except:
        log_err('Unable to connect with OWEN server!')


''' =====----- MAIN -----=====##### '''
if __name__ == '__main__':
    write_measures()
    # get_result = get_current_files()
    # if get_result == 'fresh_data':
        # current_obj_list = parse_lastdata(parse_lastcfg(read_json()))
        # write_json(current_obj_list)
        # print(current_obj_list)

    # put_current_files()

#####=====----- THE END -----=====#########################################