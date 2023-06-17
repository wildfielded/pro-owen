#!/usr/bin/python3

from time import strftime
from random import uniform
import csv

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


''' =====----- Функции -----===== '''

def generate_measure(low_edge: float, high_edge: float) -> float:
    ''' Генерирует одно значение температуры для сенсора некоторым
    случайным способом. Сейчас просто берётся случайное число из данного
    диапазона, но можно прикрутить более продвинутую генерацию.
    Arguments:
        low_edge [float] -- Нижний предел диапазона температуры
        high_edge [float] -- Верхний предел диапазона температуры
    Returns:
        [float] -- Значение температуры с округлением до 0.1
    '''
    return round(uniform(low_edge, high_edge), 1)


@inject_config()
def create_measures(last_datafile: str, last_cfgfile: str, **kwargs):
    ''' Записывает файл с новыми измерениями в локальный файл
    с сохранением формата и структуры данных.
    Arguments:
        Может принимать весь словарь именованных аргументов.
        Из них использует:
        last_datafile [str] -- Путь к локальной копии файла данных
        last_cfgfile [str] -- Путь к локальной копии конфигурационного
            файла
    Returns:
        None
    '''
    try:
        with (open(last_cfgfile, 'r', encoding='utf-8') as cf_,
              open(last_datafile, 'w', newline='', encoding='utf-8') as df_
             ):
            date_list_ = strftime('%d.%m.%Y %H:%M:%S').split()
            date_ = date_list_[0]
            time_ = date_list_[1]
            # Имена колонок файла данных
            data_cols_ = ['EventDate', 'EventTime', 'Description', 'Value']

            conf_dict_ = csv.DictReader(cf_, delimiter='\t')
            data_dict_ = csv.DictWriter(df_, data_cols_, delimiter='\t')
            # Запись первой строки файла данных (имена колонок)
            data_dict_.writeheader()
            # Построчная запись новых данных в файл
            for row_ in conf_dict_:
                writer_dict_ = {
                    'EventDate': date_,
                    'EventTime': time_,
                    'Description': row_['Description'],
                    'Value': generate_measure(float(row_['Max1']) - 15.0,
                                              float(row_['Max2']) + 20.0)
                }
                data_dict_.writerow(writer_dict_)
            log_inf('Local data file updated.')
    except:
        log_err('Unable to open data and config local files!')


@inject_config()
def put_current_files(login: str, passwd: str, domain: str,
                      cli_name: str, srv_name: str,
                      srv_ip: str, srv_port: int,
                      share_name: str, data_path: str, last_datafile: str,
                      **kwargs):
    ''' Копирует локальный файл с генерированными измерениями на сетевой
    ресурс сервера OWEN.
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
    create_measures()
    put_current_files()

    # get_result = get_current_files()
    # if get_result == 'fresh_data':
        # current_obj_list = parse_lastdata(parse_lastcfg(read_json()))
        # write_json(current_obj_list)
        # print(current_obj_list)

#####=====----- THE END -----=====#########################################