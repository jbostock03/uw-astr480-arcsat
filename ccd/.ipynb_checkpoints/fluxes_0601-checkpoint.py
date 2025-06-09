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

def total_flux(data_dir):
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
    os.chdir(data_dir)
    
    #actual values for photometry -- found by using run_reduction
    pos = [(533,564)]
    radii = [12.]
    ann_in = 15.
    ann_width = 5.
    
    #photometries
    fluxes = []
    for i in range(79):
        photometry = do_aperture_photometry(f"science{i}_run_reduction.fits", \
                                            pos, radii, ann_in, ann_width)
        fluxes.append(photometry['flux'][0])
    

    #printing information
    print('fluxes ::')
    print(fluxes)
    
    return fluxes
