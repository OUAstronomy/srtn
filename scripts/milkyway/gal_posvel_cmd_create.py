##############
# gal_posvel_cmd_create.py
# Alek K and Nick R
#############

# import libraries
from __future__ import print_function
assert sys.version_info >= (2,5)
import os
import sys
import time

# starting pos and ending pos
while True:
	try:
		int_time = raw_input("Integration Time (Same for all sources) in seconds: ")
		beam_width = raw_input("Desired Beam Width (degree): ")
		startpos = raw_input("Starting Degree: ")
		endpos = raw_input("Ending Degree: ")
		direc = raw_input("Positive(+) or negative(-) direction: ")
		azel = raw_input("Input azel offsets as az,el (-2,1): ")
		az_el = azel.split(",")
		az_el = map(int,az_el)
	except ValueError:
		continue
	if len(az_el) == 2:
		break

##################
# making cmd file
##################
# file

outname = "gal_posvel_" +startpos + "_" +endpos

fname = "gal_posvel_cmd_"+startpos + "_" +endpos+"_"+int_time+"int.txt"
f = open(fname,'w')
orig_stdout = sys.stdout
sys.stdout = f

# make degree array
degree = []
final = []
int_time = float(int_time)
startpos = float(startpos)
endpos = float(endpos)
beam_width = float(beam_width)
for i in range(int(360/beam_width)):
	degree.append(i * beam_width)

# if start/end position wasnt defined by beamwidth
if (startpos%beam_width) != 0:
	if (startpos%beam_width) > (beam_width * .5):
		startpos = startpos + abs(startpos%beam_width - beam_width)
	else:	
		startpos = startpos - startpos%beam_width
if (endpos%beam_width) != 0:
	if (endpos%beam_width) > (beam_width * .5):
		endpos = endpos + abs(endpos%beam_width - beam_width)
	else:	
		endpos = endpos - endpos%beam_width

## positive direction
if direc == "+":
	# find total num of elements in degree array
	if startpos > endpos:
		up_range_el = abs((startpos) - 360.) / beam_width
		low_range_el = (endpos / beam_width) + 1
		for element in range(int(up_range_el)):
			nstartpos = degree.index(startpos)
			final.append(degree[nstartpos + element])
		for element in range(int(low_range_el)):
			final.append(degree[element])		
	else:
		tot_el = (endpos - startpos) / beam_width + 1
		for element in range(int(tot_el)):
			nstartpos = degree.index(startpos)
			final.append(degree[nstartpos + element])
else: ## negative direction
	# find total num of elements in degree array
	if startpos < endpos:
		up_range_el = (startpos) / beam_width
		low_range_el = (abs(endpos - 360) / beam_width)
		for element in range(int(up_range_el) + 1):
			nstartpos = degree.index(startpos)
			final.append(degree[nstartpos - element])
		for element in range(int(low_range_el)):
			final.append(degree[len(degree) - 1 - element])	
	elif startpos > endpos:
		tot_el = abs(endpos - startpos) / beam_width + 1
		for element in range(int(tot_el)):
			nstartpos = degree.index(startpos)
			final.append(degree[nstartpos - element])

#print(degree)
#print(final)
#print(len(final))

# file creation
j=0
for i in range(len(final)):
	if i == 0:
		print(': record ./' + outname + ".txt")
		print('')
	print(': ' + "G" + str(final[i]))
	print(': offset ' + str(az_el[0]) + " " + str(az_el[1]))
	print(':' + str(int_time))
	if (((i * int_time)-(j*7200)) >= (7200)):
		print(':roff')
		print(':stow')
		print(':cal')
		print(':60')
		print('')
		print(': record ' + outname + "_" + str(j+2) + ".txt")
		j+=1
print(':roff')
print(':stow')

# closing file
sys.stdout = orig_stdout
f.close

print("Total Time: ", str(int_time * len(final)) )  

# making srt.cat file
fname = "srt_gal_posvel.cat"
f = open(fname,'w')
orig_stdout = sys.stdout
sys.stdout = f
print('CALMODE 20')
print('STATION 35.207 97.44 Sooner_Station')
print('SOU 23 21 12  58 44 00 Cass')
print('SOU 00 00 00  00 00 00 Sun')
print('SOU 00 00 00  00 00 00 Moon')
print('SOU 17 45 40 -29 00 28 SgrA')
print('SOU 05 35 17 -05 23 28 Orion')
print('SOU 00 42 44 41 16 09 Andr')
print('SOU 01 33 50 30 39 37 Trigl')
print('')
print('NOPRINTOUT')
print('BEAMWIDTH 5')
print('NBSW 10')
print('AZLIMITS 0 355')
print('ELLIMITS 0 89.0')
print('STOWPOS 90 0')
print('TSYS 171    ')
print('TCAL 290    // should equal ambient load')
print('RECORD 10 SPEC')
print('NUMFREQ 1024   // good choise for ADC card')
print('NUMFREQ 256    // good choice for dongle')
print('*FREQUENCY 1420.406')
print('BANDWIDTH 2.0')
print('FREQUENCY 1420.4')
print('RESTFREQ 1420.401')
print('FREQCORR -0.05   // TV dongle correction')
print('NBLOCK 5   // number of blocks per update - can be reduced for Beagle board with slow display for PCI it is hardwired to 20')
print('')
print('RFI 1420.05 0.015')
print('RFI 1420.85 0.005')
print('RFI 1421.15 0.005')
print('')
for i in range(len(degree)):
	print("GALACTIC " + str(degree[i]) + " 0.0 G" + str(degree[i]))
print("GALACTIC 360.0 0.0 G360.0")
sys.stdout = orig_stdout
f.close

#############
# end of file