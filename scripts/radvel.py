##########
# Calculating new frequency from vslr
# Nickalas Reynolds
##########

import math as m
from sys import version_info
from sys import exit
from argparse import ArgumentParser
__version__="0.0.1"

PY2 = version_info[0] == 2 
PY3 = version_info[0] == 3

_c_ = 299792458. # Speed of light in m/s
_SUPPORTED_ = [('T',10**12),('G',10**9),('M',10**6),('k',10**3),('c',10**(-2)),('m',10**(-3))]

if (not PY2 ) and (not PY3):
    print('Invalid Python Version. Use Python 2 or 3')
    exit()

# main function
if __name__ == "__main__":
    # -----------------------
    # Argument Parser Setup
    # -----------------------
    description = 'Doppler shifts the rest frequency based on the VLSR of source for centering'\
                  'Can input frequency (VLSR) as any power of 10 of Hz(m/s)'\
                  'Example 1420MHz and 4.5km/s'\
                  'Currently Supported: T,G,M,k,c,m'

    in_help = 'Input rest frequency'
    vel_help = 'Input VLSR of source'
    in_def = ''
    vel_def = ''

    # Initialize instance of an argument parser
    parser = ArgumentParser(description=description)
    parser.add_argument('-i', '--input', type=str, help=in_help, dest='rest',default=in_def)
    parser.add_argument('-v', '--vel', type=str, help=vel_help,dest='vlsr',default=vel_def)

    # Get the arguments
    args = parser.parse_args()

    _TEMPRESTFREQ_=args.rest
    _TEMPVLSR_=args.vlsr

    # For parsing the rest frequency input 
    if _TEMPRESTFREQ_ == '':
        # declaring variables
        print('Input rest frequency')
        try:
            if PY2:
                _TEMPRESTFREQ_=raw_input('Restfreq:')
            if PY3:
                _TEMPRESTFREQ_=input('Restfreq: ')
        except ValueError:
            print('Please try again, invalid value.')

    _TEMPAS_=[]
    _TEMPAI_=[]

    for i,j in enumerate(_TEMPRESTFREQ_):
        try:
            _TEMPAI_.append(int(j))
        except ValueError:
            if j != '.':
                _TEMPAS_.append(str(j))
            else:
                _TEMPAI_.append(j)

    restfreq = float(''.join(map(str,_TEMPAI_)))
    freqtype = ''.join(_TEMPAS_)

    counter=-1
    if len(freqtype) > 2:
        counter=0
        for _ITER_ in _SUPPORTED_:
            if freqtype[0] == _ITER_[0]:
                restfreq = restfreq * _ITER_[1]
                freqtype.strip(_ITER_[0])
                counter=1
    elif (len(freqtype) < 2) or (freqtype != 'Hz') or (counter==0):
        print('Incorrect Frequency type input: {}. Currently supporting: ({}) Hz'.format(str(freqtype),','.join(j[0] for j in _SUPPORTED_ if j[0])))
        exit()

    # For parsing the radial velocity input 
    if _TEMPVLSR_ == '':
        # declaring variables
        print('Input known radial velocity')
        try:
            if PY2:
                _TEMPVLSR_=raw_input('Radial velocity:')
            if PY3:
                _TEMPVLSR_=input('Radial velocity: ')
        except ValueError:
            print('Please try again, invalid value.')

    _TEMPAS_=[]
    _TEMPAI_=[]

    for i,j in enumerate(_TEMPVLSR_):
        try:
            _TEMPAI_.append(int(j))
        except ValueError:
            if j != '.':
                _TEMPAS_.append(str(j))
            else:
                _TEMPAI_.append(j)

    radvel = float(''.join(map(str,_TEMPAI_)))
    veltype = ''.join(_TEMPAS_)

    counter=-1
    if len(veltype) > 3:
        counter=0
        for _ITER_ in _SUPPORTED_:
            if veltype[0] == _ITER_[0]:
                radvel = radvel * _ITER_[1]
                veltype.strip(_ITER_[0])
                counter=1

    elif (len(veltype) < 3) or (veltype != 'm/s') or (counter==0):
        print('Incorrect velocity type input: {}. Currently supporting: ({}) m/s'.format(str(veltype),','.join(j[0] for j in _SUPPORTED_ if j[0])))
        exit()

    # forumla
    b=radvel/_c_
    b2=b**2
    g=1/m.sqrt(1-b2)
    newfreq=g*(1-b)*restfreq

    if len(freqtype) > 2:
        _SUPPORTED_ = [('T',10**12),('G',10**9),('M',10**6),('k',10**3),('c',10**(-2)),('m',10**(-3))]
        #_SUPPORTED_ = [['T',10**12],['G',10**9],['M',10**6],['k',10**3],['c',10**(-2)],['m',10**(-3)]]
        for _ITER_ in _SUPPORTED_:
            if freqtype[0] == _ITER_[0]:
                newfreq = newfreq / _ITER_[1]



    # answer
    print('New frequency is: ' + str(newfreq) + ' ' + freqtype)

#############
# end of code
