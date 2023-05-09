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
##### Директория WEB-сервера для размещения HTML
WWW_DIR = '/var/www/html/owen/'

##### Добавки путей к нужным файлам
LAST_DATAFILE = PROJECT_DIR + 'PoC/lastdata.txt'
LAST_CFGFILE = PROJECT_DIR + 'PoC/lastcfg.txt'
JSON_FILE = WWW_DIR + 'history.json'

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
DATA_PATH = 'Last/owen.txt'
CFG_PATH = 'Last/owen.cfg'

##### "True" - для сброса лога на сервер через SYSLOG
USE_SYSLOG = False
SYSLOG_ADDR = '127.0.0.1'
SYSLOG_PORT = 514
##### "True" - для сброса лога в локальный файл (для отладки)
USE_FILELOG = False
FILELOG_PATH = 'logfile.txt'



''' Старые неиспользуемые параметры
'''
##### Добавки путей к нужным файлам
HTML_OUTPUT = WWW_DIR + 'index.html'
##### OWEN отдаёт время MSK, поэтому нужен сдвиг на 5 часов (в секундах)
TZ_SHIFT = 3600.0 * 5
##### Период хранения истории измерений в секундах
HISTORY_LIMIT = 30.0 * 120

HTML_HEADER = '''<!DOCTYPE html>
<HTML LANG="ru">
<HEAD>
    <META CHARSET="utf-8">
    <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=utf-8">
    <META HTTP-EQUIV="Refresh" CONTENT="30">
    <META NAME="viewport" CONTENT="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0">
    <LINK REL="stylesheet" TYPE="text/css" HREF="style.css">
    <TITLE></TITLE>
</HEAD>
<BODY>
    <HEADER></HEADER>
    <MAIN>
        <TABLE>
            <THEAD>
                <TR>
                    <TH>Помещение</TH>
                    <TH>T&nbsp;(&deg;C)</TH>
                    <TH>Max1<BR>(жёлтый)</TH>
                    <TH>Max2<BR>(красный)</TH>
                    <TH>Время<BR>измерения</TH>
                    <TH>История</TH>
                </TR>
            </THEAD>
            <TBODY>
'''

ROW_TEMPLATE = '''                <TR>
                    <TD>$place</TD>
                    <TD class="$state">$temp</TD>
                    <TD>$max1</TD>
                    <TD>$max2</TD>
                    <TD>$mtime</TD>
                    <TD><IMG SRC="$number.png" ALT="Датчик &numero;$number"></TD>
                </TR>
'''

DIAG_TEMPLATE = '''                <TR>
                    <TD COLSPAN="6" class="$state">
                        <SPAN>$place: $diag</SPAN>$alarmbutt
                    </TD>
                </TR>
'''

HTML_FOOTER = '''            </TBODY>
        </TABLE>
    </MAIN>
    <FOOTER></FOOTER>
    <SCRIPT SRC="script.js"></SCRIPT>
</BODY>
</HTML>'''

#####=====----- THE END -----=====########################################