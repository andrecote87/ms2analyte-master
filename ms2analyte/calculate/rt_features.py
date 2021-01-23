#!/usr/bin/env python3

"""
Set of scripts for calculating chromatographic peak properties of peaks and analytes from mass spectrometry data

"""

import ms2analyte.config as config


def find_rt(peak_data):
    """Determine retention time for a peak, given Pandas dataframe of rt and intensity"""
    max_intensity = peak_data["intensity"].max()
    rt = round(peak_data[peak_data["intensity"] == max_intensity].iloc[0]["rt"], 3)

    return rt


def rt_match(rt1, rt2):
    """Determine whether two analytes have the same rt, within defined rt error"""
    if rt1 - config.rt_error <= rt2 <= rt1 + config.rt_error:
        return True
    else:
        return False


def average_rt(rt_list):
    """Calculate average rt for a set of peaks (e.g. experiment analyte rt based on replicate analyte rts).
    Currently this is a simple average calculation, but is broken out as a separate function for possible future
    changes to rt determination strategy

    """

    return round(sum(rt_list)/len(rt_list), 3)