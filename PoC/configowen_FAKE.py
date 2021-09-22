#!/usr/bin/python3

''' This file "configowen_FAKE.py" should be renamed to "configowen.py"
    and constants must be redefined for specific needs.
'''

''' General needed parameters
'''

''' Path to local file where current data should be copied '''
LAST_DATAFILE = '/home/ded/git/wf/pet-owen/PoC/lastdata.txt'
''' Attributes for AD authentication '''
LOGIN = 'WildDD'
PASSWD = 'password123'
DOMAIN = 'MYDOMAIN'
''' Local machine NetBIOS name (may be random) '''
CLI_NAME = 'testpc'
''' Network and share attributes of OWEN server '''
SRV_NAME = 'CHECKPC'
SRV_IP = '10.10.33.196'
SRV_PORT = 445
SHARE_NAME = 'c$'
FILE_PATH = '/Owen/owen.txt'

###########################################################################