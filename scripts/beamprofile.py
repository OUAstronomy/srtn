#!/usr/bin/env python
'''
Name  : Beam Profiler, beamprofile.py
Author: Nickalas Reynolds
Date  : Fall 2017
Misc  : File will create a command file for the SRT software to handle
'''

# import standard modules
from os.path import isfile as _ISFILE_
import sys
import time
from argparse import ArgumentParser

# import modules
import numpy as np

# import custom modules
from colours import colours
from version import *
import utilities

# checking python version
assert assertion()
__version__ = package_version()

# main function
if __name__ == "__main__":
    # -----------------------
    # Argument Parser Setup
    # -----------------------
    description = 'File will create a command file for the SRT software to handle\n' \
                  '{} Version: {} {}'.format(colours.WARNING,__version__,colours._RST_)

    f_help    = 'The output file identifying string'

    # Initialize instance of an argument parser
    parser = ArgumentParser(description=description)

    # Get the arguments
    args    = parser.parse_args()

    # Read in the files
    fname1 = "beam_profile_1d"
    fname2 = "beam_profile_2d"

    # Set up message logger            
    logfile = ('/tmp/{}_{}.log'.format(__file__[:-3],time.time()))
    logger = utilities.Messenger(add_timestamp=True,logfile=logfile)

    logger.header1("Starting {}....".format(__file__[:-3]))

    delfiles = [f for f in [fname1,fname2] if _ISFILE_(f)]
    logger.warn("Will delete:  {}".format(" | ".join(delfiles)))
    logger.waiting(False)
    logger._REMOVE_(delfiles)

    # make phasespace
    phasespace   = np.linspace(-30.0, 30.0, num=11)
    num = len(phasespace)
    inti = 1

    phasespace2d = np.ndarray((num,num),dtype=tuple)
    for x,y in enumerate(phasespace2d):
        for i,j in enumerate(y):
            phasespace2d[x,i] = (phasespace[x],phasespace[i])

    logger.message('This is estimated to take:\n1d:{}s\n2d:{}s'.format(4*inti*num,inti*num**2))

    ##################
    # making cmd file
    ##################

    # file 1d
    with open('{}_cmd.txt'.format(fname1),'w') as f:
        # horizontal track
        f.write(': Sun\n')
        f.write(': record {}_h.dat\n'.format(fname1))
        for i in phasespace:
            f.write(":{} offset {} 0\n".format(inti,round(i,2)))
        for i in phasespace[::-1]:
            f.write(":{} offset {} 0\n".format(inti,round(i,2)))
        f.write(": roff\n")

        # vertical track
        f.write(': Sun\n')
        f.write(': record {}_v.dat\n'.format(fname1))
        for i in phasespace:
            f.write(":{} offset 0 {}\n".format(inti,round(i,2)))
        for i in phasespace[::-1]:
            f.write(":{} offset 0 {}\n".format(inti,round(i,2)))
        f.write(": roff\n")
        f.write(": stow\n")
    logger.success('Made 1d file')

    # file 2d
    with open('{}_cmd.txt'.format(fname2),'w') as f:
        f.write(': Sun\n')
        f.write(': record {}.dat\n'.format(fname2))
        for x in phasespace2d:
            for i in x:
                f.write(":{} offset {} {}\n".format(inti,round(i[0],1),round(i[1],1)))
        f.write(": roff\n")
        f.write(": stow\n")

    logger.success('Made 2d file')

    # end of code

