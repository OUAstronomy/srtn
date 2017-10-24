#!/usr/bin/env python
'''
Name  : Utilities, utilities.py
Author: Nickalas Reynolds
Date  : Fall 2017
Misc  : File will handle misc functions (waiting and input)
'''

# imported modules
from sys import version_info
from os import remove
from os.path import isfile
from glob import glob
assert version_info >= (2,5)
import datetime
import time

# custom modules
from colours import colours


# function that creates a logger
class Messenger(object):
    PY2 = version_info[0] == 2
    PY3 = version_info[0] == 3

    use_structure = ".    "
    def __init__(self, verbosity=2, use_color=True, use_structure=False,add_timestamp=True, logfile=None):
        """
        Initialize the messenger class. Set overall verbosity level,
        use_color, use_structure flags, and add_timestamp flags.
        """
        self.verbosity = verbosity
        self.use_color = use_color
        if use_color:
            self.enable_color()
        else:
            self.disable_color()

        self.use_structure = use_structure
        self.add_timestamp = add_timestamp

        self.logfile = logfile
        if logfile is not None:
            self.f = open(logfile, 'w')  # always overwrites existing files.

    def set_verbosity(self, verbosity):
        self.verbosity = verbosity

    def get_verbosity(self):
        return self.verbosity

    def disable_color(self):
        """
        Turns off all color formatting.
        """
        self.BOLD    = ''
        self.HEADER1 = ''
        self.HEADER2 = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL    = ''
        self.MESSAGE = ''
        self.DEBUG   = ''
        self.CLEAR   = ''

    def enable_color(self):
        """
        Enable all color formatting.
        """
        # Color definitions
        self.BOLD    = colours.BOLD
        self.HEADER1 = self.BOLD + colours.HEADER
        self.HEADER2 = self.BOLD + colours.OKBLUE
        self.OKGREEN = colours.OKGREEN
        self.WARNING = colours.WARNING
        self.FAIL    = colours.FAIL
        self.MESSAGE = colours._RST_
        self.DEBUG   = colours.DEBUG
        self.CLEAR   = colours._RST_

    def _get_structure_string(self, level):
        """
        Returns a string containing the structural part of the message based
        on the integer level provided in the input.
        """

        string = ''
        if self.use_structure:
            for i in range(level):
                string = string + self.structure_string
        return string

    def _get_time_string(self):
        """
        Returns a string containing the structural part of the message based
        on the integer level provided in the input.
        """

        string = ''
        if self.add_timestamp:
            string = '[{}] '.format(datetime.datetime.today()) 
        return string
    
    def _make_full_msg(self, msg, verb_level):
        struct_string = self._get_structure_string(verb_level)
        time_string = self._get_time_string()
        return time_string + struct_string + msg

    def _write(self, cmod, msg,out=True):
        if out:
            print("{}{}{}".format(cmod,msg,self.CLEAR))
        if type(self.logfile) is str:
            self.f.write(msg + '\n')

    # PRINT COMMANDS ##########################################################
    def warn(self, msg, verb_level=0):

        if verb_level <= self.verbosity:
            full_msg = self._make_full_msg(msg, verb_level)
            self._write(self.WARNING, full_msg)

    def header1(self, msg, verb_level=0):

        if verb_level <= self.verbosity:
            full_msg = self._make_full_msg(msg, verb_level)
            self._write(self.HEADER1, full_msg)

    def header2(self, msg, verb_level=1):

        if verb_level <= self.verbosity:
            full_msg = self._make_full_msg(msg, verb_level)
            self._write(self.HEADER2, full_msg)

    def success(self, msg, verb_level=1):

        if verb_level <= self.verbosity:
            full_msg = self._make_full_msg(msg, verb_level)
            self._write(self.OKGREEN, full_msg)

    def failure(self, msg, verb_level=0):

        if verb_level <= self.verbosity:
            full_msg = self._make_full_msg(msg, verb_level)
            self._write(self.FAIL, full_msg)

    def message(self, msg, verb_level=2):

        if verb_level <= self.verbosity:
            full_msg = self._make_full_msg(msg, verb_level)
            self._write(self.MESSAGE, full_msg)

    def debug(self, msg, verb_level=3):

        if verb_level <= self.verbosity:
            full_msg = self._make_full_msg(msg, verb_level)
            self._write(self.DEBUG, full_msg)

    def pyinput(self,message=None,verb_level=0):

        total_Message = "Please input {}: ".format(message)
        if self.PY2:
            out = raw_input(total_Message)
        if self.PY3:
            out = input(total_Message)
        if verb_level <= self.verbosity:  
            full_msg = self._make_full_msg(total_Message, verb_level)
            self._write(self.DEBUG, full_msg,False)      
        return out

    def waiting(self,auto,seconds=10,verb_level=1):
        if not auto:
            self.pyinput('[RET] to continue or CTRL+C to escape')
        elif verb_level <= self.verbosity:  
            self.warn('Will continue in {}s. CTRL+C to escape'.format(seconds))
            time.sleep(seconds)

def _REMOVE_(logger,file):
    for f in glob('*'+file+'*'):
        if isfile(f):
            try:
                remove(f)
                logger.debug("Removed file {}".format(f))
            except OSError:
                logger.debug("Cannot find {} to remove".format(f))


if __name__ == "__main__":
    print('Testing module')
