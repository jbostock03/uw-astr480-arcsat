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
    """
    Calculates the total flux in each reduced science frame.

    Returns these as an array.
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
    pos = [(502,509)]
    radii = [12.]
    ann_in = 15.
    ann_width = 5.
    
    #photometries
    fluxes = []
    for i in range(104):
        photometry = do_aperture_photometry(f"science{i}_run_reduction.fits", \
                                            pos, radii, ann_in, ann_width)
        fluxes.append(photometry['flux'][0])
    

    #printing information
    print('fluxes ::')
    print(fluxes)
    
    return fluxes
