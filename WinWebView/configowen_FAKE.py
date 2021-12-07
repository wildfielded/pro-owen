#!/usr/bin/python3

''' !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    Этот файл "configowen_FAKE.py" надо переименовать в "configowen.py"
    и переопределить переменные под конкретный сервер.
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
'''
''' Набор конфиговин, нужных для настройки работы программ
'''
URL_SRV1 = 'http://10.30.40.122/owen'
URL_SRV2 = 'http://10.30.40.123/owen'

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
</BODY>
</HTML>'''

###########################################################################