#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
name: all_meta_parse
Author Nickalas Reynolds
data: March 2017
"""

# import modules
from __future__ import print_function
import sys
assert sys.version_info >= (2,5)
import HI_spec_parse as beam
import os
import glob
from six.moves import input
from astropy.io import ascii
from astropy.table import Table

# counting function
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def example_data():
    with open('exampledata_hispec.txt','w') as f:
        f.write('DATE 2017:094:10:37:20 obsn  88 az 141 el 45 freq_MHz  1420.4000 Tsys 145.521 Tant 30.670 vlsr  -44.61 glat -0.188 glon 30.118 azoff 0.00 eloff 0.00 source G30.0 \n')
        f.write('Fstart 1419.397 fstop 1421.403 spacing 0.009375 bw    2.400 fbw    2.000 MHz nfreq 256 nsam 5242880 npoint 214 integ    10 sigma    0.479 bsw 0\n')
        f.write('Spectrum      9 integration periods\n')
        f.write('164.961  164.501  164.497  165.814  164.366  163.848  164.425  164.817  163.488  164.782  164.538  164.079  163.664  163.868  164.338  164.150  165.517  164.604  164.075  163.548  165.084  164.829  165.189  165.521  165.451  164.947  165.412  163.895  165.626  163.683  164.459  164.750  163.875  165.257  165.162  164.489  164.263  165.657  163.502  164.054  164.957  164.651  164.733  164.398  164.031  164.324  164.697  165.317  164.973  164.275  166.077  164.760  164.673  164.110  166.978  165.867  164.642  164.824  164.962  165.273  165.753  165.621  165.729  167.135  164.210  164.751  164.203  166.693  164.639  176.660  173.546  169.465  166.164  167.579  166.487  169.384  169.633  170.601  172.471  174.994  176.017  177.545  180.572  181.365  182.896  183.143  184.577  185.640  186.892  185.969  185.614  186.802  185.741  187.221  185.827  185.901  187.812  187.124  185.852  186.538  186.615  186.389  186.351  186.070  185.496  186.945  185.587  186.622  187.048  188.369  189.955  190.190  191.671  192.971  194.455  194.176  193.238  193.596  195.104  195.150  198.364  200.667  203.492  207.231  208.046  208.940  209.183  208.427  208.892  208.529  208.236  206.435  206.914  208.298  210.447  206.715  193.081  185.082  179.708  178.110  176.493  177.906  177.270  179.313  179.512  179.473  179.329  180.017  180.449  181.619  182.544  183.873  185.114  184.562  184.546  184.539  183.961  182.236  180.506  178.029  176.666  173.057  170.991  170.026  169.583  169.160  167.841  168.033  167.912  167.844  167.061  167.916  166.821  168.598  166.980  166.568  167.143  166.933  167.037  166.369  165.921  165.314  167.193  167.039  165.201  166.131  166.984  166.186  166.181  166.151  166.996  166.588  167.031  167.161  167.550  166.579  167.773  166.925  167.155  166.862  166.709  166.519  167.657  169.163  167.458  173.242  173.305  168.885  167.484  168.536  169.431  169.063  167.559  167.845 \n')
        print('Made example file.')
if __name__ == "__main__":
    # identifying section to run
    while True:
        try:
            print('Make sure your file follows the appropriate format in `exampledata_hispec.txt`')
            print('Sometimes data will have the line `* entered azoff 0.000000 eloff 0.000000`, just ignore as this will remove them.')
            tempfiles = [f for f in glob.glob('exampledata_hispec.txt') if os.path.isfile(f)]
            if not tempfiles:
                example_data()
            instring = raw_input("Please input file unique identifying string eg gal: ")
        except ValueError:
            print("Please input an integer, 1 or 2.")
            continue
        if not instring:
            print("Please input a string")
            continue
        else:
            break

    # Read in the files
    # ask for identifying string 
    delfiles = [f for f in glob.glob("*h1spec*"+instring + "*") if os.path.isfile(f)]
    print("Will delete: " + " | ".join(delfiles))
    input("Press [RET] to continue.")
    files = [f for f in glob.glob(instring+'*') if os.path.isfile(f)]

    print('Files to be analyzed: ' + ','.join(files))
    raw_input("Press [RET] to continue")

    origfiles = files
    f = 'TEMPORARY_HISPEC.txt'

    # initialize arrays and constants
    answer = 2
    outname_array = []
    first_line= []      

    for filenum in range(len(files)):
        source_list = []
        position = []
        count = 0
        filenaming = []

        print("Running file: " + origfiles[filenum])
        tmpname = origfiles[filenum].strip('.txt').strip('.dat').strip('.rad')
        os.system('cp -vf ' + origfiles[filenum] + ' ' + f)
        os.system("sed -i '/entered/d' " + f)

        with open(f,'r') as feel:
            k = feel.readlines()

        for i,j in enumerate(k):
            if (i%4) == 0:
                tmp = [x for x in j.strip('\n').split(' ') if x]   
                tmp = tmp[len(tmp)-1]
                source_list.append(tmp)
        print(source_list)
        print(len(source_list))
        for i,j in enumerate(source_list):
            if i != (len(source_list)-1):
                if source_list[i+1] == source_list[i]:
                    if i == (len(source_list)-2):
                        position.append(i+1)
                        i += 1
                else:
                    position.append(i)
                    if i == (len(source_list)-2):
                        position.append(i+1)
                        i += 1
        if len(source_list) == 0:
            position = [0,]
        if not position:
            position = [0,]
        print(position)
        print(source_list)
        for i in position:
            print('Starting source: ' + source_list[i])
            with open(f,'w') as p:
                for j in range(4):
                    p.write(k[4*i + j])
            tmp = source_list[i]
            filenaming.append(source_list[i])

            outname3 = "master_h1spec_" + tmpname + '_s_' + '_'.join(filenaming) + ".txt"
            outname0 = "h1spec_" + source_list[i] + '_'  + f
            outname1 = "h1spec_sort_" + source_list[i] + '_' + f
            os.system("rm -vf " + outname0 + ' ' + outname1 + ' ' + outname3)


            # run beam command
            beam.spectrum_parse(f,outname0)

            # copy to new file and remove sources
            os.system("cat " + outname0+ " >> " + outname1)
            with open(outname1, 'r') as g:
                first_line.append(g.readline().strip('\n'))
            os.system("sed -i '1d' " + outname1)

            # intelligently concat files
            if count == 0:
                pdata = ascii.read(outname1)
                #print(data)
                count = 1
            else:
                ndata = ascii.read(outname1)
                #print(ndata)
                pdata.add_columns([ndata['freq'],ndata['vel'],ndata['Tant']],rename_duplicate=True)
            count = 1

            print("Finished source: " + source_list[i])

        # write outdata
        ascii.write(pdata,outname3)
        with open(outname3, 'r') as original: data = original.read()
        with open(outname3, 'w') as modified: modified.write(' '.join(first_line) + "\n" + data)   
        outname_array.append(outname3)

        print("Finished file: " + origfiles[filenum])
    os.system('rm -vf *' + f)

    # finished
    print("########################")
    print("Finished with all.")
    print("These are the sources processed: " + ' | '.join(first_line))
    
    print("Made files: " + ' | '.join(outname_array))    

    #############
    # end of code