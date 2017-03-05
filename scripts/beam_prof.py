###################
# beam_prof.cmd
# Alek K and Nick R
###################

# import libraries
import os
import sys
import time

# sun position
print("Read the sun az,el from command line.")
print("Values have to be 30<el<320 and 20<az<60 .")
sunaz=float(raw_input("Input sun az (281.2): "))
sunel=float(raw_input("Input sun el (281.2): "))
num=int(raw_input("Input number of points in each direction(10<num<30): "))
inti=int(raw_input("Input integration time: "))
bw=5 #  beamwidth in degrees
num=num+1
##################
# making cmd file
##################
# file
fname = "beam_prof_" + time.strftime("_%Y_%M_%d") + ".txt"
f = open(fname,'w')
orig_stdout = sys.stdout
sys.stdout = f
print(": sun")
print(": record beam_prof.dat")
for i in range(num):
	csunel = sunel + i
	for j in range(num):
		print(":" + str(inti) + " " + str(sunaz + j) + " " + str(csunel))
	for j in range(num):	
		if j != 0:
			print(":" + str(inti) + " " + str(sunaz - j) + " " + str(csunel))
	if i != 0:		
		csunel = sunel - i
		for j in range(num):
			print(":" + str(inti) + " " + str(sunaz + j) + " " + str(csunel))
		for j in range(num):	
			if j != 0:
				print(":" + str(inti) + " " + str(sunaz - j) + " " + str(csunel))			
print(": roff")
print(": stow")

sys.stdout = orig_stdout
f.close

stime=(2*num + 1)**2 * inti
mtime=int(stime/60)
mstime=stime%60
if mstime < 10:
	mstime="0" + str(mstime)
print("Time for Completion: " + str(mtime) + ":" + str(mstime))

# end of code