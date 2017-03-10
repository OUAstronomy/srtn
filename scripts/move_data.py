#############################
# Will move data to directory
# Nickalas Reynolds
# March 2017
#############################

# warning
print('')

# import libraries
import sys
import os

# locations
data_dir="/home/jjtobin/srtn/data/sources/"
sources = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
cur_sources = [x.replace(data_dir, '') for x in sources]
cwd = os.getcwd()
print("List of current sources: ",cur_sources)

# determine files
data_array=[]
name_array=[]
while True:
	data_file=""
	data_file = raw_input("Please input data filename or [RETURN] to quit: ")
	if data_file == "":
		break
	source_name = raw_input("Please input source name exactly as above or new name: ")
	data_array.append(data_file)
	name_array.append(source_name)
print("Files to move: ", data_array)
print("Locations to move to: ",data_dir,name_array)

for i in range(len(name_array)):
	if name_array[i] in cur_sources:
		os.system('cp -vr ' + cwd + '/' +  data_array[i] + ' ' + data_dir + name_array[i] + '/' + data_array[i])
		continue
	else:
		os.system('mkdir -v ' + data_dir + name_array[i])
		os.system('cp -vr ' + cwd + '/' +  data_array[i] + ' ' + data_dir + name_array[i] + '/' + data_array[i])
print('Data copy complete')

#############
# end of file