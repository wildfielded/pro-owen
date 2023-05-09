#!/usr/bin/python3

import sys
sys.path.append('..')

from OwenCommon.common_func import get_current_files, OWEN_CONN_PARAMS


''' =====----- Функции -----===== '''

def put_current_files():
    '''
    '''
    pass


''' =====----- MAIN -----=====##### '''
if __name__ == '__main__':
    print(get_current_files(**OWEN_CONN_PARAMS))

#####=====----- THE END -----=====#########################################