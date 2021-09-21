#!/usr/bin/python3

import config as cfg
from smb.SMBConnection import SMBConnection

file_object = open(cfg.TMP_FILE, 'wb')
conn = SMBConnection(cfg.LOGIN, cfg.PASSWD, cfg.WS_NAME, cfg.SRV_NAME, use_ntlm_v2=True)
conn.connect(cfg.SRV_IP, cfg.SRV_PORT)
result = conn.retrieveFile(cfg.SHARE_NAME, cfg.FILE_PATH, file_object)
print(result)
conn.close()
file_object.close()

###########################################################################