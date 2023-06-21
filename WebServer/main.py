#!/usr/bin/python3

import sys
sys.path.append('..')
#####!!!!! TEMPORAL for VENV working in Windows !!!!!#####
sys.path.append('../VENVemul/Lib/site-packages')     #####
#####!!!!! ------------------------------------ !!!!!#####
from smb.SMBConnection import SMBConnection

from OwenCommon.common_func import (log_inf, log_err, get_current_files,
                                    parse_lastdata, parse_lastcfg,
                                    read_json, write_json, generate_html)

''' =====----- MAIN -----===== '''
if __name__ == '__main__':
    get_result = get_current_files()
    if get_result == 'fresh_data':
        current_obj_list = parse_lastdata(parse_lastcfg(read_json()))
        rows_ = generate_html(current_obj_list, get_result)
        write_json(current_obj_list)
        ##### write_png(current_obj_list)
    else:
        ##### rows_ = generate_html(smb_result=get_result)
        pass
    ##### write_html(rows=rows_)

#####=====----- THE END -----=====#########################################