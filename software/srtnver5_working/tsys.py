##########
# Calculating tsys and other variables
# Nickalas Reynolds
##########

# importing libraries
import sys

#if sys.version_info < (3,0):
#    print('Incorrect python version, change "input" to "raw_input" to compile with python version < 3.0')
#assert sys.version_info >= (3,0)


# input variables as floats
try:
    phl=float(input('power hot load:'))
except ValueError:
    print('Not a number')
try:
    pcl=float(input('power cold load:'))
except ValueError:
    print('Not a number')
try:
    ht=float(input('Hot Temp:'))
except ValueError:
    print('Not a number')
try:
    ct=float(input('cold tmp:'))
except ValueError:
    print('Not a number')
if ct < 1.0:
    print('Warning, incorrect cold temperature number, less than 1K')
if ct > 10.0:
    print('Warning, incorrect cold temperature number, greater than 10K')
if ht < 100.0:
    print('Warning, incorrect hot temperature number, less than 100K')
if ht > 1000.0:
    print('Warning, incorrect cold temperature number, greater than 1000K')

# formula
yfac=phl/pcl
tsys=(ht-yfac*ct)/(yfac-1.)
print('tsys:',tsys)

gain=phl/(tsys+ht)
print('gain:',gain)
