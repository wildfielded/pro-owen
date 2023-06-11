#!/usr/bin/python3

from time import mktime, strptime, time
import json
import logging
import logging.handlers as LH_

#####!!!!! TEMPORAL for VENV working in Windows !!!!!#####
import sys                                           #####
sys.path.append('../VENVemul/Lib/site-packages')     #####
#####!!!!! ------------------------------------ !!!!!#####
from smb.SMBConnection import SMBConnection

from . import configowen as conf_


''' =====----- Переменные и константы -----===== '''

OWEN_CONN_PARAMS = {
    'login': conf_.LOGIN,
    'passwd': conf_.PASSWD,
    'domain': conf_.DOMAIN,
    'cli_name': conf_.CLI_NAME,
    'srv_name': conf_.SRV_NAME,
    'srv_ip': conf_.SRV_IP,
    'srv_port': conf_.SRV_PORT,
    'share_name': conf_.SHARE_NAME,
    'data_path': conf_.DATA_PATH,
    'cfg_path': conf_.CFG_PATH,
    'last_datafile': conf_.LAST_DATAFILE,
    'last_cfgfile': conf_.LAST_CFGFILE
}
LOGGING_PARAMS = {
    'use_syslog': conf_.USE_SYSLOG,
    'syslog_addr': conf_.SYSLOG_ADDR,
    'syslog_port': conf_.SYSLOG_PORT,
    'use_filelog': conf_.USE_FILELOG,
    'filelog_path': conf_.FILELOG_PATH
}
CONF_DICT = {
    'last_datafile': conf_.LAST_DATAFILE,
    'last_cfgfile': conf_.LAST_CFGFILE,
    'json_file': conf_.JSON_FILE,
    'login': conf_.LOGIN,
    'passwd': conf_.PASSWD,
    'domain': conf_.DOMAIN,
    'cli_name': conf_.CLI_NAME,
    'srv_name': conf_.SRV_NAME,
    'srv_ip': conf_.SRV_IP,
    'srv_port': conf_.SRV_PORT,
    'share_name': conf_.SHARE_NAME,
    'data_path': conf_.DATA_PATH,
    'cfg_path': conf_.CFG_PATH,
    'tz_shift': conf_.TZ_SHIFT,
    'use_syslog': conf_.USE_SYSLOG,
    'syslog_addr': conf_.SYSLOG_ADDR,
    'syslog_port': conf_.SYSLOG_PORT,
    'use_filelog': conf_.USE_FILELOG,
    'filelog_path': conf_.FILELOG_PATH
}

''' =====----- Классы -----===== '''

class SensorDataBlock:
    ''' Создаёт объект данных одного датчика, задаёт структуру данных в
    виде словаря и методы их обработки
    '''
    def __init__(self):
        self.sensor_dict = {'sen_num': 0,
                            'place': '',
                            'warn_t': 0.0,
                            'crit_t': 0.0,
                            'measures': [{'timestamp': 0.0,
                                          'value': 0.0,
                                          'state': 'green-state'
                                        }]
                           }

    def write_data(self, data_dict: dict):
        keys_ = data_dict.keys()
        if 'sen_num' in keys_:
            self.sensor_dict['sen_num'] = data_dict['sen_num']
        if 'place' in keys_:
            self.sensor_dict['place'] = data_dict['place']
        if 'warn_t' in keys_:
            self.sensor_dict['warn_t'] = data_dict['warn_t']
        if 'crit_t' in keys_:
            self.sensor_dict['crit_t'] = data_dict['crit_t']
        if 'state' in keys_:
            self.sensor_dict['measures'][0]['state'] = data_dict['state']
        if 'measures' in keys_:
            self.sensor_dict['measures'] = data_dict['measures'] \
                                           + self.sensor_dict['measures']


''' =====----- Настройка логирования -----===== '''

def log_setup(use_syslog: bool, syslog_addr: str, syslog_port: int,
              use_filelog: bool, filelog_path: str, **kwargs) -> object:
    ''' Настройка функционала логирования событий
    Arguments:
        use_syslog [bool] -- Сброс логов на Syslog-сервер
        syslog_addr [str] -- IP-адрес Syslog-сервера
        syslog_port [int] -- Номер порта Syslog-сервера
        use_filelog [bool] -- Сброс логов в локальный файл (для отладки)
        filelog_path [str] -- Путь к лог-файлу
    Returns:
        [obj] -- Настроенный логгер
    '''
    log_format = logging.Formatter('%(name)s %(levelname)s: "%(message)s"')
    logger_ = logging.getLogger('owen')
    logger_.setLevel(logging.INFO)
    syslog_handler = LH_.SysLogHandler(address=(syslog_addr, syslog_port))
    syslog_handler.setLevel(logging.INFO)
    syslog_handler.setFormatter(log_format)
    file_handler = logging.FileHandler(filename=filelog_path, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(log_format)
    if use_syslog:
        logger_.addHandler(syslog_handler)
    else:
        logger_.addHandler(logging.NullHandler())
    if use_filelog:
        logger_.addHandler(file_handler)
    return logger_


##### Лямбда-функции используются в других функциях
# LOGGER = log_setup(**LOGGING_PARAMS)
LOGGER = log_setup(**CONF_DICT)
log_inf = lambda inf_msg: LOGGER.info(inf_msg)
log_err = lambda err_msg: LOGGER.error(err_msg)


''' =====----- Функции -----===== '''

def get_current_files(login: str, passwd: str, domain: str,
                       cli_name: str, srv_name: str,
                       srv_ip: str, srv_port: int,
                       share_name: str, data_path: str, cfg_path: str,
                       last_datafile: str, last_cfgfile: str, **kwargs) -> str:
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
        last_datafile [str] -- Путь к локальной копии файла данных
        last_cfgfile [str] -- Путь к локальной копии конфигурационного
            файла
    Returns:
        [str] -- "fresh_data" при удачном раскладе, "ERR_missing_data"
            или "ERR_rancid_data" при ошибках.
    '''
    try:
        with SMBConnection(login, passwd, cli_name, srv_name, domain,
                        use_ntlm_v2=True, is_direct_tcp=True) as s_:
            s_.connect(srv_ip, srv_port)

            file_list_ = s_.listPath(share_name, '/', pattern=data_path)
            if file_list_:
                if file_list_[0].last_write_time > (time() - 120.0):
                    with open(last_datafile, 'wb') as f_:
                        s_.retrieveFile(share_name, data_path, f_)
                    log_inf('Fresh data file retrieved from OWEN server')
                    result_ = 'fresh_data'
                else:
                    log_err('OWEN failure. No updates for more than 2 minutes.')
                    result_ = 'ERR_rancid_data'
            else:
                log_err('Data file is missing or not readable on OWEN server')
                result_ = 'ERR_missing_data'

            if s_.listPath(share_name, '/', pattern=cfg_path):
                with open(last_cfgfile, 'wb') as g_:
                    s_.retrieveFile(share_name, cfg_path, g_)
                log_inf('Config file retrieved from OWEN server')
    except:
        log_err('Unable to connect with OWEN server!')
        result_ = 'ERR_missing_data'
    finally:
        return result_


def read_json(json_file: str, **kwargs) -> object:
    ''' Считывает файл с историческими данными в формате JSON и создаёт
    на их основе список экземпляров класса SensorDataBlock
    Arguments:
        json_file [str] -- Путь к JSON-файлу с историей данныx
    Returns:
        [obj] -- Список объектов класса SensorDataBlock
    '''
    output_obj_list_ = []
    try:
        with open(json_file, 'r', encoding='utf-8') as f_:
            history_list_ = json.load(f_)
        for dict_ in history_list_:
            sensor_obj_ = SensorDataBlock()
            sensor_obj_.write_data(dict_)
            output_obj_list_.append(sensor_obj_)
    except:
        log_err('JSON file is missing or not readable.')
    finally:
        return output_obj_list_


def write_json(**kwargs):
    pass


def parse_lastcfg(input_obj_list: list, last_cfgfile: str, **kwargs) -> object:
    ''' Парсит данные из загруженного локально файла с пороговыми
    значениями по каждому датчику с некоторой валидацией данных и
    дополняет текущий (или создаёт новый) список экземпляров (объектов)
    класса SensorDataBlock
    Arguments:
        input_obj_list [list] -- Список объектов класса SensorDataBlock
        last_cfgfile [str] -- Путь к локальной копии конфигурационного
            файла
    Returns:
        [obj] -- Список объектов класса SensorDataBlock
    '''
    try:
        with open(last_cfgfile, 'r', encoding='utf-8') as f_:
            cfg_list_ = f_.readlines()
    except UnicodeDecodeError:
        with open(last_cfgfile, 'r', encoding='cp1251') as f_:
            cfg_list_ = f_.readlines()
        log_err('Config file cp1251-encoded again.')

    output_obj_list_ = input_obj_list.copy()
    n_ = 0
    for cfg_line_ in cfg_list_[1:]:
        n_ += 1
        line_list_ = cfg_line_.strip().split('\t')
        sensor_dict_ = {'sen_num': n_,
                        'place': line_list_[0],
                        'warn_t': float(line_list_[1]),
                        'crit_t': float(line_list_[2])
                       }
        if not input_obj_list:
            sensor_obj_ = SensorDataBlock()
            sensor_obj_.write_data(sensor_dict_)
            output_obj_list_.append(sensor_obj_)
        else:
            output_obj_list_[n_ - 1].write_data(sensor_dict_)
    return output_obj_list_


def parse_lastdata(input_obj_list: list, last_datafile: str, tz_shift: float,
                   **kwargs) -> object:
    ''' Парсит данные из загруженного локально файла с измерениями по
    каждому датчику с некоторой валидацией данных, выставляет состояние
    в соответствии с пороговыми значениями и дополняет текущий (или
    создаёт новый) список экземпляров (объектов) класса SensorDataBlock.
    Arguments:
        input_obj_list [list] -- Список объектов класса SensorDataBlock
        last_datafile [str] -- Путь к локальной копии файла данных
        tz_shift [float] -- Возможный сдвиг по времени на случай, если
            таймзоны системного времени на сервере и на локальной машине
            отличаются. Например, если на сервере OWEN время MSK, а на
            локальной машине IRK, то tz_shift=3600.0*5 (5 часов).
    Returns:
        [obj] -- Список объектов класса SensorDataBlock
    '''
    try:
        with open(last_datafile, 'r', encoding='utf-8') as f_:
            data_list_ = f_.readlines()
    except UnicodeDecodeError:
        with open(last_datafile, 'r', encoding='cp1251') as f_:
            data_list_ = f_.readlines()
        log_err('Data file cp1251-encoded again.')

    output_obj_list_ = input_obj_list.copy()
    n_ = 0
    for data_line_ in data_list_[1:]:
        n_ += 1
        line_list_ = data_line_.strip().split('\t')
        sensor_dict_ = {'sen_num': n_,
                        'place': line_list_[2]
                       }
        timestamp_ = mktime(strptime(' '.join((line_list_[0], line_list_[1])),
                                     '%d.%m.%Y %H:%M:%S'
                                    )
                           ) + tz_shift
        try:
            value_ = float(line_list_[3].replace(',', '.'))
        except:
            if line_list_[3].startswith('?'):
                value_ = '???'
                state_ = 'black-state'
            else:
                value_ = '!!!'
                state_ = 'gray-state'
        else:
            if value_ < output_obj_list_[n_ - 1].sensor_dict['warn_t']:
                state_ = 'green-state'
            elif value_ < output_obj_list_[n_ - 1].sensor_dict['crit_t']:
                state_ = 'yellow-state'
            else:
                state_ = 'red-state'
        sensor_dict_['measures'] = [{'timestamp': timestamp_,
                                     'value': value_,
                                     'state': state_
                                   }]
        if not input_obj_list:
            sensor_obj_ = SensorDataBlock()
            sensor_obj_.write_data(sensor_dict_)
            output_obj_list_.append(sensor_obj_)
        else:
            output_obj_list_[n_ - 1].write_data(sensor_dict_)
    return output_obj_list_

#####=====----- THE END -----=====#########################################