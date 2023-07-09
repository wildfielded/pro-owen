#!/usr/bin/python3

from time import ctime, mktime, strptime, time
from string import Template
import json
import logging
import logging.handlers as LH_

#####!!!!! TEMPORAL for VENV working in Windows !!!!!#####
import sys                                           #####
sys.path.append('../VENVemul/Lib/site-packages')     #####
#####!!!!! ------------------------------------ !!!!!#####
from smb.SMBConnection import SMBConnection
import png

from . import configowen as conf_


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

    def get_data(self, keys_list: list) -> dict:
        output_dict_ = {}
        for key_ in keys_list:
            if key_ in self.sensor_dict.keys():
                output_dict_[key_] = self.sensor_dict[key_]
        return output_dict_


''' =====----- Декораторы -----===== '''

def inject_config(*args):
    ''' Универсальный декоратор для передачи в декорируемую функцию всех
    именованных аргументов, импортированных из configowen. Сами
    декорируемые функции способны принимать любой набор именованных
    параметров, из которых используют только нужные. Поэтому если при их
    вызове им нужно передавать дополнительные параметры, они передаются
    как позиционные аргументы.
    '''
    def function_decor(function_to_be_decor):
        def function_wrap(*args):
            CONF_DICT = {
                'www_dir': conf_.WWW_DIR,
                'last_datafile': conf_.LAST_DATAFILE,
                'last_cfgfile': conf_.LAST_CFGFILE,
                'json_file': conf_.JSON_FILE,
                'html_output': conf_.HTML_OUTPUT,
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
                'history_limit': conf_.HISTORY_LIMIT,
                'use_syslog': conf_.USE_SYSLOG,
                'syslog_addr': conf_.SYSLOG_ADDR,
                'syslog_port': conf_.SYSLOG_PORT,
                'use_filelog': conf_.USE_FILELOG,
                'filelog_path': conf_.FILELOG_PATH,
                'html_header': conf_.HTML_HEADER,
                'row_template': conf_.ROW_TEMPLATE,
                'diag_template': conf_.DIAG_TEMPLATE,
                'html_footer': conf_.HTML_FOOTER
            }
            return function_to_be_decor(*args, **CONF_DICT)
        return function_wrap
    return function_decor


''' =====----- Настройка логирования -----===== '''

@inject_config()
def log_setup(use_syslog: bool, syslog_addr: str, syslog_port: int,
              use_filelog: bool, filelog_path: str, **kwargs) -> object:
    ''' Настройка функционала логирования событий
    Keyword Arguments:
        Может принимать весь словарь именованных аргументов.
        Из них использует:
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
    if use_syslog:
        syslog_handler = LH_.SysLogHandler(address=(syslog_addr,
                                                    syslog_port))
        syslog_handler.setLevel(logging.INFO)
        syslog_handler.setFormatter(log_format)
        logger_.addHandler(syslog_handler)
    if use_filelog:
        file_handler = logging.FileHandler(filename=filelog_path,
                                           encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(log_format)
        logger_.addHandler(file_handler)
    else:
        logger_.addHandler(logging.NullHandler())
    return logger_

LOGGER = log_setup()
##### Лямбда-функции используются в других функциях
log_inf = lambda inf_msg_str: LOGGER.info(inf_msg_str)
log_err = lambda err_msg_str: LOGGER.error(err_msg_str)


''' =====----- Функции -----===== '''

@inject_config()
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
    Keyword Arguments:
        Может принимать весь словарь именованных аргументов.
        Из них использует:
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


@inject_config()
def read_json(json_file: str, **kwargs) -> list:
    ''' Считывает файл с историческими данными в формате JSON и создаёт
    на их основе список экземпляров класса SensorDataBlock
    Keyword Arguments:
        Может принимать весь словарь именованных аргументов.
        Из них использует:
        json_file [str] -- Путь к JSON-файлу с историей данныx
    Returns:
        [list] -- Список объектов класса SensorDataBlock
    '''
    output_obj_list_ = []
    try:
        with open(json_file, 'r', encoding='utf-8') as f_:
            history_list_ = json.load(f_)
        for history_dict_ in history_list_:
            sensor_obj_ = SensorDataBlock()
            sensor_obj_.write_data(history_dict_)
            output_obj_list_.append(sensor_obj_)
    except:
        log_err('JSON file is missing or not readable.')
    return output_obj_list_


@inject_config()
def write_json(input_obj_list: list, json_file: str, history_limit: float,
               **kwargs):
    ''' Записывает в файл обновлённые исторические данные в формате
    JSON. Предварительно убирает устаревшие измерения, но так, чтобы их
    осталось минимум 2 для корректной обработки включения звуковых
    оповещений.
    Arguments:
        input_obj_list [list] -- Список объектов класса SensorDataBlock
    Keyword Arguments:
        Может принимать весь словарь именованных аргументов.
        Из них использует:
        json_file [str] -- Путь к JSON-файлу с историей данныx
        history_limit [float] -- Период хранения истории измерений
            в секундах
    Returns:
        None
    '''
    output_obj_list_ = []
    for obj_ in input_obj_list:
        measure_list_ = obj_.sensor_dict['measures']
        for measure_dict_ in measure_list_[-1::-1]:
            if measure_dict_['timestamp'] < time() - history_limit:
                if len(measure_list_) <= 2:
                    break
                measure_list_.pop()
        output_obj_list_.append(obj_.sensor_dict)
    with open(json_file, 'w', encoding='utf-8') as f_:
        json.dump(output_obj_list_, f_, ensure_ascii=False, indent=2)


@inject_config()
def parse_lastcfg(input_obj_list: list, last_cfgfile: str, **kwargs) -> list:
    ''' Парсит данные из загруженного локально файла с пороговыми
    значениями по каждому датчику с некоторой валидацией данных и
    дополняет текущий (или создаёт новый) список экземпляров (объектов)
    класса SensorDataBlock
    Arguments:
        input_obj_list [list] -- Список объектов класса SensorDataBlock
    Keyword Arguments:
        Может принимать весь словарь именованных аргументов.
        Из них использует:
        last_cfgfile [str] -- Путь к локальной копии конфигурационного
            файла
    Returns:
        [list] -- Список объектов класса SensorDataBlock
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


@inject_config()
def parse_lastdata(input_obj_list: list, last_datafile: str, tz_shift: float,
                   **kwargs) -> list:
    ''' Парсит данные из загруженного локально файла с измерениями по
    каждому датчику с некоторой валидацией данных, выставляет состояние
    в соответствии с пороговыми значениями и дополняет текущий (или
    создаёт новый) список экземпляров (объектов) класса SensorDataBlock.
    Arguments:
        input_obj_list [list] -- Список объектов класса SensorDataBlock
    Keyword Arguments:
        Может принимать весь словарь именованных аргументов.
        Из них использует:
        last_datafile [str] -- Путь к локальной копии файла данных
        tz_shift [float] -- Возможный сдвиг по времени на случай, если
            таймзоны системного времени на сервере и на локальной машине
            отличаются. Например, если на сервере OWEN время MSK, а на
            локальной машине IRK, то tz_shift=3600.0*5 (5 часов).
    Returns:
        [list] -- Список объектов класса SensorDataBlock
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


@inject_config()
def generate_html(input_obj_list: list, smb_result: str,
                  row_template: str, diag_template: str, **kwargs) -> str:
    ''' Формирует HTML-код строк таблицы с данными датчиков. Заполняет
    соответствующими значениями по шаблонам ячейки таблиц и итоговый
    статус помещений, выводимый в одной или нескольких строках в конце
    таблицы.
    Arguments:
        input_obj_list [list] -- Список объектов класса SensorDataBlock
        smb_result [str] -- Результат выполнения get_current_files()
    Keyword Arguments:
        Может принимать весь словарь именованных аргументов.
        Из них использует:
        row_template [str] -- Шаблон для заполнения строки таблицы с
            данными отдельного сенсора
        diag_template [str] -- Шаблон для заполнения строки статуса
            помещения
    Returns:
        [str] -- HTML-код (многострочник) для записи в HTML-файл строк
            таблицы с текущими данными и статусом помещений
    '''
    output_rows_ = ''
    output_diag_ = ''
    rows_ = Template(row_template)
    diag_ = Template(diag_template)
    if smb_result == 'fresh_data':
        for obj_ in input_obj_list:
            sensor_dict_ = obj_.sensor_dict
            num_ = str(sensor_dict_['sen_num'])
            place_ = sensor_dict_['place']
            t_ = str(sensor_dict_['measures'][0]['value']).replace('.', ',')
            yellow_t_ = int(sensor_dict_['warn_t'])
            red_t_ = int(sensor_dict_['crit_t'])
            last_state_ = sensor_dict_['measures'][0]['state']
            try:
                prev_state_ = sensor_dict_['measures'][1]['state']
            except:
                prev_state_ = 'green-state'
            button_ = ''
            date_list_ = ctime(sensor_dict_['measures'][0]['timestamp']).split()
            measure_time_ = f'{date_list_[3]} ({date_list_[2]} {date_list_[1]})'
            output_rows_ += rows_.safe_substitute(number=num_,
                                                  place=place_,
                                                  temp=t_,
                                                  max1=yellow_t_,
                                                  max2=red_t_,
                                                  state=last_state_,
                                                  mtime=measure_time_
                                                 )
            if last_state_ != 'green-state':
                if last_state_ == 'yellow-state':
                    diag_msg_ = u'Подозрительное повышение температуры'
                elif last_state_ == 'red-state':
                    diag_msg_ = u'Критическое повышение температуры'
                elif last_state_ == 'black-state':
                    diag_msg_ = u'Нет показаний датчика больше минуты'
                elif last_state_ == 'gray-state':
                    diag_msg_ = u'Неизвестная ошибка'
                else:
                    diag_msg_ = u'Неопределённая ошибка'

                if len(sensor_dict_['measures']) > 1 and last_state_ != prev_state_:
                    button_ = u'\n                        <BUTTON ID="newalarm" STYLE="display: inline;">Выключить звук</BUTTON>'
                else:
                    button_ = ''
                output_diag_ += diag_.safe_substitute(state=last_state_,
                                                      place=place_,
                                                      diag=diag_msg_,
                                                      alarmbutt=button_
                                                     )
                log_err(f'{place_}: {diag_msg_}')
    elif smb_result == 'ERR_rancid_data':
        output_diag_ = diag_.safe_substitute(
            state='red-state',
            place='OWEN',
            diag=u'Данные давно не обновлялись.<BR>Программный сбой на сервере OWEN.',
            alarmbutt=''
            )
    elif smb_result == 'ERR_missing_data':
        output_diag_ = diag_.safe_substitute(
            state='red-state',
            place=u'OWEN',
            diag=u'Файл с данными отсутствует на сервере OWEN.',
            alarmbutt=''
            )
    if not output_diag_:
        output_diag_ = diag_.safe_substitute(
            state='green-state',
            place=u'Все датчики',
            diag=u'Температура в норме',
            alarmbutt=''
            )
    return output_rows_ + output_diag_


@inject_config()
def write_html(rows: str, html_output: str, html_header: str, html_footer: str,
               **kwargs):
    ''' Записывает HTML-файл для отдачи по HTTP. Использует заданные в
    модуле configowen шаблоны HTML-кода.
    Arguments:
        rows -- HTML-код (многострочник) для записи в HTML-файл строк
            таблицы с текущими данными и статусом помещений
    Keyword Arguments:
        Может принимать весь словарь именованных аргументов.
        Из них использует:
        html_output [str] -- Путь к HTML-файлу для отдачи по HTTP
        html_header [str] -- Верхняя часть HTML-кода до табличных строк
            с данными измерений
        html_footer [str] -- Нижняя часть HTML-кода после табличных
            строк с данными измерений
    Returns:
        None
    '''
    with open(html_output, 'w', encoding='utf-8') as h_:
        h_.write(html_header + rows + html_footer)
    log_inf('HTML file updated.')


@inject_config()
def write_png(input_obj_list: list, www_dir: str, **kwargs):
    ''' Создаёт и записывает PNG-файлы с графической историей измерений
    по каждому датчику. Каждый PNG генерится на основе предварительно
    созданной двумерной матрицы. Вертикальный размер картинки -- 60px.
    Вертикальный масштаб -- 2px/градус. На высоте 20px -- уровень
    среднего значения температуры за исторический период (отсутствующие
    значения в расчёт не берутся). При учитывании случаев резкого
    изменения показаний с возможным выходом за допустимый диапазон
    пикселей много мудрить не стали, просто обрезаем пик сверху до 60px.
    Всё равно это качественная картинка, предназначенная для плавного
    развития событий. Поэтому на соответствующем уровне могут появляются
    и исчезать жёлтые и красные линии -- соответствующие пороговые
    уровни температуры.
    Arguments:
        input_obj_list [list] -- Список объектов класса SensorDataBlock
    Keyword Arguments:
        Может принимать весь словарь именованных аргументов.
        Из них использует:
        www_dir -- Путь к директории на вэб-сервере для размещения
            PNG-файлов (там же, где и HTML-файл)
    '''
    for obj_ in input_obj_list:
        sensor_dict_ = obj_.get_data(['sen_num', 'warn_t',
                                      'crit_t', 'measures'])
        if len(sensor_dict_['measures']) == 0:
            log_err(f"write_png() -> Датчик {str(sensor_dict_['sen_num'])}: Нет последних измерений")
            continue
        measure_list_ = []
        zero_cnt_ = 0
        val_sum_ = 0
        yel_level_ = int(sensor_dict_['warn_t'] * 2)
        red_level_ = int(sensor_dict_['crit_t'] * 2)
        # Создание списка значениями и цветом для столбиков пикселей
        for measure_dict_ in sensor_dict_['measures']:
            try:
                if measure_dict_['state'] == 'red-state':
                    colorbit_ = 3
                elif measure_dict_['state'] == 'yellow-state':
                    colorbit_ = 2
                else:
                    colorbit_ = 1
                val_ = int(measure_dict_['value'] * 2)
                measure_list_.insert(0, (val_, colorbit_))
                val_sum_ += val_
            except:
                measure_list_.insert(0, (0, 0))
                zero_cnt_ += 1
        # Задание средней температуры для всей истории
        try:
            average_t_ = int(val_sum_ / (len(measure_list_) - zero_cnt_))
        except ZeroDivisionError:
            average_t_ = 20
            log_err(f'write_png() -> Деление на 0: Все измерения равны "???"')
        # Создание списка списков, или двумерного массива (матрицы)
        # с цветами пикселей в столбце. Тут столбец будущего графика
        # пока пишется списком в строку массива.
        matrix_ = []
        for value_tup_ in measure_list_:
            yel_delta_ = yel_level_ - value_tup_[0]
            red_delta_ = red_level_ - value_tup_[0]
            reduced_t_ = value_tup_[0] - average_t_ + 20
            column_list_ = [value_tup_[1] for x in range(reduced_t_)] \
                           + [0 for y in range(60 - reduced_t_)]
            column_list_len_ = len(column_list_)
            # Два жёлтых пикселя в столбике
            if reduced_t_ + yel_delta_ < column_list_len_ - 1:
                yel_position_ = reduced_t_ + yel_delta_
                column_list_[yel_position_] = 2
                column_list_[yel_position_ + 1] = 2
            # Два красных пикселя в столбике
            if reduced_t_ + red_delta_ < column_list_len_ - 1:
                red_position_ = reduced_t_ + red_delta_
                column_list_[red_position_] = 3
                column_list_[red_position_ + 1] = 3
            matrix_.append(column_list_[:60:][::-1])
        # Поворот матрицы на 90 градусов
        rotated_matrix_ = [
                [matrix_[row_][col_] for row_ in range(len(matrix_))]
                                     for col_ in range(len(matrix_[0]))
            ]
        # Создание и запись PNG-файла
        four_colors_palette_ = [(224, 224, 224),
                                (0, 160, 0),
                                (255, 192, 0),
                                (255, 64, 0)
                               ]
        png_file_ = www_dir + str(sensor_dict_['sen_num']) + '.png'
        with open(png_file_, 'wb') as f_:
            png_ = png.Writer(len(rotated_matrix_[0]), len(rotated_matrix_),
                              palette=four_colors_palette_, bitdepth=2)
            png_.write(f_, rotated_matrix_)

#####=====----- THE END -----=====#########################################