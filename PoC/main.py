#!/usr/bin/python3

import configowen as c_
from smb.SMBConnection import SMBConnection

def get_tm_data(datafile, login, passwd, domain, client,
                server, addr, port, share, path):
    file_object = open(datafile, 'wb')
    smb_connect = SMBConnection(login, passwd, client, server, domain,
                                use_ntlm_v2=True, is_direct_tcp=True)
    smb_connect.connect(addr, port)
    ##### result = smb_connect.retrieveFile(share, path, file_object)
    smb_connect.retrieveFile(share, path, file_object)
    smb_connect.close()
    file_object.close()
    ##### print(result)

if __name__ == '__main__':
    get_tm_data(c_.LAST_DATAFILE, c_.LOGIN, c_.PASSWD, c_.DOMAIN, c_.CLI_NAME,
                c_.SRV_NAME, c_.SRV_IP, c_.SRV_PORT, c_.SHARE_NAME, c_.FILE_PATH)

###########################################################################