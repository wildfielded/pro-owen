#!/usr/bin/python3

''' !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    Этот файл "configowen_FAKE.py" надо переименовать в "configowen.py"
    и переопределить переменные под конкретный сервер.
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
'''
''' Набор конфиговин, нужных для настройки работы программ
'''
##### Корневая директория размещения проекта
PROJECT_DIR = '/opt/pet/owen/'
##### Добавки путей к нужным файлам
LAST_DATAFILE = PROJECT_DIR + 'PoC/lastfile.txt'
HTML_HEADER = PROJECT_DIR + 'PoC/sample_h.html'
HTML_MIDDLE = PROJECT_DIR + 'PoC/sample_m.html'
HTML_FOOTER = PROJECT_DIR + 'PoC/sample_f.html'
HTML_SAMPLE = PROJECT_DIR + 'PoC/sample.html'
##### Атрибуты УЗ, под которой идёт обращение на сетевой ресурс сервера OWEN
LOGIN = 'WildDD'
PASSWD = 'password123'
DOMAIN = 'MYDOMAIN'
##### Имя машины, на которой всё это крутится (можно назвать от балды)
CLI_NAME = 'testpc'
##### NetBIOS/AD-имя сервака OWEN и прочие его атрибуты
SRV_NAME = 'CHECKPC'
SRV_IP = '10.10.33.196'
SRV_PORT = 445
SHARE_NAME = 'Owen$'
FILE_PATH = '/owen.txt'
##### OWEN отдаёт время MSK, поэтому нужен сдвиг на 5 часов
TZ_SHIFT = 3600.0 * 5

DICT_TEMPLATE = {
    'ID': 0,
    'place': 'место',
    'yellow_threshold': '25',
    'red_threshold': '35',
    'status': 'normal/yellow/red/old/empty',
    'measures': { 'timestamp': 'float(temp)'}
}

TR_TEMPLATE = '''            <TR>
                <TD>$placement</TD>
                <TD>$temperature</TD>
                <TD></TD>
                <TD></TD>
                <TD></TD>
            </TR>
'''

###########################################################################