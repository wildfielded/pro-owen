#!/usr/bin/python3

import configowen as c_
from smb.SMBConnection import SMBConnection

def get_last_data(output_file, login, passwd, domain, client,
                server, addr, port, share, path):
    ''' Забирает текущий файл с сервера OWEN и записывает себе локально
    '''
    file_object = open(output_file, 'wb')
    smb_connect = SMBConnection(login, passwd, client, server, domain,
                                use_ntlm_v2=True, is_direct_tcp=True)
    smb_connect.connect(addr, port)
    smb_connect.retrieveFile(share, path, file_object)
    smb_connect.close()
    file_object.close()

def write_html(input_file, output_file, header, footer):
    ''' Записывает демо-файл HTML для отдачи по HTTP
    '''
    file_object = open(header, 'r', encoding='utf-8')
    header_str = file_object.read()
    file_object.close()
    file_object = open(footer, 'r', encoding='utf-8')
    footer_str = file_object.read()
    file_object.close()
    file_object = open(input_file, 'r', encoding='cp1251')
    lastdata_str = file_object.read()
    file_object.close()
    file_object = open(output_file, 'w', encoding='utf-8')
    file_object.write(header_str + lastdata_str + footer_str)
    file_object.close()

if __name__ == '__main__':
    get_last_data(c_.LAST_DATAFILE, c_.LOGIN, c_.PASSWD, c_.DOMAIN, c_.CLI_NAME,
                c_.SRV_NAME, c_.SRV_IP, c_.SRV_PORT, c_.SHARE_NAME, c_.FILE_PATH)
    write_html(c_.LAST_DATAFILE, c_.HTML_SAMPLE, c_.HTML_HEADER, c_.HTML_FOOTER)

###########################################################################