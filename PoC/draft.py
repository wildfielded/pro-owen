#!/usr/bin/python3

import configowen as c_
from smb.SMBConnection import SMBConnection

tmpfile_object = open(c_.TMP_FILE, 'wb')
smb_connect = SMBConnection(c_.LOGIN, c_.PASSWD, c_.WS_NAME, c_.SRV_NAME, c_.DOMAIN, use_ntlm_v2=True, is_direct_tcp=True)
smb_connect.connect(c_.SRV_IP, c_.SRV_PORT)
result = smb_connect.retrieveFile(c_.SHARE_NAME, c_.FILE_PATH, tmpfile_object)
print(result)
smb_connect.close()
tmpfile_object.close()

###########################################################################