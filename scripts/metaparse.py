#!/usr/bin/env python
'''
Name  : Metadata Parser, metaparse.py
Author: Nick Reynolds
Date  : Fall 2017
Misc  :
  Command line tool to format SRT metadata files to a human-readable format.
  The current output format is given by the example below:
<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    Made from file: data.txt
    R7 S8 G10
    DATE obsn az el freq_MHz Tsys Tant vlsr glat glon azoff eloff source Fstart fstop spacing bw fbw nfreq nsam npoint integ sigma bsw
    2015:218:16:30:49 0 165 63 1421.5000 162.000 1125.714 8.19 36.980 211.928 0.00 0.00 Sun 1420.497 1422.503 0.009375 2.400 2.000 256 1048576 214 5 0.781 0
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
'''

# import modules
from argparse import ArgumentParser
from os import system as _SYSTEM_
from os.path import isfile as _ISFILE_
from glob import glob
import time

# self defined modules
from version import *
from constants import constants
from colours import colours
import utilities
from srtutilities import *

# checking python version
assert assertion()
__version__ = package_version()


def info_parse(input_file, output_file):
    _SYSTEM_("sed -i 's/ MHz / /g' " + input_file)
    _SYSTEM_("sed -i 's/ integration periods//g' " + input_file)
    with open(input_file, 'r') as f:
        input_data = [[x for x in line.strip('\n').split(' ') if x != ''] for line in f.readlines()]

    #print(input_data[0])

    # full header
    header=[]
    for _T_ in range(3):
        for _R_ in range(len(input_data[_T_])):
            if ((_R_%2)==0) and (input_data[_T_][_R_] != 'Spectrum'):
                header.append(input_data[_T_][_R_])

    #print(header)

    headernum=[]
    for _K_ in range(len(input_data)):
        if ((_K_%4) == 0):
            temp = []
        if ((_K_%4) < 3):
            for _R_ in range(len(input_data[_K_])):
                if ((_R_%2)==1):
                    temp.append(input_data[_K_][_R_])
        if ((_K_%4) == 3):
            headernum.append([item for item in temp])

    #raise RuntimeError('Custom')

    with open(output_file,'w') as f:
        f.write(' '.join(header)+'\n')
        for _I_ in headernum:
            f.write("{}\n".format(' '.join(_I_)))


# main function
if __name__ == "__main__":
    # -----------------------
    # Argument Parser Setup
    # -----------------------
    description = 'Metadata parser to format srtn metadata into a human-readable form.\n' \
                  '{} Version: {} {}'.format(colours.WARNING,__version__,colours._RST_)

    in_help = 'unique string for name of the file/s to parse, no extension'
    f_help    = 'The output file identifying string'
    a_help    = 'If toggled will run the script non interactively'
    log_help  = 'name of logfile with extension'
    v_help    = 'Integer 1-5 of verbosity level'

    # Initialize instance of an argument parser
    parser = ArgumentParser(description=description)
    parser.add_argument('-n', '--input', type=str, help=in_help, dest='infile',default='')
    parser.add_argument('-o','--o',type=str, help=f_help,dest='fout')
    parser.add_argument('--auto',action="store_true", help=a_help,dest='auto')
    parser.add_argument('-l', '--logger',type=str, help=log_help,dest='log')
    parser.add_argument('-v','--verbosity', help=v_help,default=2,dest='verb',type=int)

    # Get the arguments
    args = parser.parse_args()
    instring = args.infile
    tmpname = args.fout
    auto = args.auto
    logfile = args.log
    verbosity = args.verb

    # Set up message logger            
    if not logfile:
        logfile = ('{}_{}.log'.format(__file__[:-3],time.time()))
    if verbosity >= 3:
        logger = utilities.Messenger(verbosity=verbosity, add_timestamp=True,logfile=logfile)
    else:
        logger = utilities.Messenger(verbosity=verbosity, add_timestamp=False,logfile=logfile)
    logger.header1("Starting {}....".format(__file__[:-3]))

    logger.header2('This program will create and remove numerous temporary files for debugging.')
    logger.debug("Commandline Arguments: {}".format(args))
    example_data(logger)

    _TEMP_ = str(time.time())
    _TEMP0_ = 'TEMPORARY_RM_ERROR_'+_TEMP_+'.txt'
    _TEMP1_ = 'TEMPORARY_METADATA_'+_TEMP_+'.txt'
    logger._REMOVE_(_TEMP_)

    # if input file not specified
    while (instring == ''):
        try:
            instring = logger.pyinput("unique identifying input file name")
        except ValueError:
            logger.warn("Please input a valid chars.")
            continue
        if not instring:
            logger.warn("Please input a string")
            continue
        else:
            break

    # if output Line not specified
    while (tmpname == '') or (not tmpname):
        try:
            answer = logger.pyinput("unique output filename string")
        except ValueError:
            logger.warn("Please input a valid chars.")
            continue
        if answer:
            tmpname = answer
            break

    # Read in the files
    delfiles = [f for f in glob("master_metaparse_"+tmpname + "*") if _ISFILE_(f)]
    logger.warn("Will delete:  {}".format(" | ".join(delfiles)))
    logger.waiting(auto)

    origfiles = [f for f in glob(instring+'*') if _ISFILE_(f)]
    if origfiles == []:
        origfiles.append(instring)

    logger.success('Files to be analyzed: {}'.format(','.join(origfiles)))
    logger.waiting(auto)

    logger.waiting(auto)

    logger._REMOVE_(delfiles)
    logger._REMOVE_(_TEMP_)

    for _NUM_,_FILE_ in enumerate(origfiles):
        # starting
        logger.header1('#################################')
        logger.header2("Running file: {}".format(_FILE_))
        k = prep(_FILE_,_TEMP0_)

        # Read in the files    
        outname1="master_metaparse_{}_{}_v{}.txt".format(tmpname,_NUM_,__version__)

        # running parse
        info_parse(_TEMP0_,_TEMP1_)
        logger.success("Finished file: {}".format(_FILE_))
        logger.header1('#################################')

        with open(_TEMP1_, 'r') as original: data = original.read()
        with open(_TEMP1_, 'w') as modified: modified.write('Made from file: {}\n{}'.format(_FILE_ ,data))
        _SYSTEM_("mv -f " + _TEMP1_ + " " + outname1)


    madefiles = [f for f in glob('master_metaparse_' + tmpname+'*') if _ISFILE_(f)]

    logger.success("Finished with all files: {}".format(' | '.join(origfiles)))
    logger.header2("Made file(s): {}".format(' | '.join(madefiles)))
    logger._REMOVE_(_TEMP_)

#############
# end of code