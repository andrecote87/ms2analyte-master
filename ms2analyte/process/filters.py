#!/usr/bin/env python3

"""Set of scripts for filtering datasets using different metrics"""

import ms2analyte.config as config


def intensity(input_file):
    """Filter dataframe based on intensity cutoff from config file"""
    filtered_input_file = input_file.query('intensity>' + str(config.intensity_cutoff))

    return filtered_input_file
