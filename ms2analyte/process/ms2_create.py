#!/usr/bin/env python3

"""
Create ms2 spectra for all analytes from a given sample

NOTE: This is a legacy module, and probably doesn't work

"""

import os
import pickle
import numpy as np
from scipy.stats import linregress

import ms2analyte.config as config


def ms2_peak_to_analyte(ms2_peak_list, ms2_input_data, input_structure, input_type, input_file):
    """Append peaks from ms2 data to the largest peak from each analyte, starting from the most intense analyte and
    working downwards.

    """
    with open(os.path.join(input_structure.output_directory, input_type,
                           input_file[:-(len(input_structure.ms_data_file_suffix) + 1)] + "_analytes.pickle"), "rb") \
            as g:
        analyte_list = pickle.load(g)

    with open(os.path.join(input_structure.output_directory, input_type,
                           input_file[:-(len(input_structure.ms_data_file_suffix) + 1)] + "_dataframe.pickle"), "rb") \
            as h:
        analyte_dataframe = pickle.load(h)

    analyte_ms2_peaks = []

    for analyte in analyte_list:

        insert_data = [analyte.analyte_id, []]

        analyte_scan_array = analyte_dataframe[(analyte_dataframe["peak_id"] == analyte.max_peak_id) &
                                               (analyte_dataframe["analyte_id"] == analyte.analyte_id)].sort_values(by=["scan"])["scan"].values

        for ms2_peak in ms2_peak_list:
            if not ms2_peak.peak_assigned:
                matched_scans = sorted(np.intersect1d(analyte_scan_array, ms2_peak.scan_array))
                if len(matched_scans) >= config.matched_scan_minimum:
                    analyte_max_peak_intensities = analyte_dataframe[(analyte_dataframe["peak_id"] ==
                                                                      analyte.max_peak_id) & (analyte_dataframe["scan"].isin(matched_scans))].sort_values(by=["scan"])["intensity"].values
                    ms2_peak_intensities = ms2_input_data[(ms2_input_data["peak_id"] == ms2_peak.peak_id) &
                                                          (ms2_input_data["scan"].isin(matched_scans))].sort_values(by=["scan"])["intensity"].values

                    slope_value = linregress(analyte_max_peak_intensities, ms2_peak_intensities)

                    # Intensities must vary colinearly if masses are from the same analyte, so r2 must be high.
                    # Relationship must also be positive, so r must be > 0

                    if slope_value.rvalue ** 2 >= config.slope_r2_cuttoff and slope_value.slope > 0:
                        ms2_peak.peak_assigned = True
                        insert_data[1].append(ms2_peak)

        analyte_ms2_peaks.append(insert_data)

    return analyte_ms2_peaks


def ms2_analyte_id_append(ms2_input_data, analyte_ms2_peaks):
    """Append analyte id to rows in ms2 data that correspond to each analyte"""
    ms2_peak_to_analyte_dict = {}

    for analyte in analyte_ms2_peaks:
        analyte_id = analyte[0]
        for ms2_peak in analyte[1]:
            ms2_peak_to_analyte_dict[ms2_peak.peak_id] = analyte_id

    analyte_id_by_peak_id = []

    for row in ms2_input_data.itertuples():
        try:
            analyte_id_by_peak_id.append(ms2_peak_to_analyte_dict[row.peak_id])
        except:
            analyte_id_by_peak_id.append(None)

    ms2_input_data["analyte_id"] = analyte_id_by_peak_id

    return ms2_input_data
