#!/usr/bin/env python3

"""Set of scripts for determining whether two analytes should be matched (e.g. replicate comparison or basketing
between samples) based on degree of peak matching between analytes.

"""

import ms2analyte.config as config
from ms2analyte.calculate import mass_features


def max_peak_match(analyte1, analyte2):
    """Determine whether the maximum intensity peak from one analyte is present as a peak in another analyte.
    Useful for quickly deciding whether or not to do full unidirectional or bidirectional match on two analytes.
    If biggest peak of one is not present in the other, then match is False

    """
    analyte2_peak_mass_list = []    # List of all peak masses from analyte 2

    for peak in analyte2.peak_list:
        analyte2_peak_mass_list.append(peak.average_mass)

    for peak_mass in analyte2_peak_mass_list:
        if mass_features.mass_match(peak_mass, analyte1.max_peak_intensity_mass):
            return True


def rt_match(analyte1, analyte2):
    """Determine whether retention times of two analytes are within match tolerance from config.py"""

    if analyte1.analyte_rt + config.rt_error >= analyte2.analyte_rt >= analyte1.analyte_rt - config.rt_error:
        return True


def unidirectional_match(analyte1, analyte2):
    """Calculate whether or not two analytes are representatives of the same compound. This is based on the percentage
    of the total intensity for all peaks that matches between two analytes

    """
    analyte2_peak_mass_list = []

    for peak in analyte2.peak_list:
        analyte2_peak_mass_list.append(peak.average_mass)

    sorted_analyte2_peak_mass_list = sorted(analyte2_peak_mass_list)

    total_peak_intensity = 0
    matched_peak_intensity = 0

    for peak in analyte1.peak_list:
        total_peak_intensity += peak.max_intensity
        for peak2 in sorted_analyte2_peak_mass_list:
            if mass_features.mass_match(peak.average_mass, peak2):
                matched_peak_intensity += peak.max_intensity
            elif peak2 > peak.average_mass + config.mass_error_da:
                break

    analyte_match_score = round(matched_peak_intensity/total_peak_intensity, 2)

    if analyte_match_score >= config.analyte_match_score:
        return True

    else:
        return False


def bidirectional_match(analyte1, analyte2):
    """Calculate whether or not two analytes are from the same compound by considering fraction of peaks that match
    between analytes, but considering both A in B and B in A

    """
    if unidirectional_match(analyte1, analyte2) and unidirectional_match(analyte2, analyte1):
        return True

    else:
        return False


def relative_intensity_match(spectrum1, spectrum2):
    """Determine whether two analytes are the same compound or not by comparing relative intensity spectra (i.e. spectra
    where mass signal intensities are out of 100%. These are typically from averaged spectra, e.g. replicate analyte
    spectra that are consensus spectra from each individual replicate)

    """
    spectrum1_matched_peaks = []
    spectrum2_matched_peaks = []

    for peak2 in spectrum2:
        for peak1 in spectrum1:
            if mass_features.mass_match(peak1.average_mass, peak2.average_mass):
                if peak1 not in spectrum1_matched_peaks:
                    spectrum1_matched_peaks.append(peak1)
                spectrum2_matched_peaks.append(peak2)
                break

    if len(spectrum1_matched_peaks) > 0 and len(spectrum2_matched_peaks) > 0:

        spectrum1_intensity = sum(peak1.relative_intensity for peak1 in spectrum1)
        spectrum2_intensity = sum(peak2.relative_intensity for peak2 in spectrum2)
        spectrum1_match_intensity = sum(peak1.relative_intensity for peak1 in spectrum1_matched_peaks)
        spectrum2_match_intensity = sum(peak2.relative_intensity for peak2 in spectrum2_matched_peaks)

        if spectrum1_match_intensity/spectrum1_intensity >= config.analyte_match_score \
                and spectrum2_match_intensity/spectrum2_intensity >= config.analyte_match_score:
            return True


def modify_average(old_average, old_member_count, new_value, round_value):
    """Modify average value (e.g. mass) for an averaged feature on addition of a new member. i.e. if the average value
    for a feature is 4 based on an average from 4 input values, then adding a new value (6) will make the new average
    (4 * 4 + 6)/5

    """
    modified_value = round(((old_average * old_member_count) + new_value)/(old_member_count + 1), round_value)

    return modified_value
