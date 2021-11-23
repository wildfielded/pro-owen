#!/usr/bin/python3

from time import ctime, mktime, strptime, time
from string import Template
import json
import logging
import logging.handlers as LogHandlers_

from smb.SMBConnection import SMBConnection
import png

import configowen as c_


#####=====----- Классы -----=====#####

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
            'measures': [{'timestamp': 0.0, 'value': 0.0, 'state': 'green-state'}]
            }

    def write_data(self, data_dict: dict={}):
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

    def read_data(self, keys_list: list=[]):
        output_dict = {}
        for key_ in keys_list:
            if key_ in self.sensor_dict.keys():
                output_dict[key_] = self.sensor_dict[key_]
        return output_dict

    def read_one(self, key_str):
        if key_str in self.sensor_dict.keys():
            return self.sensor_dict[key_str]


#####=====----- Настройка логирования -----=====#####

format_ = logging.Formatter('%(name)s %(levelname)s: "%(message)s"')
syslog_ = LogHandlers_.SysLogHandler(address=(c_.SYSLOG_ADDR, c_.SYSLOG_PORT))
syslog_.setLevel(logging.INFO)
syslog_.setFormatter(format_)
logger = logging.getLogger('owen')
logger.setLevel(logging.INFO)
if c_.USE_SYSLOG:
    logger.addHandler(syslog_)
else:
    logger.addHandler(logging.NullHandler())
log_inf = lambda mi_ : logger.info(mi_)
log_err = lambda me_ : logger.error(me_)


#####=====----- Функции -----=====#####

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


def read_json():
    ''' Считывает файл с историческими данными в формате JSON и создаёт на
        их основе список экземпляров (объектов) класса SensorDataBlock
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
        log_err('JSON file is missing or not readable.')
    return output_obj_list


def write_json(input_obj_list):
    ''' Записывает в файл обновлённые исторические данные в формате JSON.
        Предварительно убирает устаревшие измерения, но так, чтобы их
        осталось минимум 2 для корректной обработки включения звуковых
        оповещений.
    '''
    output_obj_list = []
    for obj_ in input_obj_list:
        m_list_ = obj_.sensor_dict['measures']
        for m_ in m_list_[-1::-1]:
            if m_['timestamp'] < time() - c_.HISTORY_LIMIT:
                if len(m_list_) <= 2:
                    break
                m_list_.pop()
        output_obj_list.append(obj_.sensor_dict)
    with open(c_.JSON_FILE, 'w', encoding='utf-8') as f_:
        json.dump(output_obj_list, f_, ensure_ascii=False, indent=2)


def parse_lastcfg(input_obj_list: list=[]):
    ''' Парсит данные из загруженного файла с пороговыми значениями по каждому
        датчику с некоторой валидацией данных и дополняет текущий (или создаёт
        новый) список экземпляров (объектов) класса SensorDataBlock
    '''
    try:
        with open(c_.LAST_CFGFILE, 'r', encoding='utf-8') as f_:
            cfg_list = f_.readlines()
    except UnicodeDecodeError:
        with open(c_.LAST_CFGFILE, 'r', encoding='cp1251') as f_:
            cfg_list = f_.readlines()
        log_err('Config file cp1251-encoded again.')
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
        if not input_obj_list:
            sensor_obj = SensorDataBlock()
            sensor_obj.write_data(dict_)
            output_obj_list.append(sensor_obj)
        else:
            output_obj_list[n_ - 1].write_data(dict_)
    return output_obj_list


def parse_lastdata(input_obj_list: list=[]):
    ''' Парсит данные из загруженного файла с измерениями по каждому датчику
        с некоторой валидацией данных, выставляет состояние в соответствии с
        пороговыми значениями и дополняет текущий (или создаёт новый) список
        экземпляров (объектов) класса SensorDataBlock
    '''
    try:
        with open(c_.LAST_DATAFILE, 'r', encoding='utf-8') as f_:
            data_list = f_.readlines()
    except UnicodeDecodeError:
        with open(c_.LAST_DATAFILE, 'r', encoding='cp1251') as f_:
            data_list = f_.readlines()
        log_err('Data file cp1251-encoded again.')
    output_obj_list = input_obj_list.copy()
    n_ = 0
    for line_ in data_list[1:]:
        n_ += 1
        list_ = line_.strip().split('\t')
        dict_ = {
            'sen_num': n_,
            'place': list_[2],
            }
        t_ = mktime(strptime(' '.join((list_[0], list_[1])), '%d.%m.%Y %H:%M:%S')) + c_.TZ_SHIFT
        try:
            v_ = float(list_[3].replace(',', '.'))
        except:
            if list_[3].startswith('?'):
                v_ = '???'
                s_ = 'black-state'
            else:
                v_ = '!!!'
                s_ = 'gray-state'
        else:
            if v_ < output_obj_list[n_ - 1].sensor_dict['warn_t']:
                s_ = 'green-state'
            elif v_ < output_obj_list[n_ -1].sensor_dict['crit_t']:
                s_ = 'yellow-state'
            else:
                s_ = 'red-state'
        dict_['measures'] = [{'timestamp': t_, 'value': v_, 'state': s_}]
        if not input_obj_list:
            sensor_obj = SensorDataBlock()
            sensor_obj.write_data(dict_)
            output_obj_list.append(sensor_obj)
        else:
            output_obj_list[n_ - 1].write_data(dict_)
    return output_obj_list


def generate_html(input_obj_list: list=[], smb_result=''):
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
            s0_ = dict_['measures'][0]['state']
            try:
                s1_ = dict_['measures'][1]['state']
            except:
                s1_ = 'green-state'
            b_ = ''
            list_ = ctime(dict_['measures'][0]['timestamp']).split()
            m_ = '{} ({} {})'.format(list_[3], list_[2], list_[1])
            output_rows += rows_.safe_substitute(number=n_, place=p_, temp=t_,
                                                 max1=y_, max2=r_,
                                                 state=s0_, mtime=m_)
            if s0_ != 'green-state':
                if s0_ == 'yellow-state':
                    d_ = u'Подозрительное повышение температуры'
                elif s0_ == 'red-state':
                    d_ = u'Критическое повышение температуры'
                elif s0_ == 'black-state':
                    d_ = u'Нет показаний датчика больше минуты'
                elif s0_ == 'gray-state':
                    d_ = u'Неизвестная ошибка'
                else:
                    d_ = u'Неопределённая ошибка'
                if len(dict_['measures']) > 1 and s0_ != s1_:
                    b_ = u'\n                        <BUTTON ID="newalarm" STYLE="display: inline;">Выключить звук</BUTTON>'
                else:
                    b_ = ''
                output_diag += diag_.safe_substitute(state=s0_, place=p_,
                                                     diag=d_, alarmbutt=b_)
                log_err(''.join([p_, ': ', d_]))
    elif smb_result == 'ERR_rancid_data':
        output_diag = diag_.safe_substitute(state='red-state',
                                            place=u'OWEN',
                                            diag=u'Данные не обновлялись больше двух минут.<BR>Программный сбой на сервере OWEN.',
                                            alarmbutt='')
    elif smb_result == 'ERR_missing_data':
        output_diag = diag_.safe_substitute(state='red-state',
                                            place=u'OWEN',
                                            diag=u'Файл с данными отсутствует на сервере OWEN.',
                                            alarmbutt='')
    if not output_diag:
        output_diag = diag_.safe_substitute(state='green-state',
                                            place=u'Все датчики',
                                            diag=u'Температура в норме',
                                            alarmbutt='')
    return output_rows + output_diag


def write_html(rows=''):
    ''' Записывает файл HTML для отдачи по HTTP. Использует заданные в модуле
        configowen шаблоны HTML-кода и Template для заполнения строк таблицы.
    '''
    with open(c_.HTML_OUTPUT, 'w', encoding='utf-8') as h_:
        h_.write(c_.HTML_HEADER + rows + c_.HTML_FOOTER)
    log_inf('HTML file updated.')


def write_png(input_obj_list):
    ''' Самый простой вариант создания графиков.
        Создаёт двумерную матрицу для создания PNG-файла по каждому датчику.
        Вертикальный размер картинки = 40px.  Масштаб = 4px/градус.
        Шкалы нет, на середине высоты (20px) - уровень среднего значения
        температуры за исторический период (нулевые значения не берутся
        в расчёт).
        При учитывании случаев резкого изменения показаний с возможным выходом
        за допустимый диапазон пикселей много мудрить не стали, просто обрезаем
        лист сверху до 40 элементов.  Всё равно это качественная картинка,
        предназначенная для плавного развития событий.
    '''
    for obj_ in input_obj_list:
        dict_ = obj_.read_data(['sen_num', 'measures'])
        if len(dict_['measures']) == 0:
            log_err('write_png -> Sensor #' + str(dict_['sen_num']) + ': No fresh measures.')
            continue
        m_list_ = []
        m_zero_ = 0
        m_sum_ = 0
        for m_ in dict_['measures']:
            try:
                if m_['state'] == 'red-state':
                    colorbit_ = 3
                elif m_['state'] == 'yellow-state':
                    colorbit_ = 2
                else:
                    colorbit_ = 1
                m_list_.insert(0, (int(float(m_['value']) * 4), colorbit_))
                m_sum_ += int(float(m_['value']) * 4)
            except:
                m_list_.insert(0, (0, 0))
                m_zero_ += 1
        try:
            average_t_ = int(m_sum_ / (len(m_list_) - m_zero_))
        except ZeroDivisionError:
            average_t_ = 20
            log_err('write_png -> Division by zero due to all results are _???_')

        m_matrix_ = []
        for m_ in m_list_:
            reduced_m_ = m_[0] - average_t_ + 20
            list_ = [m_[1] for y_ in range(reduced_m_)] + [0 for z_ in range(40 - reduced_m_)]
            int_list_ = [x_ for x_ in list_]
            m_matrix_.append(int_list_[:40:][::-1])
        transposed_matrix_ = [[m_matrix_[row_][col_] for row_ in range(len(m_matrix_))]
                                                  for col_ in range(len(m_matrix_[0]))]

        four_colors = [(224, 224, 224), (0, 160, 0), (255, 192, 0), (255, 64, 0)]
        png_file_ = c_.WWW_DIR + str(dict_['sen_num']) + '.png'
        with open(png_file_, 'wb') as f_:
            p_ = png.Writer(len(transposed_matrix_[0]), len(transposed_matrix_),
                           palette=four_colors, bitdepth=2)
            p_.write(f_, transposed_matrix_)


def write_advpng(input_obj_list):
    ''' Продвинутый вариант создания графиков.
        Создаёт двумерную матрицу для создания PNG-файла по каждому датчику.
        В отличие от предыдущего варианта - вертикальный размер картинки = 60px.
        Масштаб = 2px/градус. Уровень среднего значения остался на высоте 20px.
        Просто сверху добавляется ещё 20px для наглядности - там могут появляться
        жёлтые и красные пороговые уровни температуры.
    '''
    for obj_ in input_obj_list:
        dict_ = obj_.read_data(['sen_num', 'warn_t', 'crit_t', 'measures'])
        if len(dict_['measures']) == 0:
            log_err('write_png -> Sensor #' + str(dict_['sen_num']) + ': No fresh measures.')
            continue
        m_list_ = []
        m_zero_ = 0
        m_sum_ = 0
        yelp_ = int(dict_['warn_t'] * 2)
        redp_ = int(dict_['crit_t'] * 2)
        for m_dict_ in dict_['measures']:
            try:
                if m_dict_['state'] == 'red-state':
                    colorbit_ = 3
                elif m_dict_['state'] == 'yellow-state':
                    colorbit_ = 2
                else:
                    colorbit_ = 1
                m_ = int(m_dict_['value'] * 2)
                m_list_.insert(0, (m_, colorbit_))
                m_sum_ += m_
            except:
                m_list_.insert(0, (0, 0))
                m_zero_ += 1
        try:
            average_t_ = int(m_sum_ / (len(m_list_) - m_zero_))
        except ZeroDivisionError:
            average_t_ = 20
            log_err('write_png -> Division by zero due to all results are _???_')

        m_matrix_ = []
        for m_tup_ in m_list_:
            yel_delta_ = yelp_ - m_tup_[0]
            red_delta_ = redp_ - m_tup_[0]
            reduced_m_ = m_tup_[0] - average_t_ + 20
            list_ = [m_tup_[1] for y_ in range(reduced_m_)] + [0 for z_ in range(60 - reduced_m_)]
            list_len_ = len(list_)
            if reduced_m_ + yel_delta_ < list_len_ - 1:
                yel_pos_ = reduced_m_ + yel_delta_
                list_[yel_pos_] = 2
                list_[yel_pos_ + 1] = 2
            if reduced_m_ + red_delta_ < len(list_) - 1:
                red_pos_ = reduced_m_ + red_delta_
                list_[red_pos_] = 3
                list_[red_pos_ + 1] = 3
            m_matrix_.append(list_[:60:][::-1])
        transposed_matrix_ = [[m_matrix_[row_][col_] for row_ in range(len(m_matrix_))]
                                                  for col_ in range(len(m_matrix_[0]))]

        four_colors = [(224, 224, 224), (0, 160, 0), (255, 192, 0), (255, 64, 0)]
        png_file_ = c_.WWW_DIR + str(dict_['sen_num']) + '.png'
        with open(png_file_, 'wb') as f_:
            p_ = png.Writer(len(transposed_matrix_[0]), len(transposed_matrix_),
                           palette=four_colors, bitdepth=2)
            p_.write(f_, transposed_matrix_)


#####=====----- Собственно, сама программа -----=====#####

if __name__ == '__main__':
    get_result = get_current_files()
    if get_result == 'fresh_data':
        current_obj_list = parse_lastdata(parse_lastcfg(read_json()))
        rows_ = generate_html(current_obj_list, smb_result=get_result)
        write_json(current_obj_list)
        write_advpng(current_obj_list)
    else:
        rows_ = generate_html(smb_result=get_result)
    write_html(rows=rows_)

###########################################################################