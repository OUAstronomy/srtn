'''
Creates plots to correct baselines
author: John Tobin and Nick Reynolds
Date: March 2017
'''
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
from matplotlib.pyplot import draw as draw
from matplotlib.ticker import ScalarFormatter
import matplotlib.ticker as ticker
from six.moves import input
from matplotlib.widgets import LassoSelector
from matplotlib.path import Path
from scipy.optimize import curve_fit

# import custom modules
from colours import colours
from constants import constants
import utilities
from version import *
__version__ = package_version()

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

# main function
if __name__ == "__main__":
    # -----------------------
    # Argument Parser Setup
    # -----------------------
    description = 'Reads in masterfile output from all_hispec.py and reduces. ' \
                  'Will flatten baselines, remove RFI, and find the integrated intensity. ' \
                  'Version: ' + __version__

    in_help   = 'name of the file to parse'
    spec_help = colours.OKGREEN + 'Current things to work on:\n-Make final pretty plot\n' + colours._RST_
    f_help    = 'The output file identifying string'
    a_help    = 'If toggled will run the script non interactively'
    log_help  = 'name of logfile with extension'
    v_help    = 'Integer 1-5 of verbosity level'

    # Initialize instance of an argument parser
    parser = ArgumentParser(description=description)
    parser.add_argument('-i', '--input', type=str, help=in_help, dest='fin',default='')
    parser.add_argument('-o','--output',type=str, help=f_help,dest='fout',default='')
    parser.add_argument('-w','--work', help=spec_help,default='',dest='work',action='store_true')
    parser.add_argument('--auto',action="store_true", help=a_help,dest='auto')
    parser.add_argument('-l', '--logger',type=str, help=log_help,dest='log')
    parser.add_argument('-v','--verbosity', help=v_help,default=2,dest='verb',type=int)

    # Get the arguments
    args = parser.parse_args()
    orig_datafile = args.fin
    ooutfilename = args.fout
    worki = args.work
    auto = args.auto
    logfile = args.log
    verbosity = args.verb

    # Set up message logger            
    if not logfile:
        logfile = ('{}_{}.log'.format(__file_[:-3],time.time()))
    logger = utilities.Messenger(verbosity=verbosity, add_timestamp=True,logfile=logfile)
    logger.header1("Starting {}....".format(__file__[:-3]))

    # checking for extra dep
    if worki is True:
        logger.debug(spec_help)
        exit()

    # checking if args exist
    if not orig_datafile:
        logger.message("Make sure data is if correct format")
    while not orig_datafile:
        try:
            orig_datafile = logger.pyinput("data file name for plotting: ")
        except ValueError:
            continue
        if orig_datafile != "":
            break
    while not ooutfilename:
        try:
            ooutfilename = logger.pyinput("unique output filename (no extension): ")
            break
        except ValueError:
            continue


    # version control
    _VLINE_ = orig_datafile.split(".txt")[0].split("_v")[1]
    try:
        assert _VLINE_ == __version__
    except AssertionError:
        logger.warning('Input file version {} doesn\'t match programs version {}'.format(_VLINE_,__version__))
        _A_ = logger.waiting(auto)
        if (_A_ == ' ') or (_A_ == 'n') or (_A_ == 'N'):
            exit()
        else:
            logger.message('Continuing...')



    # handle files
    files = [f for f in glob(ooutfilename+'*') if isfile(f)]
    logger.warn("Will remove these files: {}".format(' | '.join(files)))
    logger.message("\n")

    _TEMP_ = time.time()
    datafile = 'TEMPORARY_FILE_SPECREDUC_{}_0.txt'.format(_TEMP_)
    _TEMPB_ = 'TEMPORARY_FILE_SPECREDUC_{}'.format(_TEMP_)
    _TEMP0_ = 'TEMPORARY_FILE_SPECREDUC_{}.txt'.format(_TEMP_)
    _TEMP1_ = 'TEMPORARY_FILE_SPECREDUC_{}_1.txt'.format(_TEMP_)
    _TEMP2_ = 'TEMPORARY_FILE_SPECREDUC_{}_2.txt'.format(_TEMP_)

    logger.waiting(auto)
    utilities._REMOVE_(logger,ooutfilename)
    utilities._REMOVE_(logger,TEMPB)
    _SYSTEM_('cp -f ' + orig_datafile + ' ' + datafile)

    # getting firstlines
    _SYSTEM_('head -n 2 ' + datafile + ' > ' + _TEMP0_)
    with open(_TEMP0_,'r') as f:
        first = ''.join(f.readlines())
    _SYSTEM_("sed -i '1d' " + datafile)
    with open(datafile, 'r') as f:
        first_line=f.readline().strip('\n').split(" ")
    _SYSTEM_("sed -i '1d' " + datafile)
    data = ascii.read(datafile)

    # to verify correct input
    logger.header2("Will reduce these sources: {}".format(" | ".join(first_line)))
    
    # starting at non-zero source
    acstart = ''
    counting = 0
    while True:
        try:
            newstart = logger.pyinput('Do you wish to start at a source (y or [SPACE]/[RET] or n): ')
            if(newstart == ' ' ) or (newstart == 'y'):
                acstart = logger.pyinput('Input source exactly: ')
            elif (newstart == '' ) or (newstart == 'n'):
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
    total_num = 0
    while total_num < len(first_line):
        if counting == 1:
            total_num = first_line.index(acstart)
            counting = 0
        if total_num == 0:     
            col1 = "vel"
            col2 = "Tant"
            col0 = "vel_vlsr"
        else:
            col1 = "vel_" + str(total_num)
            col2 = "Tant_" + str(total_num)
            col0 = "vel_vlsr_" + str(total_num)
        outfilename = ooutfilename + "_" + first_line[total_num]
        logger.warn('Working on: ' + outfilename)
        with open(_TEMP2_,'w') as _T_:
            _T_.write('Working on: ' + outfilename + '\n')
        minvel = min(data[col1])
        maxvel = max(data[col1])
        data.sort([col1])
        
        # plot raw data
        plt.ion()
        f=plt.subplot(121)
        rawdata=f.scatter(data[col1],data[col2],color='black')
        plt.plot(data[col1],data[col2],color='red',linestyle='steps')
        # prepare mask
        f.set_title('lasso selection:')
        f.tick_params('both', which='major', length=15, width=1, pad=15)
        f.tick_params('both', which='minor', length=7.5, width=1, pad=15)
        ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
        f.set_ylabel('Antenna Temperature (K)', fontsize=18)
        f.set_xlabel('V$_{lsr}$ (km/s)', fontsize=18)
        draw()
        # baseline
        baseline_med=np.median(data[col2])-0.5
        baseline_ul=baseline_med*1.02
        logger.message('Median of baseline: ' + str(baseline_med) + ' and 2sigma baseline ' + str(baseline_ul))
        with open(_TEMP2_,'a') as _T_:
            _T_.write('Median of baseline: ' + str(baseline_med) + ' and 2sigma baseline ' + str(baseline_ul) + '\n')

        # actual defining mask
        msk_array = []
        temp = []
        while True:
            selector = SelectFromCollection(f, rawdata)
            logger.header2("Draw mask regions around the non-baseline features...")
            draw()
            logger.pyinput('[RET] to accept selected points')
            temp = selector.xys[selector.ind]
            msk_array = np.append(msk_array,temp)
            selector.disconnect()
            # Block end of script so you can check that the lasso is disconnected.
            answer = logger.pyinput("if you want to draw another lasso region (y or [SPACE]/n or [RET]): ")
            plt.show()
            if ((answer == "n") or (answer == "")):
                break
        logger.waiting(auto)

        # draw and reset
        plt_iter = 0
        k=plt.figure(plt_iter+1)
        plt_iter += 1
        f=k.add_subplot(121)
        f.set_title("Raw Data")
        rawdata=f.plot(data[col1],data[col2],color='black',linestyle='steps')
        f.set_xlabel('V$_{lsr}$ (km/s)', fontsize=18)
        draw()
        outfilename_iter =0
        plt.savefig(outfilename + "_" + str(outfilename_iter) + ".pdf")

        # need to invert mask to polyfit region
        mask_inv = []
        for i in range(len(msk_array)):
            mask_inv = np.append(mask_inv,np.where(data[col1] == msk_array[i]))
        mask_tot = np.linspace(0,len(data)-1,num=len(data))
        mask = np.delete(mask_tot,mask_inv)
        mask = map(int,mask)
        logger.waiting(auto)

        # show projected baselines
        fig=plt.figure(plt_iter+1)
        plt_iter += 1
        plt.title("Projected Baselines")
        lin1=plt.plot(data[col1],data[col2],color='black',linestyle='steps')
        lin2=plt.plot([minvel,maxvel],[baseline_med,baseline_med],color='red',linestyle='steps')
        lin3=plt.plot([minvel,maxvel],[baseline_ul,baseline_ul],color='red',linestyle='steps')
        plt.tick_params('both', which='major', length=15, width=1, pad=15)
        plt.tick_params('both', which='minor', length=7.5, width=1, pad=15)
        ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
        plt.ylabel('Antenna Temperature (K)', fontsize=18)
        plt.xlabel('V$_{lsr}$ (km/s)', fontsize=18)
        draw()
        outfilename_iter +=1
        plt.savefig(outfilename + "_" + str(outfilename_iter) + ".pdf")

        # fitting baseline to higher order polynomial
        newask = ' '
        while (newask == 'n') or (newask == 'N') or (newask == ' '):
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
            plt.figure(plt_iter+1)
            plt_iter += 1
            plt.clf()
            plt.title("plotting fitted baseline")
            lin1=plt.plot(data[col1],data[col2],color='black',linestyle='steps')
            lin2=plt.plot(data[col1],fit_fn(data[col1]),color='red',linestyle='steps')
            plt.tick_params('both', which='major', length=15, width=1, pad=15)
            plt.tick_params('both', which='minor', length=7.5, width=1, pad=15)
            ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
            plt.ylabel('Antenna Temperature (K)', fontsize=18)
            plt.xlabel('V$_{lsr}$ (km/s)', fontsize=18)
            draw()
            newask = logger.pyinput('Was this acceptable?(y or [RET]/n or [SPACE]) ')
            if (newask == 'y') or (newask == 'Y') or (newask == ''):
                logger.waiting(auto)
                with open(_TEMP2_,'a') as _T_:
                    _T_.write("The polynomial is: \n {}\n".format(fit_fn))
                break


        outfilename_iter +=1
        plt.savefig(outfilename + "_" + str(outfilename_iter) + ".pdf")

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
        plt.figure(plt_iter+1)
        plt_iter += 1
        plt.title("Plotting the corrected baseline")
        lin1=plt.plot(data[col1],spectra_blcorr,color='black',linestyle='steps')
        lin2=plt.plot([minvel,maxvel],[0,0],color='red',linestyle='steps')
        plt.tick_params('both', which='major', length=15, width=1, pad=15)
        plt.tick_params('both', which='minor', length=7.5, width=1, pad=15)
        ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
        plt.ylabel('Antenna Temperature (K)', fontsize=18)
        plt.xlabel('V$_{lsr}$ (km/s)', fontsize=18)
        draw()
        logger.waiting(auto)
        outfilename_iter +=1
        plt.savefig(outfilename + "_" + str(outfilename_iter) + ".pdf")

        # define the RFI
        plt.ion()
        t=plt.subplot(122)
        t.set_title('lasso selection:')
        lin10=plt.scatter(data[col1],spectra_blcorr,color='black')
        lin2=plt.plot(data[col1],spectra_blcorr,color='blue',linestyle='steps')
        lin3=plt.plot([minvel,maxvel],[0,0],color='red',linestyle='steps')
        plt.tick_params('both', which='major', length=15, width=1, pad=15)
        plt.tick_params('both', which='minor', length=7.5, width=1, pad=15)
        ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
        plt.ylabel('Antenna Temperature (K)', fontsize=18)
        plt.xlabel('V$_{lsr}$ (km/s)', fontsize=18)
        draw()

        temp = []
        rfi_mask_array = []
        rfi_mask = []
        while True:
            selector = SelectFromCollection(t, lin10)
            logger.header2("Draw RFI mask regions")
            draw()
            logger.pyinput('[RET] to accept selected points')
            temp = selector.xys[selector.ind]
            rfi_mask_array = np.append(rfi_mask_array,temp)
            selector.disconnect()
            # Block end of script so you can check that the lasso is disconnected.
            answer = logger.pyinput("if you want to draw another lasso region (y or [SPACE]/n or [RET]): ")
            plt.show()
            if ((answer == "n") or (answer == "")):
                break
        logger.waiting(auto)

        newask = ' '
        _TRY_ =1
        for i in range(len(rfi_mask_array)):
            rfi_mask = np.append(rfi_mask,np.where(data[col1] == rfi_mask_array[i]))
        rfi_mask = map(int,rfi_mask)
        logger.message('RFI: {}'.format(','.join(map(str,rfi_mask))))

        def gauss(x,mu,sigma,A):
            return A*np.exp(-(x-mu)**2/2./sigma**2)

        def bimodal(x,mu1,sigma1,A1,mu2,sigma2,A2):
            return gauss(x,mu1,sigma1,A1)+gauss(x,mu2,sigma2,A2)

        # remove rfi
        while (newask == 'n') or (newask == 'N') or (newask == ' '):
            _TEMPSPEC_ = ''
            _TEMPSPEC_ = spectra_blcorr
            # fitting polynomial nth order to baseline
            if _TRY_ == 1:
                rfi_fit = np.polyfit(data[col1][mask],_TEMPSPEC_[mask],polynumfit)
                rfi_fit_fn = np.poly1d(rfi_fit)

            # fit Gaussian
            elif _TRY_ == 2:
                _expected1=(1.,rms,1.)
                _params1,_cov1=curve_fit(gauss,data[col1],_TEMPSPEC_,_expected1)
                _sigma1=np.sqrt(np.diag(_cov1))

                rfi_fit_fn = 'gauss(x,mu1,sigma1,A1)' + ','.join(map(str,_params1))

            elif _TRY_ == 3:
                _expected2=(1.,rms,1.,1.,rms,1.)
                _params2,_cov2=curve_fit(bimodal,data[col1],_TEMPSPEC_,_expected2)
                _sigma2=np.sqrt(np.diag(_cov2))

                for _RFI_ in rfi_mask:
                    logger.warn("Region of RFI: {}".format(_TEMPSPEC_[_RFI_]))
                    _TEMPSPEC_[_RFI_] = bimodal(_RFI_,_params2[0],_params2[1],_params2[2],_params2[3],_params2[4],_params2[5])
                    logger.warn("Region of RFI after fit {}".format(_TEMPSPEC_[_RFI_]))

                rfi_fit_fn = 'gauss(x,mu1,sigma1,A1)+gauss(x,mu2,sigma2,A2)' + ','.join(map(str,_params2))

            elif _TRY_ >= 4:
                logger.fail('Auto fitting RFI failed, setting values to zero...')
                _TEMPSPEC_[rfi_mask] = 0.0
                break
            '''
            for I in data[col1]:
                if I < 100 && I >= 0:
                    print(I,_TEMPSPEC_[int(I)])
            '''
            # plotting fitted baseline to original image
            plt.figure(plt_iter+1)
            plt_iter += 1
            plt.clf()
            plt.title("Plotting RFI removal")
            if _TRY_ == 1:
                lin2=plt.plot(data[col1],rfi_fit_fn(_TEMPSPEC_),color='red',linestyle='steps',label='model')
                for _RFI_ in rfi_mask:
                    print(_TEMPSPEC_[_RFI_])
                    _TEMPSPEC_[_RFI_] = rfi_fit_fn(_RFI_) 
                    print(_TEMPSPEC_[_RFI_])
            elif _TRY_ == 2:
                lin2 = plt.plot(data[col1],gauss(data[col1],_params1[0],_params1[1],_params1[2]),color='red',label='model',linestyle='steps')
                for _RFI_ in rfi_mask:
                    print(_TEMPSPEC_[_RFI_])
                    _TEMPSPEC_[_RFI_] = gauss(data[col1][_RFI_],_params1[0],_params1[1],_params1[2])
                    print(_TEMPSPEC_[_RFI_])
            elif _TRY_ == 3:
                lin2 = plt.plot(data[col1],bimodal(data[col1],_params2[0],_params2[1],_params2[2],_params2[3],_params2[4],_params2[5]),color='red',label='model',linestyle='steps')
                for _RFI_ in rfi_mask:
                    print(_TEMPSPEC_[_RFI_])
                    _TEMPSPEC_[_RFI_] = bimodal(data[col1][_RFI_],_params2[0],_params2[1],_params2[2],_params2[3],_params2[4],_params2[5])
                    print(_TEMPSPEC_[_RFI_])

            lin1=plt.plot(data[col1],_TEMPSPEC_,color='black',linestyle='steps')
            plt.tick_params('both', which='major', length=15, width=1, pad=15)
            plt.tick_params('both', which='minor', length=7.5, width=1, pad=15)
            ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
            plt.ylabel('Antenna Temperature (K)', fontsize=18)
            plt.xlabel('V$_{lsr}$ (km/s)', fontsize=18)
            draw()
            newask = logger.pyinput('if this is acceptable?(y or [RET]/n or [SPACE]) ')
            if (newask == 'y') or (newask == 'Y') or (newask == ''):
                logger.waiting(auto)
                with open(_TEMP2_,'a') as _T_:
                    _T_.write("The polynomial is: \n %s" % rfi_fit_fn + '\n')
                break
            elif (newask == 'n') or (newask == 'N') or (newask == ' '):
                _TRY_ +=1

            spectra_blcorr = _TEMPSPEC_
        # draw and reset
        plt.figure(plt_iter+1)
        plt_iter += 1
        plt.title("Corrected Baseline and RFI removed")
        lin2=plt.plot(data[col1],spectra_blcorr,color='blue',linestyle='steps')
        if _TRY_ == 1:
            lin4=plt.plot(data[col1],rfi_fit_fn(data[col1]),color='green',linestyle='steps')
        lin3=plt.plot([minvel,maxvel],[0,0],color='red',linestyle='steps')
        plt.tick_params('both', which='major', length=15, width=1, pad=15)
        plt.tick_params('both', which='minor', length=7.5, width=1, pad=15)
        ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
        plt.ylabel('Antenna Temperature (K)', fontsize=18)
        plt.xlabel('V$_{lsr}$ (km/s)', fontsize=18)
        draw()
        logger.waiting(auto)
        outfilename_iter +=1
        plt.savefig(outfilename + "_" + str(outfilename_iter) + ".pdf")

        # Final correction plot 
        plt.figure(plt_iter+1)
        plt_iter += 1
        plt.xlim(minvel,maxvel)
        plt.ylim(-5,maxt * 1.1)
        lin1=plt.plot(data[col1],spectra_blcorr,color='black',linestyle='steps')
        plt.tick_params('both', which='major', length=15, width=1, pad=15)
        plt.tick_params('both', which='minor', length=7.5, width=1, pad=15)
        ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
        plt.title("Final correction plot ")
        plt.ylabel('Antenna Temperature (K)', fontsize=18)
        plt.xlabel('V$_{lsr}$ (km/s)', fontsize=18)
        draw()
        logger.waiting(auto)
        outfilename_iter +=1
        plt.savefig(outfilename + "_" + str(outfilename_iter) + ".pdf")

        # intensity estimate
        while True:
            try:
                intensity_answer = logger.pyinput('Sigma value for Guassian (integers * rms) or [RET] for default 5 sigma: ')
                if intensity_answer == '':
                    intensity_answer = 5.0
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
        with open(_TEMP2_,'a') as _T_:
            _T_.write('Sigma value for Guassian: {}\n'.format(intensity_answer))

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

        plt.figure(plt_iter+1)
        plt_iter += 1
        plt.xlim(minvel,maxvel)
        plt.ylim(-5,max(spectra_blcorr) * 1.1)
        lin1=plt.plot(data[col1],spectra_blcorr,color='black',linestyle='steps')
        lin2=plt.plot(data[col1][intensity_mask_guess],np.zeros(len(data[col1][intensity_mask_guess])),color='blue',linestyle='dotted')
        lin3=plt.plot([minint,minint],[0,maxt],color='blue',linestyle='dotted')
        lin4=plt.plot([maxint,maxint],[0,maxt],color='blue',linestyle='dotted')
        plt.tick_params('both', which='major', length=15, width=1, pad=15)
        plt.tick_params('both', which='minor', length=7.5, width=1, pad=15)
        ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
        plt.title("Intensity Line Estimate")
        plt.ylabel('Antenna Temperature (K)', fontsize=18)
        plt.xlabel('V$_{lsr}$ (km/s)', fontsize=18)
        draw()
        logger.waiting(auto)
        outfilename_iter +=1
        plt.savefig(outfilename + "_" + str(outfilename_iter) + ".pdf")

        answer = ""
        while True:
            try:
                answer_ok = logger.pyinput("if the guess for the line intensity okay (y or [RET]/n or [SPACE]): ")
                if ((answer_ok == "y") or (answer_ok == "")):
                    intensity_mask = intensity_mask_guess
                    break
                else:
                    # define the Intensity
                    plt.ion()
                    t=plt.subplot(122)
                    t.set_title('lasso selection:')
                    lin10=plt.scatter(data[col1],spectra_blcorr,color='black')
                    lin2=plt.plot(data[col1],spectra_blcorr,color='blue',linestyle='steps')
                    lin3=plt.plot([minvel,maxvel],[0,0],color='red',linestyle='steps')
                    plt.tick_params('both', which='major', length=15, width=1, pad=15)
                    plt.tick_params('both', which='minor', length=7.5, width=1, pad=15)
                    ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
                    plt.ylabel('Antenna Temperature (K)', fontsize=18)
                    plt.xlabel('V$_{lsr}$ (km/s)', fontsize=18)
                    draw()
                    # recovering intensity of line 
                    temp = []
                    intensity_mask_array = []
                    intensity_mask = []
                    while True:
                        selector = SelectFromCollection(t, lin10)
                        plt.header2("Draw a box around all Gaussian points.")
                        draw()
                        logger.pyinput('Press Enter to accept selected points')
                        temp = selector.xys[selector.ind]
                        intensity_mask_array = np.append(intensity_mask_array,temp)
                        selector.disconnect()
                        # Block end of script so you can check that the lasso is disconnected.
                        answer = logger.pyinput("Want to draw another lasso region (y or [SPACE]/n or [RET]): ")
                        plt.show()
                        if ((answer == "n") or (answer == "")):
                            break
                    logger.waiting(auto)
                    for i in range(len(intensity_mask_array)):
                        intensity_mask = np.append(intensity_mask,np.where(data[col1] == intensity_mask_array[i]))
                    intensity_mask = map(int,intensity_mask)
                    # draw and reset
                    minint=min(data[col1][intensity_mask])
                    maxint=max(data[col1][intensity_mask])
                    k=plt.figure(plt_iter+1)
                    plt_iter += 1
                    f=k.add_subplot(121)
                    f.set_title("With Line Intensity Mask")
                    lin1=plt.plot(data[col1],spectra_blcorr,color='black',linestyle='steps')
                    lin2=plt.plot(data[col1][intensity_mask],np.zeros(len(data[col1][intensity_mask])),color='blue',linestyle='dotted')
                    lin3=plt.plot([minint,minint],[0,maxt],color='blue',linestyle='dotted')
                    lin4=plt.plot([maxint,maxint],[0,maxt],color='blue',linestyle='dotted')                
                    f.set_xlabel('V$_{lsr}$ (km/s)', fontsize=18)
                    draw()
                    break
            except ValueError:
                continue

        # showing Intensity Mask
        minint=min(data[col1][intensity_mask])
        maxint=max(data[col1][intensity_mask])
        plt.figure(plt_iter+1)
        plt_iter += 1
        plt.xlim(minvel,maxvel)
        plt.ylim(-5,max(spectra_blcorr) * 1.1)
        lin1=plt.plot(data[col1],spectra_blcorr,color='black',linestyle='steps')
        lin2=plt.plot(data[col1][intensity_mask],np.zeros(len(data[col1][intensity_mask])),color='blue',linestyle='dotted')
        lin3=plt.plot([minint,minint],[0,maxt],color='blue',linestyle='dotted')
        lin4=plt.plot([maxint,maxint],[0,maxt],color='blue',linestyle='dotted')
        plt.tick_params('both', which='major', length=15, width=1, pad=15)
        plt.tick_params('both', which='minor', length=7.5, width=1, pad=15)
        ticks_font = mpl.font_manager.FontProperties(size=16, weight='normal', stretch='normal')
        plt.title("Intensity Mask")
        plt.ylabel('Antenna Temperature (K)', fontsize=18)
        plt.xlabel('V$_{lsr}$ (km/s)', fontsize=18)
        draw()
        logger.waiting(auto)
        outfilename_iter +=1
        plt.savefig(outfilename + "_" + str(outfilename_iter) + ".pdf")

        # intensity
        intensity=np.sum(spectra_blcorr[intensity_mask])
        chanwidth=abs(max(data[col1])-min(data[col1]))/len(data[col1])
        if ((answer_ok == 'y') or (answer_ok == '')):
            intensity_rms=rms*chanwidth*(float(len(intensity_mask[0])))**0.5
        else:
            intensity_rms=rms*chanwidth*(float(len(intensity_mask)))**0.5
        logger.message("Intensity: ")
        logger.message("{} +- {} (K km/s)".format((intensity)*chanwidth,intensity_rms))
        with open(_TEMP2_,'a') as _T_:
            _T_.write('Intensity: {} +- {} (K km/s)'.format((intensity)*chanwidth,intensity_rms))

        # write to file
        try:
            spec_final = Table([data[col0],data[col1],data[col2],spectra_blcorr], names=('vel_sub', 'vel', 'Tant_raw', 'Tant_corr'))
        except KeyError:
            spec_final = Table([data[col1],data[col2],spectra_blcorr], names=('vel', 'Tant_raw', 'Tant_corr'))           
        ascii.write(spec_final,_TEMP1_)
        with open(_TEMP1_, 'r') as original: ndata = original.read()
        with open(_TEMP1_, 'w') as modified: modified.write(ndata)  #first + first_line[total_num] + '\n'+str((intensity)*chanwidth) + '+/-' + str(intensity_rms) + 'K km/s' + '\n' +
        _SYSTEM_('cp -f ' + _TEMP1_ + ' ' + outfilename + "_spectra_corr.txt")
        _SYSTEM_('cp -f ' + _TEMP2_ + ' ' + outfilename + "_parameters.txt")




        # pretty plot to go here




        # close and reset
        logger.pyinput("[RET] to continue to complete this source...")
        plt.close("all")
        total_num +=1

    logger.pyinput("[RET] to exit")
    plt.show()
    print("\n")

    # finished
    utilities._REMOVE_(_TEMPB_)

    logger.header2("#################################")
    logger.success("Finished with all.")
    logger.message("These are the sources processed: {}".format(' | '.join(first_line)))
    logger.message("These are the files processed: {}".format(orig_datafile))
    files = [f for f in glob(outfilename+'*') if isfile(f)]
    logger.header2("Made the following files: {} and logfile: {}".format(', '.join(files),logfile))
    plt.close()

    #############
    # end of code