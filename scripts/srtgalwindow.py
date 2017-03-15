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
from __future__ import print_function
import sys
import os
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz, Galactic
import numpy as np
import matplotlib.pyplot as plt
from astropy.visualization import astropy_mpl_style
#from astropy.utils import iers     # improving precision if needed
#iers.IERS.iers_table = iers.IERS_A.open(iers.IERS_A_URL)

#plt.style.use(astropy_mpl_style)

# solving the date in Norman
l=0 #galactic longitude
b=0 #galactic latitude
Date='2017-3-20'
utcoffset = -5*u.hour #not 6 since DST in effect
norman = EarthLocation(lat='35d13m21.2s', lon='-97d26m22.1s', height=370*u.m)
midnight = Time(Date+' 00:00:00') - utcoffset
div = 15

# preparing file
outname = "srt_gal_time_window.txt"
os.system("rm -f " + outname + '*')
with open(outname,'a') as f,open(outname + ".bak",'a') as f1:
	# solving for gal positions
	f1.write("Fully lists the timeframe where the gal coord will be at certain alt \n")
	f1.write("15 Minute intervals (0.25). Pairs times eg [0.0, 0.5, 11.0, 23.75] is 0000 to 0030 and 1100 to 2345 \n")
	f.write("Lists the timeframe where the gal coord will be at certain alt \n")
	f.write("15 Minute intervals (0.25). Pairs times eg [0.0, 0.5, 11.0, 23.75] is 0000 to 0030 and 1100 to 2345 \n")
	f1.write("\n")
	f.write("\n")
	for j in range(int(360/div)):
		l=(j)*div
		targcoord = Galactic(l*u.degree,b*u.degree)
		alttwenty = []
		altzero = []
		nalttwenty = []
		naltzero = []
		for i in range(96): #15 minute intervals
			frame_obs = AltAz(obstime=midnight+(i*0.25)*u.hour,location=norman)
			targaltaz = targcoord.transform_to(frame_obs)
			
			if targaltaz.alt > 20*u.degree:
				alttwenty.append(i*0.25)
				
			if targaltaz.alt > 0*u.degree:
				altzero.append(i*0.25)
		f1.seek(0)
		f1.write('Times at which gal (l='+str(l)+', b='+str(b)+') is above an altitude of twenty degrees: \n')
		f1.seek(0)
		f1.write(str(alttwenty))
		f1.seek(0)
		f1.write('\nTimes at which gal (l='+str(l)+', b='+str(b)+') is above the horizon: \n')
		f1.seek(0)
		f1.write(str(altzero))
		f1.seek(0)
		f1.write("\n")
		if alttwenty:
			nalttwenty.append(alttwenty[0])
			for i in range(len(alttwenty)-1):
				temp = alttwenty[i]
				if (temp + .25) != alttwenty[i+1]:
					nalttwenty.append(temp)
					nalttwenty.append(alttwenty[i+1])
				if i == len(alttwenty)-2:
					nalttwenty.append(alttwenty[i+1])
			alttwenty = nalttwenty
		if altzero:
			naltzero.append(altzero[0])
			for i in range(len(altzero)-1):
				temp = altzero[i]
				if (temp + .25) != altzero[i+1]:
					naltzero.append(temp)
					naltzero.append(altzero[i+1])
				if i == len(altzero)-2:
					naltzero.append(altzero[i+1])
			altzero = naltzero		
		f.seek(0)
		f.write('Times at which gal (l='+str(l)+', b='+str(b)+') is above an altitude of twenty degrees: \n')
		f.seek(0)
		f.write(str(alttwenty))
		f.seek(0)
		f.write('\nTimes at which gal (l='+str(l)+', b='+str(b)+') is above the horizon: \n')
		f.seek(0)
		f.write(str(altzero))
		f.seek(0)
		f.write("\n")
		print('Progress ' + str(j+1) + ' of ' + str(int(360/div)))
# closing file
	f.close
	f1.close
print("Finished all")

#############
# end of code