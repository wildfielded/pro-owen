#!/usr/bin/python3

import sys
sys.path.append('..')

# from OwenCommon import common_func as CF_
# from OwenCommon import configowen as CO_
from OwenCommon.common_func import pull_current_files, OWEN_CONN_PARAMS
# from OwenCommon import configowen as conf_


''' =====----- MAIN -----=====##### '''
if __name__ == '__main__':
    pull_current_files(**OWEN_CONN_PARAMS)

#####=====----- THE END -----=====#########################################