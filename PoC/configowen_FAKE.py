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
LAST_DATAFILE = PROJECT_DIR + 'PoC/lastdata.txt'
LAST_CFGFILE = PROJECT_DIR + 'PoC/lastcfg.txt'
HTML_HEADER = PROJECT_DIR + 'PoC/sample_h.html'
HTML_FOOTER = PROJECT_DIR + 'PoC/sample_f.html'
HTML_OUTPUT = PROJECT_DIR + 'PoC/sample.html'
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
DATA_PATH = 'owen.txt'
CFG_PATH = 'owen.cfg'
##### OWEN отдаёт время MSK, поэтому нужен сдвиг на 5 часов (в секундах)
TZ_SHIFT = 3600.0 * 5

ROW_TEMPLATE = '''            <TR>
                <TD>$place</TD>
                <TD>$temp</TD>
                <TD>$max1</TD>
                <TD>$max2</TD>
                <TD>$mtime</TD
                <TD></TD>
            </TR>
'''

###########################################################################