##############
# m31 and m33 cmd_create.py
# Alek K and Nick R
#############

# import libraries
import os
import sys
import time

# filenames
outname = "m31m33_cmd"
source = ["Andr","Trig1"]
fname = [source[0] + ".txt",source[1] + ".txt"] 
freq=[1422.9,1421.8]


# calibration
calaz = raw_input("Calibration az: ")
calel = raw_input("Calibration el: ")
try:
	inti = raw_input("Integration time(hh:mm:ss) or in seconds: ")
	totalsec=int(inti)
except ValueError:
	integration = inti.split(":")
	totalsec = int(integration[0]) * 3600 + int(integration[1]) * 60 + int(integration[2])
ototalsec=totalsec

# init files
f = open(outname,'w')
orig_stdout = sys.stdout
sys.stdout = f

for i in range(2):
	totalsec=ototalsec
	mod=int(totalsec/1800)
	print(': record ' + fname[i])
	print(": " + calaz + " " + calel)
	print(": freq " + str(freq[i]) + " 20 0")
	print(": calibrate")
	print(": " + source[i])
	while mod > 0:
		curint = 1800
		mod-=1
		totalsec -= curint
		print(":" + str(curint) + " b")
		print(": " + calaz + " " + calel)
		print(": calibrate")
		print(": " + source[i])
	if totalsec > 0:
		curint = totalsec
		print(":" + str(curint) + " b")
	print(':roff')
	print('')
print(':stow')
sys.stdout = orig_stdout
f.close

#############
# end of file