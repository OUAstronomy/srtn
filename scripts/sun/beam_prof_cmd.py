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
fname = "beam_prof_2d_" + str(inti) + "int_" + str(num-1) + "off_cmd.txt"
f = open(fname,'w')
orig_stdout = sys.stdout
sys.stdout = f
print(": Sun")
print(": record beam_prof_2d_" + str(inti) + "int_" + str(num-1) + "off.txt")
for i in range(num):
	for j in range(num):
		print(":" + str(inti) + " offset " + str(j) + " " + str(i))
	for j in range(num):
		if j != 0:
			print(":" + str(inti) + " offset -" + str(j) + " " + str(i))
	if i != 0:
		for j in range(num):
			print(":" + str(inti) + " offset " + str(j) + " -" + str(i))
		for j in range(num):
			if j != 0:
				print(":" + str(inti) + " offset -" + str(j) + " -" + str(i))	
print(": roff")
print(": stow")

sys.stdout = orig_stdout
f.close

fname = "beam_prof_1d_" + str(inti) + "int_" + str(num-1) + "off_cmd.txt"
f = open(fname,'w')
orig_stdout = sys.stdout
sys.stdout = f
print(": Sun")
print(": record beam_prof_1d_" + str(inti) + "int_" + str(num-1) + "off.txt")
for j in range(num):
	print(":" + str(inti) + " offset " + str(j) + " " + str(0))
for j in range(num):
	if j != 0:
		print(":" + str(inti) + " offset -" + str(j) + " " + str(0))
for j in range(num):
	if j != 0:
		print(":" + str(inti) + " offset " + str(0) + " " + str(j))
for j in range(num):
	if j != 0:
		print(":" + str(inti) + " offset " + str(0) + " -" + str(j))	
print(": roff")
print(": stow")

sys.stdout = orig_stdout
f.close

stime=(2*num)**2 * inti
mtime=int(stime/60)
mstime=stime%60
if mstime < 10:
	mstime="0" + str(mstime)
print("Time for 2D Completion: " + str(mtime) + ":" + str(mstime))

stime=(4*num+1) * inti
mtime=int(stime/60)
mstime=stime%60
if mstime < 10:
	mstime="0" + str(mstime)
print("Time for 1D Completion: " + str(mtime) + ":" + str(mstime))


# end of code
