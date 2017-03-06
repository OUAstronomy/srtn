###################
# beam_prof.cmd
# Alek K and Nick R
###################

# import libraries
import os
import sys
import time

# sun position
num=int(raw_input("Input number of points in each direction(10<num<30): "))
inti=int(raw_input("Input integration time: "))
num=num+1

##################
# making cmd file
##################
# file
fname = "beam_prof" + ".txt"
f = open(fname,'w')
orig_stdout = sys.stdout
sys.stdout = f
print(": sun")
print(": record beam_prof.dat")
for i in range(num):
	for j in range(num):
		print(": offset " + str(j) + " " + str(i))
	for j in range(num):
		if j != 0:
			print(": offset -" + str(j) + " " + str(i))
	if i != 0:
		for j in range(num):
			print(": offset " + str(j) + " -" + str(i))
		for j in range(num):
			if j != 0:
				print(": offset -" + str(j) + " -" + str(i))	
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