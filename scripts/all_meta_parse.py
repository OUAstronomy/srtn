#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
name: all_meta_parse
Author Nickalas Reynolds
data: March 2017
"""

# import modules
from __future__ import print_function
from argparse import ArgumentParser
from sys import version_info
assert version_info >= (2,5)
from os import system as _SYSTEM_
from os.path import isfile as _ISFILE_
from glob import glob
__version__ = "0.1"

PY2 = version_info[0] == 2 
PY3 = version_info[0] == 3

# colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# creates example
def example_data():
    with open('exampledata_metaparse.txt','w') as f:
        f.write('DATE 2017:094:10:37:20 obsn  88 az 141 el 45 freq_MHz  1420.4000 Tsys 145.521 Tant 30.670 vlsr  -44.61 glat -0.188 glon 30.118 azoff 0.00 eloff 0.00 source G30.0 \n')
        f.write('Fstart 1419.397 fstop 1421.403 spacing 0.009375 bw    2.400 fbw    2.000 MHz nfreq 256 nsam 5242880 npoint 214 integ    10 sigma    0.479 bsw 0\n')
        f.write('Spectrum      9 integration periods\n')
        f.write('164.961  164.501  164.497  165.814  164.366  163.848  164.425  164.817  163.488  164.782  164.538  164.079  163.664  163.868  164.338  164.150  165.517  164.604  164.075  163.548  165.084  164.829  165.189  165.521  165.451  164.947  165.412  163.895  165.626  163.683  164.459  164.750  163.875  165.257  165.162  164.489  164.263  165.657  163.502  164.054  164.957  164.651  164.733  164.398  164.031  164.324  164.697  165.317  164.973  164.275  166.077  164.760  164.673  164.110  166.978  165.867  164.642  164.824  164.962  165.273  165.753  165.621  165.729  167.135  164.210  164.751  164.203  166.693  164.639  176.660  173.546  169.465  166.164  167.579  166.487  169.384  169.633  170.601  172.471  174.994  176.017  177.545  180.572  181.365  182.896  183.143  184.577  185.640  186.892  185.969  185.614  186.802  185.741  187.221  185.827  185.901  187.812  187.124  185.852  186.538  186.615  186.389  186.351  186.070  185.496  186.945  185.587  186.622  187.048  188.369  189.955  190.190  191.671  192.971  194.455  194.176  193.238  193.596  195.104  195.150  198.364  200.667  203.492  207.231  208.046  208.940  209.183  208.427  208.892  208.529  208.236  206.435  206.914  208.298  210.447  206.715  193.081  185.082  179.708  178.110  176.493  177.906  177.270  179.313  179.512  179.473  179.329  180.017  180.449  181.619  182.544  183.873  185.114  184.562  184.546  184.539  183.961  182.236  180.506  178.029  176.666  173.057  170.991  170.026  169.583  169.160  167.841  168.033  167.912  167.844  167.061  167.916  166.821  168.598  166.980  166.568  167.143  166.933  167.037  166.369  165.921  165.314  167.193  167.039  165.201  166.131  166.984  166.186  166.181  166.151  166.996  166.588  167.031  167.161  167.550  166.579  167.773  166.925  167.155  166.862  166.709  166.519  167.657  169.163  167.458  173.242  173.305  168.885  167.484  168.536  169.431  169.063  167.559  167.845 \n')
        print('Made example file.')


def info_parse(input_file, output_file):
    _SYSTEM_("sed -i 's/ MHz / /g' " + input_file)
    _SYSTEM_("sed -i 's/ integration periods//g' " + input_file)
    with open(input_file, 'rb') as f:
        input_data = [filter(None, line.replace('\n', '').split(' ')) for line in f.readlines()]


    # full header
    header=[]
    for _T_ in range(2):
        for _R_ in range(len(input_data[_T_])):
            if ((_R_%2)==0):
                header.append(input_data[_T_][_R_])

    headernum=[]

    for _K_ in range(len(input_data)):
        if ((_K_%4) < 3):
            for _R_ in range(len(input_data[_K_])):
                if ((_R_%2)==1):
                    headernum.append(input_data[_K_][_R_])
        if (_K_ == 2):
            headernum.append('\n')


    with open(output_file,'w') as f:
        f.write(' '.join(header)+'\n')
        for _I_ in headernum:
            f.write("%s " % _I_)


# main function
if __name__ == "__main__":
    # -----------------------
    # Argument Parser Setup
    # -----------------------
    description = 'parser to format srtn raw data into a gnuplot-readable form ' \
                  'Version: ' + __version__

    in_help = 'unique string for name of the file to parse, no extension'

    # Initialize instance of an argument parser
    parser = ArgumentParser(description=description)
    parser.add_argument('-n', '--input', type=str, help=in_help, dest='infile',default='')

    # Get the arguments
    args = parser.parse_args()
    instring = args.infile

    print('Make sure your file follows the appropriate format in `exampledata_metaparse.txt`')
    tempfiles = [f for f in glob('exampledata_metaparse.txt') if _ISFILE_(f)]
    if not tempfiles:
        example_data()

    TEMPSTRING='TEMPORARY_META_'
    _SYSTEM_(TEMPSTRING+'*')
    _TEMP0_ = TEMPSTRING+'_0.txt'
    _TEMP1_ = TEMPSTRING+'_1.txt'


    # if input file not specified
    while (instring == ''):
        try:
            instring = raw_input("Please input file unique identifying string (no extension): e.g. gal: ")
        except ValueError:
            print("Please input a valid chars.")
            continue
        if not instring:
            print("Please input a string")
            continue
        else:
            break

    # input files
    origfiles = [f for f in glob(instring+'*') if _ISFILE_(f)]

    print('Reading in files: {}'.format(origfiles))

    delfiles = [f for f in glob("master_meta*"+instring + "*") if _ISFILE_(f)]
    print("Will delete: " + bcolors.FAIL + " | ".join(delfiles) + bcolors.ENDC)
    if PY2:
        raw_input("Press [RET] to continue.")
    elif PY3:
        input("Press [RET] to continue.")
    _SYSTEM_('rm -vf ' + TEMPSTRING + '* ' + ' '.join(delfiles))

    for _NUM_,_FILE_ in enumerate(origfiles):
        # starting
        print('#################################')
        print("Running file: " + _FILE_)
        _SYSTEM_('cp -vf ' + _FILE_ + ' ' + _TEMP0_)

        # Read in the files    
        outname1="master_meta_" + instring + '_' + str(_NUM_) + ".txt"

        # running parse
        info_parse(_TEMP0_,_TEMP1_)
        print("Finished file: " + _FILE_)
        print('#################################')

        with open(_TEMP1_, 'r') as original: data = original.read()
        with open(_TEMP1_, 'w') as modified: modified.write('all_meta_parse.py version: ' + str(__version__) + '\n Made from file: ' + _FILE_ + '\n'+ data) 
        _SYSTEM_("mv -vf " + _TEMP1_ + " " + outname1)


    madefiles = [f for f in glob('master*' + instring+'*') if _ISFILE_(f)]

    print("Finished with all files:"  + ' | '.join(origfiles))
    print("Made file(s): " + bcolors.OKGREEN + ' | '.join(madefiles) + bcolors.ENDC)
    _SYSTEM_('rm -vf ' + TEMPSTRING + '* ')
    print('#################################')

#############
# end of code