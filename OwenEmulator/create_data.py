#!/usr/bin/python3

import sys
sys.path.append('..')
#####!!!!! TEMPORAL for VENV working in Windows !!!!!#####
import sys                                           #####
sys.path.append('../VENVemul/Lib/site-packages')     #####
#####!!!!! ------------------------------------ !!!!!#####
from smb.SMBConnection import SMBConnection

from OwenCommon.common_func import (get_current_files, read_json, parse_lastcfg,
                                    CONF_DICT)


''' =====----- Функции -----===== '''

def generate_measures():
    pass


def put_current_files(login: str, passwd: str, domain: str,
                      cli_name: str, srv_name: str,
                      srv_ip: str, srv_port: int,
                      share_name: str, data_path: str, last_datafile: str,
                      last_datafile_TEST: str, data_path_TEST: str, **kwargs):
    ''' Записывает файл с генерированными измерениями на сетевой ресурс
    Arguments:
    Returns:
        none
    '''
    try:
        with SMBConnection(login, passwd, cli_name, srv_name, domain,
                           use_ntlm_v2=True, is_direct_tcp=True) as s_:
            s_.connect(srv_ip, srv_port)
            with open(last_datafile_TEST, 'rb') as f_:
                s_.storeFile(share_name, data_path_TEST, f_)
    except:
        log_err('Unable to connect with OWEN server!')


''' =====----- MAIN -----=====##### '''
if __name__ == '__main__':
    get_result = get_current_files(**CONF_DICT)
    current_obj_list = parse_lastcfg(read_json(**CONF_DICT), **CONF_DICT)
    print(current_obj_list)
    
    put_current_files(last_datafile_TEST='logfile.txt', data_path_TEST='Owen/Log_File.txt', **CONF_DICT)

#####=====----- THE END -----=====#########################################