#!/usr/bin/python3

import configowen as c_
import json
import png
from time import ctime, mktime, strptime, time
from string import Template
from smb.SMBConnection import SMBConnection

class SensorDataBlock:
    ''' Создаёт объект данных одного датчика, задаёт стуктуру данных в виде
        словаря и методы их обработки
    '''
    def __init__(self):
        self.sensor_dict = {
            'sen_num': 0,
            'place': '',
            'warn_t': 0.0,
            'crit_t': 0.0,
            'measures': [{'timestamp': 0.0, 'value': 0.0, 'state': 'green-state'},]
            }

    def write_data(self, data_dict: dict = {}):
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
            self.sensor_dict['measures'] = data_dict['measures'] + self.sensor_dict['measures']

    def read_data(self, keys_list: list = []):
        output_dict = {}
        for key_ in keys_list:
            if key_ in self.sensor_dict.keys():
                output_dict[key_] = self.sensor_dict[key_]
        return output_dict

    def read_one(self, key_str):
        if key_str in self.sensor_dict.keys():
            return self.sensor_dict[key_str]


#####=====----- Функции -----=====#####

def get_current_files():
    ''' Забирает файл с последними измерениями и на всякий случай (если есть)
        текущий файл с пороговыми значениями с сервера OWEN и записывает себе
        локально. Проверяет наличие и свежесть файла с измерениями (чтобы не
        старше двух минут), иначе возвращает соответственно строку "ERR_missing_data"
        или "ERR_rancid_data".
    '''
    with SMBConnection(c_.LOGIN, c_.PASSWD, c_.CLI_NAME, c_.SRV_NAME, c_.DOMAIN,
                       use_ntlm_v2=True, is_direct_tcp=True) as s_:
        s_.connect(c_.SRV_IP, c_.SRV_PORT)

        check_list_ = s_.listPath(c_.SHARE_NAME, '/', pattern=c_.DATA_PATH)
        if len(check_list_) == 1:
            if check_list_[0].last_write_time > (time() - 120.0):
                result_ = 'fresh_data'
                with open(c_.LAST_DATAFILE, 'wb') as f_:
                    s_.retrieveFile(c_.SHARE_NAME, c_.DATA_PATH, f_)
            else:
                result_ = 'ERR_rancid_data'
        else:
            result_ = 'ERR_missing_data'

        check_list_ = s_.listPath(c_.SHARE_NAME, '/', pattern=c_.CFG_PATH)
        if len(check_list_) == 1:
            with open(c_.LAST_CFGFILE, 'wb') as g_:
                s_.retrieveFile(c_.SHARE_NAME, c_.CFG_PATH, g_)

        s_.close()
    return result_


def read_json():
    ''' Считывает файл с историческими данными в формате JSON и создаёт на их
        основе список объектов класса SensorDataBlock
    '''
    output_obj_list = []
    try:
        with open(c_.JSON_FILE, 'r', encoding='utf-8') as f_:
            history_list = json.load(f_)
        for dict_ in history_list:
            sensor_obj = SensorDataBlock()
            sensor_obj.write_data(dict_)
            output_obj_list.append(sensor_obj)
    except:
        #####!!!!! Заглушка. Нужен обработчик.
        pass
    return output_obj_list


def write_json(input_obj_list):
    ''' Записывает в файл обновлённые исторические данные в формате JSON
    '''
    output_obj_list = []
    for obj_ in input_obj_list:
        for m_ in obj_.sensor_dict['measures'][-1::-1]:
            if m_['timestamp'] < time() - c_.HISTORY_LIMIT:
                obj_.sensor_dict['measures'].pop()
        output_obj_list.append(obj_.sensor_dict)
    with open(c_.JSON_FILE, 'w', encoding='utf-8') as f_:
        json.dump(output_obj_list, f_, ensure_ascii=False, indent=2)


def parse_lastcfg(input_obj_list: list = []):
    ''' Парсит данные из загруженного файла с пороговыми значениями по каждому
        датчику с некоторой валидацией данных и дополняет текущий (или создаёт
        новый) список объектов класса SensorDataBlock
    '''
    try:
        with open(c_.LAST_CFGFILE, 'r', encoding='utf-8') as f_:
            cfg_list = f_.readlines()
    except UnicodeDecodeError:
        with open(c_.LAST_CFGFILE, 'r', encoding='cp1251') as f_:
            cfg_list = f_.readlines()
    output_obj_list = input_obj_list.copy()
    n_ = 0
    for line_ in cfg_list[1:]:
        n_ += 1
        list_ = line_.strip().split('\t')
        dict_ = {
            'sen_num': n_,
            'place': list_[0],
            'warn_t': float(list_[1]),
            'crit_t': float(list_[2])
            }
        if len(input_obj_list) == 0:
            sensor_obj = SensorDataBlock()
            sensor_obj.write_data(dict_)
            output_obj_list.append(sensor_obj)
        else:
            #####if output_obj_list[n_ - 1].read_one('place') == dict_['place'] and output_obj_list[n_ - 1].read_one('sen_num') == dict_['sen_num']:
                #####pass
            output_obj_list[n_ - 1].write_data(dict_)
    return output_obj_list


def parse_lastdata(input_obj_list: list = []):
    ''' Парсит данные из загруженного файла с измерениями по каждому датчику с
        некоторой валидацией данных и дополняет текущий (или создаёт новый)
        список объектов класса SensorDataBlock
    '''
    try:
        with open(c_.LAST_DATAFILE, 'r', encoding='utf-8') as f_:
            data_list = f_.readlines()
    except UnicodeDecodeError:
        with open(c_.LAST_DATAFILE, 'r', encoding='cp1251') as f_:
            data_list = f_.readlines()
    output_obj_list = input_obj_list.copy()
    n_ = 0
    for line_ in data_list[1:]:
        n_ += 1
        list_ = line_.strip().split('\t')
        dict_ = {
            'sen_num': n_,
            'place': list_[2],
            }
        t_ = mktime(strptime(list_[0] + ' ' + list_[1], '%d.%m.%Y %H:%M:%S')) + c_.TZ_SHIFT
        try:
            v_ = float(list_[3].replace(',', '.'))
            state_ = 'green-state'
        except:
            v_ = -273.15
            if '?' in list_[3]:
                state_ = 'black-state'
            else:
                state_ = 'gray-state'
        dict_['measures'] = [{'timestamp': t_, 'value': v_, 'state': state_}]
        if len(input_obj_list) == 0:
            sensor_obj = SensorDataBlock()
            sensor_obj.write_data(dict_)
            output_obj_list.append(sensor_obj)
        else:
            output_obj_list[n_ - 1].write_data(dict_)
    return output_obj_list


def set_status(input_obj_list):
    ''' Выставляет "status", который потом используется для индикации алертов
    '''
    output_obj_list = input_obj_list.copy()
    for obj_ in output_obj_list:
        dict_ = obj_.read_data(['status', 'warn_t', 'crit_t', 'measures'])
        if dict_['measures'][0]['state'] == 'black-state':
            dict_['measures'][0]['value'] = '???'
        elif dict_['measures'][0]['state'] == 'gray-state':
            dict_['measures'][0]['value'] = '!!!'
        else:
            if dict_['measures'][0]['value'] > dict_['crit_t']:
                dict_['measures'][0]['state'] = 'red-state'
            elif dict_['measures'][0]['value'] > dict_['warn_t']:
                dict_['measures'][0]['state'] = 'yellow-state'
            else:
                #####dict_['measures'][0]['state'] = green-state
                pass
        obj_.write_data({'state': dict_['measures'][0]['state']})
    return output_obj_list


def generate_html(input_obj_list: list = [], smb_result=''):
    ''' Принимает список объектов класса SensorDataBlock и заполняет
        соответствующими значениями по шаблонам табличные ячейки и итоговое
        состояние помещений, выводимое в одной или нескольких строках в конце
        таблицы.
    '''
    output_rows = ''
    output_diag = ''
    rows_ = Template(c_.ROW_TEMPLATE)
    diag_ = Template(c_.DIAG_TEMPLATE)
    if smb_result == 'fresh_data':
        for obj_ in input_obj_list:
            dict_ = obj_.sensor_dict
            n_ = str(dict_['sen_num'])
            p_ = dict_['place']
            t_ = str(dict_['measures'][0]['value']).replace('.', ',')
            y_ = int(dict_['warn_t'])
            r_ = int(dict_['crit_t'])
            s_ = dict_['measures'][0]['state']
            list_ = ctime(dict_['measures'][0]['timestamp']).split()
            m_ = '{} ({} {})'.format(list_[3], list_[2], list_[1])
            output_rows += rows_.safe_substitute(number=n_, place=p_, temp=t_,
                                                 max1=y_, max2=r_, status=s_, mtime=m_)
            if s_ == 'black-state':
                d_ = u'Нет показаний датчика больше минуты'
                output_diag += diag_.safe_substitute(status=s_, place=p_, state=d_)
            elif s_ == 'yellow-state':
                d_ = u'Подозрительное повышение температуры'
                output_diag += diag_.safe_substitute(status=s_, place=p_, state=d_)
            elif s_ == 'red-state':
                d_ = u'Критическое повышение температуры'
                output_diag += diag_.safe_substitute(status=s_, place=p_, state=d_)
            elif s_ == 'gray-state':
                d_ = u'Неизвестная ошибка'
                output_diag += diag_.safe_substitute(status=s_, place=p_, state=d_)
    elif smb_result == 'ERR_rancid_data':
        output_diag = diag_.safe_substitute(status='red-state',
                                            place=u'OWEN',
                                            state=u'Данные не обновлялись больше двух минут.\nПрограммный сбой на сервере OWEN.')
    elif smb_result == 'ERR_missing_data':
        output_diag = diag_.safe_substitute(status='red-state',
                                            place=u'OWEN',
                                            state=u'Файл с данными отсутствует на сервере OWEN.')
    if len(output_diag) == 0:
        output_diag = diag_.safe_substitute(status='green-state',
                                            place=u'Все датчики',
                                            state=u'Температура в норме')
    return output_rows + output_diag


def write_html(rows=''):
    ''' Записывает файл HTML для отдачи по HTTP. Использует записанные в configowen
        шаблоны HTML-кода и Template для заполнения строк таблицы.
    '''
    with open(c_.HTML_OUTPUT, 'w', encoding='utf-8') as o_:
        o_.write(c_.HTML_HEADER + rows + c_.HTML_FOOTER)


def generate_bitmaps(input_obj_list):
    ''' Создаёт двумерную матрицу для создания PNG-файла по каждому датчику.
        Вертикальный размер картинки = 40px. Масштаб = 4px/градус. Шкалы нет,
        на середине высоты (20px) - уровень среднего значения температуры за
        исторический период (нулевые значения не берутся в расчёт).
        При учитывании случаев резкого изменения показаний с возможным выходом
        за допустимый диапазон пикселей много мудрить не стали, просто обрезаем
        лист сверху до 40 элементов. Всё равно это качественная картинка,
        предназначенная для плавного развития событий.
    '''
    for obj_ in input_obj_list:
        m_list_ = []
        dict_ = obj_.read_data(['sen_num', 'measures'])
        m_zero_ = 0
        m_sum_ = 0
        for m_ in dict_['measures']:
            try:
                if m_['state'] == 'red-state':
                    colorbit_ = '3'
                elif m_['state'] == 'yellow-state':
                    colorbit_ = '2'
                else:
                    colorbit_ = '1'
                m_list_.insert(0, (int(float(m_['value']) * 4), colorbit_))
                m_sum_ += int(float(m_['value']) * 4)
            except:
                m_list_.insert(0, (0, '0'))
                m_zero_ += 1
        average_t_ = int(m_sum_ / (len(m_list_) - m_zero_))

        m_matrix_ = []
        for m_ in m_list_:
            reduced_m_ = m_[0] - average_t_ + 20
            new_list_ = list((m_[1] * reduced_m_) + ('0' * (40 - reduced_m_)))
            new_int_ = [int(x) for x in new_list_]
            m_matrix_.append(new_int_[:40:][::-1])
        transposed_matrix_ = [[m_matrix_[row_][col_] for row_ in range(len(m_matrix_))] for col_ in range(len(m_matrix_[0]))]

        four_colors = [(224, 224, 224), (0, 160, 0), (255, 192, 0), (255, 64, 0)]
        png_file_ = c_.WWW_DIR + str(dict_['sen_num']) + '.png'
        with open(png_file_, 'wb') as f_:
            w = png.Writer(len(transposed_matrix_[0]), len(transposed_matrix_),
                           palette=four_colors, bitdepth=2)
            w.write(f_, transposed_matrix_)


#####=====----- Собственно, сама программа -----=====#####

if __name__ == '__main__':
    get_result = get_current_files()
    if get_result == 'fresh_data':
        current_obj_list = read_json()
        current_obj_list = parse_lastcfg(current_obj_list)
        current_obj_list = parse_lastdata(current_obj_list)
        current_obj_list = set_status(current_obj_list)
        rows_ = generate_html(current_obj_list, smb_result=get_result)
        write_json(current_obj_list)
        generate_bitmaps(current_obj_list)
    else:
        rows_ = generate_html(smb_result=get_result)
    write_html(rows=rows_)

###########################################################################