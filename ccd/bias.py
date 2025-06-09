#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Filename: bias.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from astropy.stats import sigma_clip

def create_median_bias(bias_list, median_bias_filename):
    """This function must:

    - Accept a list of bias file paths as bias_list.
    - Read each bias file and create a list of 2D numpy arrays.
    - Use a sigma clipping algorithm to combine all the bias frames using
      the median and removing outliers outside 3-sigma for each pixel.
    - Save the resulting median bias frame to a FITS file with the name
      median_bias_filename.
    - Return the median bias frame as a 2D numpy array.

    """

    biases = []
    
    #reading bias files
    for path in bias_list:
        data = fits.getdata(path)
        biases.append(data.astype(np.float32))

    #sigma clipping algorithm
    biases_clip = sigma_clip(biases,sigma=3.,cenfunc='median',axis=0)

    #combining to one frame
    median_bias = np.ma.median(biases_clip,axis=0).data

    #####
    #header for saving file
    header = fits.getheader(bias_list[0])

    # Here is some code to create a new FITS file from the resulting median bias frame.
    # You can replace the header with something more meaningful with information.
    primary = fits.PrimaryHDU(data=median_bias, header=header)
    primary.header['COMMENT'] = 'Median bias image'
    hdul = fits.HDUList([primary])
    hdul.writeto(median_bias_filename, overwrite=True)

    return median_bias
