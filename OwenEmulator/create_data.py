#!/usr/bin/python3

import sys
sys.path.append('..')

from OwenCommon.common_func import get_current_files, read_json, CONF_DICT


''' =====----- Функции -----===== '''

def put_current_files():
    '''
    '''
    pass


''' =====----- MAIN -----=====##### '''
if __name__ == '__main__':
    get_result = get_current_files(**CONF_DICT)
    if get_result == 'fresh_data':
        current_obj_list = read_json(**CONF_DICT)

#####=====----- THE END -----=====#########################################