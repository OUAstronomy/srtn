##########
# Calculating new frequency from radial velocity
##########

# import libraries
import math as m

# declaring variables
print('Input rest frequency in MHz')
try:
	restfreq=float(input('Restfreq (MHz):'))
except ValueError:
	print('Not a number')
print('Input known radial velocity in km/s')
try:
	radvel=float(input('Radial Velocity (km/s):'))
except ValueError:
	print('Not a number')

# formula
c=299792.458 # km/s
b=radvel/c
b2=b**2
g=1/m.sqrt(1-b2)
newfreq=g*(1-b)*restfreq

# output
print 'New frequency is:' + str(newfreq) + 'MHz'

# end-of-code
