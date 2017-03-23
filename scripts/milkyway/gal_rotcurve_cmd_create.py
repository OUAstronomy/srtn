##############
# gal_posvel_cmd_create.py
# Alek K and Nick R
#############

# import libraries
import sys
from __future__ import print_function
assert sys.version_info >= (2,5)

# declare variables
startpos=0
endpos=90
while True:
    try:
        int_time=int(raw_input("Input desired integration time per position(>20): "))
        azel = raw_input("Input azel offsets as az,el (-2,1): ")
        az_el = azel.split(",")
        az_el = map(int,az_el)
    except ValueError:
        continue
    if len(az_el) == 2:
        break
    
# declare array
degree=[]
for i in range(90+1):
	if (i%10 == 0) or (i%10 == 10) :
		degree.append(i)
print degree
##################
# making cmd file
##################
# file
outname = "gal_rot_" +str(startpos) + "_" +str(endpos)

fname = "gal_rot_cmd_"+str(startpos) + "_" +str(endpos)+"_"+str(int_time)+"int.txt"
f = open(fname,'w')
orig_stdout = sys.stdout
sys.stdout = f

print(': record ./' + outname + ".txt")
for i in range(len(degree)):
	print(': ' + "G" + str(degree[i])+'.0')
    print(': offset ' + str(az_el[0]) + " " + str(az_el[1]))
	print(':' + str(int_time))
print(':roff')
print(':stow')

# closing file
sys.stdout = orig_stdout
f.close

print("Total Time: ", str(int_time * len(degree)) )  

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
	print("GALACTIC " + str(degree[i])+'.0' + " 0.0 G" + str(degree[i])+'.0')
print("GALACTIC 360.0 0.0 G360.0")
sys.stdout = orig_stdout
f.close

#############
# end of file