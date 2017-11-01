#!/usr/bin/env python
'''
Name  : SRT Utilities, srtutilities.py
Author: Nickalas Reynolds
Date  : Fall 2017
Misc  : File will handle misc srt specific function
'''

# import modules
from os import system as _SYSTEM_
from sys import exit

# creates example data file
def example_data(logger):
    logger.debug('Make sure your file follows the appropriate format in `exampledata.txt`')
    with open('exampledata.txt','w') as f:
        f.write('DATE 2017:094:10:37:20 obsn  88 az 141 el 45 freq_MHz  1420.4000 Tsys 145.521 Tant 30.670 vlsr  -44.61 glat -0.188 glon 30.118 azoff 0.00 eloff 0.00 source G30.0 \n')
        f.write('Fstart 1419.397 fstop 1421.403 spacing 0.009375 bw    2.400 fbw    2.000 MHz nfreq 256 nsam 5242880 npoint 214 integ    10 sigma    0.479 bsw 0\n')
        f.write('Spectrum      9 integration periods\n')
        f.write('164.961  164.501  164.497  165.814  164.366  163.848  164.425  164.817  163.488  164.782  164.538  164.079  163.664  163.868  164.338  164.150  165.517  164.604  164.075  163.548  165.084  164.829  165.189  165.521  165.451  164.947  165.412  163.895  165.626  163.683  164.459  164.750  163.875  165.257  165.162  164.489  164.263  165.657  163.502  164.054  164.957  164.651  164.733  164.398  164.031  164.324  164.697  165.317  164.973  164.275  166.077  164.760  164.673  164.110  166.978  165.867  164.642  164.824  164.962  165.273  165.753  165.621  165.729  167.135  164.210  164.751  164.203  166.693  164.639  176.660  173.546  169.465  166.164  167.579  166.487  169.384  169.633  170.601  172.471  174.994  176.017  177.545  180.572  181.365  182.896  183.143  184.577  185.640  186.892  185.969  185.614  186.802  185.741  187.221  185.827  185.901  187.812  187.124  185.852  186.538  186.615  186.389  186.351  186.070  185.496  186.945  185.587  186.622  187.048  188.369  189.955  190.190  191.671  192.971  194.455  194.176  193.238  193.596  195.104  195.150  198.364  200.667  203.492  207.231  208.046  208.940  209.183  208.427  208.892  208.529  208.236  206.435  206.914  208.298  210.447  206.715  193.081  185.082  179.708  178.110  176.493  177.906  177.270  179.313  179.512  179.473  179.329  180.017  180.449  181.619  182.544  183.873  185.114  184.562  184.546  184.539  183.961  182.236  180.506  178.029  176.666  173.057  170.991  170.026  169.583  169.160  167.841  168.033  167.912  167.844  167.061  167.916  166.821  168.598  166.980  166.568  167.143  166.933  167.037  166.369  165.921  165.314  167.193  167.039  165.201  166.131  166.984  166.186  166.181  166.151  166.996  166.588  167.031  167.161  167.550  166.579  167.773  166.925  167.155  166.862  166.709  166.519  167.657  169.163  167.458  173.242  173.305  168.885  167.484  168.536  169.431  169.063  167.559  167.845 \n')
    logger.debug('Made example file.')

# preps the data file, returns the data from the file
def prep(orig,inputfile):
    _SYSTEM_('cp -f {} {}'.format(orig,inputfile))
    _SYSTEM_("sed -i '/entered/d' {}".format(inputfile))
    _SYSTEM_("sed -i '/cmd out of limits/d' {}".format(inputfile))
    _SYSTEM_("sed -i '/Scan/d' {}".format(inputfile))

    with open(inputfile,'r') as f:
        f.seek(0)
        _TMPLINE_=f.readline().strip('\n').split(' ')
    if 'azoff' not in _TMPLINE_:  # check if format is correct of file
        _SYSTEM_("sed -i -e 's/source/azoff 0.00 eloff 0.00 source/g' " + inputfile)

    with open(inputfile,'r') as f:
        f.seek(0)
        allines = [[x for x in line.strip('\n').split(' ') if x != ''] for line in f.readlines()]
    return allines

class locations(object):

    def __init__(self):
        self.locations = {'norman':['35d13m21.2s','-97d26m22.1s',370,-4],\
                          'apo':['','',2300,-5]}

    def get_locations(self):
        return ', '.join([i for i in self.locations])

    def add_location(self,location):
        if not self.verify_location(location[0]):
            try:
                if len(location) == 5:
                    self.locations[location[0]] = [location[1],location[2],float(location[3]),int(location[4])]
                else:
                    raise RuntimeError('Incorrect format, please follow: \n\
                                        [{},{}] which is [name,lat,long,height,timezone] and \n\
                                        lat is North bias, long is East Bias, height is in meters, timezone is integer from utc\
                                        '.format('norman',','.join(self.locations['norman'])))
            except IndexError:
                raise RuntimeError('Incorrect format, please follow: \n\
                                    [{},{}] which is [name,lat,long,height,timezone] and \n\
                                    lat is North bias, long is East Bias,height is in meters, timezone is integer from utc\
                                    '.format('norman',','.join(self.locations['norman'])))

    def verify_location(self,checking):
        if checking in self.locations:
            return True
        else:
            return False

class special(object):

    def fwhm(self,sig):
        import numpy as np
        return 2. * ((2. * np.log10(2.)) ** 0.5) * (sig)

    def get_params(self):
        return self.params

    def set_params(self,params):
        self.params = params

    # single gaussian
    def gaussian(self,x,mu,sig,A):
        from numpy import inner,exp
        vector = inner(x - mu,x - mu)
        return A * exp(-0.5 * (vector/sig)** 2)

    # multigaussian single dimension
    def multigauss(self,x,mugrid,siggrid,Agrid):
        total = []
        for mu,sig,A in zip(mugrid,siggrid,Agrid):
            temp = self.gaussian(x,mu,sig,A)
            total += temp
        if len(total) != len(x):
            raise RuntimeError('Shape of multigauss and x range not the same')
            exit()
        else:
            return total

    def polynomial(self,x,coeff):
        total = []
        if (type(coeff) != list) or (type(coeff) != np.ndarray):
            coeff = [coeff,]
        for order in range(len(coeff)):
            temp = coeff[order] * x[:] ** order
            total += temp
        if len(total) != len(x):
            raise RuntimeError('Shape of polynomial and x range not the same')
            exit()
        else:
            return total

    # bessel function
    def bessel2(self,x ,order):
        from scipy.special import yv
        return yv(order, x)

if __name__ == "__main__":
    print("Testing module...")
    
