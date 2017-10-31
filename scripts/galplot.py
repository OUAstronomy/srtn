#!/usr/bin/env python
'''
Name  : Galaxy Plotter, galplot.py
Author: Nickalas Reynolds and Patrick Vallely
Date  : Fall 2017
Misc  : Creates plots for timeframes which the galaxy will be above horizon
'''

# import custom modules
from version import *
import utilities
import srtutilities
from colours import colours

# import standard modules
from sys import exit
from argparse import ArgumentParser
import time
import datetime
__today__ = datetime.datetime.today().strftime('%Y-%m-%d')

# import nonstandard modules
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, FK5, get_sun, Galactic
import numpy as np
import matplotlib.pyplot as plt
from astropy.visualization import astropy_mpl_style
plt.style.use(astropy_mpl_style)


# checking python version
assert assertion()
__version__ = package_version()

# main function
if __name__ == "__main__":
    # -----------------------
    # Argument Parser Setup
    # -----------------------
    description = 'Creates plots for the galaxy to tell when certains times are up\n' \
                  '{} Version: {} {}'.format(colours.WARNING,__version__,colours._RST_)

    out_help  = 'Name of output plots'
    log_help  = 'Name of logfile with extension'
    v_help    = 'Integer 1-5 of verbosity level'
    d_help    = 'Date you want to check (default today) YYYY-MM-DD'
    loc_help  = 'Location you want to search, defaults to Norman.\n\
                 Use -w add to add a new location temporarily\n\
                 Call --list to see complete list'
    list_help = 'Complete list of locations stored within the srtutilities.py file'
    show_help = 'Will display the images'

    # Initialize instance of an argument parser
    parser = ArgumentParser(description=description)
    parser.add_argument('-o','--o',type=str, help=out_help,dest='fout')
    parser.add_argument('-l', '--logger',type=str, help=log_help,dest='log')
    parser.add_argument('-v','--verbosity', help=v_help,default=2,dest='verb',type=int)
    parser.add_argument('-d','--date',help=d_help,default=__today__,dest='date')
    parser.add_argument('-w','--where',help=loc_help,default='norman',dest='loca',type=str)
    parser.add_argument('--list',help=list_help,action='store_true',dest='list')
    parser.add_argument('--show',help=show_help,action='store_true',dest='show')

    # Get the arguments
    args          = parser.parse_args()
    outname       = args.fout
    logfile       = args.log
    verbosity     = args.verb
    Date          = args.date
    locationname  = args.loca
    locations     = srtutilities.locations()

    # Set up message logger            
    if not logfile:
        logfile = ('{}_{}.log'.format(__file__[:-3],time.time()))
    if verbosity >= 3:
        logger = utilities.Messenger(verbosity=verbosity, add_timestamp=True,logfile=logfile)
    else:
        logger = utilities.Messenger(verbosity=verbosity, add_timestamp=False,logfile=logfile)
    logger.header1("Starting {}....".format(__file__[:-3]))
    logger.header2('This program will create and remove numerous temporary files for debugging.')
    logger.debug("Commandline Arguments: {}".format(','.join(args)))

    # check location listing
    if args.list:
        logger.success('Locations {}\n'.format(locations.get_locations()))
        exit('Quitting...')

    # check location validity
    # adding a new location first if needed
    if locationname == '' or locationname == None:
        locationname = logger.pyinput('"nameoflocation" or "add" to choose a known location or add a new one')
    elif locationname == 'add':
        newloc = logger.pyinput('a csv of the new location like"{},{}"'\
                                .format('norman','j'.join(locations['norman'])))
        newloc = newloc.split(',')
        locations.add_location(newloc)
        locationname = newloc[0]

    # check date
    if Date == '' or Date == None:
        if verbosity >= 2:
            Date = logger.pyinput('date in format YYY-MM-DD')
        else:
            Date = __today__

    # check output name
    if outname == '' or outname == None:
        if verbosity >= 2:
            outname = logger.pyinput('name of output plots').strip('.py')
        else:
            outname = "galplot_{}".format(__today__)
    else:
        outname = outname.strip('.py')

    # verifying the location exists within dictionary
    if locations.verify_location(locationname):
        fulldict = locations.locations[locationname]
    else:
        logger.warn('Location not found check: \nLocations {}\n'.format(locations.get_locations()))
        exit('Quitting...')

    # now putting into new object
    location = EarthLocation(lat=fulldict[0], lon=fulldict[1], height=fulldict[2]*u.m)
    # setting deg
    b=0*u.degree #galactic latitude
    utcoffset = locations.locations[locationname][3]*u.hour #not 6 since DST in effect

    # defining target
    targcoord0 = Galactic(0*u.degree,b)
    targcoord60= Galactic(60*u.degree,b)
    targcoord120= Galactic(120*u.degree,b)
    targcoord180= Galactic(180*u.degree,b)
    targcoord240= Galactic(240*u.degree,b)
    targcoord300= Galactic(300*u.degree,b)
    targcoord360= Galactic(360*u.degree,b)

    # configuring location and curr time
    time = Time(Date+' 23:00:00') - utcoffset
    midnight = Time(Date+' 00:00:00') - utcoffset
    delta_midnight = np.linspace(-0, 24, 300)*u.hour

    # performing transformation
    frame_obs = AltAz(obstime=midnight+delta_midnight,location=location)
    targaltaz0 = targcoord0.transform_to(frame_obs)
    targaltaz60= targcoord60.transform_to(frame_obs)
    targaltaz120= targcoord120.transform_to(frame_obs)
    targaltaz180= targcoord180.transform_to(frame_obs)
    targaltaz240= targcoord240.transform_to(frame_obs)
    targaltaz300= targcoord300.transform_to(frame_obs)
    targaltaz360= targcoord360.transform_to(frame_obs)

    # plotting
    plt.figure(1,figsize=[10,7]) #allows code to generate and display multiple different plots
    plt.plot(delta_midnight, targaltaz0.alt,'b',label='l=0$^\circ$')
    plt.plot(delta_midnight, targaltaz60.alt,'r',label='l=60$^\circ$')
    plt.plot(delta_midnight, targaltaz120.alt,'g',label='l=120$^\circ$')
    plt.plot([0,24], [20,20], 'k-', lw=2)
    plt.xlim(-0, 24)
    plt.ylim(0, 90)
    plt.xlabel('Hours from CDT Midnight')
    plt.ylabel('Target Altitude (Degrees)')
    plt.legend()
    plt.title('Galactic Coordinate Altitudes')
    plt.draw()
    plt.savefig(outname+'_1.pdf')

    plt.figure(2,figsize=[10,7]) #can call other figures and edit them if desired
    plt.plot(delta_midnight, targaltaz120.alt,'b',label='l=120$^\circ$')
    plt.plot(delta_midnight, targaltaz180.alt,'r',label='l=180$^\circ$')
    plt.plot(delta_midnight, targaltaz240.alt,'g',label='l=240$^\circ$')
    plt.plot([0,24], [20,20], 'k-', lw=2)
    plt.xlim(-0, 24)
    plt.ylim(0, 90)
    plt.xlabel('Hours from CDT Midnight')
    plt.ylabel('Target Altitude (Degrees)')
    plt.legend()
    plt.title('Galactic Coordinate Altitudes')
    plt.draw()
    plt.savefig(outname+'_2.pdf')

    plt.figure(3,figsize=[10,7]) 
    plt.plot(delta_midnight, targaltaz240.alt,'b',label='l=240$^\circ$')
    plt.plot(delta_midnight, targaltaz300.alt,'r',label='l=300$^\circ$')
    plt.plot(delta_midnight, targaltaz360.alt,'g',label='l=360$^\circ$ (0$^\circ$)')
    plt.plot([0,24], [20,20], 'k-', lw=2)
    plt.xlim(-0, 24)
    plt.ylim(0, 90)
    plt.xlabel('Hours from CDT Midnight')
    plt.ylabel('Target Altitude (Degrees)')
    plt.legend()
    plt.title('Galactic Coordinate Altitudes')
    plt.draw()
    plt.savefig(outname+'_3.pdf')

    if args.show:
        plt.show()

    logger.success('Created files: {}_(1-3).py and logger: {}'.format(outname,logfile))
    logger.header1("Finished all")

    #############
    # end of code