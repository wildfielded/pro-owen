#!/usr/bin/python3

''' Набор конфиговин, нужных для настройки работы программ
'''
DEFAULT_CONF = {
    'FILES': {},
    'NETWORK': {
        'srv1_url': 'http://10.30.40.122/owen/',
        'srv2_url': 'http://10.30.40.123/owen/',
        },
    'LOGGING': {},
    'SAMBA': {},
    'PARAMETERS': {},
    }

HTML_HEADER = '''<!DOCTYPE html>
<HTML LANG="ru">
<HEAD>
    <META CHARSET="utf-8">
    <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=utf-8">
    <META HTTP-EQUIV="Refresh" CONTENT="30">
    <META NAME="viewport" CONTENT="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0">
    <STYLE>
        body {
            font-family: Arial, sans-serif;
        }
        table,
        td,
        th {
            border-collapse: collapse;
            border-style: solid;
            border-width: 1px;
            padding: 0 10px 0 10px;
        }
        th {
            text-align: center;
        }
        td:nth-of-type(n+2) {
            text-align: center;
        }
        .green-state {
            background-color: #bbffbb;
        }
        .yellow-state {
            background-color: #ffff88;
            font-weight: 700;
        }
        .red-state {
            background-color: #ff0000;
            color: #ffffff;
            font-weight: 700;
        }
        .gray-state {
            background-color: #775533;
            color: #ffffff;
            font-weight: 700;
        }
        .black-state {
            background-color: #000000;
            color: #ffffff;
            font-weight: 700;
        }
    </STYLE>
    <TITLE>OWEN Temperatures</TITLE>
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