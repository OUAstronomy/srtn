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

# identifying section to run
while True:
	try:
		answer = int(raw_input("Do you have multiple(or single), single target files(1) or a single file with multiple targets(2): "))
		instring = raw_input("Please input unique identifying string eg gal: ")
	except ValueError:
		print("Please input an integer, 1 or 2.")
		continue
	if (answer != 1) and (answer != 2):
		print("Please input an integer, 1 or 2.")
		continue
	else:
		break

# Read in the files
# ask for identifying string 
outname3 = "master_h1spec_sort_" + instring + ".txt"
delfiles = [f for f in glob.glob("*h1spec*"+instring + "*") if os.path.isfile(f)]
input("Press [RET] to continue. Will delete: " + " | ".join(delfiles))
os.system("rm -vf *h1spec*"  + instring + "* " )
files = [f for f in glob.glob('*'+instring+'*') if os.path.isfile(f)]
all_files = [f for f in glob.glob('*') if os.path.isfile(f)]
backup_files = [f for f in glob.glob('.*') if os.path.isfile(f)]
if ("." + f + ".bak ") in backup_files:
	os.system("mv -vf ." + f + ".bak "  + f)


first_line= []
count = 0
# first section to run
if answer == 1:
	files = [f for f in glob.glob('*' + instring + '*') if os.path.isfile(f)]
	print(files)
	outname_array = []
	for f in files:
		print("Running file: " + f)
		outname0 = "h1spec_"+f
		outname1 = "h1spec_sort_" + f
		os.system("rm -vf " + outname0)
		outname_array.append(outname0)
		os.system("sed -i.bak '/entered/d' " + f)
		lines = [line.strip() for line in f.readlines() if len(line.strip()) != 0]
		os.system("mv -vf " + f + ".bak ." + f + ".bak ")
		beam.spectrum_parse(f,outname0)
		print("Finished file: " + f)
		os.system("cat " + outname0+ " >> " + outname1)
		with open(outname1, 'r') as f:
		    first_line.append(f.readline().strip('\n'))
		os.system("sed -i '1d' " + outname1)

		if count ==0:
			data = ascii.read(outname1)
			#print(data)
			count =1
		else:
			ndata = ascii.read(outname1)
			#print(ndata)
			data.add_columns([ndata['freq'],ndata['vel'],ndata['Tant']],rename_duplicate=True)
		count = 1
	ascii.write(data,outname3)
	with open(outname3, 'r') as original: data = original.read()
	with open(outname3, 'w') as modified: modified.write(' '.join(first_line) + "\n" + data)	

	print("########################")
	print("Finished with all.")
	print("These are the sources processed: " + ' | '.join(first_line))
	print("If single file, then " + outname1 + " | " + outname3 + " are the same.")
	print("Made files: " + ' | '.join(outname_array) + " | " + outname1 + " | " + outname3)	

# second section
else:
	'''
	while True:
		try:
			files = [f for f in glob.glob('*' + instring + '*') if os.path.isfile(f)]
			f = str(files)
		except ValueError:
			continue
	outname_array = []
	print("Running file: " + f)
	activefile = "active_" + f
	bakfile = "backfile_" + f
	os.system("sed -i.bak '/entered/d' " + f)
	lines = [line.strip() for line in f.readlines() if len(line.strip()) != 0]
	os.system("mv -vf " + f + ".bak ." + f + ".bak ")
	filelength = file_len(f)
	os.system("cat " + f + " > " + bakfile)
	outname0 = "h1spec_"+f
	outname1 = "h1spec_sort_" + f
	os.system("rm -vf " + outname0)
	outname_array.append(outname0)
'''

'''
	with open(activefile,'w') as ac:
		with open(bakfile,'r') as bc:
			for fileit,fline in enumerate(bc):
				for nfileit in range(fileit/4)
					if fileit == 1 + 4*nfileit:
						ac.write(fline)
						'''
						'''
	beam.spectrum_parse(active,outname0)
	print("Finished file: " + f)
	os.system("cat " + outname0+ " >> " + outname1)
	with open(outname1, 'r') as f:
	    first_line.append(f.readline().strip('\n'))
	os.system("sed -i '1d' " + outname1)

	if count ==0:
		data = ascii.read(outname1)
		#print(data)
		count =1
	else:
		ndata = ascii.read(outname1)
		#print(ndata)
		data.add_columns([ndata['freq'],ndata['vel'],ndata['Tant']],rename_duplicate=True)
	count = 1
	ascii.write(data,outname3)
	with open(outname3, 'r') as original: data = original.read()
	with open(outname3, 'w') as modified: modified.write(' '.join(first_line) + "\n" + data)	
	os.system("rm -vf " + activefile + " " + bakfile)

	print("########################")
	print("Finished with all.")
	print("These are the sources processed: " + ' | '.join(first_line))
	print("If single file, then " + outname1 + " | " + outname3 + " are the same.")
	print("Made files: " + ' | '.join(outname_array) + " | " + outname1 + " | " + outname3)	

'''

	"Currently not supported. Please separate the sources into individual files and retry."
#############
# end of code