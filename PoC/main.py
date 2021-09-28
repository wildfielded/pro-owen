#!/usr/bin/python3

import configowen as c_
from string import Template as T_
from smb.SMBConnection import SMBConnection

def get_current_file(output_file, login, passwd, domain, client,
                     server, addr, port, share, path):
    ''' Забирает текущий файл с сервера OWEN и записывает себе локально
    '''
    with open(output_file, 'wb') as f_:
        with SMBConnection(login, passwd, client, server, domain,
                           use_ntlm_v2=True, is_direct_tcp=True) as s_:
            s_.connect(addr, port)
            s_.retrieveFile(share, path, f_)
            s_.close()

def get_current_data_tmp(last_file, row_template):
    ''' Выдирает данные из текущего локального файла и заполняет по шаблону
        табличные ячейки значения по месту датчика и температуре
    '''
    result_str = ''
    with open(last_file, 'r', encoding='cp1251') as f_:
        content_lst = f_.readlines()
    for line in content_lst[1:]:
        line_lst = line.strip().split('\t')
        tab_tr = T_(row_template)
        result_str += tab_tr.substitute(placement=line_lst[2],
                                        temperature=line_lst[3])
    return result_str

def write_html(input_file, output_file, header_file,
               middle_file, footer_file, rows=''):
    ''' Записывает демо-файл HTML для отдачи по HTTP. Пока использует
        записанные в файлы куски HTML-кода и Template для заполнения
        строк таблицы
    '''
    with open(header_file, 'r', encoding='utf-8') as f_:
        header_str = f_.read()
    with open(middle_file, 'r', encoding='utf-8') as f_:
        middle_str = f_.read()
    with open(footer_file, 'r', encoding='utf-8') as f_:
        footer_str = f_.read()
    with open(input_file, 'r', encoding='cp1251') as f_:
        lastdata_str = f_.read()
    with open(output_file, 'w', encoding='utf-8') as f_:
        f_.write(header_str + lastdata_str + middle_str + rows + footer_str)

if __name__ == '__main__':
    get_current_file(c_.LAST_DATAFILE, c_.LOGIN, c_.PASSWD, c_.DOMAIN,
                     c_.CLI_NAME, c_.SRV_NAME, c_.SRV_IP, c_.SRV_PORT,
                     c_.SHARE_NAME, c_.FILE_PATH)
    tab_rows = get_current_data_tmp(c_.LAST_DATAFILE, c_.TR_TEMPLATE)
    write_html(c_.LAST_DATAFILE, c_.HTML_SAMPLE, c_.HTML_HEADER, c_.HTML_MIDDLE,
               c_.HTML_FOOTER, rows=tab_rows)

###########################################################################