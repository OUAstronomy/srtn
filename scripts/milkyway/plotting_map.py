############
# PLots Position v Velocity v temperature of galaxy
# Nickalas Reynolds
################

# import libraries
from __future__ import print_function
import sys
assert sys.version_info >= (2,5)
import numpy as np
import os
import glob
from astropy.io import ascii
from six.moves import input
from astropy.table import Column,join,Table

# useful filenames
_tempfile_ = 'PLOTTING_TEMPORARY_FILE'
_TEMP_ = 'TEMPORARY'

os.system('rm -vf ' + _tempfile_ + '* ' + _TEMP_)

answer = raw_input('Want to plot with VLSR subtracted or Raw Velocity: [1 or 2 respectively] ')
if answer == '1':
    columnvel = 'vel'
elif answer == '2':
    columnvel = 'vel_sub'

# load files
files = [f for f in glob.glob('*G*') if os.path.isfile(f)]
if _tempfile_ in files: files.remove(_tempfile_)
print('Running on : ' + '|'.join(files))
input('Press [RET] to continue')

temp = [f.replace('_spectra_corr.txt','').split('_') for f in files]
tempname = []
for i in temp:
    tempname.append(i[len(i)-1])


# degrees corresponding to each file
degfile = [ float(x.replace('G','')) for x in tempname ]
for i,x in enumerate(degfile):
    if x > 180.0: 
        degfile[i]=(x-360)

# all degrees of plane
degrees = [float(x*2.5) for x in range(int(360/2.5)+1)]
for i,x in enumerate(degrees):
    if x > 180.0: 
        degrees[i]=(x-360)

returndeg = []

for i in degrees:
    if i not in degfile:
        returndeg.append(i)




print(len(degfile))
print(len(files))
# combining data together
count = 0
mint = 99
maxt = 0


for i,j in enumerate(degfile):
    # intelligently concat files
    print('Starting file: ' + files[i])
    os.system('cp -vf ' + files[i] + ' ' + _TEMP_)
    os.system("sed -i '1,2,3d' " + _TEMP_)
    try:              
        if count == 0:
            pdata = ascii.read(files[i])
            pdata.remove_column('Tant_raw')
            temparray = []
            for k in range(len(pdata[columnvel])):
                temparray.append(j)
            aa = Column(temparray, name='lon')
            pdata.add_column(aa, index=0)
            count = 1
            for lk in pdata['Tant_corr']:
                if mint > lk:
                    mint = lk
                if maxt < lk:
                    maxt = lk        
        elif count == 1:
            ndata = ascii.read(files[i])
            ndata.remove_column('Tant_raw')
            temparray = []
            for k in range(len(ndata[columnvel])):
                temparray.append(j)
            aa = Column(temparray, name='lon')
            ndata.add_column(aa, index=0)
            pdata = join(pdata,ndata, join_type='outer')
            for lk in ndata['Tant_corr']:
                if mint > lk:
                    mint = lk
                if maxt < lk:
                    maxt = lk
        print('Finished file: ' + files[i])
    except ValueError,e:
        print(e)
        raw_input('Press return to view file of problems.')
        os.system('cat ' + files[i])
        raw_input('Press return to view table.')
        print(pdata)
        print("Error on file: " + files[i])
        sys.exit('Quitting Program')
    except KeyError,e:
        print(e)
        raw_input('Press return to view file of problems.')
        os.system('cat ' + files[i])
        raw_input('Press return to view table.')
        print(pdata)
        print("Error on file: " + files[i])
        sys.exit('Quitting Program')



for i,j in enumerate(returndeg):
    kdata = ndata
    ndata.remove_column('lon')
    temparray = []
    for k in range(214):
        temparray.append(j)
    cc = Column(temparray, name='lon')
    kdata.add_column(cc, index=0)
    for i  in range(214):
        kdata['Tant_corr'][i] = mint
    pdata = join(pdata,kdata, join_type='outer')


pdata.sort('lon')
ascii.write(pdata,_tempfile_)
os.system("sed -i 's/lon/#lon/' " + _tempfile_)
os.system("sed -i 's/ /      /g' " + _tempfile_)
os.system('rm -vf ' + _TEMP_)