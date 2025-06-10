import batman
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def plot_lightcurve(fluxes, t, params, \
                    filename='lightcurve.png', zoom=False):
    """
    Plots the lightcurve for given fluxes using the batman package.

    inputs:
    fluxes: array of fluxes from total_flux()
    t:      array of times of observations
    params: array of parameters to be used by the batman package
    zoom:   boolean; set as True to zoom into the baseline of the lightcurve
    """
    #plot theme
    sns.set_theme('paper', color_codes=True, palette='colorblind', font_scale=1)

    #plotting data
    plt.scatter(t,fluxes/np.max(fluxes),label='Fluxes (normalised)')
    plt.plot(t,curve,color='C1',label='Light curve fit')

    #plot settings
    plt.legend()
    plt.xlabel('Time since start of observations')
    plt.ylabel('Flux (normalised)')
    plt.title('Light curve for transit')

    if zoom == True:
        plt.ylim(0.9,1.02)
        
    plt.savefig(filename)