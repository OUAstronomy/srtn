from astropy.time import Time
import os
from astropy.table import Table
from astropy.io import ascii

input_file='master_meta_active_0.txt'

TEMP='temp.txt'

os.system('cp -vf ' + input_file + ' ' + TEMP) 

os.system('sed -i "1,2d" ' + TEMP)

pdata = ascii.read(TEMP)


origtime = Time(pdata[0][0])
origtime.format = 'yday'
for _NUM_,_VAL_ in enumerate(pdata):
    newtime = Time(pdata[_NUM_][0])
    newtime.format = 'yday'
    pdata[_NUM_][0] =  round((newtime - origtime).value*86400, 3)

