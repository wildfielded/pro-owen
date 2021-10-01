#!/usr/bin/python3

import configowen as c_
import time
from string import Template as T_
from smb.SMBConnection import SMBConnection

class SensorDataBlock:
    ''' Создаёт объект единичного датчика, задаёт его стуктуру данных и методы
        обработки
    '''
    def __init__(self):
        self.sensor_dict = {
            'line_num': 0,
            'place': 'nowhere',
            'warn_t': 1.0,
            'crit_t': 1.0,
            'status': 'normal',
            'measures': [ { 'timestamp': 1.0, 'value': 1.0 }, ]
        }

    def write_data(self, data_dict: dict = {}):
        if 'line_num' in data_dict.keys():
            self.sensor_dict['line_num'] = data_dict['line_num']
        if 'place' in data_dict.keys():
            self.sensor_dict['place'] = data_dict['place']
        if 'warn_t' in data_dict.keys():
            self.sensor_dict['warn_t'] = data_dict['warn_t']
        if 'crit_t' in data_dict.keys():
            self.sensor_dict['crit_t'] = data_dict['crit_t']
        if 'status' in data_dict.keys():
            self.sensor_dict['status'] = data_dict['status']
        if 'measures' in data_dict.keys():
            self.sensor_dict['measures'] = data_dict['measures']
            #####self.sensor_dict.insert(0, data_dict['measures'])

    def read_data(self, keys_list: list = []):
        result_dict = {}
        for k_ in keys_list:
            if k_ in self.sensor_dict.keys():
                result_dict[k_] = self.sensor_dict[k_]
        return result_dict

#####=====----- Functions -----=====#####

def get_current_files(output_datafile, output_cfgfile, login, passwd, domain,
                     client, server, addr, port, share, data_path, cfg_path):
    ''' Забирает файл с последними измерениями и на всякий случай текущий файл с
        пороговыми значениями с сервера OWEN и записывает себе локально
    '''
    with SMBConnection(login, passwd, client, server, domain,
                       use_ntlm_v2=True, is_direct_tcp=True) as s_:
        s_.connect(addr, port)
        with open(output_datafile, 'wb') as f_:
            s_.retrieveFile(share, data_path, f_)
        with open(output_cfgfile, 'wb') as g_:
            s_.retrieveFile(share, cfg_path, g_)
        s_.close()

def get_current_obj_list(last_file, tz_shift):
    ''' Выдирает данные из текущего локального файла измерений и возвращает
        список объектов класса SensorDataBlock с данными по каждому сенсору
    '''
    with open(last_file, 'r', encoding='cp1251') as f_:
        data_list = f_.readlines()
    obj_list = []
    n_ = 0
    for l_ in data_list[1:]:
        n_ += 1
        line_list = l_.strip().split('\t')
        dict_ = {
            'line_num': n_,
            'place': line_list[2],
            'measures': [ {}, ]
            }
        dict_['measures'][0]['timestamp'] = time.mktime(time.strptime(line_list[0] + ' ' + line_list[1], '%d.%m.%Y %H:%M:%S')) + tz_shift
        dict_['measures'][0]['value'] = float(line_list[3].replace(',', '.'))
        sensor_obj = SensorDataBlock()
        sensor_obj.write_data(dict_)
        obj_list.append(sensor_obj)
    return obj_list

def generate_rows(input_obj_list, row_template):
    ''' Принимает список объектов класса SensorDataBlock и заполняет по шаблону
        табличные ячейки соответствующими значениями
    '''
    output_str = ''
    for obj_ in input_obj_list:
        p_ = obj_.read_data(['place'])['place']
        t_ = str(obj_.read_data(['measures'])['measures'][0]['value']).replace('.', ',')
        y_ = obj_.read_data(['warn_t'])['warn_t']
        r_ = obj_.read_data(['crit_t'])['crit_t']
        m_ = time.ctime(obj_.read_data(['measures'])['measures'][0]['timestamp'])
        tab_tr = T_(row_template)
        output_str += tab_tr.safe_substitute(placement=p_, temperature=t_, max1yellow=y_, max2red=r_, measuretime=m_)
    return output_str

def write_html(input_file, output_file, header_file,
               middle_file, footer_file, rows=''):
    ''' Записывает демо-файл HTML для отдачи по HTTP. Пока использует
        записанные в файлы куски HTML-кода и Template для заполнения
        строк таблицы
    '''
    with open(header_file, 'r', encoding='utf-8') as h_:
        header_str = h_.read()
    with open(middle_file, 'r', encoding='utf-8') as m_:
        middle_str = m_.read()
    with open(footer_file, 'r', encoding='utf-8') as f_:
        footer_str = f_.read()
    with open(input_file, 'r', encoding='cp1251') as i_:
        lastdata_str = i_.read()
    with open(output_file, 'w', encoding='utf-8') as o_:
        o_.write(header_str + lastdata_str + middle_str + rows + footer_str)

if __name__ == '__main__':
    get_current_files(c_.LAST_DATAFILE, c_.LAST_CFGFILE, c_.LOGIN, c_.PASSWD,
                     c_.DOMAIN, c_.CLI_NAME, c_.SRV_NAME, c_.SRV_IP, c_.SRV_PORT,
                     c_.SHARE_NAME, c_.DATA_PATH, c_.CFG_PATH)
    current_obj_list = get_current_obj_list(c_.LAST_DATAFILE, c_.TZ_SHIFT)
    tab_rows = generate_rows(current_obj_list, c_.TR_TEMPLATE)
    write_html(c_.LAST_DATAFILE, c_.HTML_SAMPLE, c_.HTML_HEADER, c_.HTML_MIDDLE,
               c_.HTML_FOOTER, rows=tab_rows)

###########################################################################