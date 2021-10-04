#!/usr/bin/python3

import configowen as c_
import time
from string import Template as T_
from smb.SMBConnection import SMBConnection

class SensorDataBlock:
    ''' Создаёт объект данных одного датчика, задаёт стуктуру данных в виде
        словаря и методы их обработки
    '''
    def __init__(self):
        self.sensor_dict = {
            'line_num': 0,
            'place': '',
            'warn_t': 0,
            'crit_t': 0,
            'status': '',
            'measures': [ { 'timestamp': 0, 'value': 0 }, ]
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
        output_dict = {}
        for k_ in keys_list:
            if k_ in self.sensor_dict.keys():
                output_dict[k_] = self.sensor_dict[k_]
        return output_dict

    def read_one(self, key_str):
        if key_str in self.sensor_dict.keys():
            return self.sensor_dict[key_str]

    def read_all(self):
        return self.sensor_dict

#####=====----- Функции -----=====#####

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

def create_obj_list(last_file, last_cfg, tz_shift):
    ''' Создаёт рабочий список объектов класса SensorDataBlock из загруженных
        файлов с измерениями и пороговыми значениями по каждому датчику с
        некоторой валидацией данных
    '''
    with open(last_file, 'r', encoding='cp1251') as f_:
        data_list = f_.readlines()
    with open(last_cfg, 'r', encoding='cp1251') as g_:
        cfg_list = g_.readlines()
    output_obj_list = []
    n_ = 0
    m_ = 0
    for data_ in data_list[1:]:
        n_ += 1
        data_list = data_.strip().split('\t')
        data_dict = {
            'line_num': n_,
            'place': data_list[2],
            'measures': [ {}, ]
            }
        data_dict['measures'][0]['timestamp'] = time.mktime(time.strptime(data_list[0] + ' ' + data_list[1], '%d.%m.%Y %H:%M:%S')) + tz_shift
        data_dict['measures'][0]['value'] = float(data_list[3].replace(',', '.'))
        sensor_obj = SensorDataBlock()
        sensor_obj.write_data(data_dict)
        output_obj_list.append(sensor_obj)
    for conf_ in cfg_list[1:]:
        m_ += 1
        cfg_list = conf_.strip().split('\t')
        cfg_dict = {
            'line_num': m_,
            'place': cfg_list[0],
            'warn_t': float(cfg_list[1]),
            'crit_t': float(cfg_list[2])
            }
        if output_obj_list[m_ - 1].read_data([ 'place' ])['place'] == cfg_dict['place'] and output_obj_list[m_ - 1].read_data([ 'line_num' ])['line_num'] == cfg_dict['line_num']:
                print(m_)
                output_obj_list[m_ - 1].write_data(cfg_dict)
    return output_obj_list

def fill_current_data(last_file, tz_shift, input_obj_list: list = []):
    ''' Выдирает данные из текущего локального файла измерений и возвращает
        список объектов класса SensorDataBlock с данными по каждому сенсору
    '''
    with open(last_file, 'r', encoding='cp1251') as f_:
        data_list = f_.readlines()
    output_obj_list = input_obj_list
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
        output_obj_list.append(sensor_obj)
    return output_obj_list

def fill_current_cfg(last_cfg, input_obj_list: list = []):
    ''' Выдирает данные из текущего локального файла с порогами и возвращает
        список объектов класса SensorDataBlock с данными по каждому сенсору
    '''
    with open(last_cfg, 'r', encoding='cp1251') as f_:
        cfg_list = f_.readlines()
    output_obj_list = input_obj_list
    n_ = 0
    for l_ in cfg_list[1:]:
        n_ += 1
        line_list = l_.strip().split('\t')
        dict_ = {
            'line_num': n_,
            'place': line_list[0],
            'warn_t': line_list[1],
            'crit_t': line_list[2]
            }
        sensor_obj = SensorDataBlock()
        sensor_obj.write_data(dict_)
        output_obj_list.append(sensor_obj)
    return output_obj_list

def generate_rows(input_obj_list, row_template):
    ''' Принимает список объектов класса SensorDataBlock и заполняет по шаблону
        табличные ячейки соответствующими значениями
    '''
    output_str = ''
    for obj_ in input_obj_list:
        dict_ = obj_.read_data([ 'place', 'warn_t', 'crit_t', 'measures' ])
        p_ = dict_['place']
        t_ = str(dict_['measures'][0]['value']).replace('.', ',')
        y_ = dict_['warn_t']
        r_ = dict_['crit_t']
        list_ = time.ctime(dict_['measures'][0]['timestamp']).split()
        m_ = '{} ({} {})'.format(list_[3], list_[2], list_[1])
        row_ = T_(row_template)
        output_str += row_.safe_substitute(place=p_, temp=t_, max1=y_, max2=r_, mtime=m_)
    return output_str

def write_html(output_file, header_file, footer_file, rows=''):
    ''' Записывает файл HTML для отдачи по HTTP. Пока использует записанные в
        файлы куски HTML-кода и Template для заполнения строк таблицы
    '''
    with open(header_file, 'r', encoding='utf-8') as h_:
        header_str = h_.read()
    with open(footer_file, 'r', encoding='utf-8') as f_:
        footer_str = f_.read()
    with open(output_file, 'w', encoding='utf-8') as o_:
        o_.write(header_str + rows + footer_str)

#####=====----- Собственно, сама программа -----=====#####

if __name__ == '__main__':
    get_current_files(c_.LAST_DATAFILE, c_.LAST_CFGFILE, c_.LOGIN, c_.PASSWD,
                     c_.DOMAIN, c_.CLI_NAME, c_.SRV_NAME, c_.SRV_IP, c_.SRV_PORT,
                     c_.SHARE_NAME, c_.DATA_PATH, c_.CFG_PATH)
    current_obj_list = fill_current_data(c_.LAST_DATAFILE, c_.TZ_SHIFT)
    #####current_obj_list = fill_current_cfg(c_.LAST_CFGFILE, pre_obj_list)
    tab_rows = generate_rows(current_obj_list, c_.ROW_TEMPLATE)
    write_html(c_.HTML_OUTPUT, c_.HTML_HEADER, c_.HTML_FOOTER, rows=tab_rows)

###########################################################################