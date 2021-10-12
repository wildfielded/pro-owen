#!/usr/bin/python3

import configowen as c_
from time import ctime, mktime, strptime, time
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
            'warn_t': 0.,
            'crit_t': 0.,
            'status': '',
            'measures': [{'timestamp': 0., 'value': 0.},]
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
            self.sensor_dict['measures'].insert(0, data_dict['measures'][0])

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
    result_ = {}
    with SMBConnection(login, passwd, client, server, domain,
                       use_ntlm_v2=True, is_direct_tcp=True) as s_:
        s_.connect(addr, port)

        check_list_ = s_.listPath(share, '/', pattern=data_path)
        if len(check_list_) == 1:
            if check_list_[0].last_write_time > (time() - 60.):
                result_['status'] = 'fresh_data'
                with open(output_datafile, 'wb') as f_:
                    s_.retrieveFile(share, data_path, f_)
            else:
                result_['status'] = 'rancid_data'

        check_list_ = s_.listPath(share, '/', pattern=cfg_path)
        if len(check_list_) == 1:
            with open(output_cfgfile, 'wb') as g_:
                s_.retrieveFile(share, cfg_path, g_)
        s_.close()

    return result_


def parse_lastdata(last_file, tz_shift, input_obj_list: list = []):
    ''' Парсит данные из загруженного файла с измерениями по каждому датчику с
        некоторой валидацией данных и дополняет текущий (или создаёт новый)
        список объектов класса SensorDataBlock
    '''
    with open(last_file, 'r', encoding='cp1251') as f_:
        data_list = f_.readlines()
    if len(input_obj_list) == 0:
        output_obj_list = []
        n_ = 0
        for line_ in data_list[1:]:
            n_ += 1
            list_ = line_.strip().split('\t')
            dict_ = {
                'line_num': n_,
                'place': list_[2],
                'measures': [{},]
                }
            dict_['measures'][0]['timestamp'] = mktime(strptime(list_[0] + ' ' + list_[1], '%d.%m.%Y %H:%M:%S')) + tz_shift
            dict_['measures'][0]['value'] = float(list_[3].replace(',', '.'))
            sensor_obj = SensorDataBlock()
            sensor_obj.write_data(dict_)
            output_obj_list.append(sensor_obj)
    else:
        #####!!!!! Заглушка. Нужна обработка переданного списка объектов
        output_obj_list = input_obj_list
    return output_obj_list


def parse_lastcfg(last_cfg, input_obj_list: list = []):
    ''' Парсит данные из загруженного файла с пороговыми значениями по каждому
        датчику с некоторой валидацией данных и дополняет текущий (или создаёт
        новый) список объектов класса SensorDataBlock
    '''
    with open(last_cfg, 'r', encoding='cp1251') as f_:
        cfg_list = f_.readlines()
    if len(input_obj_list) == 0:
        output_obj_list = []
        n_ = 0
        for line_ in cfg_list[1:]:
            n_ += 1
            list_ = line_.strip().split('\t')
            dict_ = {
                'line_num': n_,
                'place': list_[0],
                'warn_t': float(list_[1]),
                'crit_t': float(list_[2])
                }
            sensor_obj = SensorDataBlock()
            sensor_obj.write_data(dict_)
            output_obj_list.append(sensor_obj)
    else:
        output_obj_list = input_obj_list
        n_ = 0
        for line_ in cfg_list[1:]:
            n_ += 1
            list_ = line_.strip().split('\t')
            dict_ = {
                'line_num': n_,
                'place': list_[0],
                'warn_t': float(list_[1]),
                'crit_t': float(list_[2])
                }
            if output_obj_list[n_ - 1].read_one('place') == dict_['place'] and output_obj_list[n_ - 1].read_one('line_num') == dict_['line_num']:
                output_obj_list[n_ - 1].write_data(dict_)
    return output_obj_list


def set_status(input_obj_list):
    ''' Выставляет "status", который потом используется для индикации алертов
    '''
    output_obj_list = input_obj_list
    for obj_ in output_obj_list:
        dict_ = obj_.read_data(['status', 'warn_t', 'crit_t', 'measures'])
        if dict_['measures'][0]['value'] > dict_['crit_t']:
            dict_['status'] = 'red-alert'
        elif dict_['measures'][0]['value'] > dict_['warn_t']:
            dict_['status'] = 'yellow-alert'
        else:
            dict_['status'] = 'normal'
        obj_.write_data(dict_)
    return output_obj_list


def generate_rows(input_obj_list, row_template):
    ''' Принимает список объектов класса SensorDataBlock и заполняет по шаблону
        табличные ячейки соответствующими значениями
    '''
    output_str = ''
    for obj_ in input_obj_list:
        #####dict_ = obj_.read_data(['place', 'warn_t', 'crit_t', 'measures'])
        dict_ = obj_.read_all()
        p_ = dict_['place']
        t_ = str(dict_['measures'][0]['value']).replace('.', ',')
        y_ = int(dict_['warn_t'])
        r_ = int(dict_['crit_t'])
        s_ = dict_['status']
        list_ = ctime(dict_['measures'][0]['timestamp']).split()
        m_ = '{} ({} {})'.format(list_[3], list_[2], list_[1])
        row_ = T_(row_template)
        output_str += row_.safe_substitute(place=p_, temp=t_, max1=y_, max2=r_, status=s_, mtime=m_)
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
    current_obj_list = parse_lastdata(c_.LAST_DATAFILE, c_.TZ_SHIFT)
    current_obj_list = parse_lastcfg(c_.LAST_CFGFILE, current_obj_list)
    current_obj_list = set_status(current_obj_list)
    tab_rows = generate_rows(current_obj_list, c_.ROW_TEMPLATE)
    write_html(c_.HTML_OUTPUT, c_.HTML_HEADER, c_.HTML_FOOTER, rows=tab_rows)

###########################################################################