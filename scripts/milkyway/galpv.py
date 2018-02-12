#!/usr/bin/env python
'''
Name  : Galaxy Position-Velocity CMD creator, galpv.py
Author: Nickalas Reynolds
Date  : Fall 2017
Misc  : Will create an appropriate srt.cat and command file for 
        wanted to observe the milky way galaxy
'''

# imported standard modules
import sys
import argparse
import math as m
from math import acos,sqrt,pi,cos,sin

def ang_vec(deg):
    rad = deg*pi/180.
    return (cos(rad),sin(rad))
def length(v):
    return sqrt(v[0]**2+v[1]**2)
def dot_product(v,w):
   return v[0]*w[0]+v[1]*w[1]
def determinant(v,w):
   return v[0]*w[1]-v[1]*w[0]
def inner_angle(v,w):
   cosx=dot_product(v,w)/(length(v)*length(w))
   rad=acos(cosx) # in radians
   return rad*180/pi # returns degrees
def angle_clockwise(A, B):
    inner=inner_angle(A,B)
    det = determinant(A,B)
    if det>0: #this is a property of the det. If the det < 0 then B is clockwise of A
        return inner
    else: # if the det > 0 then A is immediately clockwise of B
        return 360-inner

# checking python version
assert sys.version_info[0] >= 3

parser = argparse.ArgumentParser()
parser.add_argument('-r','--resolution',dest='r',default=5,type=float)
parser.add_argument('-sd','--startdegree',type=float,dest='sd',required=True)
parser.add_argument('-ed','--enddegree',type=float,dest='ed',required=True)
parser.add_argument('-d', '--direction',type=str, default="+",dest='d')
parser.add_argument('-i', '--integration',type=int, default=120,dest='i')
parser.add_argument('--debug',action='store_true')
args = parser.parse_args()

if args.d == '+':
    outname = "galpv_{}_p_{}".format(args.sd,args.ed)
else:
    outname = "galpv_{}_m_{}".format(args.sd,args.ed)

assert args.d in ['-','+']
start = args.sd%360
end   = args.ed%360


# make degree array
if ((360./args.r) % 1) != 0:
    print('Resolution is improper, will still generate file')
alldegrees = [round(x*args.r,2) for x in range(int(360./args.r))]

if args.d == "+":# positive direction
    diff = round(angle_clockwise(ang_vec(start),ang_vec(end)),2)
    numd = int(m.ceil(diff/args.r))
    final = [round((start + x*args.r),2)%360 for x in range(numd)]

elif args.d == "-": # negative direction
    diff = round(360.-angle_clockwise(ang_vec(start),ang_vec(end)),2)
    numd = int(m.ceil(diff/args.r))
    final = [round((start - x*args.r),2)%360  for x in range(numd)]

if end != 0:
    final.append(end)

print(diff,numd,start,end)

# CMD file creation
totaltime=len(final)*args.i
with open(outname+'_cmd.txt','w') as f:
    f.write(': record ./{}\n'.format(outname+'.dat'))
    for x in final:
        f.write(':{} G{}\n'.format(args.i,x))
    f.write(':roff\n')
    f.write(':stow\n')
    f.write('')

print("Total Time: {}s ".format(totaltime))  

# making srt.cat file
with open(outname+'.cat','w') as f:
    f.write('BIGRAS\n')
    f.write('CALMODE 20\n')
    f.write('STATION 35.207 97.44 Sooner_Station\n')
    f.write('SOU 00 00 00  00 00 00 Sun\n')
    f.write('\n')
    for i in final:
        f.write("GALACTIC {} 0.0 G{}\n".format(round(i,2),round(i,2)))
    f.write('\n')
    f.write('NOPRINTOUT\n')
    f.write('BEAMWIDTH 5\n')
    f.write('NBSW 10\n')
    f.write('AZLIMITS 0 360\n')
    f.write('ELLIMITS 0 90.0\n')
    f.write('STOWPOS 90 2\n')
    f.write('TSYS 125    \n')
    f.write('TCAL 1200    // should equal ambient load\n')
    f.write('RECORD 5 SPEC\n')
    f.write('NUMFREQ 256    // good choice for dongle\n')
    f.write('BANDWIDTH 2.0\n')
    f.write('FREQUENCY 1420.406\n')
    f.write('RESTFREQ 1420.406\n')
    f.write('FREQCORR -0.05   // TV dongle correction\n')
    f.write('NBLOCK 5   // number of blocks per update - can be reduced for Beagle board with slow display for PCI it is hardwired to 20\n')
    f.write('COUNTPERSTEP 100 // to move with old SRT is steps\n')
    f.write('ROT2SLP 2  // change rot2 sleep time to 3 seconds - default is 1 second\n')
    f.write('NOISECAL 70 // default is 300\n')
    f.write('')

#############
# end of file
