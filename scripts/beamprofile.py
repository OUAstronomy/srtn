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
    a_help    = 'If toggled will run the script non interactively'
    log_help  = 'name of logfile with extension'
    v_help    = 'Integer 1-5 of verbosity level'
    num_help  = 'resolution of the beam you want'
    deg_help  = 'number of degrees max away from the sun (>=20)'

    # Initialize instance of an argument parser
    parser = ArgumentParser(description=description)
    parser.add_argument('-o','--o',type=str,default=int(time.time()),help=f_help,dest='fout')
    parser.add_argument('--auto',action="store_true", help=a_help,dest='auto')
    parser.add_argument('-l','--logger',type=str, help=log_help,dest='log')
    parser.add_argument('-v','--verbosity', help=v_help,default=2,dest='verb',type=int)
    parser.add_argument('-d','--degrees', help=deg_help,default=20,dest='deg',type=int)
    parser.add_argument('-n','--number', help=num_help,default=2,dest='num',type=int)

    # Get the arguments
    args      = parser.parse_args()
    outname   = args.fout
    auto      = args.auto
    logfile   = args.log
    verbosity = args.verb
    number    = args.num
    degrees   = args.deg


    # Set up message logger    
    if not logfile:
        logfile = ('{}_{}.log'.format(__file__[:-3],time.time()))
    if verbosity >= 3:
        logger = utilities.Messenger(verbosity=verbosity, add_timestamp=True,logfile=logfile)
    else:
        logger = utilities.Messenger(verbosity=verbosity, add_timestamp=False,logfile=logfile)
    logger.header1("Starting {}....".format(__file__[:-3]))
    logger.debug("Commandline Arguments: {}".format(args))

    logger.header2('This program will create and remove numerous temporary files for debugging.')

    # if output Line not specified
    while (outname == '') or (not outname):
        try:
            answer = logger.pyinput("unique output filename string (no ext)")
        except ValueError:
            logger.warn("Please input a valid chars.")
            continue
        if answer:
            outname = answer
            break

    # if degrees < 20
    while (degrees < 20) or (not degrees):
        try:
            answer = int(logger.pyinput("number of degrees away from sun"))
        except ValueError:
            logger.warn("Please input a valid chars.")
            continue
        if answer:
            degrees = answer
            break

    # Read in the files
    fname1 = "beam_profile_command_1d_{}.txt".format(outname)
    fname2 = "beam_profile_command_2d_{}.txt".format(outname)
    fname3 = "beam_profile_1d_{}.txt".format(outname)
    fname4 = "beam_profile_2d_{}.txt".format(outname)

    delfiles = [f for f in [fname1,fname2] if _ISFILE_(f)]
    logger.warn("Will delete:  {}".format(" | ".join(delfiles)))
    logger.waiting(auto)
    logger._REMOVE_(delfiles)

    # make phasespace
    phasespace = np.linspace(-degrees,degrees,int(2*degrees/number))
    inti = 1

    logger.message('This is estimated to take:\n1d:{}s\n2d:{}s'.format(2*inti*len(phasespace),inti*len(phasespace)**2))

    ##################
    # making cmd file
    ##################
    # file 1d
    with open(fname1,'w') as f:
        f.write(': Sun\n')
        f.write(': record {}\n'.format(fname3))
        for i in phasespace:
            f.write(":{} offset {} {}\n".format(inti,0,round(i,2)))
        for i in phasespace:
            if i != 0:
                f.write(":{} offset {} {}\n".format(inti,round(i,2),0))   
        f.write(": roff\n")
        f.write(": stow\n")

    logger.success('Made 1d file')

    # file 2d
    count = False
    with open(fname2,'w') as f:
        f.write(': Sun\n')
        f.write(': record {}\n'.format(fname4))
        for i in phasespace:
            for j in phasespace:
                if (j !=0) and (i != 0) and (count != True):
                    f.write(":{} offset {} {}\n".format(inti,round(i,2),round(j,2)))
                else:
                    f.write(":{} offset {} {}\n".format(inti,round(i,2),round(j,2)))
                    count = True 
        f.write(": roff\n")
        f.write(": stow\n")

    logger.success('Made 2d file')

    # end of code

