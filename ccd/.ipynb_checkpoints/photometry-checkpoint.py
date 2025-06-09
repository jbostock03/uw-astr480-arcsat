#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Filename: photometry.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from photutils.aperture import aperture_photometry, CircularAperture, CircularAnnulus
from astropy.table import vstack

def do_aperture_photometry(
    image,
    positions,
    radii,
    sky_radius_in,
    sky_annulus_width,
):
    """This function must:

    - Accept a fully reduced science image as a file and read it.
    - Accept a list of positions on the image as a list of tuples (x, y).
    - Accept a list of aperture radii as a list of floats.
    - Accept a the radius at which to measure the sky background as sky_radius_in.
    - Accept a the width of the annulus as sky_annulus_width.
    - For each position and radius, calculate the flux in the aperture, subtracting
      the sky background. You can do this any way that you like but probably you'll
      want to use SkyCircularAnnulus from photutils.
    - The function should return the results from the aperture photometry. Usually
      this will be an astropy table from calling photutils aperture_photometry, but
      it can be something different if you use a different library.

    Note that the automated tests just check that you are returning from this
    function, but they do not check the contents of the returned data.

    """

    #reading reduced science image & cosmic ray mask (if exists) from reduce_science_frame()
    hdul = fits.open(image)
    data = hdul[0].data
    cosmics = hdul[1].data.astype(bool) if len(hdul) > 1 else None

    phot_arr = []

    for r in radii:
        #apertures
        ap = CircularAperture(positions,r)
    
        #annulus -- outer radius = inner + width
        an = CircularAnnulus(positions,sky_radius_in,sky_annulus_width+sky_radius_in)

        #computing photometries
        phot_data = aperture_photometry(data, ap, mask=cosmics)
        phot_data['annulus_sum'] = aperture_photometry(data, an, mask=cosmics)['aperture_sum']

        #adding radii and areas of apertures/annuli to table for later
        phot_data['r_ap'] = ap.r
        phot_data['r_in'] = an.r_in
        phot_data['r_out'] = an.r_out
        phot_data['area_ap'] = ap.area
        phot_data['area_an'] = an.area

        #sky bg for a given aperture is found by multiplying ratio of areas aperture/annulus
        phot_data['skyBg'] = phot_data['annulus_sum'] * (phot_data['area_ap']/phot_data['area_an'])

        #flux is aperture sum - sky bg
        phot_data['flux'] = phot_data['aperture_sum'] - phot_data['skyBg']

        #storing data
        phot_arr.append(phot_data)

    #stacking array of tables -- ignore warnings as they can can be distracting
    aperture_photometry_data = vstack(phot_arr, metadata_conflicts='silent').group_by('id')

    return aperture_photometry_data


def plot_radial_profile(aperture_photometry_data, output_filename="radial_profile.png"):
    """This function must:

    - Accept a table of aperture photometry data as aperture_photometry_data. This
      is probably a photutils table, the result of do_aperture_photometry, but you
      can pass anything you like. The table/input data can contain a single target
      or multiple targets, but it must include multiple apertures.
    - Plot the radial profile of a target in the image using matplotlib. If you
      have multiple targets, label them correctly.
    - Plot a vertical line at the radius of the sky aperture used for the photometry.
    - Save the plot to the file specified in output_filename.

    """
    #number of targets
    n = np.max(aperture_photometry_data['id'])

    plt.figure()
    for idx in range(0,n):
        id1 = aperture_photometry_data.groups[idx]   #loop over each object
        colour = cm.inferno(idx / n)                 #colours so profile matches aperture radius line
                
    #plotting radial profile for each target
        flux = np.diff(id1['flux'], prepend=0)
        area = np.diff(id1['area_ap'], prepend=0)
        rad_prof = flux/area
        plt.plot(id1['r_ap'], rad_prof, label=f"Target: ({id1[0]['xcenter']:.0f},{id1[0]['ycenter']:.0f})",color=colour)

    #plotting vertical lines shortly after radial profile flattens
        r_best = id1[np.argmax(rad_prof < 1)]['r_ap']
        plt.axvline(r_best,linestyle='--',alpha=0.8,label='Best aperture radius',color=colour)
    
    #plot formatting
    plt.title('Radial profiles')
    plt.xlabel('Radius (pixels)')
    plt.ylabel('Profile')
    plt.grid()
    plt.legend()

    plt.savefig(output_filename)
