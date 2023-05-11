#!/usr/bin/python3

import sys
sys.path.append('..')

from OwenCommon.common_func import (get_current_files, read_json, parse_lastcfg,
                                    CONF_DICT)


''' =====----- Функции -----===== '''

def generate_measures():
    pass


def put_current_files():
    ''' Записывает файл с генерированными измерениями на сетевой ресурс
    '''
    pass


''' =====----- MAIN -----=====##### '''
if __name__ == '__main__':
    get_result = get_current_files(**CONF_DICT)
    current_obj_list = parse_lastcfg(read_json(**CONF_DICT), **CONF_DICT)
    print(current_obj_list)

#####=====----- THE END -----=====#########################################