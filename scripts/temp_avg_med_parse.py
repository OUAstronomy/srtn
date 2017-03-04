#!/usr/bin/python
#############################
# Sort HI spec
# Author: Alek K. and Nick R.
#############################

# import libraries
import os
import numpy as np
import matplotlib.pyplot as plt

print("DON\'T RUN ON MAC")
print("Run with Python version 2.7.5 and 3.1")

# file name
fname = "orig.txt"
forig=fname
os.system("cp -vf " + fname + " backup.txt")
# fname=raw_input("Filename: ")

# removing first line and makes 2 files, 1 of freq and 1 of temp
sednewfile = "sed_" + fname
os.system("rm -vf " + sednewfile)
os.system("sed '1d' " + fname + " > " + sednewfile)
awknewfile = "awk_" + fname
os.system("rm -vf " + awknewfile)
os.system("awk '{print $1}' " + sednewfile + " > " + awknewfile)

# open file, read values, and remove null space/newlines
with open(awknewfile) as f:
	np.freq_array = f.readlines()
np.freq_array = [x.strip() for x in np.freq_array]

# modifying old file for temperature arrays
fname="temp_" + fname
os.system("rm -vf " + fname)
os.system("awk '!($1=\"\") !($2=\"\")' " + forig + " > " + fname)
os.system("sed -i '1d' " + fname)

# open file, read values, and remove null space/newlines
with open(fname) as f:
	np.temp_string_array = f.readlines()
np.temp_string_array = [x.strip() for x in np.temp_string_array]

# define arrays
np.temp_float_array=[]
np.median=[]
np.angry=[]
np.res=[]

# find median
for k in range(len(np.temp_string_array)):
	np.temp_float_array.append(np.temp_string_array[k].split())
	for j in range(len(np.temp_float_array[k])):
		np.temp_float_array[k][j] = float(np.temp_float_array[k][j])
	np.median.append(np.temp_float_array[k][len(np.temp_float_array[k][:])/2])


# find mean.... Angry because python is mean
for k in range(len(np.temp_string_array)):
	np.temp_float_array.append(np.temp_string_array[k].split())
	temp_sum=0
	for j in range(len(np.temp_float_array[k])):
		np.temp_float_array[k][j] = float(np.temp_float_array[k][j])
		temp_sum=np.temp_float_array[k][j] + temp_sum
	np.angry.append(temp_sum/len(np.temp_float_array[k][:]))

#print(np.median)
#print(np.angry)
#print(np.freq_array)
#print(len(np.median))
#print(len(np.angry))
#print(len(np.freq_array))
print("Made files: ",sednewfile," ", awknewfile, " ",fname)

#end()

for j in range(len(np.temp_string_array)):
	np.res.append(210 + (np.angry[j]-np.median[j]))

# plotting
fig = plt.figure()
ax = plt.subplot(111)
#ax.set_xlim([-1.0,1.0])
#ax.set_ylim([-1.0,1.0])
ax.set_xlabel("Frequency (MHz)")
ax.set_ylabel("Temperature (K)")
plt.plot(np.freq_array,np.median,'r',label='Median')
plt.plot(np.freq_array,np.angry,'b',label='Mean==Angry')
plt.plot(np.freq_array,np.res,'g',label='Residual')
plt.show()



# end of code