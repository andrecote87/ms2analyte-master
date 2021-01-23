#!/usr/bin/env python3

"""Set of scripts for calculating drift spectral properties of peaks and analytes from IMS data"""

import ms2analyte.config as config


def average_drift(drift_list):
    """Calculate the average drift time, given a list of drift times"""
    average_drift_value = round(sum(drift_list)/len(drift_list), 1)
    return average_drift_value


def drift_match(drift1, drift2):
    """Determine whether two drift times are within required drift time error of one another"""
    drift_match_bool = False

    if drift1 - config.drift_time_error <= drift2 <= drift1 + config.drift_time_error:
        drift_match_bool = True

    return drift_match_bool
