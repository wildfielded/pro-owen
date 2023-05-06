#!/usr/bin/python3

import sys
sys.path.append('..')
#####!!!!! TEMPORAL for VENV working in Windows !!!!!#####
sys.path.append('../VENVemul/Lib/site-packages')     #####
#####!!!!! ------------------------------------ !!!!!#####
# from time import time
import logging
import logging.handlers as LogHandlers_

from smb.SMBConnection import SMBConnection

from OwenCommon import configowen as conf_


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
    'last_cfgfile': conf_.LAST_CFGFILE
}
LOGGING_PARAMS = {
    'use_syslog': conf_.USE_SYSLOG,
    'syslog_addr': conf_.SYSLOG_ADDR,
    'syslog_port': conf_.SYSLOG_PORT,
}


def log_setup(use_syslog: bool, syslog_addr: str, syslog_port: int,) -> object:
    ''' Настройка функционала логирования событий
    Arguments:
        use_syslog [bool] -- Сброс логов на Syslog-сервер
        syslog_addr [str] -- IP-адрес Syslog-сервера
        syslog_port [int] -- Номер порта Syslog-сервера
    Returns:
        [obj] --
    '''
    format_ = logging.Formatter('%(name)s %(levelname)s: "%(message)s"')
    syslog_ = LogHandlers_.SysLogHandler(address=(syslog_addr, syslog_port))
    syslog_.setLevel(logging.INFO)
    syslog_.setFormatter(format_)
    logger_ = logging.getLogger('owen')
    logger_.setLevel(logging.INFO)
    if use_syslog:
        logger_.addHandler(syslog_)
    else:
        logger_.addHandler(logging.NullHandler())
    return logger_


def log_inf(inf_msg_: str):
    log_setup(**LOGGING_PARAMS).info(inf_msg_)
def log_err(err_msg_: str):
    log_setup(**LOGGING_PARAMS).error(err_msg_)
# log_inf = lambda inf_msg_ : logger.info(inf_msg_)
# log_err = lambda err_msg_ : logger.error(err_msg_)


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
            log_inf('Config file retrieved from OWEN server')

        s_.close()


def push_current_files():
    '''
    '''
    pass

#####=====----- THE END -----=====#########################################