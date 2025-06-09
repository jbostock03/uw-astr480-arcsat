#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Filename: flats.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from astropy.stats import sigma_clip

def create_median_flat(
    flat_list,
    bias_filename,
    median_flat_filename,
    dark_filename=None,
):
    """This function must:

    - Accept a list of flat file paths to combine as flat_list. Make sure all
      the flats are for the same filter.
    - Accept a median bias frame filename as bias_filename (the one you created using
      create_median_bias).
    - Read all the images in flat_list and create a list of 2D numpy arrays.
    - Read the bias frame.
    - Subtract the bias frame from each flat image.
    - Optionally you can pass a dark frame filename as dark_filename and subtract
      the dark frame from each flat image (remember to scale the dark frame by the
      exposure time of the flat frame).
    - Use a sigma clipping algorithm to combine all the bias-corrected flat frames
      using the median and removing outliers outside 3-sigma for each pixel.
    - Create a normalised flat divided by the median flat value.
    - Save the resulting median flat frame to a FITS file with the name
      median_flat_filename.
    - Return the normalised median flat frame as a 2D numpy array.

    """

    flats = []
    filters = []
    exptimes = []
    
    #reading filters & confirming same filter
    ref_f = fits.getheader(flat_list[0])['FILTER']
    for path in flat_list:
        header = fits.getheader(path)
        f = header['FILTER']
        t = header['EXPTIME']

        #verify filter
        if f != ref_f:
            raise Exception(f'The flats are not from the same filter! {ref_f} and {f}')
        
        #reading flat files if same filter
        data = fits.getdata(path)
        flats.append(data.astype(np.float32))
        filters.append(f)
        exptimes.append(t)

    #reading bias & dark files
    median_bias = fits.getdata(bias_filename)
    if dark_filename != None:
        median_dark = fits.getdata(dark_filename)

    #subtracting
        flat_sub = flats - median_bias - median_dark*exptimes[0]
    else:
        flat_sub = flats - median_bias
    
    #sigma clipping algorithm
    flats_clip = sigma_clip(flat_sub,sigma=3.,cenfunc='median',axis=0)
    
    #combining to one frame & normalised
    median_flat = np.ma.median(flats_clip,axis=0).data / np.ma.median(flats_clip).data

    #####
    #header for saving file
    header = fits.getheader(flat_list[0])

    #create_median_bias code for how to create a new FITS file
    primary = fits.PrimaryHDU(data=median_flat, header=header)
    primary.header['COMMENT'] = 'Normalised median flat image'    #comment to desribe file
    primary.header['COMMENT'] = f'BIAS: {bias_filename}'          #comment for bias used
    if dark_filename != None:
        primary.header['COMMENT'] = f'DARK: {dark_filename}'      #comment for dark used (if applicable)
    hdul = fits.HDUList([primary])
    hdul.writeto(median_flat_filename, overwrite=True)
    
    return median_flat


def plot_flat(
    median_flat_filename,
    ouput_filename="median_flat.png",
    profile_ouput_filename="median_flat_profile.png",
):
    """This function must:

    - Accept a normalised flat file path as median_flat_filename.
    - Read the flat file.
    - Plot the flat frame using matplotlib.imshow with reasonable vmin and vmax
      limits. Save the plot to the file specified by output_filename.
    - Take the median of the flat frame along the y-axis. You'll end up with a
      1D array.
    - Plot the 1D array using matplotlib.
    - Save the plot to the file specified by profile_output_filename.

    """

    #reading flat file
    median_flat = fits.getdata(median_flat_filename)

    #taking vmin/vmax to be median -+ 3 stdev
    _min = np.median(median_flat) - 3.0*np.std(median_flat)
    _max = np.median(median_flat) + 3.0*np.std(median_flat)

    #plotting flat frame
    plt.figure()
    plt.title('Median flat frame')
    plt.xlabel('x (pixels)'); plt.ylabel('y (pixels)')
    plt.imshow(median_flat,cmap='gray',vmin=_min,vmax=_max)
    plt.colorbar().set_label('Counts')
    plt.savefig(ouput_filename)

    #median along y axis (each row) => axis=1
    median_flat_1d = np.median(median_flat,axis=1)

    #plotting profile
    plt.figure()
    plt.title('Profile of medians of each row')
    plt.xlabel('Row (pixels)'); plt.ylabel('Median counts')
    plt.plot(median_flat_1d)
    plt.grid()
    plt.savefig(profile_ouput_filename)
    
