#!/usr/bin/python2
###########################
# Create user and directory
# Nickalas Reynolds
# 2017 May 6
###########################

# import modules
from os.path import isdir as _ISDIR_
from os import system as _SYSTEM_
from sys import version_info
from sys import exit
from argparse import ArgumentParser
from time import strftime

# constants
_HOME_ = '/home/jjtobin'
_SRTDIR_ = _HOME_ + '/srtn'
_DATADIR_ = _SRTDIR_ + '/data'
_LOGDIR_ = _HOME_ + '/logs'
_ORIGDIR5 = _SRTDIR_ + '/.srt_program/srtnver5_working'
_ORIGDIR6 = _SRTDIR_ + '/.srt_program/srtnver6_working'
_CODER_ = 'Nick Reynolds, nickreynolds@ou.edu, NH406'
_CURR_TIME_ = '{}'.format(strftime("%Y_%B_%d"))
PY2 = version_info[0] == 2 
PY3 = version_info[0] == 3

if (not PY2 ) and (not PY3):
    print('Invalid Python Version. Use Python 2 or 3')
    exit()

# define functions
def _makedir(_NAME_): # makes directory
    proc = '_makedir'
    _count_ = 0
    while True:
        try:
            _count_ +=1
            _SYSTEM_('mkdir -v ' + _NAME_)
        except ValueError:
            print('Failed to make the directory')
            _writelog(proc,args,_TMP_USER_,_TMP_)
            exit()
        except SystemError:
            print('Failed to make the directory')
            _writelog(proc,args,_TMP_USER_,_TMP_)
            exit()
        except BaseException:
            print('Failed to make the directory')
            _writelog(proc,args,_TMP_USER_,_TMP_)
            exit()
        if _ISDIR_(_NAME_):
            break
        if _count_ >= 10:
            _writelog(proc,args,_TMP_USER_,_TMP_)
            print('Error occured since mkdir failed 10 times.')
            print('Potentially a major error with file naming.\n Retry with a different filename.\nThis error will be output to the log but also inform the main coder <' + _CODER_ +'>\n')
            exit()
    return _NAME_

def _chkdir(_NAME_): # checks for directory uniqueness
    if _ISDIR_(_NAME_):
        return True
    elif not _ISDIR_(_NAME_):
        return False

def _makeinit(_DIR_,_USER_): # creates the init file
    with open(_DIR_,'w') as f:
        f.write('# Init File \n')
        f.write('# Lines with # or * or // are ignored \n')
        f.write('# Follow the following example lines \n')
        f.write('# Name of observers \n')
        f.write('# Project/Group \n')
        f.write('# Position (Grad/Professor) \n')
        f.write('# Semester of Observation \n')
        f.write('# \n')
        f.write(_USER_ + '\n')
        f.write(_USER_ + '\n')
        f.write('Undergrad/Graduate Students \n')
        f.write(_CURR_TIME_ + '\n')

    return True

def _popdir(_NAME_): # populates the final directory
    _SYSTEM_('cp -vrf ' + _ORIGDIR + '/* ' + _NAME_ + '/')
    _SYSTEM_('ln -s ' + _DATADIR_ + ' ' + _NAME_ + '/')
    return True

def _writelog(_PROC_,args,_TMP_USER_,_TMP_):
    _LOG = _LOGDIR_ + '/' + _CURR_TIME_+ '.log'
    with open(_LOG,'w') as g:
        g.write('Log was created on: ' + _CURR_TIME_ + '\n')
        g.write('Failed on process: ' + _PROC_ + '\n')
        g.write('User/group: ' + _TMP_USER_ + '\n')
        g.write('Directory: ' + _TMP_ + '\n')
        g.write('Fed arguments: ' + args)
    print('Created log file at ' + _LOG)

# main function
if __name__ == "__main__":

    # -----------------------
    # Argument Parser Setup
    # -----------------------
    description = 'This code will create the proper directory structure and link appropriate files.' \
                  'Will prompt user for input and if none given, will detault name.' \

    dir_help = 'Name of directory to create.'
    name_help = 'Name of observer or group.'
    version = 'Version of the SRT program to use.'

    # Initialize instance of an argument parser
    parser = ArgumentParser(description=description)

    parser.add_argument('--o', help=dir_help,dest='output')
    parser.add_argument('--u', help=name_help,dest='user')
    parser.add_argument('--n', help=version,dest='version')


    # Get the arguments
    args = parser.parse_args()
    _TEMP_OUT_= args.output
    _TMP_USER_= args.user
    _TMP_VER_=args.version

    # ask for file and check for existance
    fcounter = 0
    print('Please do not use \\ in this code. Results can be...unpredictable.')
    while True:
        try:
            if not _TMP_USER_:
                if PY2 and (fcounter == 0):
                    _TMP_USER_ = raw_input('Please input your name or group name: ').strip(' ').strip('\\')
                    fcounter = 1
                elif PY3 and (fcounter == 0):  
                    _TMP_USER_ = input('Please input your name or group name: ').strip(' ').strip('\\')
                    fcounter = 1
            if not _TEMP_OUT_:
                if PY2:
                    _TMP_ = raw_input('Please input a unique directory you wish to have: ').strip(' ').strip('\\')
                elif PY3:
                    _TMP_ = input('Please input a unique directory you wish to have: ').strip(' ').strip('\\')
            elif _TEMP_OUT_:
                _TMP_ = _TEMP_OUT_
                _TEMP_OUT_ = ''
            if not _TMP_VER_:
                if PY2:
                    _TMP_VER_ = raw_input('Please input srt version you wish to have [5,6]: ').strip(' ').strip('\\')
                elif PY3:
                    _TMP_VER_ = input('Please input srt version you wish to have [5,6]: ').strip(' ').strip('\\')
            _TMP_ = _SRTDIR_ + '/' + _TMP_
            if _chkdir(_TMP_):
                print('Invalid directory! Please input a new directory name.')
                continue
            elif not _chkdir(_TMP_):
                break
        except SystemExit:
            _writelog(proc,args,_TMP_USER_,_TMP_)
            print('Cancelled program, did not make any directories or files.')
    while True:
        try:
            if _TMP_VER_ == '5':
                _ORIGDIR = _ORIGDIR5
            elif _TMP_VER_ == '6':
                _ORIGDIR = _ORIGDIR6
            else:
                _ORIGDIR = _ORIGDIR5
            _OUTPUT_DIR_ = _makedir(_TMP_)
            _INIT_ = _OUTPUT_DIR_ + '/observer.init'
            _makeinit(_INIT_,_TMP_USER_)
            _popdir(_OUTPUT_DIR_)
        except TypeError:
            try:
                if _OUTPUT_DIR_:
                    _SYSTEM_('rm -vf ' + _OUTPUT_DIR_ + '/*')
                    _SYSTEM_('rmdir -vf ' + _OUTPUT_DIR_)
            except NameError:
                continue
            print('Failed at creation...Retrying')
            continue
        except KeyboardInterrupt:
            try:
                if _OUTPUT_DIR_:
                    _SYSTEM_('rm -vf ' + _OUTPUT_DIR_ + '/*')
                    _SYSTEM_('rmdir -vf ' + _OUTPUT_DIR_)
            except NameError:
                continue
            print('Failed at creation...Retrying')
            continue
        except NameError:
            print('Failed at creation...Retrying')
            continue
        if _OUTPUT_DIR_ and _INIT_:
            break


    print('Made the directory <' + _OUTPUT_DIR_ + '> and \n the observer file <' + _INIT_ + '>\n For the user/group <' + _TMP_USER_ + '>\n')
    print('Finished all. Exiting program.')
    exit()
