'''
Creates plots to correct baselines
author: John Tobin and Nick Reynolds
Date: March 2017
'''

# import modules
import numpy as np
import os
import glob
from astropy.table import Table
from astropy.io import ascii
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.pyplot import draw as draw
from matplotlib.ticker import ScalarFormatter
import matplotlib.ticker as ticker
from six.moves import input
from matplotlib.widgets import LassoSelector
from matplotlib.path import Path


# read data
#data = ascii.read("tobin-g110-reduced.dat")

# define useful variables
print ("Data needs to be of format: freq vel Tant")
while True:
	try:
		outfilename = raw_input("Input filename for output (no extension): ")
		datafile = raw_input("Input data file for plot: ")
		if outfilename != "":
			break
	except ValueError:
		continue

# handle files
files = [f for f in glob.glob('*'+outfilename+'*') if os.path.isfile(f)]
print("Will remove these files:")
print(files)
print("\n")
input("Press [RET] to continue")
os.system("rm -vf *" + outfilename + "*")
data = ascii.read(datafile)
minvel = min(data['vel'])
maxvel = max(data['vel'])
data.sort(['vel'])

# plot raw data
plt.ion()
f=plt.subplot(121)
rawdata=f.scatter(data['vel'],data['Tant'],color='black')
plt.plot(data['vel'],data['Tant'],color='red',linestyle='steps')
# prepare mask
f.set_title('lasso selection:')
f.tick_params('both', which='major', length=15, width=1, pad=15)
f.tick_params('both', which='minor', length=7.5, width=1, pad=15)
ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
f.set_ylabel('Antenna Temperature (K)', fontsize=18)
f.set_xlabel('V$_{lsr}$ (kms/s)', fontsize=18)
draw()
# baseline
baseline_med=np.median(data['Tant'])-0.5
baseline_ul=baseline_med*1.02
print(baseline_med, baseline_ul)

# prepare mask lasso command
class SelectFromCollection(object):
    def __init__(self, ax, collection, alpha_other=0.3):
        self.canvas = ax.figure.canvas
        self.collection = collection
        self.alpha_other = alpha_other

        self.xys = collection.get_offsets()
        self.Npts = len(self.xys)

        # Ensure that we have separate colors for each object
        self.fc = collection.get_facecolors()
        if len(self.fc) == 0:
            raise ValueError('Collection must have a facecolor')
        elif len(self.fc) == 1:
            self.fc = np.tile(self.fc, self.Npts).reshape(self.Npts, -1)

        self.lasso = LassoSelector(ax, onselect=self.onselect)
        self.ind = []

    def onselect(self, verts):
        path = Path(verts)
        self.ind = np.nonzero([path.contains_point(xy) for xy in self.xys])[0]
        self.fc[:, -1] = self.alpha_other
        self.fc[self.ind, -1] = 1
        self.collection.set_facecolors(self.fc)
        self.canvas.draw_idle()

    def disconnect(self):
        self.lasso.disconnect_events()
        self.fc[:, -1] = 1
        self.collection.set_facecolors(self.fc)
        self.canvas.draw_idle()

# actual defining mask
msk_array = []
temp = []
while True:
    selector = SelectFromCollection(f, rawdata)
    print("Draw mask regions around the Gaussians")
    draw()
    input('Press Enter to accept selected points')
    temp = selector.xys[selector.ind]
    #print(temp)
    #print(type(temp))
    msk_array = np.append(msk_array,temp)
    selector.disconnect()
    # Block end of script so you can check that the lasso is disconnected.
    answer = raw_input("Want to draw another lasso region (y or [SPACE]/n or [RET]): ")
    plt.show()
    if ((answer == "n") or (answer == "")):
    	break
input("Press [RET] to continue")

# draw and reset
k=plt.figure(1)
f=k.add_subplot(121)
f.set_title("Raw Data")
rawdata=f.plot(data['vel'],data['Tant'],color='black',linestyle='steps')
f.set_xlabel('V$_{lsr}$ (kms/s)', fontsize=18)
draw()
outfilename_iter =0
plt.savefig(outfilename + "_" + str(outfilename_iter) + ".pdf")

# need to invert mask to polyfit region
mask_inv = []
for i in range(len(msk_array)):
	mask_inv = np.append(mask_inv,np.where(data['vel'] == msk_array[i]))
# print(mask_inv)
mask_tot = np.linspace(0,len(data)-1,num=len(data))
mask = np.delete(mask_tot,mask_inv)
mask = map(int,mask)
#print(mask)
input("Press [RET] to continue")

# show projected baselines
fig=plt.figure(2)
plt.title("projected baselines")
lin1=plt.plot(data['vel'],data['Tant'],color='black',linestyle='steps')
lin2=plt.plot([minvel,maxvel],[baseline_med,baseline_med],color='red',linestyle='steps')
lin3=plt.plot([minvel,maxvel],[baseline_ul,baseline_ul],color='red',linestyle='steps')
plt.tick_params('both', which='major', length=15, width=1, pad=15)
plt.tick_params('both', which='minor', length=7.5, width=1, pad=15)
ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
plt.ylabel('Antenna Temperature (K)', fontsize=18)
plt.xlabel('V$_{lsr}$ (kms/s)', fontsize=18)
draw()
outfilename_iter +=1
plt.savefig(outfilename + "_" + str(outfilename_iter) + ".pdf")

# fitting polynomial 4th order to baseline
fit = np.polyfit(data['vel'][mask],data['Tant'][mask],4)
fit_fn = np.poly1d(fit) 
input("Press [RET] to continue")

# plotting fitted baseline to original image
plt.figure(3)
plt.title("plotting fitted baseline")
lin1=plt.plot(data['vel'],data['Tant'],color='black',linestyle='steps')
lin2=plt.plot(data['vel'],fit_fn(data['vel']),color='red',linestyle='steps')
plt.tick_params('both', which='major', length=15, width=1, pad=15)
plt.tick_params('both', which='minor', length=7.5, width=1, pad=15)
ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
plt.ylabel('Antenna Temperature (K)', fontsize=18)
plt.xlabel('V$_{lsr}$ (kms/s)', fontsize=18)
draw()
outfilename_iter +=1
plt.savefig(outfilename + "_" + str(outfilename_iter) + ".pdf")

# defining corrected spectra
spectra_blcorr=data['Tant'].copy()
spectra_blcorr=data['Tant']-fit_fn(data['vel'])
maxt = max(spectra_blcorr)
mint = min(spectra_blcorr)

# defining RMS
rms=np.std(spectra_blcorr[mask])
print('RMS Noise: ',rms, 'K')
input("Press [RET] to continue")

# plotting the corrected baseline
plt.figure(4)
plt.title("plotting the corrected baseline")
lin1=plt.plot(data['vel'],spectra_blcorr,color='black',linestyle='steps')
lin2=plt.plot([minvel,maxvel],[0,0],color='red',linestyle='steps')
plt.tick_params('both', which='major', length=15, width=1, pad=15)
plt.tick_params('both', which='minor', length=7.5, width=1, pad=15)
ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
plt.ylabel('Antenna Temperature (K)', fontsize=18)
plt.xlabel('V$_{lsr}$ (kms/s)', fontsize=18)
outfilename_iter +=1
plt.savefig(outfilename + "_" + str(outfilename_iter) + ".pdf")
draw()

# define the RFI
plt.ion()
t=plt.subplot(122)
t.set_title('lasso selection:')
lin10=plt.scatter(data['vel'],spectra_blcorr,color='black')
lin2=plt.plot(data['vel'],spectra_blcorr,color='blue',linestyle='steps')
lin3=plt.plot([minvel,maxvel],[0,0],color='red',linestyle='steps')
plt.tick_params('both', which='major', length=15, width=1, pad=15)
plt.tick_params('both', which='minor', length=7.5, width=1, pad=15)
ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
plt.ylabel('Antenna Temperature (K)', fontsize=18)
plt.xlabel('V$_{lsr}$ (kms/s)', fontsize=18)
draw()

temp = []
rfi_mask_array = []
rfi_mask = []
while True:
    selector = SelectFromCollection(t, lin10)
    print("Draw RFI mask regions")
    draw()
    input('Press Enter to accept selected points')
    temp = selector.xys[selector.ind]
    #print(temp)
    #print(type(temp))
    rfi_mask_array = np.append(rfi_mask_array,temp)
    selector.disconnect()
    # Block end of script so you can check that the lasso is disconnected.
    answer = raw_input("Want to draw another lasso region (y or [SPACE]/n or [RET]): ")
    plt.show()
    if ((answer == "n") or (answer == "")):
    	break
input("Press [RET] to continue")
for i in range(len(rfi_mask_array)):
	rfi_mask = np.append(rfi_mask,np.where(data['vel'] == rfi_mask_array[i]))
rfi_mask = map(int,rfi_mask)
#print(rfi_mask)
#print(spectra_blcorr[rfi_mask])
#print(spectra_blcorr)
spectra_blcorr[rfi_mask]=0.0
#print(spectra_blcorr[rfi_mask])

# draw and reset
plt.figure(5)
plt.title("Corrected Baseline and RFI")
lin2=plt.plot(data['vel'],spectra_blcorr,color='blue',linestyle='steps')
lin3=plt.plot([minvel,maxvel],[0,0],color='red',linestyle='steps')
plt.tick_params('both', which='major', length=15, width=1, pad=15)
plt.tick_params('both', which='minor', length=7.5, width=1, pad=15)
ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
plt.ylabel('Antenna Temperature (K)', fontsize=18)
plt.xlabel('V$_{lsr}$ (kms/s)', fontsize=18)
outfilename_iter +=1
plt.savefig(outfilename + "_" + str(outfilename_iter) + ".pdf")
draw()

# Final correction plot 
plt.figure(6)
plt.xlim(minvel,maxvel)
plt.ylim(-5,maxt * 1.1)
lin1=plt.plot(data['vel'],spectra_blcorr,color='black',linestyle='steps')
plt.tick_params('both', which='major', length=15, width=1, pad=15)
plt.tick_params('both', which='minor', length=7.5, width=1, pad=15)
ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
plt.title("Final correction plot ")
plt.ylabel('Antenna Temperature (K)', fontsize=18)
plt.xlabel('V$_{lsr}$ (km/s)', fontsize=18)
draw()
outfilename_iter +=1
plt.savefig(outfilename + "_" + str(outfilename_iter) + ".pdf")

# intensity estimate
intensity_mask_guess = np.where((spectra_blcorr >= 5. * rms) & (spectra_blcorr >= -5. * rms))
minint=min(data['vel'][intensity_mask_guess])
maxint=max(data['vel'][intensity_mask_guess])
plt.figure(6)
plt.xlim(minvel,maxvel)
plt.ylim(-5,max(spectra_blcorr) * 1.1)
lin1=plt.plot(data['vel'],spectra_blcorr,color='black',linestyle='steps')
lin2=plt.plot(data['vel'][intensity_mask_guess],np.zeros(len(data['vel'][intensity_mask_guess])),color='blue',linestyle='dotted')
lin3=plt.plot([minint,minint],[0,maxt],color='blue',linestyle='dotted')
lin4=plt.plot([maxint,maxint],[0,maxt],color='blue',linestyle='dotted')
plt.tick_params('both', which='major', length=15, width=1, pad=15)
plt.tick_params('both', which='minor', length=7.5, width=1, pad=15)
ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
plt.title("Intensity Line Estimate")
plt.ylabel('Antenna Temperature (K)', fontsize=18)
plt.xlabel('V$_{lsr}$ (km/s)', fontsize=18)
draw()
outfilename_iter +=1
plt.savefig(outfilename + "_" + str(outfilename_iter) + ".pdf")

answer = ""
while True:
	try:
		answer = raw_input("Is the guess for the line intensity okay (y or [RET]/n or [SPACE]): ")
		if ((answer == "y") or (answer == "")):
			intensity_mask = intensity_mask_guess
			break
		else:
			# define the Intensity
			plt.ion()
			t=plt.subplot(122)
			t.set_title('lasso selection:')
			lin10=plt.scatter(data['vel'],spectra_blcorr,color='black')
			lin2=plt.plot(data['vel'],spectra_blcorr,color='blue',linestyle='steps')
			lin3=plt.plot([minvel,maxvel],[0,0],color='red',linestyle='steps')
			plt.tick_params('both', which='major', length=15, width=1, pad=15)
			plt.tick_params('both', which='minor', length=7.5, width=1, pad=15)
			ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
			plt.ylabel('Antenna Temperature (K)', fontsize=18)
			plt.xlabel('V$_{lsr}$ (kms/s)', fontsize=18)
			draw()
			# recovering intensity of line 
			temp = []
			intensity_mask_array = []
			rfi_mask = []
			while True:
				selector = SelectFromCollection(t, lin10)
				print("Draw a box around Gaussian")
				draw()
				input('Press Enter to accept selected points')
				temp = selector.xys[selector.ind]
				#print(temp)
				#print(type(temp))
				intensity_mask_array = np.append(intensity_mask_array,temp)
				selector.disconnect()
				# Block end of script so you can check that the lasso is disconnected.
				answer = raw_input("Want to draw another lasso region (y or [SPACE]/n or [RET]): ")
				plt.show()
				if ((answer == "n") or (answer == "")):
					break
			input("Press [RET] to continue")
			for i in range(len(intensity_mask_array)):
				intensity_mask = np.append(intensity_mask,np.where(data['vel'] == intensity_mask_array[i]))
			intensity_mask = map(int,intensity_mask)
	except ValueError:
		continue


# showing Intensity Mask
minint=min(data['vel'][intensity_mask])
maxint=max(data['vel'][intensity_mask])
plt.figure(7)
plt.xlim(minvel,maxvel)
plt.ylim(-5,max(spectra_blcorr) * 1.1)
lin1=plt.plot(data['vel'],spectra_blcorr,color='black',linestyle='steps')
lin2=plt.plot(data['vel'][intensity_mask],np.zeros(len(data['vel'][intensity_mask])),color='blue',linestyle='dotted')
lin3=plt.plot([minint,minint],[0,maxt],color='blue',linestyle='dotted')
lin4=plt.plot([maxint,maxint],[0,maxt],color='blue',linestyle='dotted')
plt.tick_params('both', which='major', length=15, width=1, pad=15)
plt.tick_params('both', which='minor', length=7.5, width=1, pad=15)
ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
plt.title("Intensity Mask")
plt.ylabel('Antenna Temperature (K)', fontsize=18)
plt.xlabel('V$_{lsr}$ (km/s)', fontsize=18)
draw()
outfilename_iter +=1
plt.savefig(outfilename + "_" + str(outfilename_iter) + ".pdf")

# intensity
intensity=np.sum(spectra_blcorr[intensity_mask])
chanwidth=abs(max(data['vel'])-min(data['vel']))/len(data['vel'])
intensity_rms=rms*chanwidth*(float(len(intensity_mask[0])))**0.5
print("\n")
print("Intensity: ")
print((intensity)*chanwidth, '+/-',intensity_rms, 'K km/s')

# write to file
spec_final = Table([data['vel'],data['Tant'],spectra_blcorr], names=('vel', 'Tant_raw', 'Tant_corr'))
ascii.write(spec_final, outfilename + "_spectra_corr.txt")

input("Press [RET] to exit")
plt.show()
print("\n")
files = [f for f in glob.glob('*'+outfilename+'*') if os.path.isfile(f)]
print("Made the following files:")
print(files)
plt.close()

#############
# end of code