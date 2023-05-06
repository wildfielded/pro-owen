#!/usr/bin/python3

import sys
sys.path.append('..')

from OwenCommon.common_func import pull_current_files, OWEN_CONN_PARAMS


''' =====----- MAIN -----=====##### '''
if __name__ == '__main__':
    pull_current_files(**OWEN_CONN_PARAMS)

#####=====----- THE END -----=====#########################################