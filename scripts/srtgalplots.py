# coding: utf-8
'''
Creates srt_gal_time_window.txt file which houses
	the raw time outputs for when certain coordinates 
	will rise
Orig Author: Patrick Vallely
Adapted by: Nickalas Reynolds
Date: March 2017
'''

# import modules
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, FK5, get_sun, Galactic
import numpy as np
import matplotlib.pyplot as plt
from astropy.visualization import astropy_mpl_style
#plt.style.use(astropy_mpl_style)

# setting deg
b=0*u.degree #galactic latitude

# configuring date
Date='2017-3-20'
utcoffset = -5*u.hour #not 6 since DST in effect

# defining target
targcoord0 = Galactic(0*u.degree,b)
targcoord60= Galactic(60*u.degree,b)
targcoord120= Galactic(120*u.degree,b)
targcoord180= Galactic(180*u.degree,b)
targcoord240= Galactic(240*u.degree,b)
targcoord300= Galactic(300*u.degree,b)
targcoord360= Galactic(360*u.degree,b)

# configuring location and curr time
norman = EarthLocation(lat='35d13m21.2s', lon='-97d26m22.1s', height=370*u.m)
time = Time(Date+' 23:00:00') - utcoffset
midnight = Time(Date+' 00:00:00') - utcoffset
delta_midnight = np.linspace(-0, 24, 300)*u.hour

# performing transformation
frame_obs = AltAz(obstime=midnight+delta_midnight,location=norman)
targaltaz0 = targcoord0.transform_to(frame_obs)
targaltaz60= targcoord60.transform_to(frame_obs)
targaltaz120= targcoord120.transform_to(frame_obs)
targaltaz180= targcoord180.transform_to(frame_obs)
targaltaz240= targcoord240.transform_to(frame_obs)
targaltaz300= targcoord300.transform_to(frame_obs)
targaltaz360= targcoord360.transform_to(frame_obs)

# plotting
plt.figure(1) #allows code to generate and display multiple different plots
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

plt.figure(2) #can call other figures and edit them if desired
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

plt.figure(3) 
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

plt.show()

print("Finished all")

#############
# end of code