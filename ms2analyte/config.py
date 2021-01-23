#!/usr/bin/env python3

"""
user modifiable variables for MS2Analyte

mass_error_da = Fixed mass error in Daltons

mass_error_ppm = Relative mass error in parts per million

rt_error = Fixed retention time error in minutes

intensity_cutoff = Intensity cutoff to be met for including data points in raw data

carbon_isotope_offset = Mass difference between 12C and 13C

allowed_charge_values = Upper limit for allowed charge states (e.g. if '4' then all charges up to [M + 4H]4+ allowed)

scan_split_gap_size = Size of gap between scans that causes them to be split in to two peaks.
A value of two means one missing scan does not trigger a split, but two consecutive missing scans does

minimum_peak_scan_count = Minimum number of data points required to keep a given peak for further analysis

drift_time_error = Drift time error for peaks to be considered the same

peak_to_trough_split_ratio = (minimum intensity/maximum intensity) ratio below which a minimum in a peak causes
it to be split into two peaks

slope_r2_cuttoff = The key variable in the platform. Defines how similar peak shapes have to be in order for these peaks
to be considered part of the same analyte

matched_scan_minimum = The number of matching scans that a pair of peaks has to have before they will be compared as
part of the same analyte

analyte_peak_minimum = The minimum number of peaks that an analyte must contain to be retained. Typically 1 is a poor
number because noise spikes have no isotopes, so will all be kept, whereas 2 will remove these

analyte_match_score = The fraction of peak intensities that have to match between two analytes for them to be considered
the same compound

Safe Mode ensures users are informed about operations that refactor/delete data to resolve conflicts.
If true, functions that resolve data conficts will ask for permission before proceeding. If False, conflicts will be
resolved without input.

Example:

An example is peak_create.resolve_scan_duplicates, which removes duplicate scan data from individual peaks.
However, if these are IMS data, and InputDataStructure.ims_exists was accidentally set to False, legitimate IMS peak
data will be deleted.
The advantage of safe_mode = False is that the analysis will not wait for input, which is helpful for forcing large
datasets to complete without erroring out. However, these results will contain errors and should not be used for
research purposes. safe_mode = False is mostly used for debugging.

minimum_mass_offset_instances = Minimum number of peaks required with the same mass offset to accept this offset for
peak matching

spectral_matching_minimum_cosine_score = Minimum required cosine score to include edge between spectral nodes

minimum_experiment_analyte_mass_peak_count = Minimum number of times a mass peak must appear between samples in order
to be retained in the experiment analyte mass spectrum. WARNING: setting this to any value greater than 1 will remove
all mass spec peaks for analytes that only appear once in the experiment.

"""

__author__ = 'Roger Linington'
__copyright__ = 'Copyright 2019, Linington Lab'
__credits__ = ['Roger Linington']
__license__ = 'TBD'
__version__ = '1.0.0'
__maintainer__ = 'Roger Linington'
__email__ = 'rliningt@sfu.ca'
__status__ = 'Alpha'

mass_error_da = 0.01
mass_error_ppm = 5
rt_error = 0.1
intensity_cutoff = 2000
carbon_isotope_offset = 1.0034
allowed_charge_values = 4
scan_split_gap_size = 2
minimum_peak_scan_count = 3
drift_time_error = 1
peak_to_trough_split_ratio = 0.5
slope_r2_cuttoff = 0.9
matched_scan_minimum = 3
analyte_peak_minimum = 2
analyte_match_score = 0.6
safe_mode = False

# The next variables are for spectral matching in the calculate.spectral_matching tools

minimum_mass_offset_instances = 2
spectral_matching_minimum_cosine_score = 0.5

# The next variables are used in basketing

minimum_experiment_analyte_mass_peak_count = 1
