# uw-astr480-arcsat
Project files for ASTR 480 ARCSAT observations.

# Files

## `/ccd/...`
.py files for code to run reductions using the observed data. This is adapted from the _CCD Reduction_ assignment:

**`reduction.run_reduction`**: this performs the entire CCD reduction process on the data from 20250603 (HAT-P-36 b).

**`reduction_0601.run_reduction`**: this performs the entire CCD reduction process on the data from 20250601 (XO-1 b).


**`fluxes.total_flux`**: this calculates fluxes for each reduced science frame for the data from 20250603 (HAT-P-36 b).

**`fluxes_0601.total_flux`**: this calculates fluxes for each reduced science frame for the data from 20250601 (XO-1 b).

**`lightcurve.plot_lightcurve`**: this plots a lightcurve for given fluxes using the `batman` package.

## `/data/...`
The raw data used for the data analysis. Only the data from 20250601 is here due to memory limitations.

## `/reduced_data/...`
The reduced data files. Only the data from 20250601 is here due to memory limitations.

## `visualisation.ipynb`
Running the `run_reduction()` function on the data.

## `lightcurve.ipynb`
Running the `total_flux()` function on the data, and plotting the light curve.

### `***.png`
Saved images of light curves for the paper.

# Acknowledgements
Kreidberg, Laura. "batman: basic transit model calculation in Python." Publications of the Astronomical Society of the Pacific 127.957 (2015): 1161.

Based on observations obtained with Apache Point Observatory's 0.5-m Astrophysical Research Consortium Small Aperture Telescope.
