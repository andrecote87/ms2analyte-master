#!/usr/bin/env python3

"""Tools to build analytes from peak output from peak_create.py"""

from scipy.stats import linregress
import numpy as np
from operator import attrgetter

from ms2analyte.calculate import mass_features, rt_features
import ms2analyte.config as config


class MassPeak:
    """Class containing all relevant data for each individual mass peak from peak_create"""
    def __init__(self, dataframe, peak_id, max_intensity, min_scan, max_scan, scan_array, average_mass, rt,
                 average_drift, peak_assigned):
        self.dataframe = dataframe
        self.peak_id = peak_id
        self.max_intensity = max_intensity
        self.min_scan = min_scan
        self.max_scan = max_scan
        self.scan_array = scan_array
        self.average_mass = average_mass
        self.rt = rt
        self.average_drift = average_drift
        self.peak_assigned = peak_assigned


class Analyte:
    """Class containing data on peak ids for each assigned analyte"""
    def __init__(self, analyte_id, peak_list, max_peak_id, max_peak_intensity_mass, max_peak_intensity, analyte_rt,
                 replicate_match, replicate_analyte_id, experiment_match, experiment_analyte_id, blank_match):
        self.analyte_id = analyte_id
        self.peak_list = peak_list
        self.max_peak_id = max_peak_id
        self.max_peak_intensity_mass = max_peak_intensity_mass
        self.max_peak_intensity = max_peak_intensity
        self.analyte_rt = analyte_rt
        self.replicate_match = replicate_match
        self.replicate_analyte_id = replicate_analyte_id
        self.experiment_match = experiment_match
        self.experiment_analyte_id = experiment_analyte_id
        self.blank_match = blank_match


def peak_df_to_obj(input_data):
    """Create peak objects from Pandas dataframe"""
    peak_list = []

    for peak, data in input_data.groupby("peak_id"):
        peak_id = peak
        max_intensity = data["intensity"].max()
        min_scan = data["scan"].min()
        max_scan = data["scan"].max()
        scan_array = data["scan"].values
        average_mass = round(data["mz"].mean(), 4)
        rt = rt_features.find_rt(data[["rt", "intensity"]])
        average_drift = round(data["drift"].mean(), 1)
        peak_assigned = False

        peak_list.append(MassPeak(data, peak_id, max_intensity, min_scan, max_scan, scan_array, average_mass, rt,
                                  average_drift, peak_assigned))

    sorted_peak_list = sorted(peak_list, key=attrgetter("max_intensity"), reverse=True)

    return sorted_peak_list


def peak_list_to_dict(peak_list):
    """Create dict of peaks"""
    peak_dict = {}

    for peak in peak_list:
        peak_dict[peak.peak_id] = peak

    return peak_dict


def peak_to_analyte(peak_list, input_data):
    """Create analyte from peaks by comparing slope of intensities on scan by scan basis for peaks with overlapping
    scans

    """
    analyte_list = []
    current_analyte_id = 1

    peak_dict = peak_list_to_dict(peak_list)

    # Look at most intense peak in list. If not already assigned to an analyte, start new analyte and add peak

    for origin_peak in peak_list:
        if not origin_peak.peak_assigned:
            origin_peak.peak_assigned = True
            current_analyte = Analyte(current_analyte_id, [origin_peak], None, None, None, None, None, None, None,
                                      None, None)

            # look iteratively at all peaks and decide if peak shape matches first peak in new analyte. If so, add

            for test_peak in peak_list:
                if not test_peak.peak_assigned:
                    matched_scans = sorted(np.intersect1d(origin_peak.scan_array, test_peak.scan_array))
                    if len(matched_scans) >= config.matched_scan_minimum:
                        origin_peak_intensities = input_data[(input_data["peak_id"] == origin_peak.peak_id) &
                                                             (input_data["scan"].isin(matched_scans))].sort_values(by=["scan"])["intensity"].values
                        test_peak_intensities = input_data[(input_data["peak_id"] == test_peak.peak_id) &
                                                           (input_data["scan"].isin(matched_scans))].sort_values(by=["scan"])["intensity"].values

                        slope_value = linregress(origin_peak_intensities, test_peak_intensities)

                        # Intensities must vary colinearly if masses are from the same analyte, so r2 must be high.
                        # Relationship must also be positive, so r must be > 0

                        if slope_value.rvalue ** 2 >= config.slope_r2_cuttoff and slope_value.slope > 0:
                            test_peak.peak_assigned = True
                            current_analyte.peak_list.append(test_peak)

            if len(current_analyte.peak_list) >= config.analyte_peak_minimum:
                analyte_list.append(current_analyte)
                print("Completed analysis for analyte " + str(current_analyte_id))
                current_analyte_id += 1

    # Determine maximum intensity peak for analyte, and append max intensity and mass of most intense peak to each
    # analyte
    # Calculate analyte rt by taking average rt of all peaks that make up analyte

    for analyte in analyte_list:
        max_intensity = 0
        max_peak = 0
        for peak in analyte.peak_list:
            if peak.max_intensity > max_intensity:
                max_intensity = peak.max_intensity
                max_peak = peak.peak_id
        analyte.max_peak_id = max_peak
        analyte.max_peak_intensity = max_intensity
        analyte.max_peak_intensity_mass = peak_dict[max_peak].average_mass
        analyte.analyte_rt = rt_features.find_rt(peak_dict[max_peak].dataframe)

        # print("analyte " + str(analyte.analyte_id) + " length = " + str(len(analyte.peak_list)))

    print("Total number of peaks = " + str(len(peak_list)))
    print("Total number of analytes = " + str(len(analyte_list)))

    return analyte_list


def analyte_isotope_filter(analyte_list):
    """Filter analytes, and only keep those that contain at least one peak with a 13C isotope"""
    filtered_analyte_list = []

    for analyte in analyte_list:
        isotope_peak = False
        peak_mass_list = []
        for peak in analyte.peak_list:
            peak_mass_list.append(peak.average_mass)
        sorted_peak_mass_list = sorted(peak_mass_list)
        for index, peak_mass in enumerate(sorted_peak_mass_list[:-1]):
            for peak_mass2 in sorted_peak_mass_list[index + 1:]:
                if mass_features.isotope_match(peak_mass, peak_mass2):
                    isotope_peak = True
                    break
        if isotope_peak:
            filtered_analyte_list.append(analyte)

    print("Total number of analytes with isotopes = " + str(len(filtered_analyte_list)))

    return filtered_analyte_list


def analyte_id_append(input_data, analyte_list):
    """Add new column to dataframe that lists analyte_id by referencing peak ids in each analyte from peak_to_analyte"""
    peak_to_analyte_dict = {}

    for analyte in analyte_list:
        for peak in analyte.peak_list:
            peak_to_analyte_dict[peak.peak_id] = analyte.analyte_id

    analyte_id_by_peak_id = []

    for row in input_data.itertuples():
        try:
            analyte_id_by_peak_id.append(peak_to_analyte_dict[row.peak_id])
        except:
            analyte_id_by_peak_id.append(None)

    input_data["analyte_id"] = analyte_id_by_peak_id

    return input_data
