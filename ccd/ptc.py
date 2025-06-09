#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Filename: ptc.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from astropy.io import fits
import numpy as np

def calculate_gain(files):
    """This function must:

    - Accept a list of files that you need to calculate the gain
      (two files should be enough, but what kind?).
    - Read the files and calculate the gain in e-/ADU.
    - Return the gain in e-/ADU.

    """
    #flats are used for the gain due to high signal level
    flats = []

    #relatively flat region for good statistics
    region = (slice(100,-100),slice(100,-100))
    
    #reading img types & confirming flats
    for path in files:
        header = fits.getheader(path)
        img_type = header['IMAGETYP']

        #verify flat frames
        if img_type != 'FLAT':
            raise Exception(f'Use flats to calculate gain! TYPE = {img_type}')
        
        #reading files if flat
        data = fits.getdata(path)
        flats.append(data[region].astype(np.float32))

    #calculate variance of the difference between 2 flats
    flat_diff = flats[1] - flats[0]
    flat_diff_var = np.var(flat_diff)

    #signal = average of 2 flats
    mean_signal = 0.5 * np.mean(flats[0] + flats[1])

    #calculate the gain
    gain = (2 * mean_signal / flat_diff_var).astype(np.float64)

    return gain


def calculate_readout_noise(files, gain):
    """This function must:

    - Accept a list of files that you need to calculate the readout noise
      (two files should be enough, but what kind?).
    - Accept the gain in e-/ADU as gain. This should be the one you calculated
      in calculate_gain.
    - Read the files and calculate the readout noise in e-.
    - Return the readout noise in e-.

    """

    #biases are used for the readout noise due to no signal by definition
    biases = []

    #trim edges only as biases are very flat
    region = (slice(100,-100),slice(100,-100))
    
    #reading img types & confirming biases
    for path in files:
        header = fits.getheader(path)
        img_type = header['IMAGETYP']

        #verify bias frames
        if img_type != 'BIAS':
            raise Exception(f'Use biases to calculate readout noise! TYPE = {img_type}')
        
        #reading files if bias
        data = fits.getdata(path)
        biases.append(data[region].astype(np.float32))

    #calculate variance of the difference between 2 biases
    bias_diff = biases[1] - biases[0]
    bias_diff_var = np.var(bias_diff)

    #calculate readout noise
    rn_adu = np.sqrt(bias_diff_var / 2)
    readout_noise = (rn_adu * gain).astype(np.float64)
    
    return readout_noise
