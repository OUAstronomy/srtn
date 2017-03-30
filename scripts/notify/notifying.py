#!/usr/bin/python
'''
provide notification on vnc window
Nickalas Reynolds
29 March 2017
'''

# import libraries
from __future__ import print_function
import glob
import os

# input file variables
# _db='.notify_feed' # urgent message
_db='notify_new'
_dc='notify_def' # backup message

# checking existance
all_files = [f for f in glob.glob('*notify*') if os.path.isfile(f)]

# try reading database file
if _db in all_files:
    with open(_db,'r') as f:
        _db_lines = f.read().splitlines()
        _db_answer = _db_lines[0]
        _db_message = _db_lines[1]
        # if the notify not needed, read other file
        if ((_db_answer == "n") or (_db_answer == "N")):
            with open(_dc,'r') as g:
                _dc_lines = g.read().splitlines()
                _dc_answer = _dc_lines[0]
                _dc_message = _dc_lines[1]
                # see if notify is needed for backup
                if ((_dc_answer == "Y") or (_dc_answer == "y")):
                    os.system("notify-send -u normal \"" + _dc_message +"\"" )
        # run command if notify needed
        elif ((_db_answer == "Y") or (_db_answer == "y")):
            os.system("notify-send -u critical \"" + _db_message +"\"" )

# if database file didnt exist, try backup
elif _dc in all_files:
    with open(_dc,'r') as g:
        _db_lines = g.read().splitlines()
        _db_answer = _dc_lines[0]
        _db_message = _dc_lines[1]
        if ((_db_answer == "Y") or (_db_answer == "y")):
            os.system("notify-send -u normal \"" + _db_message +"\"" )

#############
# end of code
