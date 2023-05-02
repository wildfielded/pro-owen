#!/usr/bin/python3

from time import time

from smb.SMBConnection import SMBConnection

##### import configowen as c_

def get_current_files():
    ''' Забирает файл с последними измерениями и на всякий случай (если есть)
        текущий файл с пороговыми значениями с сервера OWEN и записывает себе
        локально.  Проверяет наличие и свежесть файла с измерениями (чтобы не
        старше двух минут), иначе возвращает соответственно строку
        "ERR_missing_data" или "ERR_rancid_data".
    '''
    with SMBConnection(c_.LOGIN, c_.PASSWD, c_.CLI_NAME, c_.SRV_NAME, c_.DOMAIN,
                       use_ntlm_v2=True, is_direct_tcp=True) as s_:
        s_.connect(c_.SRV_IP, c_.SRV_PORT)

        file_list_ = s_.listPath(c_.SHARE_NAME, '/', pattern=c_.DATA_PATH)
        if file_list_:
            if file_list_[0].last_write_time > (time() - 120.0):
                with open(c_.LAST_DATAFILE, 'wb') as f_:
                    s_.retrieveFile(c_.SHARE_NAME, c_.DATA_PATH, f_)
                log_inf('Fresh data file retrieved from OWEN server')
                result_ = 'fresh_data'
            else:
                log_err('OWEN failure. Data file has not been updated for more than 2 min.')
                result_ = 'ERR_rancid_data'
        else:
            log_err('Data file is missing on OWEN server.')
            result_ = 'ERR_missing_data'

        if s_.listPath(c_.SHARE_NAME, '/', pattern=c_.CFG_PATH):
            with open(c_.LAST_CFGFILE, 'wb') as g_:
                s_.retrieveFile(c_.SHARE_NAME, c_.CFG_PATH, g_)
            log_inf('Config file retrieved from OWEN server.')

        s_.close()
    return result_

#####=====----- THE END -----=====#########################################