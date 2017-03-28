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
import meta_parse
import os
import glob

# ask for identifying string 
while True:
	try:
		answer = raw_input("Do you have multiple, single target files(1) or running beam profiling(2): ")
	except ValueError:
		print("Please input an integer, 1 2")
		continue
	if (int(answer) != 1) and (int(answer) != 2):
		print("Please input an integer, 1 2.")
		continue
	else:
		break

# Read in the files
if int(answer) == 1:
	print("Will restore any *.bak file to the original if it exists.")
	print("This assumes your file has Azoff, eloff, Tant in columns 12,13,8 respectively.")
	instring = raw_input("Please input unique identifying string. Will read all files with this string in it eg gal will read beam_gal.cat and gal_1.txt: ")
	outname3 = "master_meta_sort_" + instring + ".txt"
	outname1="meta_sort_" + instring + ".txt"
	os.system("rm -vf "  + outname1 + "* "  + outname3 + "* " )
	all_files = [f for f in glob.glob('*') if os.path.isfile(f)]
	backup_files = [f for f in glob.glob('.*') if os.path.isfile(f)]
	files = [f for f in glob.glob('*'+instring+'*') if os.path.isfile(f)]
	print(files)

	outname_array=[]
	for f in files:
		outname0="meta_"+f
		outname_array.append(outname0)
		print("########################")
		if ("." + f + ".bak ") in backup_files:
			os.system("mv -vf ." + f + ".bak "  + f)
		os.system("sed -i.bak '/entered/d' " + f)
		os.system("mv -vf " + f + ".bak ." + f + ".bak ")

		print("Running file: " + f)
		meta_parse.info_parse(f,outname0)
		print("Finished file: " + f)
		os.system("cat " + outname0+ " >> " + outname1)

	os.system("sed -i '1d' " + outname1)
	with open(outname1, 'r') as f:
	    first_line = f.readline()

	os.system("sed -i '/DATE/d' " + outname1)
	with open(outname1, 'r') as original: data = original.read()
	with open(outname1, 'w') as modified: modified.write(first_line + data)
	os.system("sed -i '1d' " + outname3)
	print("########################")
	print("Finished with all.")
	print("If single file, then " + outname1 + " | " + outname3 + " are the same.")
	print("Made files: " + outname_array + " | " + outname1 + " | " + outname3)	

if int(answer) == 2:
	print("Will restore any *.bak file to the original if it exists.")
	print("This assumes your file has Azoff, eloff, Tant in columns 12,13,8 respectively.")
	instring = raw_input("Please input unique identifying string. Will read all files with this string in it eg gal will read beam_gal.cat and gal_1.txt: ")
	os.system("rm -vf *meta*beam*prof*" + instring + "*" )
	all_files = [f for f in glob.glob('*') if os.path.isfile(f)]
	backup_files = [f for f in glob.glob('.*') if os.path.isfile(f)]
	file = [f for f in glob.glob('*'+instring+'*') if os.path.isfile(f)]
	outname3 = "master_meta_sort_beamprof_" + str(len(file)) + instring + ".txt"
	os.system("echo '' > " + outname3)
	print(file)
	for files in file:
		print("########################")
		if ("." + files + ".bak ") in backup_files:
			os.system("mv -vf ." + files + ".bak "  + files)
		outname0="meta_all_beamprof_"+files
		outname1="meta_sort_beamprof_" + files
		os.system("sed -i.bak '/entered/d' " + files)
		os.system("mv -vf " + files + ".bak ." + files + ".bak ")

		print("Running file: " + files)
		meta_parse.info_parse(files,outname0)

		first_line = "Azoff eloff Tant"
	 	os.system("awk -F '     ' '{print $11,$12,$7}' " + outname0  + " > " + outname1)
		os.system("sed -i '1d' " + outname1)
		with open(outname1, 'r') as original: data = original.read()
		with open(outname1, 'w') as modified: modified.write(first_line + "\n" + data)
		os.system("cat " + outname1 + " >> " + outname3) 
		os.system("sed -i '/Azoff/d' " + outname3)
		os.system("sed -i '1d' " + outname3)
		with open(outname3, 'r') as original: data = original.read()
		with open(outname3, 'w') as modified: modified.write(first_line + "\n" + data)		
		print("Finished file: " + files)
	print("########################")
	print("Finished with all.")
	print("If single file, then " + outname1 + " | " + outname3 + " are the same.")
	print("Made files: " + outname0 + " | " + outname1 + " | " + outname3)	
#############
# end of code