#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Filename: reduction.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import pathlib
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.stats import sigma_clipped_stats
from photutils.centroids import centroid_1dg

def run_reduction(data_dir):
    """This function must run the entire CCD reduction process. You can implement it
    in any way that you want but it must perform a valid reduction for the two
    science frames in the dataset using the functions that you have implemented in
    this module. Then perform aperture photometry on at least one of the science
    frames, using apertures and sky annuli that make sense for the data. The function
    must accept the data_dir as an argument, which is the path to the directory with
    the raw data.

    No specific output is required but make sure the function prints/saves all the
    relevant information to the screen or to a file, and that any plots are saved to
    PNG or PDF files.

    """

    #import functions
    from ccd.bias import create_median_bias
    from ccd.darks import create_median_dark
    from ccd.flats import create_median_flat, plot_flat
    from ccd.science import reduce_science_frame
    from ccd.photometry import do_aperture_photometry, plot_radial_profile
    from ccd.ptc import calculate_gain, calculate_readout_noise

    # Get the lists of files
    bias_list = glob.glob(os.path.join(data_dir, "./Bias*.fit*"))
    dark_list = glob.glob(os.path.join(data_dir, "./Dark*.fit*"))
    flat_list = glob.glob(os.path.join(data_dir, "./*flat*.fit*"))
    science_list = glob.glob(os.path.join(data_dir, "./XO1*.fit*"))

    #reduction process
    bias = create_median_bias(bias_list,'bias_run_reduction.fits')
    dark = create_median_dark(dark_list,'bias_run_reduction.fits','dark_run_reduction.fits')
    flat = create_median_flat(flat_list,'bias_run_reduction.fits', \
                              'flat_run_reduction.fits','dark_run_reduction.fits')
    science = []
    for i in range(len(science_list)):
        sci_temp = reduce_science_frame(science_list[i],'bias_run_reduction.fits', \
                                        'flat_run_reduction.fits','dark_run_reduction.fits', \
                                        reduced_science_filename=f"science{i}_run_reduction.fits")
        science.append(sci_temp)
    
    #gain and readout noise
    gain = calculate_gain(flat_list)
    rn = calculate_readout_noise(bias_list,gain)

    ### PHOTOMETRY ON FIRST REDUCED SCIENCE FRAME
    sci_data = science[0]

    #blank region for accurate median of sky background for subtraction
    bg_region = (slice(600,700),slice(600,700))
    bg_med = sigma_clipped_stats(sci_data[bg_region], sigma=3.0)[1]
    
    #first guesses for photometry -- found by investigating science frames in ds9
    pos_guess = [(530,565)]
    radii = np.linspace(1,20,40)
    ann_in = 22.
    ann_width = 5.

    #centroiding
    pos = []
    offset = 20
    
    for x, y in pos_guess:
        data_cent = sci_data[y-offset:y+offset, x-offset:x+offset]   #small region around source
        xc, yc = centroid_1dg(data_cent - bg_med)                    #using 1d gaussian algorithm
        xc += (x - offset)                              #as centroid is w.r.t. selected region
        yc += (y - offset)
        pos.append((xc,yc))
    
    #photometry table
    photometry = do_aperture_photometry("science0_run_reduction.fits", \
                                        pos, radii, ann_in, ann_width)
    ### PLOTTING
    #for plotting
    imgs = [bias,dark] + science
    
    #for plot titles
    img_type = ['bias','dark']
    for i, img in enumerate(science):
        img_type.append(f'science (index = {i})')

    #plotting flat frame and medians of rows
    plot_flat('flat_run_reduction.fits')
    
    for i, img in enumerate(imgs):
    #taking vmin/vmax to be median -+ 3 stdev
        _min = np.median(img) - 3*np.std(img)
        _max = np.median(img) + 3*np.std(img)
    #plot settings
        plt.figure()
        plt.title(f'Median/reduced {img_type[i]} frame')
        plt.xlabel('x (pixels)'); plt.ylabel('y (pixels)')
        plt.imshow(img,cmap='gray',vmin=_min,vmax=_max)
        plt.colorbar().set_label('Counts');
        
        #for science frame that has had photometry, adding 
        #markers to objects that have been measured
        if i == 2:
            for j, (xc,yc) in enumerate(pos):
                plt.scatter(xc, yc, c='r', marker='$O$', alpha=0.6, \
                            label='Objects for photometry' if j == 0 else None)
            plt.legend();
        
    #plotting radial profiles
    plot_radial_profile(photometry, "radial_profile0_run_reduction.png")

    #printing information
    print('GAIN & READOUT NOISE ::')
    print(f'Gain: {gain}')
    print(f'Readout noise: {rn}')
    print()
    print('Photometry data from science0_run_reduction.fits ::')
    print(photometry)
    
    return
