#!/usr/bin/env python
'''
Name  : Plot Beam, plotbeam.py
Author: Nickalas Reynolds
Date  : Fall 2017
Misc  : Will plot the beam profile from the metadata.
'''

# import standard modules
import os
import time
from sys import exit
_TIME_=time.time()
from argparse import ArgumentParser
import pylab
import math

# import nonstandard modules
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import ascii
from scipy import asarray as ar , exp
import scipy.interpolate
from scipy.optimize import curve_fit

# import custom modules
from colours import colours
from version import *
import utilities
from srtutilities import special

# checking python version
assert assertion()
__version__ = package_version()


# main function
if __name__ == "__main__":
    # -----------------------
    # Argument Parser Setup
    # -----------------------
    description = 'Plots the beam profile from the metadata\n' \
                  '{} Version: {} {}'.format(colours.WARNING,__version__,colours._RST_)

    i_help    = 'The input filename with ext'
    f_help    = 'The output filename without ext'
    a_help    = 'If toggled will run the script non interactively'
    log_help  = 'name of logfile with extension'
    v_help    = 'Integer 1-5 of verbosity level'
    dim_help  = 'number of dimensions to be plotted'

    # Initialize instance of an argument parser
    parser = ArgumentParser(description=description)
    parser.add_argument('-i','--input',type=str,help=i_help,dest='fin')
    parser.add_argument('-o','--o',type=str,default=int(_TIME_),help=f_help,dest='fout')
    parser.add_argument('--auto',action="store_true", help=a_help,dest='auto')
    parser.add_argument('-l','--logger',type=str, help=log_help,dest='log')
    parser.add_argument('-v','--verbosity', help=v_help,default=2,dest='verb',type=int)
    parser.add_argument('-d','--dim', help=dim_help,default=1,dest='dim',type=int)

    # Get the arguments
    args       = parser.parse_args()
    inname     = args.fin
    outname    = args.fout
    auto       = args.auto
    logfile    = args.log
    verbosity  = args.verb
    dimensions = args.dim

    print("Program is being worked on...")
    exit()

    # Set up message logger    
    if not logfile:
        logfile = ('{}_{}.log'.format(__file__[:-3],_TIME_))
    if verbosity >= 3:
        logger = utilities.Messenger(verbosity=verbosity, add_timestamp=True,logfile=logfile)
    else:
        logger = utilities.Messenger(verbosity=verbosity, add_timestamp=False,logfile=logfile)
    logger.header1("Starting {}....".format(__file__[:-3]))
    logger.debug("Commandline Arguments: {}".format(args))
    logger.header2('This program will create and remove numerous temporary files for debugging.')

    # if output Line not specified
    while (inname == '') or (not inname):
        try:
            inname = logger.pyinput("filename with ext")
            break
        except ValueError:
            logger.warn("Please input a valid chars.")
            continue
        except IOError:
            logger.warn('File not found, try again')
            continue

    # reading data
    temp = "TEMPORARY_PLOTBEAM_{}".format(_TIME_)
    tempf = "{}.txt".format(temp)
    logger._REMOVE_(temp)
    os.system('cp -f {} {}'.format(inname,tempf))
    count = 0
    while True:
        try:
            if count > 9:
                logger.failure('Failed to read in after 10 attempts')
                exit()
            os.system('sed -i -e "/Made/d" {}'.format(tempf))
            data = ascii.read(tempf,delimiter=' ')
            break
        except IOError:
            os.system('sed -i "1d" {}'.format(tempf))
            count += 1

    # splitting data
    #x = data['azoff'][:]
    x = np.linspace(-10,10,len(data['Tant']))
    x1p=np.linspace(np.min(x),np.max(x),2*len(x))
    #y = data['eloff'][:]
    y = np.linspace(-10,10,len(x))
    y1p=np.linspace(np.min(y),np.max(y),2*len(y))
    z = data['Tant'][:]
    madefiles=[]

    # separate dimension
    if dimensions == 1:

        # plotting
        plt.figure(figsize=[10,7])

        # azoff
        plt.subplot(221)
        plt.scatter(x, z, color = "red" , label = 'Azoff' , marker = 's' , edgecolors = 'none')
        plt.show()
        mu1  = np.average(x)
        sig1 = np.std(x)
        amp1 = np.max(z)
        plt.xlabel('Offset (degrees)')
        plt.ylabel('T$_{bol}$ (K)')
        function = special().gaussian
        popt , pcov = curve_fit(function, x,z, p0 = [mu1,sig1,amp1])
        plt.plot(x1p , function(x1p , *popt) , '--' , color = 'red' , label = 'gaussian fit')
        fwhm = special().fwhm(popt[2])
        logger.message('FWHM for az: {}'.format(fwhm))

        # eloff
        plt.subplot(222)
        plt.scatter(y,z , color = "blue" , label = 'Eloff' , marker = 's' , edgecolors = 'none')
        mu2 = np.average(y)
        sig2 = np.std(y)
        plt.xlabel('Offset (degrees)')
        popt2 , pcov2 = curve_fit(function, y,z , p0 = [mu2,sig2,amp1])
        plt.plot(x1p , function(y1p , *popt2) , '--' , color = 'blue' , label = 'guassian fit')
        fwhm = special().fwhm(popt2[2])
        logger.message('FWHM for el: ' + str(abs(fwhm)))
        plt.legend()
        plt.draw()
        madefiles.append('beam_profile_fit_1d.pdf')
        plt.savefig(file)
        if verbosity >= 2:
            plt.show()

    elif answer == 2:
        print("Brace yourself, this takes awhile...")
        x=[]
        y=[]
        z=[]
        for i in range(len(data)):
            x.append(data['Azoff'][i])
            y.append(data['eloff'][i])
            z.append(data['Tant'][i])
        # Set up a regular grid of interpolation points
        nInterp = 200
        xi, yi = np.linspace(min(x), max(x), nInterp), np.linspace(min(y), max(y), nInterp)
        xi, yi = np.meshgrid(xi, yi)

        # Interpolate; there's also method='cubic' for 2-D data such as here
        #rbf = scipy.interpolate.Rbf(x, y, z, function='linear')
        #zi = rbf(xi, yi)
        zi = scipy.interpolate.griddata((x, y), z, (xi, yi), method='linear')
        zj = scipy.interpolate.griddata((x, y), z, (xi, yi), method='nearest')
        plt.subplot(221)
        plt.imshow(zi, vmin=min(z), vmax=max(z), origin='lower',
                   extent=[min(x), max(x), min(y), max(y)])
        plt.xlabel("Az")
        plt.ylabel("El")        

        plt.subplot(222)
        plt.imshow(zj, vmin=min(z), vmax=max(z), origin='lower',
                   extent=[min(x), max(x), min(y), max(y)])
        plt.xlabel("Az")
        madefile.append('beam_profile_fit_2d.pdf')
        plt.colorbar()
        plt.show()

    logger.success("Finished with file: {}".format(inname))
    logger.header2("Made file(s): {}".format(' | '.join(madefiles)))
    logger._REMOVE_(temp)

#############
# end of code