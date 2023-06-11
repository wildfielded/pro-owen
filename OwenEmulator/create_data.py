#!/usr/bin/python3

import sys
sys.path.append('..')
#####!!!!! TEMPORAL for VENV working in Windows !!!!!#####
import sys                                           #####
sys.path.append('../VENVemul/Lib/site-packages')     #####
#####!!!!! ------------------------------------ !!!!!#####
from smb.SMBConnection import SMBConnection

from OwenCommon.common_func import (get_current_files, read_json, parse_lastcfg,
                                    parse_lastdata, log_inf, log_err, CONF_DICT)


''' =====----- Функции -----===== '''

def generate_measures():
    ''' Генерирует значения сенсоров некоторым псевдослучайным способом
    Arguments:
        none
    Returns:
        none
    '''
    pass


def put_current_files(login: str, passwd: str, domain: str,
                      cli_name: str, srv_name: str,
                      srv_ip: str, srv_port: int,
                      share_name: str, data_path: str, last_datafile: str,
                      **kwargs):
    ''' Записывает файл с генерированными измерениями на сетевой ресурс
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
        last_datafile [str] -- Путь к локальной копии файла данных
    Returns:
        none
    '''
    try:
        with SMBConnection(login, passwd, cli_name, srv_name, domain,
                           use_ntlm_v2=True, is_direct_tcp=True) as s_:
            s_.connect(srv_ip, srv_port)
            with open(last_datafile, 'rb') as f_:
                s_.storeFile(share_name, data_path, f_)
            log_inf('OK')
    except:
        log_err('Unable to connect with OWEN server!')


''' =====----- MAIN -----=====##### '''
if __name__ == '__main__':
    get_result = get_current_files(**CONF_DICT)
    if get_result == 'fresh_data':
        current_obj_list = parse_lastdata(parse_lastcfg(read_json(**CONF_DICT),
                                                        **CONF_DICT
                                                       ),
                                          **CONF_DICT
                                         )
        print(current_obj_list)
    
    # put_current_files(**CONF_DICT)

#####=====----- THE END -----=====#########################################