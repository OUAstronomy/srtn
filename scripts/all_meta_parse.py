#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
name: all_meta_parse
Author Nickalas Reynolds
data: March 2017
"""

# import modules
import meta_parse
import os
import glob

# ask for identifying string 
# ask for identifying string 
while True:
	try:
		answer = raw_input("Do you have multiple, single target files(1) or running beam profiling(2) or  multiple beam profiling(3): ")
	except ValueError:
		print("Please input an integer, 1 2 3.")
		continue
	if (int(answer) != 1) and (int(answer) != 2) and (int(answer) != 3):
		print("Please input an integer, 1 2 3.")
		continue
	else:
		break

# Read in the files
if int(answer) == 1:
	instring = raw_input("Please input identifying string eg gal: ")
	os.system("rm -f *" + instring + "*.bak* *meta*" + instring + "*" )
	files = [f for f in glob.glob('*'+instring+'*') if os.path.isfile(f)]
	print(files)
	outname0="meta_"+f
	outname1="meta_sort_" + str(len(files)) + instring + ".txt"
	os.system("echo '' > " + outname)

	for f in files:
		print("########################")
		os.system("sed -i.bak '/entered/d' " + f)
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
	print("Finished with all.")
	print("########################")
	print("Made file " + outname0 + ", " + outname1)	

if int(answer) == 2:
	instring = raw_input("Please input filename: ")
	os.system("rm -f *" + instring + "*.bak* *meta*" + instring + "*" )
	files = [f for f in glob.glob(instring) if os.path.isfile(f)]
	files=str(files[0])
	print(files)
	outname0="meta_"+files
	outname1="meta_sort_" + files
	os.system("sed -i.bak '/entered/d' " + files)

	print("Running file: " + files)
	meta_parse.info_parse(files,outname0)
	print("Finished file: " + files)

	first_line = "Azoff eloff Tant"
 	os.system("awk -F '     ' '{print $11,$12,$7}' " + outname0  + " > " + outname1)
	os.system("sed -i '1d' " + outname1)
	with open(outname1, 'r') as original: data = original.read()
	with open(outname1, 'w') as modified: modified.write(first_line + "\n" + data)
	print("########################")
	print("Made file " + outname0 + ", " + outname1)	

if int(answer) == 3:
	instring = raw_input("Please input identifying string eg beam_prof_1d: ")
	os.system("rm -f *" + instring + "*.bak* *meta*" + instring + "*" )
	file = [f for f in glob.glob('*'+instring+'*') if os.path.isfile(f)]
	outname3 = "master_meta_sort_" + str(len(file)) + instring + ".txt"
	os.system("echo '' > " + outname3)
	print(file)
	for files in file:
		print("########################")
		outname0="meta_"+files
		outname1="meta_sort_" + files
		os.system("sed -i.bak '/entered/d' " + files)

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
	print("Made file " + outname3 + ", " + outname1)	
#############
# end of code