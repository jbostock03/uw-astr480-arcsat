#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Filename: science.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from astropy.stats import sigma_clip
from astroscrappy import detect_cosmics

def reduce_science_frame(
    science_filename,
    median_bias_filename,
    median_flat_filename,
    median_dark_filename,
    reduced_science_filename="reduced_science.fits",
):
    """This function must:

    - Accept a science frame filename as science_filename.
    - Accept a median bias frame filename as median_bias_filename (the one you created
      using create_median_bias).
    - Accept a median flat frame filename as median_flat_filename (the one you created
      using create_median_flat).
    - Accept a median dark frame filename as median_dark_filename (the one you created
      using create_median_dark).
    - Read all files.
    - Subtract the bias frame from the science frame.
    - Subtract the dark frame from the science frame. Remember to multiply the
      dark frame by the exposure time of the science frame. The exposure time can
      be found in the header of the FITS file.
    - Correct the science frame using the flat frame.
    - Optionally, remove cosmic rays.
    - Save the resulting reduced science frame to a FITS file with the filename
      reduced_science_filename.
    - Return the reduced science frame as a 2D numpy array.

    """

    
    #reading all files
    data = fits.getdata(science_filename)
    science = data.astype(np.float32)
    exptime = fits.getheader(science_filename)['EXPTIME']
    
    median_bias = fits.getdata(median_bias_filename)
    median_flat = fits.getdata(median_flat_filename)
    median_dark = fits.getdata(median_dark_filename)

    #corrected science frame
    science_corr = (science - median_bias - median_dark*exptime)/median_flat

    #cleaned of cosmic ray
    cosmic_mask, reduced_science = detect_cosmics(science_corr)

    #####
    #header for saving file
    header = fits.getheader(science_filename)

    #create_median_bias code for how to create a new FITS file
    primary = fits.PrimaryHDU(data=reduced_science, header=header)
    primary.header['COMMENT'] = 'Reduced science image'           #comment to desribe file
    primary.header['COMMENT'] = f'BIAS: {median_bias_filename}'   #comment for bias used
    primary.header['COMMENT'] = f'DARK: {median_dark_filename}'   #comment for dark used
    primary.header['COMMENT'] = f'FLAT: {median_flat_filename}'   #comment for flat used
    hdul = fits.HDUList([primary])
    hdul.append(fits.ImageHDU(cosmic_mask.astype(int), name="MASK"))  # mask as extension
    hdul.writeto(reduced_science_filename, overwrite=True)
    
    return reduced_science
