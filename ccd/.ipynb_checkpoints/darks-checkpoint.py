#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Filename: darks.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from astropy.stats import sigma_clip

def create_median_dark(dark_list, bias_filename, median_dark_filename):
    """This function must:

    - Accept a list of dark file paths to combine as dark_list.
    - Accept a median bias frame filename as bias_filename (the one you created using
      create_median_bias).
    - Read all the images in dark_list and create a list of 2D numpy arrays.
    - Read the bias frame.
    - Subtract the bias frame from each dark image.
    - Divide each dark image by its exposure time so that you get the dark current
      per second. The exposure time can be found in the header of the FITS file.
    - Use a sigma clipping algorithm to combine all the bias-corrected dark frames
      using the median and removing outliers outside 3-sigma for each pixel.
    - Save the resulting dark frame to a FITS file with the name median_dark_filename.
    - Return the median dark frame as a 2D numpy array.

    """

    darks = []
    exptimes=[]
    
    #reading dark files
    for path in dark_list:
        data = fits.getdata(path)
        darks.append(data.astype(np.float32))

        #exposure times
        exptimes.append(fits.getheader(path)['EXPTIME'])

    #reading bias file
    median_bias = fits.getdata(bias_filename)

    #subtracting bias from darks
    dark_sub = darks - median_bias

    #dark_current = dark_sub / exptimes
    dark_current = np.empty_like(dark_sub, dtype=np.float32)
    
    for i in range(len(exptimes)):
        dark_current[i] = dark_sub[i] / exptimes[i]

    #sigma clipping algorithm
    darks_clip = sigma_clip(dark_current,sigma=3.,cenfunc='median',axis=0)
    
    #combining to one frame
    median_dark = np.ma.median(darks_clip,axis=0).data

    #####
    #header for saving file
    header = fits.getheader(dark_list[0])
    
    #create_median_bias code for how to create a new FITS file
    primary = fits.PrimaryHDU(data=median_dark, header=header)
    primary.header['COMMENT'] = 'Median dark image'             #comment to desribe file
    primary.header['COMMENT'] = f'BIAS: {bias_filename}'        #comment for bias used
    hdul = fits.HDUList([primary])
    hdul.writeto(median_dark_filename, overwrite=True)

    return median_dark
