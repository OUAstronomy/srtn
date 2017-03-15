import astropy
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from astropy.io import ascii
from matplotlib.ticker import ScalarFormatter
import matplotlib.ticker as ticker
import math

%matplotlib inline

data = ascii.read("tobin-g110-reduced.dat")

#print data
#print data['Name','Tbol']

#print data['Lbol','Tbol']

fig=plt.figure(figsize=(10,7))
ax = fig.add_subplot(111)
#ax.set_xlim(0,71.0)
#ax.set_ylim(-5,5)

lin1=ax.plot(data['vel'],data['Tant'],color='black',linestyle='steps')

ax.tick_params('both', which='major', length=15, width=1, pad=15)
ax.tick_params('both', which='minor', length=7.5, width=1, pad=15)

ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
#for label in (ax.get_xticklabels() + ax.get_yticklabels()):
#            label.set_fontproperties(ticks_font)
#for axis in [ax.xaxis, ax.yaxis]:
#    axis.set_major_formatter(ScalarFormatter())
#    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y,pos: ('{{:.{:1d}f}}'.format(int(np.maximum(-np.log10(y),0)))).format(y)))
for axis in ['top','bottom','left','right']:
   ax.spines[axis].set_linewidth(2)

ax.set_ylabel('Antenna Temperature (K)', fontsize=18)
ax.set_xlabel('V$_{lsr}$ (kms/s)', fontsize=18)









baseline_med=np.median(data['Tant'])-0.5
baseline_ul=baseline_med+baseline_med*0.02

print(baseline_med, baseline_ul)
fig=plt.figure(figsize=(10,7))
ax = fig.add_subplot(111)
#ax.set_xlim(0,71.0)
#ax.set_ylim(-5,5)

lin1=ax.plot(data['vel'],data['Tant'],color='black',linestyle='steps')
lin2=ax.plot([-200,200],[baseline_med,baseline_med],color='black',linestyle='steps')
lin3=ax.plot([-200,200],[baseline_ul,baseline_ul],color='black',linestyle='steps')

ax.tick_params('both', which='major', length=15, width=1, pad=15)
ax.tick_params('both', which='minor', length=7.5, width=1, pad=15)

ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
#for label in (ax.get_xticklabels() + ax.get_yticklabels()):
#            label.set_fontproperties(ticks_font)
#for axis in [ax.xaxis, ax.yaxis]:
#    axis.set_major_formatter(ScalarFormatter())
#    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y,pos: ('{{:.{:1d}f}}'.format(int(np.maximum(-np.log10(y),0)))).format(y)))
for axis in ['top','bottom','left','right']:
   ax.spines[axis].set_linewidth(2)

ax.set_ylabel('Antenna Temperature (K)', fontsize=18)
ax.set_xlabel('V$_{lsr}$ (kms/s)', fontsize=18)





mask1=np.where((data['vel'] > -250.0) & (data['vel'] < -120))
mask2=np.where((data['vel'] > 100.0 ) & (data['vel'] < 240.0))
mask3=np.where((data['vel'] > 50.0 ) & (data['vel'] < 80.0))

mask=np.append(mask1,mask2)
mask=np.append(mask,mask3)

print(mask)
fit = np.polyfit(data['vel'][mask],data['Tant'][mask],4)
fit_fn = np.poly1d(fit) 
fig=plt.figure(figsize=(10,7))
ax = fig.add_subplot(111)
#ax.set_xlim(0,71.0)
#ax.set_ylim(-5,5)

lin1=ax.plot(data['vel'],data['Tant'],color='black',linestyle='steps')
lin2=ax.plot(data['vel'],fit_fn(data['vel']),color='black',linestyle='steps')

ax.tick_params('both', which='major', length=15, width=1, pad=15)
ax.tick_params('both', which='minor', length=7.5, width=1, pad=15)

ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
#for label in (ax.get_xticklabels() + ax.get_yticklabels()):
#            label.set_fontproperties(ticks_font)
#for axis in [ax.xaxis, ax.yaxis]:
#    axis.set_major_formatter(ScalarFormatter())
#    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y,pos: ('{{:.{:1d}f}}'.format(int(np.maximum(-np.log10(y),0)))).format(y)))
for axis in ['top','bottom','left','right']:
   ax.spines[axis].set_linewidth(2)

ax.set_ylabel('Antenna Temperature (K)', fontsize=18)
ax.set_xlabel('V$_{lsr}$ (kms/s)', fontsize=18)



spectra_blcorr=data['Tant'].copy()
spectra_blcorr=data['Tant']-fit_fn(data['vel'])

rms=np.std(spectra_blcorr[mask])
print('RMS Noise: ',rms, 'K')
fig=plt.figure(figsize=(10,7))
ax = fig.add_subplot(111)
#ax.set_xlim(0,71.0)
#ax.set_ylim(-5,5)

lin1=ax.plot(data['vel'],spectra_blcorr,color='black',linestyle='steps')

ax.tick_params('both', which='major', length=15, width=1, pad=15)
ax.tick_params('both', which='minor', length=7.5, width=1, pad=15)

ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
#for label in (ax.get_xticklabels() + ax.get_yticklabels()):
#            label.set_fontproperties(ticks_font)
#for axis in [ax.xaxis, ax.yaxis]:
#    axis.set_major_formatter(ScalarFormatter())
#    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y,pos: ('{{:.{:1d}f}}'.format(int(np.maximum(-np.log10(y),0)))).format(y)))
for axis in ['top','bottom','left','right']:
   ax.spines[axis].set_linewidth(2)

ax.set_ylabel('Antenna Temperature (K)', fontsize=18)
ax.set_xlabel('V$_{lsr}$ (kms/s)', fontsize=18)


rfi_mask=np.where((data['vel'] > 79.0) & (data['vel'] < 99.0))
spectra_blcorr[rfi_mask]=0.0

rfi_mask=np.where((data['vel'] > -190.0) & (data['vel'] < -185.0))
spectra_blcorr[rfi_mask]=0.0
#rfi_mask=np.where((data['vel'] > -50.0) & (data['vel'] < -48))
#chanrfi=int(rfi_mask[0])
#spectra_blcorr[rfi_mask]=(spectra_blcorr[chanrfi+1]+spectra_blcorr[chanrfi-1])/2.0


#velocity_mask1=(data['vel'] > 0).nonzero()
#velocity_mask2=(data['vel'] < 60).nonzero()
#print(velocity_mask)
#print(velocity_mask1,velocity_mask2)


fig=plt.figure(figsize=(10,7))
ax = fig.add_subplot(111)
ax.set_xlim(-200,200)
ax.set_ylim(-5,70)

lin1=ax.plot(data['vel'],spectra_blcorr,color='black',linestyle='steps')
ax.tick_params('both', which='major', length=15, width=1, pad=15)
ax.tick_params('both', which='minor', length=7.5, width=1, pad=15)

ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
#for label in (ax.get_xticklabels() + ax.get_yticklabels()):
#            label.set_fontproperties(ticks_font)
#for axis in [ax.xaxis, ax.yaxis]:
#    axis.set_major_formatter(ScalarFormatter())
#    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y,pos: ('{{:.{:1d}f}}'.format(int(np.maximum(-np.log10(y),0)))).format(y)))
for axis in ['top','bottom','left','right']:
   ax.spines[axis].set_linewidth(2)

ax.set_ylabel('Antenna Temperature (K)', fontsize=18)
ax.set_xlabel('V$_{lsr}$ (km/s)', fontsize=18)
ax.text(-150,66.0, 'Nielsen Hall Radio Telescope',fontsize=16)
ax.text(-150,63.5, 'Hydrogen 21 cm emission line',fontsize=16)
ax.text(-150,61.0, 'Galactic lat=0, long=110.0;      37 minute exposure',fontsize=16)
fig.savefig('G110-long.pdf')





intensity_mask=np.where((data['vel'] > -150.0) & (data['vel'] < 25.0))

fig=plt.figure(figsize=(10,7))
ax = fig.add_subplot(111)
ax.set_xlim(-200,200)
ax.set_ylim(-5,70)

lin1=ax.plot(data['vel'],spectra_blcorr,color='black',linestyle='steps')
lin2=ax.plot(data['vel'][intensity_mask],np.zeros(len(data['vel'][intensity_mask])),color='black',linestyle='dotted')
ax.tick_params('both', which='major', length=15, width=1, pad=15)
ax.tick_params('both', which='minor', length=7.5, width=1, pad=15)

ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
#for label in (ax.get_xticklabels() + ax.get_yticklabels()):
#            label.set_fontproperties(ticks_font)
#for axis in [ax.xaxis, ax.yaxis]:
#    axis.set_major_formatter(ScalarFormatter())
#    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y,pos: ('{{:.{:1d}f}}'.format(int(np.maximum(-np.log10(y),0)))).format(y)))
for axis in ['top','bottom','left','right']:
   ax.spines[axis].set_linewidth(2)

ax.set_ylabel('Antenna Temperature (K)', fontsize=18)
ax.set_xlabel('V$_{lsr}$ (km/s)', fontsize=18)
ax.text(-150,66.0, 'Nielsen Hall Radio Telescope',fontsize=16)
ax.text(-150,63.5, 'Hydrogen 21 cm emission line',fontsize=16)
ax.text(-150,61.0, 'Galactic lat=0, long=110.0;      37 minute exposure',fontsize=16)

intensity=np.sum(spectra_blcorr[intensity_mask])
chanwidth=data['vel'][0]-data['vel'][1]
#print(len(intensity_mask[0]))
intensity_rms=rms*chanwidth*(float(len(intensity_mask[0])))**0.5
print((intensity)*chanwidth, '+/-',intensity_rms, 'K km/s')
