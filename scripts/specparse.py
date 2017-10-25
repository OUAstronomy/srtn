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
__version__ = package_version()

# lines to evaluate
LINES = {'H1':1420.406} # linename: MHz
mol_name = ','.join([x for x in LINES])

# constants
c = constants.c/10**4

# creates example data file
def example_data():
    with open('exampledata_hispec.txt','w') as f:
        f.write('DATE 2017:094:10:37:20 obsn  88 az 141 el 45 freq_MHz  1420.4000 Tsys 145.521 Tant 30.670 vlsr  -44.61 glat -0.188 glon 30.118 azoff 0.00 eloff 0.00 source G30.0 \n')
        f.write('Fstart 1419.397 fstop 1421.403 spacing 0.009375 bw    2.400 fbw    2.000 MHz nfreq 256 nsam 5242880 npoint 214 integ    10 sigma    0.479 bsw 0\n')
        f.write('Spectrum      9 integration periods\n')
        f.write('164.961  164.501  164.497  165.814  164.366  163.848  164.425  164.817  163.488  164.782  164.538  164.079  163.664  163.868  164.338  164.150  165.517  164.604  164.075  163.548  165.084  164.829  165.189  165.521  165.451  164.947  165.412  163.895  165.626  163.683  164.459  164.750  163.875  165.257  165.162  164.489  164.263  165.657  163.502  164.054  164.957  164.651  164.733  164.398  164.031  164.324  164.697  165.317  164.973  164.275  166.077  164.760  164.673  164.110  166.978  165.867  164.642  164.824  164.962  165.273  165.753  165.621  165.729  167.135  164.210  164.751  164.203  166.693  164.639  176.660  173.546  169.465  166.164  167.579  166.487  169.384  169.633  170.601  172.471  174.994  176.017  177.545  180.572  181.365  182.896  183.143  184.577  185.640  186.892  185.969  185.614  186.802  185.741  187.221  185.827  185.901  187.812  187.124  185.852  186.538  186.615  186.389  186.351  186.070  185.496  186.945  185.587  186.622  187.048  188.369  189.955  190.190  191.671  192.971  194.455  194.176  193.238  193.596  195.104  195.150  198.364  200.667  203.492  207.231  208.046  208.940  209.183  208.427  208.892  208.529  208.236  206.435  206.914  208.298  210.447  206.715  193.081  185.082  179.708  178.110  176.493  177.906  177.270  179.313  179.512  179.473  179.329  180.017  180.449  181.619  182.544  183.873  185.114  184.562  184.546  184.539  183.961  182.236  180.506  178.029  176.666  173.057  170.991  170.026  169.583  169.160  167.841  168.033  167.912  167.844  167.061  167.916  166.821  168.598  166.980  166.568  167.143  166.933  167.037  166.369  165.921  165.314  167.193  167.039  165.201  166.131  166.984  166.186  166.181  166.151  166.996  166.588  167.031  167.161  167.550  166.579  167.773  166.925  167.155  166.862  166.709  166.519  167.657  169.163  167.458  173.242  173.305  168.885  167.484  168.536  169.431  169.063  167.559  167.845 \n')
        print('Made example file.')

# parses the data
def spectrum_parse(input_file, _SPEC, output_file):
    """
    Parse out the spectrum data (frequency and pwr)
    :param input_file:
    :param output_file:
    :return:
    """
    # Open the file and extract all the data to a list, split at spaces, and newline stripped
    with open(input_file, 'rb') as f:
        data = [filter(None, line.strip('\n').split(' ')) for line in f.readlines()]

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
        velsub.append(vsrc-vlsr)
        vels.append(vsrc)

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
            spacing_size = ['18'] * len(freq_pwrs)
            formatter_string = '{:<' + '}{:<'.join(spacing_size) + '}\n'

            # write out line of data to file
            f.write(formatter_string.format(*freq_pwrs))


# main function
if __name__ == "__main__":
    # -----------------------
    # Argument Parser Setup
    # -----------------------
    description = 'Spectra parser to format srtn spectrum data into a gnuplot-readable form. This parses a file ' \
                  'for rotation curve surveys. it prints the column numbers of the last spectrum taken before ' \
                  'the telescope moved to the next point. the velocities associated with frequencies ' \
                  'red/blueshifted from the center freq. of 1420.406 MHz are also calculated.\n' \
                  '{} Version: {} {}'.format(colours.WARNING,__version__,colours._RST_)

    in_help   = 'name of the file to parse'
    spec_help = 'The Line center for the spectra as string. Defaults to 21cm H1 at 1420.406 MHz '
    f_help    = 'The output file identifying string'
    a_help    = 'If toggled will run the script non interactively'
    log_help  = 'name of logfile with extension'
    v_help    = 'Integer 1-5 of verbosity level'

    # Initialize instance of an argument parser
    parser = ArgumentParser(description=description)
    parser.add_argument('-n', '--input', type=str, help=in_help, dest='infile')
    parser.add_argument('-s', '--line', type=str, help=spec_help,dest='line')
    parser.add_argument('-o','--o',type=str, help=f_help,dest='fout')
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

    logger.header2('Make sure your file follows the appropriate format in `exampledata_hispec.txt`')
    logger.header2('This program will create and remove numerous temporary files for debugging.')
    if not _ISFILE_('exampledata_hispec.txt'):
        example_data()
        logger.warn('Example file no found, Made example file')

    # if input file not specified
    while (instring == '') or (not tmpname):
        try:
            instring = logger.pyinput("unique identifying input file name string")
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

    # if input Line not specified
    while (_LINE_ == '') or (not _LINE_):
        try:
            _LINE_ = logger.pyinput('specific line emission from {} : '.format(mol_name))
            if (_LINE_ == '') or (not _LINE_): # default to H1
                _LINE_ = LINES['H1']
            break
        except ValueError:
            logger.warn('Error with input, try again.')
            continue
        if _LINE_ not in [x for x in LINES]:
            logger.warn('Please enter name exactly.')
            continue
        elif _LINE_ in [x for x in LINES]:
            break
    _SPECTRA_ = LINES[_LINE_]

    # Read in the files
    delfiles = [f for f in glob("*h1spec*"+instring + "*") if _ISFILE_(f)]
    [delfiles.append(f) for f in glob("master*"+tmpname + "*") if _ISFILE_(f)]
    logger.warn("Will delete:  {}".format(" | ".join(delfiles)))
    logger.waiting(auto)
    files = [f for f in glob(instring+'*') if _ISFILE_(f)]

    logger.success('Files to be analyzed: {}'.format(','.join(files)))
    logger.waiting(auto)

    origfiles = files
    _TEMP_ = str(time.time())
    _TEMP0_ = 'TEMPORARY_RM_ERROR_'+_TEMP_+'.txt'
    _TEMP1_ = 'TEMPORARY_1_SOURCE_'+_TEMP_+'.txt'
    _TEMP2_ = 'TEMPORARY__SOURCES_'+_TEMP_+'.txt'
    utilities._REMOVE_(logger,_TEMP_)

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
        _SYSTEM_('cp -f ' + origfiles[filenum] + ' ' + _TEMP0_)
        _SYSTEM_("sed -i '/entered/d' " + _TEMP0_)
        _SYSTEM_("sed -i '/cmd out of limits/d' " + _TEMP0_)
        _SYSTEM_("sed -i '/Scan/d' " + _TEMP0_)

        with open(_TEMP0_,'r') as f:
            f.seek(0)
            _TMPLINE_=f.readline().strip('\n').split(' ')
        if 'azoff' not in _TMPLINE_:  # check if format is correct of file
            _SYSTEM_("sed -i -e 's/source/azoff 0.00 eloff 0.00 source/g' " + _TEMP0_)

        with open(_TEMP0_,'r') as f:
            f.seek(0)
            k = [filter(None, line.strip('\n').split(' ')) for line in f.readlines()]


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
                utilities._REMOVE_(logger,outname0)
                utilities._REMOVE_(logger,outname1)

                # run spectrum parse command
                try:
                    spectrum_parse(_TEMP1_,_SPECTRA_,outname0)
                except ValueError:
                    logger.fail('Error running spectrum_parse command on: {} on source: {}'.format(origfiles[filenum],source_list[i]))

                # copy to new file and remove sources
                _SYSTEM_("cat " + outname0+ " >> " + outname1)
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
                    logger.fail("Error in concat:")
                    print pdata
                    print ndata
                    logger.waiting(auto)
                    logger.warn('Check file {}'.format(outname1))
                    exit('Quitting Program')

                logger.success("Finished source: " + source_list[i])
                first_line.append(source_list[i])

        ascii.write(pdata,_TEMP2_)

        logger.success("Finished file: " + origfiles[filenum])
        all_first.append(','.join(first_line))

    outname3 = "master_h1spec_" + tmpname + '_s_' + '_'.join(filenaming) + '_v'+ str(__version__) +".txt"

    utilities._REMOVE_(logger,outname3)
    with open(_TEMP2_, 'r') as original: data = original.read()
    with open(_TEMP2_, 'w') as modified: modified.write('Made from files: {}\'\n\'{}\'\n\'{}'.format(','.join(files),' '.join(first_line),data))
    _SYSTEM_('cp -f ' + _TEMP2_ + ' ' + outname3)
    utilities._REMOVE_(logger,_TEMP_)

    # finished
    logger.header2("#################################")
    logger.success("Finished with all.")
    logger.debug("These are the sources processed: {}".format(' | '.join(all_first)))
    
    logger.header1("Made files:  {} and logfile: {}".format(outname3,logfile)) 

    #############
    # end of code
