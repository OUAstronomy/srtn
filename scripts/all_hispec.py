#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
name: all_meta_parse
Author Nickalas Reynolds
data: March 2017
"""

# import modules
import HI_spec_parse as beam
import os
import glob

# ask for identifying string 
instring = raw_input("Please input identifying string eg gal: ")
while True:
	try:
		answer = int(raw_input("Do you have multiple, single target files(1) or a single file with multiple targets(2): "))
	except ValueError:
		print("Please input an integer, 1 or 2.")
		continue
	if (answer != 1) and (answer != 2):
		print("Please input an integer, 1 or 2.")
		continue
	else:
		break

# Read in the files
if answer == 1:
	files = [f for f in glob.glob('*' + instring + '*') if os.path.isfile(f)]
	print(files)
	outname="h1spec_gal" + str(len(files)) + ".txt"
	os.system("echo '' > " + outname)

	for f in files:
		print("Running file: " + f)
		beam.spectrum_parse(f,"h1spec_"+f)
		print("Finished file: " + f)
		os.system("cat h1spec_" + f + " >> " + outname)
	print("Finished with all.")

	os.system("sed -i.bak '1d' " + outname)
	with open(outname, 'r') as f:
		first_line = f.readline()

	os.system("sed -i '/entered/d' " + outname)

	with open(outname, 'r') as original: data = original.read()
	with open(outname, 'w') as modified: modified.write(first_line + data)

#############
# end of code