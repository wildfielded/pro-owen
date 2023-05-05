#!/usr/bin/python3

import sys
sys.path.append('..')

# from OwenCommon import common_func as CF_
# from OwenCommon import configowen as CO_
from OwenCommon.common_func import pull_current_files
from OwenCommon import configowen as conf_


''' =====----- MAIN -----=====##### '''
if __name__ == '__main__':
    OWEN_CONN_ATTRS = {
        'login': conf_.LOGIN,
        'passwd': conf_.PASSWD,
        'domain': conf_.DOMAIN,
        'cli_name': conf_.CLI_NAME,
        'srv_name': conf_.SRV_NAME,
        'srv_ip': conf_.SRV_IP,
        'srv_port': conf_.SRV_PORT,
        'share_name': conf_.SHARE_NAME,
        'data_path': conf_.DATA_PATH,
        'cfg_path': conf_.CFG_PATH,
        'last_cfgfile': conf_.LAST_CFGFILE
    }
    pull_current_files(**OWEN_CONN_ATTRS)

#####=====----- THE END -----=====#########################################