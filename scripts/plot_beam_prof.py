#! / usr / bin / env python
# - * - coding: utf-8 - * -
"""
name: plot_beam_prof
Author Nickalas Reynolds and Patrick Vallely
data: March 2017
"""
# import modules
import os
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import ascii
from scipy.optimize import curve_fit
from scipy import asarray as ar , exp
from scipy.special import yn

# read file
#fname = raw_input("Input master meta filename: ")
fname = "master_meta_sort_23_13.txt"
#fname = "meta_sort_beam_prof_1d_30int_20off_3_13_17.txt"
#fname = "meta_sort_beam_prof_1d_30int_20off_3_13_17_2.txt"
data = ascii.read(fname)
#print data

# splitting data
x1 = []
x2 = []
y1 = []
y2 = []
for i in range(len(data)):
	# azoff
	if data['Azoff'][i] == 0:
		if data['eloff'][i] == 0:
			x1.append(data['Azoff'][i])
			y1.append(data['Tant'][i])
	elif data['Azoff'][i] != 0:
		x1.append(data['Azoff'][i])
		y1.append(data['Tant'][i])
	# eloff
	if data['eloff'][i] == 0:
		if data['Azoff'][i] == 0:
			x2.append(data['eloff'][i])
			y2.append(data['Tant'][i])
	elif data['eloff'][i] != 0:
		x2.append(data['eloff'][i])
		y2.append(data['Tant'][i])
#print(str(len(x1)))
#print(str(len(x2)))
#print(str(len(y1)))
#print(str(len(y2)))

# gaussian
def gaus(x , a , x0 , sigma):
 	return a * exp(-(x-x0) ** 2 / (2 * sigma ** 2))
def bessel2(a , b , var):
 	return yn(a , b * var)

# max for plotting
max_val = 0
for i in range(len(data)):
 	max_val = max(max_val , data['eloff'][i])

# plotting
plt.figure(1)

# azoff
plt.subplot(221)
plt.scatter(x1 , y1 , color = "red" , label = 'Azoff' , marker = 's' , edgecolors = 'none')
mu1 = np.array(y1).mean()
sigma1 = np.array(y1).std()
plt.xlabel('Offset (degrees)' , fontsize = 18)
plt.ylabel('T$_{bol}$ (K)' , fontsize = 18)
popt , pcov = curve_fit(gaus , x1 , y1 , p0 = [1 , mu1 , sigma1])
x1p=np.linspace(-20,20,100)
plt.plot(x1p , gaus(x1p , *popt) , '--' , color = 'red' , label = 'fit')
'''
a = 2
func1 = lambda var1 , b1 : bessel2(a , b1 , var1)
[b] , pcov = curve_fit(func1 , x1 , y1)
print pcov # plt.plot(x1,bessel2(a,*b))
'''
# eloff
plt.subplot(222)
plt.scatter(x2 , y2 , color = "blue" , label = 'eloff' , marker = 's' , edgecolors = 'none')
mu2 = np.array(y2).mean()
sigma2 = np.array(y2).std()
plt.xlabel('Offset (degrees)' , fontsize = 18)
popt2 , pcov2 = curve_fit(gaus , x2 , y2 , p0 = [1 , mu2 , sigma2])
plt.plot(x1p , gaus(x1p , *popt2) , '--' , color = 'blue' , label = 'fit')
plt.savefig('bp_Gaussian_fits.pdf')

plt.show()

#############
# end of code