#!/usr/bin/python3

''' !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    Этот файл "configowen_FAKE.py" надо переименовать в "configowen.py"
    и переопределить переменные под конкретный сервер.
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
'''
''' Набор параметров, нужных для настройки работы программ
'''
##### Корневая директория размещения проекта
PROJECT_DIR = '/opt/pet/owen/'
##### Добавки путей к нужным файлам
LAST_DATAFILE = PROJECT_DIR + 'PoC/lastdata.txt'
HTML_HEADER = PROJECT_DIR + 'PoC/sample_h.html'
HTML_FOOTER = PROJECT_DIR + 'PoC/sample_f.html'
HTML_SAMPLE = PROJECT_DIR + 'PoC/sample.html'
##### Атрибуты УЗ, под которой идёт обращение на шару сервера OWEN
LOGIN = 'WildDD'
PASSWD = 'password123'
DOMAIN = 'MYDOMAIN'
##### Имя машины, на которой всё это крутится (можно назвать от балды)
CLI_NAME = 'testpc'
##### NetBIOS/AD-имя сервака OWEN и прочие его атрибуты
SRV_NAME = 'CHECKPC'
SRV_IP = '10.10.33.196'
SRV_PORT = 445
SHARE_NAME = 'c$'
FILE_PATH = '/Owen/owen.txt'

###########################################################################