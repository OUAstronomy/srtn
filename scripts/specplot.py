#!/usr/bin/env python
'''
Name  : Spectrum Reduction, specreduc.py
Author: Nickalas Reynolds
Date  : Fall 2017
Misc  : Will reduce the 1d spectra data from the specparse program
        Will output numerous plots along the way and ask if you want to delete the intermediate steps at the end
'''

# import standard modules
from sys import version_info,exit
from os import system as _SYSTEM_
from os.path import isfile
from glob import glob
from argparse import ArgumentParser
import time

# import nonstandard modules
import numpy as np
from astropy.table import Table
from astropy.io import ascii
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import matplotlib.ticker as ticker
from matplotlib.widgets import LassoSelector
from matplotlib.path import Path
from scipy.optimize import curve_fit
from scipy.integrate import trapz
ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')

# import custom modules
from colours import colours
from constants import constants
import utilities
from version import *

# checking python version
assert assertion()
__version__ = package_version()

####################################################################################
# prepare mask lasso command
####################################################################################
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

####################################################################################
# plotting command
####################################################################################
class plotter(object):
    def __init__(self,title,logger=None,size=[10,7]):
        self.size   = size
        self.title  = title
        self.logger = logger
        self.data   = {}

    def open(self,numsubs=(1,1),xlabel=None,ylabel=None):
        self.numsubs = numsubs
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.f = plt.subplots(nrows=numsubs[0], ncols=numsubs[1],figsize=self.size)
        self.f[1].tick_params('both', which='major', length=15, width=1, pad=15)
        self.f[1].tick_params('both', which='minor', length=7.5, width=1, pad=15)
        self.f[1].set_ylabel(ylabel, fontsize=18)
        self.f[1].set_xlabel(xlabel, fontsize=18)
        self.f[1].set_title(self.title)

    def scatter(self,x,y,datalabel,**kwargs):
        self.data[datalabel] = self.f[1].scatter(x,y,**kwargs)

    def plot(self,x,y,datalabel,**kwargs):
        self.data[datalabel] = self.f[1].plot(x,y,**kwargs)

    def int(self):
        plt.ion()

    def draw(self):
        plt.legend()
        plt.draw()

    def selection(self,label):
        temp      = []
        msk_array = []
        while True:
            selector = SelectFromCollection(self.f[1], self.data[label],0.1)
            self.logger.header2("Draw mask regions around the non-baseline features...")
            self.draw()
            self.logger.pyinput('[RET] to accept selected points')
            temp = selector.xys[selector.ind]
            msk_array = np.append(msk_array,temp)
            selector.disconnect()
            # Block end of script so you can check that the lasso is disconnected.
            answer = self.logger.pyinput("(y or [SPACE]/n or [RET]) Want to draw another lasso region")
            plt.show()
            if ((answer.lower() == "n") or (answer == "")):
                self.save('TEMPORARY_FILE_SPECREDUC_PLOT.pdf')
                break
        self.logger.waiting(auto)
        return msk_array

    def save(self,name):
        plt.savefig(name)

    def resetplot(self,title):
        plt.clf()
        self.title = title
        self.data = {}
        self.open(self.numsubs,self.xlabel,self.ylabel)
        self.limits()

    def limits(self,xlim=None,ylim=None):
        if xlim:
            self.f[1].set_xlim(xlim[0],xlim[1])
        if ylim:
            self.f[1].set_ylim(ylim[0],ylim[1])

####################################################################################
# create fitting code for gauss bimodal lines etc
####################################################################################
def gauss(x,mu,sigma,A):
    return A*np.exp(-(x-mu)**2/2./sigma**2)

def bimodal(x,mu1,sigma1,A1,mu2,sigma2,A2):
    return gauss(x,mu1,sigma1,A1)+gauss(x,mu2,sigma2,A2)

####################################################################################
# main function
####################################################################################
if __name__ == "__main__":
    # -----------------------
    # Argument Parser Setup
    # -----------------------
    description = 'Reads in masterfile output from all_hispec.py and reduces. ' \
                  'Will flatten baselines, remove RFI, and find the integrated intensity.\n' \
                  '{} Version: {} {}'.format(colours.WARNING,__version__,colours._RST_)

    in_help   = 'name of the file to parse'
    spec_help = colours.OKGREEN + 'Current things to work on:\
                \n-Make final pretty plot\
                \nAlso add function that uses Ridge Regression to auto fit everything' + colours._RST_
    f_help    = 'The output file identifying string'
    a_help    = 'If toggled will run the script non interactively'
    log_help  = 'name of logfile with extension'
    v_help    = 'Integer 1-5 of verbosity level'

    # Initialize instance of an argument parser
    #############################################################################
    parser = ArgumentParser(description=description)
    parser.add_argument('-i', '--input', type=str, help=in_help, dest='fin',required=True)
    parser.add_argument('-o','--output',type=str, help=f_help,dest='fout',required=True)
    parser.add_argument('-w','--work', help='print things to work on',dest='work',action='store_true')
    parser.add_argument('--auto',action="store_true", help=a_help,dest='auto')
    parser.add_argument('-l', '--logger',type=str, help=log_help,dest='log')
    parser.add_argument('-v','--verbosity', help=v_help,default=2,dest='verb',type=int)

    # Get the arguments
    #############################################################################
    args = parser.parse_args()
    orig_datafile = args.fin
    ooutfilename = args.fout
    worki = args.work
    auto = args.auto
    logfile = args.log
    verbosity = args.verb

    # Set up message logger       
    #############################################################################     
    if not logfile:
        logfile = ('{}_{}.log'.format(__file__[:-3],time.time()))
    logger = utilities.Messenger(verbosity=verbosity, add_timestamp=True,logfile=logfile)
    logger.header1("Starting {}....".format(__file__[:-3]))
    logger.debug("Commandline Arguments: {}".format(args))

    # checking for extra dep
    #############################################################################
    if worki is True:
        logger.success(spec_help)
        exit()

    # version control
    #############################################################################
    _VLINE_ = orig_datafile.split(".txt")[0].split("_v")[1]
    try:
        assert _VLINE_ == __version__
    except AssertionError:
        logger.warning('Input file version {} doesn\'t match programs version {}'.format(_VLINE_,__version__))
        _A_ = logger.waiting(auto)
        if (_A_ == ' ') or (_A_.lower() == 'n'):
            exit()
        else:
            logger.message('Continuing...')

    # handle files
    #############################################################################
    files = [f for f in glob(ooutfilename+'*') if isfile(f)]
    if files == []:
        files = ['None',]
    logger.failure("Will remove these files: {}\n".format(' | '.join(files)))
    logger.warn('Move these to a directory if you don\'t want these deleted')

    _TEMP_ = str(time.time())
    datafile = 'TEMPORARY_FILE_SPECREDUC_{}_0.txt'.format(_TEMP_)
    _TEMPB_ = 'TEMPORARY_FILE_SPECREDUC_{}'.format(_TEMP_)
    _TEMP0_ = 'TEMPORARY_FILE_SPECREDUC_{}.txt'.format(_TEMP_)
    _TEMP1_ = 'TEMPORARY_FILE_SPECREDUC_{}_1.txt'.format(_TEMP_)
    _TEMP2_ = 'TEMPORARY_FILE_SPECREDUC_{}_2.txt'.format(_TEMP_)
    _TEMP3_ = []

    logger.waiting(auto)
    logger._REMOVE_(files)
    logger._REMOVE_(_TEMP_)
    _SYSTEM_('cp -f ' + orig_datafile + ' ' + datafile)

    # getting firstlines
    #############################################################################
    _SYSTEM_('head -n 2 ' + datafile + ' > ' + _TEMP0_)
    with open(_TEMP0_,'r') as f:
        first = ''.join(f.readlines())
    _SYSTEM_("sed -i '1d' " + datafile)
    with open(datafile, 'r') as f:
        first_line=f.readline().strip('\n').split(" ")
    _SYSTEM_("sed -i '1d' " + datafile)
    data = ascii.read(datafile)

    # to verify correct input
    #############################################################################
    logger.header2("Will reduce these ({}) sources: {}".format(len(first_line),"|".join(first_line)))
    
    # starting at non-zero source
    #############################################################################
    acstart = ''
    counting = 0
    while True:
        try:
            newstart = logger.pyinput('(y or [SPACE]/[RET] or n) Do you wish to start at a source')
            if(newstart == ' ' ) or (newstart.lower() == 'y'):
                acstart = logger.pyinput('Input source exactly')
            else:
                break
            if acstart in first_line:
                counting = 1
                break
            else:
                logger.debug('Try again')
                continue
        except ValueError:
            continue

    # actual plotting now
    #############################################################################
    total_num = 0
    while total_num < len(first_line):
        if counting == 1:
            total_num = first_line.index(acstart)
            counting = 0
        if total_num == 0:     
            col1 = "vel"
            col2 = "Tant"
            col0 = "vel_vlsr"
            col3 = 'freq'
        else:
            col1 = "vel_{}".format(total_num)
            col2 = "Tant_{}".format(total_num)
            col0 = "vel_vlsr_{}".format(total_num)
            col3 = "freq_{}".format(total_num)

        outfilename = ooutfilename + "_" + first_line[total_num]
        logger.warn('Working on: {}'.format(outfilename))
        with open(_TEMP2_,'w') as _T_:
            _T_.write('Working on: {}\n'.format(outfilename ))
        minvel = min(data[col1])
        maxvel = max(data[col1])
        data.sort([col1])
        
        # plot raw data
        #########################################################################
        x2label = ''
        x1label = r'V$_{lsr}$ (km/s)'
        ylabel = 'Antenna Temperature (K)'

        rawfig = plotter('Raw Data Lasso',logger)
        rawfig.int()
        rawfig.open((1,1),x1label,ylabel)
        rawfig.scatter(data[col1],data[col2],'scatter raw')
        rawfig.plot(data[col1],data[col2],'line raw',color='red',linestyle='steps')
        # prepare mask
        rawfig.draw()
        # baseline
        baseline_med=np.median(data[col2])/1.02
        baseline_ul=baseline_med*1.02
        logger.message('Median of baseline: {} and 2sigma baseline {}'.format(baseline_med,baseline_ul))
        with open(_TEMP2_,'a') as _T_:
            _T_.write('Median of baseline: {} and 2sigma baseline {}'.format(baseline_med,baseline_ul))

        # actual defining mask
        msk_array = rawfig.selection('scatter raw')

        # draw and reset
        
        reset = plotter('Raw Data',logger)
        reset.open((1,1),x1label,ylabel)
        reset.plot(data[col1],data[col2],'raw data',color='black',linestyle='steps')
        reset.draw()
        outfilename_iter =0
        _TEMPNAME = "{}_{}.pdf".format(outfilename,outfilename_iter)
        _TEMP3_.append(_TEMPNAME)
        reset.save(_TEMPNAME)

        # need to invert mask to polyfit region
        mask_inv = []
        for i in range(len(msk_array)):
            mask_inv = np.append(mask_inv,np.where(data[col1] == msk_array[i]))
        mask_tot = np.linspace(0,len(data)-1,num=len(data))
        mask = np.delete(mask_tot,mask_inv)
        mask = [int(x) for x in mask]
        logger.waiting(auto)

        # show projected baselines
        reset.resetplot('Projected Baselines')
        reset.plot(data[col1],data[col2],'raw',color='black',linestyle='steps')
        reset.plot([minvel,maxvel],[baseline_med,baseline_med],'lower',color='red',linestyle='steps')
        reset.plot([minvel,maxvel],[baseline_ul,baseline_ul],'upper',color='red',linestyle='steps')
        reset.draw()
        outfilename_iter +=1
        _TEMPNAME = "{}_{}.pdf".format(outfilename,outfilename_iter)
        _TEMP3_.append(_TEMPNAME)
        reset.save(_TEMPNAME)

        # fitting baseline to higher order polynomial
        newask = ' '
        while (newask.lower() == 'n')or (newask == ' '):
            polyfit = ''
            asking = 0
            while True:
                try:
                    asking = logger.pyinput('what order polynomial do you want to fit to the baseline (integer) or [RET] for 4? ')
                    if asking == '':
                        polynumfit = 4
                        break
                    polynumfit = int(asking)
                except ValueError:
                    logger.message('Please input an integer.')
                    continue
                if polynumfit:
                    break

            # fitting polynomial 4th order to baseline
            fit = np.polyfit(data[col1][mask],data[col2][mask],polynumfit)
            fit_fn = np.poly1d(fit)
            logger.waiting(auto)

            # plotting fitted baseline to original image
            
            reset.resetplot('Plotting fitted baseline')
            reset.plot(data[col1],data[col2],'data',color='black',linestyle='steps',label='data')
            reset.plot(data[col1],fit_fn(data[col1]),'model',color='red',linestyle='steps',label='model')
            reset.draw()
            newask = logger.pyinput('(y or [RET]/n or [SPACE]) Was this acceptable? ')
            if (newask.lower() == 'y') or (newask == ''):
                logger.waiting(auto)
                with open(_TEMP2_,'a') as _T_:
                    _T_.write("The polynomial is: \n {}\n".format(fit_fn))
                break


        outfilename_iter +=1
        _TEMPNAME = "{}_{}.pdf".format(outfilename,outfilename_iter)
        _TEMP3_.append(_TEMPNAME)
        reset.save(_TEMPNAME)

        # defining corrected spectra
        spectra_blcorr=data[col2].copy()
        spectra_blcorr=data[col2]-fit_fn(data[col1])
        maxt = max(spectra_blcorr)
        mint = min(spectra_blcorr)

        # defining RMS
        rms=np.std(spectra_blcorr[mask])
        logger.message('RMS Noise: {}K'.format(rms))
        with open(_TEMP2_,'a') as _T_:
            _T_.write('RMS Noise: {}K\n'.format(rms))
        logger.waiting(auto)

        # plotting the corrected baseline
        reset.resetplot('Plotting the corrected baseline')
        reset.plot(data[col1],spectra_blcorr,'data',color='black',linestyle='steps',label='data')
        reset.plot([minvel,maxvel],[0,0],'baseline',color='red',linestyle='steps',label='flat baseline')
        reset.draw()
        logger.waiting(auto)
        outfilename_iter +=1
        _TEMPNAME = "{}_{}.pdf".format(outfilename,outfilename_iter)
        _TEMP3_.append(_TEMPNAME)
        reset.save(_TEMPNAME)

        # define the RFI
        lasso = plotter('Lasso selection:',logger)
        lasso.int()
        lasso.open((1,1),x1label,ylabel)
        lasso.scatter(data[col1],spectra_blcorr,'data',color='black',label='datapoints')
        lasso.plot(data[col1],spectra_blcorr,'rfi',color='blue',linestyle='steps',label='rfi')
        lasso.plot([minvel,maxvel],[0,0],'flat',color='red',linestyle='steps',label='flat baseline')
        lasso.draw()

        temp = []
        rfi_mask_array = lasso.selection('data')
        rfi_mask = []

        newask = ' '
        _TRY_ =1
        for i in range(len(rfi_mask_array)):
            rfi_mask = np.append(rfi_mask,np.where(data[col1] == rfi_mask_array[i]))
        rfi_mask = [int(x) for x in rfi_mask]
        logger.debug('RFI mask region: {}'.format(','.join(map(str,rfi_mask))))

        # remove rfi
        logger.message("Will try fitting with simple polynomial, gaussian, bimodal, or fail")
        rfi_fit_fn_ans=''
        while ((newask.lower() == 'n')or (newask == ' ')) and (len(rfi_mask) > 0):
            _TEMPSPEC_ = spectra_blcorr
            FITX    = np.delete(data[col1],rfi_mask)
            FITSPEC = np.delete(_TEMPSPEC_,rfi_mask)
            mu = data[col1][np.where(spectra_blcorr == max(spectra_blcorr))][0]
            gaussrms = abs(data[col1][rfi_mask[len(rfi_mask)-1]] - data[col1][rfi_mask[0]])*2.
            # fitting polynomial nth order to baseline
            try:
                if _TRY_ == 1:
                    logger.warn('Polynomial fit...')
                    rfi_fit = np.polyfit(FITX,FITSPEC,20)
                    rfi_poly_fn = np.poly1d(rfi_fit)
                    rfi_fit_fn = rfi_poly_fn
                    function = rfi_poly_fn(data[col1])

                # fit Gaussian
                elif _TRY_ == 2:
                    logger.warn('Gaussian fit...')
                    _expected1=[mu,gaussrms,np.max(_TEMPSPEC_)]
                    logger.debug("Input params: {}".format(_expected1))
                    _params1,_cov1=curve_fit(gauss,FITX,FITSPEC,_expected1)
                    logger.debug("Fit params: {}".format(_params1))
                    _sigma1=np.sqrt(np.diag(_cov1))
                    function = gauss(data[col1],*_expected1)

                    rfi_fit_fn = 'gauss(x,mu1,sigma1,A1)' + ','.join(map(str,_params1))

                elif _TRY_ == 3:
                    logger.warn('Bimodal Gaussian fit...')
                    _expected2=[mu,gaussrms,np.max(_TEMPSPEC_),mu,gaussrms,np.max(_TEMPSPEC_)]
                    logger.debug("Input params: {}".format(_expected2))
                    _params2,_cov2=curve_fit(bimodal,FITX,FITSPEC,_expected2)
                    _sigma2=np.sqrt(np.diag(_cov2))
                    logger.debug("Fit params: {}".format(_params2))
                    function = bimodal(data[col1],*_expected2)

                    rfi_fit_fn = 'gauss(x,mu1,sigma1,A1)+gauss(x,mu2,sigma2,A2)' + ','.join(map(str,_params2))

                elif _TRY_ >= 4:
                    logger.failure('Auto fitting RFI failed...')
                    functions = ['polynomial','gaussian','bimodal']
                    ans = logger.pyinput("(integer or [RET]) name of better fit {} or set values to zero with [RET]".format(functions))
                    if ans.lower() in functions:
                        _TRY_ = int(functions.index(ans)+1)
                    else:
                        _TEMPSPEC_[rfi_mask] = 0.0
                        break

                # plotting fitted baseline to original image
                
                reset.resetplot('Plotting RFI removal')
                if _TRY_ == 1:
                    for _RFI_ in rfi_mask:
                        logger.debug("Region of RFI: {}".format(_TEMPSPEC_[_RFI_]))
                        _TEMPSPEC_[_RFI_] = rfi_poly_fn(data[col1][_RFI_]) 
                        logger.debug("Region of RFI after fit: {}".format(_TEMPSPEC_[_RFI_]))
                    reset.plot(data[col1],rfi_poly_fn(data[col1]),'polyfit',color='yellow',linestyle='steps',label='Poly model')
                elif _TRY_ == 2:
                    for _RFI_ in rfi_mask:
                        logger.debug("Region of RFI: {}".format(_TEMPSPEC_[_RFI_]))
                        _TEMPSPEC_[_RFI_] = gauss(data[col1][_RFI_],*_params1)
                        logger.debug("Region of RFI after fit: {}".format(_TEMPSPEC_[_RFI_]))
                    reset.plot(data[col1],gauss(data[col1],*_params1),'gauss',color='red',linestyle='steps',label='Gauss model')
                elif _TRY_ == 3:
                    for _RFI_ in rfi_mask:
                        logger.debug("Region of RFI: {}".format(_TEMPSPEC_[_RFI_]))
                        _TEMPSPEC_[_RFI_] = bimodal(data[col1][_RFI_],*_params2)
                        logger.debug("Region of RFI after fit: {}".format(_TEMPSPEC_[_RFI_]))
                    reset.plot(data[col1],bimodal(data[col1],*_params2),'bimodal',color='orange',linestyle='steps',label='Bimodal model')
            except RuntimeError:
                logger.failure('Couldn\'t converge on try {}, setting values to zero...'.format(_TRY_))
                rfi_fit_fn = "Fitter failed...."
                _TEMPSPEC_[rfi_mask] = 0.0            
            reset.plot(data[col1],_TEMPSPEC_,'data',color='black',linestyle='steps',label='data')
            reset.limits(ylim=(-1,1.2*max(spectra_blcorr)))
            reset.draw()
            newask = logger.pyinput('(y or [RET]/n or [SPACE]) Is this acceptable? ')
            if (newask.lower() == 'y') or (newask == ''):
                logger.waiting(auto)
                with open(_TEMP2_,'a') as _T_:
                    _T_.write("The function is: \n{}\n".format(rfi_fit_fn))
                break
            else:
                _TRY_ +=1

        # draw and reset
        try:
            spectra_blcorr = _TEMPSPEC_
        except:
            pass

        corr = plotter("Corrected Baseline and RFI removed",logger)
        corr.open((1,1),x1label,ylabel)
        corr.plot(data[col1],spectra_blcorr,'corrected',color='black',linestyle='steps',label='corrected')
        corr.plot([minvel,maxvel],[0,0],'flat',color='red',linestyle='steps',label='flat baseline')
        corr.limits(ylim=(-1,1.2*max(spectra_blcorr)))
        corr.draw()
        logger.waiting(auto)
        outfilename_iter +=1
        _TEMPNAME = "{}_{}.pdf".format(outfilename,outfilename_iter)
        _TEMP3_.append(_TEMPNAME)
        corr.save(_TEMPNAME)

        # Final correction plot 
        
        final = plotter('Final corrected plot',logger)
        final.open((1,1),x1label,ylabel)
        final.limits(xlim=(minvel,maxvel),ylim=(mint-1,maxt * 1.1))
        final.plot(data[col1],spectra_blcorr,'data',color='black',linestyle='steps',label='data')
        final.draw()
        logger.waiting(auto)
        outfilename_iter +=1
        _TEMPNAME = "{}_{}.pdf".format(outfilename,outfilename_iter)
        _TEMP3_.append(_TEMPNAME)
        final.save(_TEMPNAME)

        # intensity estimate
        while True:
            try:
                intensity_answer = logger.pyinput('Sigma value for Gaussian (integers * rms) or [RET] for default 5 sigma or "none" to skip')
                if intensity_answer == '':
                    intensity_answer = 5.0
                elif str(intensity_answer).lower() == 'none':
                    break
                intensity_answer = float(intensity_answer)
            except ValueError:
                logger.warn('Please input integer or float.')
                continue
            if intensity_answer <= 3.:
                logger.warn('Low signal Gaussian, result maybe incorrect.')
                logger.warn('Gaussian signal: {}*rms'.format(intensity_answer))
                break
            if intensity_answer > 3.:
                logger.message('Gaussian signal: {}*rms'.format(intensity_answer))
                break
        if str(intensity_answer).lower() != 'none':
            with open(_TEMP2_,'a') as _T_:
                _T_.write('Sigma value for Gaussian: {}\n'.format(intensity_answer))

            while True:
                try:
                    intensity_mask_guess = np.where((spectra_blcorr >= intensity_answer * rms) & (spectra_blcorr >= -intensity_answer * rms))
                    minint=min(data[col1][intensity_mask_guess])
                    maxint=max(data[col1][intensity_mask_guess])
                    while True:
                        if len(intensity_mask_guess) == 0:
                            intensity_answer -=1
                            intensity_mask_guess = np.where((spectra_blcorr >= intensity_answer * rms) & (spectra_blcorr >= -intensity_answer * rms))
                            minint=min(data[col1][intensity_mask_guess])
                            maxint=max(data[col1][intensity_mask_guess])
                        if intensity_answer == 0:
                            intensity_mask_guess = np.linspace(len(data[col1])/4-1,3*len(data[col1])/4-1, num = len(data[col1])/2)
                        if len(intensity_mask_guess) > 0:
                            break
                except ValueError:
                    continue
                if len(intensity_mask_guess) > 0:
                    break

            # Intensity line estimate
            lie = plotter('Intensity Line Estimate',logger)
            lie.open((1,1),x1label,ylabel)
            lie.limits(xlim=(minvel,maxvel),ylim=(mint-1,maxt * 1.1))
            lie.plot(data[col1],spectra_blcorr,'data',color='black',linestyle='steps',label='data')
            lie.plot(data[col1][intensity_mask_guess],np.zeros(len(data[col1][intensity_mask_guess])),'est',color='blue',linestyle='dotted')
            lie.plot([minint,minint],[0,maxt],'lower',color='blue',linestyle='dotted')
            lie.plot([maxint,maxint],[0,maxt],'upper',color='blue',linestyle='dotted')
            lie.draw()
            logger.waiting(auto)
            outfilename_iter +=1
            _TEMPNAME = "{}_{}.pdf".format(outfilename,outfilename_iter)
            _TEMP3_.append(_TEMPNAME)
            lie.save(_TEMPNAME)

            answer = ""
            while True:
                try:
                    answer_ok = logger.pyinput("(y or [RET]/n or [SPACE]) Is region guess for the line intensity is okay")
                    if ((answer_ok.lower() == "y") or (answer_ok == "")):
                        intensity_mask = intensity_mask_guess
                        break
                    else:
                        # define the Intensity
                        lasso.resetplot('Lasso selection:')
                        lasso.scatter(data[col1],spectra_blcorr,'data',color='black')
                        lasso.plot(data[col1],spectra_blcorr,'dataselect',color='blue',linestyle='steps')
                        lasso.plot([minvel,maxvel],[0,0],'int',color='red',linestyle='steps')
                        lasso.draw()
                        # recovering intensity of line 
                        temp = []
                        intensity_mask_array = lasso.selection('data')
                        intensity_mask = []

                        logger.waiting(auto)
                        for i in range(len(intensity_mask_array)):
                            intensity_mask = np.append(intensity_mask,np.where(data[col1] == intensity_mask_array[i]))
                        intensity_mask = [int(x) for x in intensity_mask]

                        # draw and reset
                        minint=min(data[col1][intensity_mask])
                        maxint=max(data[col1][intensity_mask])
                        
                        reset.resetplot('With Line Intensity Mask')
                        reset.plot(data[col1],spectra_blcorr,'data',color='black',linestyle='steps')
                        reset.plot(data[col1][intensity_mask],np.zeros(len(data[col1][intensity_mask])),'bottom',color='blue',linestyle='dotted')
                        reset.plot([minint,minint],[0,maxt],'lower',color='blue',linestyle='dotted')
                        reset.plot([maxint,maxint],[0,maxt],'upper',color='blue',linestyle='dotted')                
                        reset.draw()
                        break
                except ValueError:
                    continue

            # showing Intensity Mask

            intensitymask = plotter('Intensity Mask',logger)
            intensitymask.open((1,1),x1label,ylabel)
            intensitymask.limits(xlim=(minvel,maxvel),ylim=(mint,maxt * 1.1))
            intensitymask.plot(data[col1],spectra_blcorr,'data',color='black',linestyle='steps',label='Data')
            intensitymask.plot(data[col1][intensity_mask],np.zeros(len(data[col1][intensity_mask])),'bottom',color='blue',linestyle='dotted')
            intensitymask.plot([minint,minint],[0,maxt],'lower',color='blue',linestyle='dotted')
            intensitymask.plot([maxint,maxint],[0,maxt],'upper',color='blue',linestyle='dotted')
            intensitymask.draw()
            logger.waiting(auto)
            outfilename_iter +=1
            _TEMPNAME = "Final.{}_{}.pdf".format(outfilename,outfilename_iter)
            #_TEMP3_.append(_TEMPNAME)
            intensitymask.save(_TEMPNAME)
            intensitymask.draw()
            plt.show()

            # intensity
            intensity=trapz(spectra_blcorr[intensity_mask],intensity_mask)
            chanwidth=abs(max(data[col1])-min(data[col1]))/len(data[col1])
            if ((answer_ok.lower() == 'y') or (answer_ok == '')):
                intensity_rms=rms*chanwidth*(float(len(intensity_mask[0])))**0.5
            else:
                intensity_rms=rms*chanwidth*(float(len(intensity_mask)))**0.5
            logger.message("Intensity: ")
            logger.message("{} +- {} (K km/s)".format(intensity,intensity_rms))
            with open(_TEMP2_,'a') as _T_:
                _T_.write('Intensity: {} +- {} (K km/s)'.format(intensity,intensity_rms))
        else:
            with open(_TEMP2_,'a') as _T_:
                _T_.write('No intensity guess\n')
        # write to file
        try:
            spec_final = Table([data[col3],data[col0],data[col1],data[col2],spectra_blcorr], names=('freq','vel_sub', 'vel', 'Tant_raw', 'Tant_corr'))
        except KeyError:
            spec_final = Table([data[col3],data[col1],data[col2],spectra_blcorr], names=('freq', 'vel', 'Tant_raw', 'Tant_corr'))           
        ascii.write(spec_final,_TEMP1_,overwrite=True)
        with open(_TEMP1_, 'r') as original: ndata = original.read()
        with open(_TEMP1_, 'w') as modified: modified.write(ndata)  #first + first_line[total_num] + '\n'+str((intensity)*chanwidth) + '+/-' + str(intensity_rms) + 'K km/s' + '\n' +
        _SYSTEM_('cp -f ' + _TEMP1_ + ' ' + outfilename + "_spectra_corr.txt")
        _SYSTEM_('cp -f ' + _TEMP2_ + ' ' + outfilename + "_parameters.txt")




        # pretty plot to go here




        # close and reset
        ans = ''
        ans = logger.pyinput("[RET] to continue to complete this source or [SPACE] to cancel out...")

        plt.close("all")
        total_num +=1
        if ans == ' ':
            total_num = len(first_line) + 1

    logger.pyinput("[RET] to exit")

    # finished
    logger._REMOVE_(_TEMPB_)

    logger.header2("#################################")
    logger.success("Finished with all.")
    logger.message("These are the sources processed: {}".format(' | '.join(first_line)))
    logger.message("These are the files processed: {}".format(orig_datafile))
    files = [f for f in glob(outfilename+'*') if isfile(f)]
    logger.header2("Made the following files: {} and logfile: {}".format(', '.join(files),logfile))
    ans = logger.pyinput("(y or [RET] / n or [SPACE]) if you would like to delete the intermediate files")
    if ans == "" or ans.lower() == 'y':
        for delfile in _TEMP3_:
            logger._REMOVE_(delfile)

    plt.close()

    #############
    # end of code
