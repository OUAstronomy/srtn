#!/usr/bin/env python
'''
Name  : Spectrum Parse, specparse.py
Author: Nick Reynolds
Date  : Fall 2017
Misc  :
  Command line tool to format SRT spectrum output data files to a gnuplot-readable format.
  The current output format is given by the example below:
<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    Made from file: data.txt
    R7 S8 G10
    freq vel vel_vlsr Tant freq_1 vel_1 vel_vlsr_1 Tant_1 freq_2 vel_2 vel_vlsr_2 Tant_2
    1419.397 2171.19039917 2131.12039917 145.083 1419.397 2173.46039917 2131.12039917 142.132
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
'''

# self defined modules
from version import *
from constants import constants
from colours import colours
import utilities
from srtutilities import *

# import standard modules
from sys import version_info,exit
from os import system as _SYSTEM_
import select
from argparse import ArgumentParser
from os.path import isfile as _ISFILE_
from glob import glob
import time

# import astropy 
from astropy.io import ascii
from astropy.table import Table

# checking python version
assert assertion()
__version__ = package_version()

# lines to evaluate
LINES = {'H1':1420.406} # linename: MHz
mol_name = ','.join([x for x in LINES])

# constants
c = constants.c/10**5

# parses the data
def spectrum_parse(input_file, _SPEC, output_file):
    """
    Parse out the spectrum data (frequency and pwr)
    :param input_file:
    :param output_file:
    :return:
    """
    # Open the file and extract all the data to a list, split at spaces, and newline stripped
    with open(input_file, 'r') as f:
        data = [[x for x in line.strip('\n').split(' ') if x != ''] for line in f.readlines()]

    length        = len(data[0])-1
    source        = str(data[0][data[0].index('source')+1])
    fstart        = float(data[1][1])   # fstart value for the file (assumes single value per file)
    fstop         = float(data[1][3])    # fstop value for the file (assumes single value per file)
    spacing       = float(data[1][5])  # spacing value for the file (assumes single value per file)
    vlsr          = float(data[0][data[0].index('vlsr') + 1])
    freq_steps    = int(round((fstop - fstart) / spacing))  # get the number of frequency steps
    measure_count = len(data[3])                         # get the number of pwr data points
    azoff         = float(data[0][data[0].index('azoff') + 1])
    eloff         = float(data[0][data[0].index('eloff') + 1])

    # Make sure the number of pwr data points is the same as the expected number of freq steps
    if freq_steps != measure_count:
        raise RuntimeError('Number of frequency steps not equal to number of data points')

    # generate all frequencies
    freqs = [(spacing * i) + fstart for i in range(freq_steps)]

    # get the spectrum data from the data list
    spec_data = data[3::4]

    # for HI spectra, generate a velocity corresponding to each frequency in freqs, for doppler shift
    if not _SPEC:
        q = 1./1420.406 # MHz ^ -1
    elif _SPEC:
        q = 1./_SPEC
    velsub = []
    vels = []
    for r in freqs:
        w = 1./r
        vsrc = c*((w-q)/q)
        velsub.append(round(vsrc-vlsr,5))
        vels.append(round(vsrc,5))

    # write to output file
    with open(output_file, 'w') as f:
        f.write('#! Spawned from File: {} \n'.format(input_file))
        f.write("{}\n".format(source))
        f.write('freq     vel     vel_vlsr     Tant\n')
        for i, freq in enumerate(freqs):
            # get all power values associated with the current frequency
            freq_pwrs = [str(spec[i]) for spec in spec_data]
            # prepend the frequency to the found powers
            freq_pwrs.insert(0, str(freq))
            # ADD VELOCITIES TO COLUMN AFTER FREQ
            freq_pwrs.insert(1, str(vels[i]))
            freq_pwrs.insert(1, str(velsub[i]))
            # set the format spacing to 18 (arbitrarily) to make even columns
            spacing_size = ['25'] * len(freq_pwrs)
            formatter_string = '{:<' + '}{:<'.join(spacing_size) + '}\n'

            # write out line of data to file
            f.write(formatter_string.format(*freq_pwrs))


# main function
if __name__ == "__main__":
    # -----------------------
    # Argument Parser Setup
    # -----------------------
    description = 'Spectra parser to format srtn spectrum data into a gnuplot-readable form. This parses a file ' \
                  'for rotation curve surveys. It prints the column numbers of the last spectrum taken before ' \
                  'the telescope moved to the next point, the velocities associated with frequencies ' \
                  'red/blueshifted from the center freq. of 1420.406 MHz are also calculated.\n' \
                  '{} Version: {} {}'.format(colours.WARNING,__version__,colours._RST_)

    in_help   = 'unique identifier name of the file/s to parse'
    spec_help = 'The Line center for the spectra as string. Defaults to 21cm H1 at 1420.406 MHz '
    f_help    = 'The output file identifying string'
    a_help    = 'If toggled will run the script non interactively'
    log_help  = 'name of logfile with extension'
    v_help    = 'Integer 1-5 of verbosity level'

    # Initialize instance of an argument parser
    parser = ArgumentParser(description=description)
    parser.add_argument('-n', '--input', type=str, help=in_help, dest='infile',required=True)
    parser.add_argument('-s', '--line', type=str, help=spec_help,dest='line',default='H1')
    parser.add_argument('-o','--o',type=str, help=f_help,dest='fout',required=True)
    parser.add_argument('--auto',action="store_true", help=a_help,dest='auto')
    parser.add_argument('-l', '--logger',type=str, help=log_help,dest='log')
    parser.add_argument('-v','--verbosity', help=v_help,default=2,dest='verb',type=int)

    # Get the arguments
    args = parser.parse_args()
    instring = args.infile
    tmpname = args.fout
    _LINE_ = args.line
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
    logger.debug("Commandline Arguments: {}".format(args))

    logger.header2('This program will create and remove numerous temporary files for debugging.')
    example_data(logger)

    _SPECTRA_ = LINES[_LINE_]

    # Read in the files
    delfiles = [f for f in glob("master_specparse_"+tmpname + "*") if _ISFILE_(f)]
    logger.warn("Will delete:  {}".format(" | ".join(delfiles)))
    logger.waiting(auto)
    files = [f for f in glob(instring+'*') if _ISFILE_(f)]
    if files == []:
        files.append(instring)

    logger.success('Files to be analyzed: {}'.format(','.join(files)))
    logger.waiting(auto)

    origfiles = files
    _TEMP_ = str(time.time())
    _TEMP0_ = 'TEMPORARY_RM_ERROR_'+_TEMP_+'.txt'
    _TEMP1_ = 'TEMPORARY_1_SOURCE_'+_TEMP_+'.txt'
    _TEMP2_ = 'TEMPORARY__SOURCES_'+_TEMP_+'.txt'
    logger._REMOVE_(_TEMP_)
    logger._REMOVE_(delfiles)

    # initialize arrays and constants
    all_first = []
    filenaming = []
    count = 0
    first_line= []
    ndata = []
    pdata = []

    # cycle through all files
    for filenum in range(len(files)):
        source_list = []
        position = []
         
        # starting
        logger.header2("#################################")
        logger.message("Running file: {}".format(origfiles[filenum]))
        # creating temp file and removing errors
        k = prep(origfiles[filenum],_TEMP0_)

        # creating source list
        for i,j in enumerate(k):
            if (i%4) == 0:
                tmp = j[j.index('source')+1]
                source_list.append(tmp)
        for i,j in enumerate(source_list):
            if i != (len(source_list)-1):
                if source_list[i+1] == source_list[i]:
                    if i == (len(source_list)-2):
                        position.append(i+1)
                        i += 1
                else:
                    position.append(i)
                    if i == (len(source_list)-2):
                        position.append(i+1)
                        i += 1
        if (len(source_list) == 0) or (not position):
            position = [0,]

        # makes sure to not calculate at stow
        newindex = [i for i,x in enumerate(source_list) if x == 'at_stow']

        for i in position:
            if not i in newindex:
                logger.message('Starting source: {}'.format(source_list[i]))
                with open(_TEMP1_,'w') as p:
                    p.seek(0)
                    for j in range(4):
                        p.write(' '.join(k[4*i + j]))
                        p.write('\n')
                tmp = source_list[i]
                # file handling
                if (i==position[0]) and ((filenum == 0) or (filenum == (len(files)-1))):
                    filenaming.append(source_list[position[0]])

                outname0 = "h1spec_" + source_list[i] + '_'  + _TEMP1_
                outname1 = "h1spec_sort_" + source_list[i] + '_' + _TEMP1_
                logger._REMOVE_(outname0)
                logger._REMOVE_(outname1)

                # run spectrum parse command
                try:
                    spectrum_parse(_TEMP1_,_SPECTRA_,outname0)
                except ValueError:
                    logger.failure('Error running spectrum_parse command on: {} on source: {}'.format(origfiles[filenum],source_list[i]))

                # copy to new file and remove sources
                _SYSTEM_("cp -f " + outname0+ " " + outname1)
                _SYSTEM_("sed -i '1,2d' " + outname1)

                # intelligently concat files
                try:              
                    if count == 0:
                        pdata = ascii.read(outname1)
                        #print(data)
                        count = 1
                    else:
                        ndata = ascii.read(outname1)
                        #print(ndata)
                        pdata.add_columns([ndata['freq'],ndata['vel'],ndata['vel_vlsr'],ndata['Tant']],rename_duplicate=True)
                    count = 1
                except ValueError:
                    logger.failure("Error in concat:")
                    logger.waiting(auto)
                    logger.warn('Check file {}'.format(outname1))
                    exit('Quitting Program')

                logger.success("Finished source: " + source_list[i])
                first_line.append(source_list[i])

        ascii.write(pdata,_TEMP2_)

        logger.success("Finished file: " + origfiles[filenum])
        all_first.append(','.join(first_line))

    outname3 = "master_specparse_" + tmpname + '_s_' + '_'.join(filenaming) + '_v'+ str(__version__) +".txt"

    logger._REMOVE_(outname3)
    with open(_TEMP2_, 'r') as original: data = original.read()
    with open(_TEMP2_, 'w') as modified: modified.write('Made from files: {}\n{}\n{}\n'.format(','.join(files),' '.join(first_line),data))
    _SYSTEM_('cp -f ' + _TEMP2_ + ' ' + outname3)
    logger._REMOVE_(_TEMP_)

    # finished
    logger.header2("#################################")
    logger.success("Finished with all.")
    logger.debug("These are the sources processed: {}".format('|'.join(all_first)))
    
    logger.header1("Made files:  {} and logfile: {}".format(outname3,logfile)) 

    #############
    # end of code
