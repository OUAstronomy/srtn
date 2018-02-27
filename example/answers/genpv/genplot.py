#!/usr/bin/env python

import numpy as np
import math
import matplotlib.pyplot as plt
from os.path import isfile
from glob import glob
from argparse import ArgumentParser

def doppler(val,rest=1420.406):
    '''
    '''
    c = 2.99792458e8  # m/s
    return (val-rest)/rest * c/1000.

def plotterSpectra(x,y,title,save=True):
    plt.clf()
    plt.figure(figsize=[15,12])
    plt.plot(x,y,'b-')
    locs = np.linspace(x[0],x[-1],50)
    nlab = [doppler(i) for i in locs]
    labels = ['{}\n{}'.format(j,nlab[i]) for i,j in enumerate(locs)]
    plt.xticks(locs,labels)
    plt.xlabel('Frequency (MHz)\nVelocity (Km/s)')
    plt.ylabel('Tant (K)')
    plt.title(title)
    plt.margins(0.2)
    plt.subplots_adjust(bottom=0.15)
    plt.draw()
    if save:
        plt.savefig(title+'.pdf')
    plt.show()

def plotterPV(x,y,title):
    plt.clf()
    plt.figure(figsize=[15,12])
    plt.plot(x,y,'b-')
    labels = ['{}\n{}'.format(i,round(8.5*np.sin(i*np.pi/180.),2)) for i in x]
    plt.xticks(x,labels)
    plt.xlabel('Position (degrees)\n(Kpc)')
    plt.ylabel('Velocity (Km/s)')
    plt.title(title)
    plt.margins(0.2)
    plt.subplots_adjust(bottom=0.15)
    plt.draw()
    plt.savefig(title+'.pdf')
    plt.show()

def find_nearest(array,value):
    idx = (np.abs(array-value)).argmin()
    return array[idx]

def maxV(x,y):
    sig = 4. * np.std(y)
    print(sig)
    print(find_nearest(y,sig))
    print(x[y.tolist().index(find_nearest(y,sig))])
    return x[y.tolist().index(find_nearest(y,sig))]



parser = ArgumentParser(description='For plotting rotation curve, not well generalized check code')
parser.add_argument('-i', '--input', type=str, help='Input filename or indentifying string', dest='input',default='G')
parser.add_argument('-o', '--output',type=str, help='Name of output file',dest='output',default='galrot')
parser.add_argument('-p', '--plot',dest='plot',action='store_true',help='Toggle this if you want to plot all positions')
args = parser.parse_args()

listoffiles = [x for x in glob(args.input+'*') if ('.pyc' not in x) and (isfile(x) and ('.pdf' not in x))]
print(listoffiles)
finalmatrix = {}
for x in listoffiles:
    tempmatrix = np.loadtxt(x,skiprows=1).reshape(-1,2)
    #vels = np.array([doppler(y)/1000. for y in tempmatrix[:,0]]).reshape(-1,1)

    finalmatrix['.'.join(x.split('.')[:-1])] = tempmatrix # np.append(tempmatrix,vels,1)

plottingmatrix=[]
for i in finalmatrix:
    x = finalmatrix[i][:,0]
    y = finalmatrix[i][:,1]
    print(i)
    if args.plot:
        plotterSpectra(x,y,i)
    maxv = maxV(x,y)
    plottingmatrix.append([float(i.strip('G')),doppler(maxv)])

a = np.array(plottingmatrix).reshape(-1,2)
plottingmatrix = a[a[:,0].argsort()]
print(plottingmatrix)

plotterPV(plottingmatrix[:,0],plottingmatrix[:,1],args.output)


