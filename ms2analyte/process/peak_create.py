#!/usr/bin/env python3

"""Tools to build peaks from raw mass spectrometry scan"""

from scipy.signal import find_peaks
import numpy as np
import sys

from ms2analyte.calculate import mass_features, drift_features
import ms2analyte.config as config


def mass_bin(input_data):
    """Divide original scan by scan data points in to mass peaks based only on mass difference. All data points within a
    given mass range are put together regardless of retention time.

    """
    sorted_input_data = input_data.sort_values(by=['mz'])
    sorted_input_data["peak_id"] = None

    previous_mass = 0
    peak_counter = 0

    for index, row in sorted_input_data.iterrows():
        mass_difference = row["mz"] - previous_mass

        if mass_difference > config.mass_error_da:
            peak_counter += 1
        sorted_input_data.at[index, "peak_id"] = peak_counter
        previous_mass = row["mz"]

    print("Number of mass bin peaks = " + str(sorted_input_data["peak_id"].max()))

    sorted_input_data = remove_small_peaks(sorted_input_data)

    return sorted_input_data


def remove_baseline_signals(input_data):
    """Identify baseline signals that exist in large regions of the chromatogram and remove"""
    pass


def mass_range_check(input_data):
    """Review mass bin peaks and make sure that the total mass difference is not more than allowed mass difference from
    config.py This can be caused by 'chaining' of data points within peak

    """
    next_peak_id = input_data["peak_id"].max() + 1
    split_counter = 1

    while split_counter > 0:

        split_counter = 0

        for peak, data in input_data.groupby("peak_id"):
            below_minimum_masses = []
            above_maximum_masses = []
            peak_min_mass = data["mz"].min()
            peak_max_mass = data["mz"].max()

            if peak_max_mass - peak_min_mass > 2 * config.mass_error_da:
                for index, row in data.iterrows():
                    if row["mz"] + config.mass_error_da < data["mz"].mean():
                        below_minimum_masses.append(index)
                    elif row["mz"] - config.mass_error_da > data["mz"].mean():
                        above_maximum_masses.append(index)

                if len(below_minimum_masses) > 0:
                    for index in below_minimum_masses:
                        input_data.at[index, "peak_id"] = next_peak_id
                    next_peak_id += 1
                    split_counter += 1

                if len(above_maximum_masses) > 0:
                    for index in above_maximum_masses:
                        input_data.at[index, "peak_id"] = next_peak_id

                    next_peak_id += 1
                    split_counter += 1

        input_data = remove_small_peaks(input_data)

    print("Mass range check complete")

    return input_data


def find_scan_duplicates(input_data):
    """Review mass peaks to make sure that they only have one datapoint for each scan number

    More than one data point per scan number can be encountered if the data is IMS data but
    InputDataStructure.ims_exists was incorrectly set to False.
    Alternatively, some import formats can permit the inclusion of mass peaks with very similar masses from the same
    scan.

    """
    for peak, data in input_data.groupby("peak_id"):
        if len(data[data.duplicated(["scan"], keep=False)]) > 0:  # If there are duplicate scans for this peak
            print("WARNING: Found multiple data points for a single scan for at least one peak")
            return True

    return False


def resolve_scan_duplicates(input_data):
    """Resolve cases where a single peak contains multiple data points for the same scan"""

    # If safe mode set, require user input to approve data manipulation before proceeding

    if config.safe_mode:
        selection_made = False
        processing_selection = input("WARNING: Peaks detected containing duplicate scan numbers. Likely causes are "
                                     "either not selecting the 'IMS data' button for IMS datasets, or importing data "
                                     "via third party conversion tools. To exit and change setup "
                                     "parameters, enter 1. To proceed with duplicate removal, enter 2.")
        while not selection_made:
            if processing_selection == "1":
                sys.exit()
            elif processing_selection == "2":
                selection_made = True
            else:
                processing_selection = ("ERROR: That was not a valid response. Enter either '1' to exit or '2' to "
                                        "proceed")

    # scan peaks for cases that contain duplicate scan numbers

    for peak, data in input_data.groupby("peak_id"):
        if len(data[data.duplicated(["scan"], keep=False)]) > 0:
            peak_mass = data["mz"].mean()
            data["mass_difference"] = abs(data.mz - peak_mass)
            for scan, scan_data in data.groupby("scan"):
                if len(scan_data) > 1:
                    # Create list of indices for matching scan rows
                    scan_index_list = scan_data.index.tolist()
                    # Remove index of row with lowest mass error to the peak average
                    scan_index_list.remove(scan_data[scan_data.mass_difference == scan_data.mass_difference.min()].index.tolist()[0])
                    # Remove the rest of the matching rows from the dataframe
                    input_data = input_data.drop(scan_index_list)

    print("Resolve scan duplicates complete ")

    return input_data


def isotope_filter(input_data):
    """Filter mass peaks from mass bin to remove peaks that do not have a plausible isotope peak in the dataset"""
    peak_average_mass_dict = {}
    peak_average_mass_list = []
    isotope_matched_peaks = []

    # Create reference objects

    for peak, data in input_data.groupby("peak_id"):
        peak_average_mass = round(data["mz"].mean(), 4)
        peak_average_mass_dict[peak] = peak_average_mass
        peak_average_mass_list.append(peak_average_mass)

    # For each peak look for isotope matches. Look for both matches above and below the peak, so that for A0 peaks
    # the A1 (first 13C peak) is captured (upper_target_mass) and for the last isotope peak in a series, the previous
    # 13C peak is captured.
    # Consider mass differences for all charge states, because charge state impacts mass difference.

    for peak in peak_average_mass_dict:
        for z in range(1, config.allowed_charge_values + 1):
            lower_target_mass = peak_average_mass_dict[peak] - (config.carbon_isotope_offset/z)
            upper_target_mass = peak_average_mass_dict[peak] + (config.carbon_isotope_offset/z)
            for average_peak in peak_average_mass_list:
                if mass_features.mass_match(lower_target_mass, average_peak) \
                        or mass_features.mass_match(upper_target_mass, average_peak):
                    if peak not in isotope_matched_peaks:
                        isotope_matched_peaks.append(peak)
                        break

    print("Peak isotope filter complete")

    # Only return rows from input file if this peak has a matching isotope peak in the dataset.

    return input_data[input_data["peak_id"].isin(isotope_matched_peaks)]


def scan_split(input_data):
    """Split peaks in to two subpeaks if more than one contiguous scan number is missing from the peak list"""
    max_peak_id = input_data["peak_id"].max()

    for peak, data in input_data.groupby("peak_id"):
        current_scan_value = data["scan"].min()
        current_peak_id = peak

        # If there is a gap of more than x scans, split into two peaks
        for index, row in data.sort_values("scan").iterrows():
            if row["scan"] - current_scan_value > config.scan_split_gap_size:
                max_peak_id += 1
                current_peak_id = max_peak_id
            input_data.at[index, "peak_id"] = current_peak_id
            current_scan_value = row["scan"]

    input_data = remove_small_peaks(input_data)

    print("Scan split complete")

    return input_data


def drift_split(input_data):
    """Identify peaks which have multiple data points in the same scan and split in to separate peaks based on drift
    time

    """
    max_peak_id = input_data["peak_id"].max()
    scan_duplicates = True

    while scan_duplicates:

        duplicate_counter = 0

        for peak, data in input_data.groupby("peak_id"):
            if len(data[data.duplicated(["scan"], keep=False)]) > 0:    # If there are duplicate scans for this peak
                duplicate_counter += 1

    # Make two groups by taking data for first scan(s), finding first scan whose drift time occurs most frequently in
    # peak and making this group 1, then putting all other first scans in to group two. If there is only one scan data
    # point in first scan (typical) then group 2 is empty. If there are two, place one each in groups 1 + 2, if more
    # than two (rare) then group 2 contains multiple data points for a single scan, which will get resolved in the next
    # cycle of the while loop until this condition is no longer true

                group_one_indices = []
                group_two_indices = []

                max_drift_match_count = 0
                max_drift_match_index = 0

                for first_scan_index, first_scan in data[data["scan"] == data["scan"].min()].iterrows():
                    scan_drift_match_count = len(data["drift"].between(first_scan["drift"] - config.drift_time_error,
                                                 first_scan["drift"] + config.drift_time_error).index)
                    if scan_drift_match_count > max_drift_match_count:
                        max_drift_match_count = scan_drift_match_count
                        max_drift_match_index = first_scan_index

                # Add best drift match to whole peak to group one
                group_one_indices.append(max_drift_match_index)
                # If there are any, add other first scan indices to group two
                group_two_indices += data[(data["scan"] == data["scan"].min()) &
                                          ~data.index.isin([max_drift_match_index])].index.tolist()

                # Next look at all other scan data and decide if it belongs in group 1 or group 2

                for scan_index, scan in data[data["scan"] > data["scan"].min()].sort_values("scan").iterrows():

                    # If a given scan has more than one data point, decide if any of these belong in group 1 and if so,
                    # pick the best fit and put the rest in group two

                    if len(data[data["scan"] == scan["scan"]]) > 1:
                        if scan_index in group_one_indices or scan_index in group_two_indices:
                            continue
                        else:
                            group_one_match_error = 100000
                            group_one_match_index = None
                            for duplicate_index, duplicate_scan in data[data["scan"] == scan["scan"]].iterrows():
                                drift_match_error = abs(duplicate_scan["drift"] - data[data.index.isin(group_one_indices)]["drift"].mean())
                                if drift_match_error < group_one_match_error and drift_features.drift_match(duplicate_scan["drift"], data[data.index.isin(group_one_indices)]["drift"].mean()):
                                    group_one_match_error = drift_match_error
                                    group_one_match_index = duplicate_index

                            if group_one_match_index is not None:
                                group_one_indices.append(group_one_match_index)
                                group_two_indices += data[(data["scan"] == scan["scan"]) &
                                                          ~data.index.isin([group_one_match_index])].index.tolist()
                            else:
                                group_two_indices += data[data["scan"] == scan["scan"]].index.tolist()

                    # If a given scan has only one data point then decide if it belongs in group one or not.

                    elif len(data[data["scan"] == scan["scan"]]) == 1:
                        if drift_features.drift_match(scan["drift"],
                                                      data[data.index.isin(group_one_indices)]["drift"].mean()):
                            group_one_indices.append(scan_index)
                        else:
                            group_two_indices.append(scan_index)
                    else:
                        print("WARNING: Error with scan count in drift_split")

                if len(group_two_indices) > 0:
                    max_peak_id += 1
                    for index in group_two_indices:
                        input_data.loc[index, "peak_id"] = max_peak_id

            # print("Finishing peak " + str(peak))

        input_data = remove_small_peaks(input_data)

        if duplicate_counter == 0:
            scan_duplicates = False

    print("Drift time peak split complete")

    return input_data


def remove_small_peaks(input_data):
    """Remove peaks if the peak data contains fewer than three datapoints"""
    for peak, data in input_data.groupby("peak_id"):
        if len(data.index) < config.minimum_peak_scan_count:
            input_data = input_data[input_data.peak_id != peak]

    return input_data


def remove_no_maxima_peaks(input_data):
    """Remove 'peaks' that don't have an intensity maximum. Without this they are just slopes, so have no
    chromatographic peak shape, so are not real analytes and will not match to other real peak intensity distributions.

    """
    for peak, data in input_data.groupby("peak_id"):
        # maximum_index_list is an array of intensity values arranged by scan number
        maximum_index_list = find_peaks(data.sort_values("scan")["intensity"].values)[0]
        peak_maxima_count = maximum_index_list.size
        if peak_maxima_count == 0:
            input_data = input_data[input_data.peak_id != peak]

    return input_data


def peak_minima_trim(input_data):
    """Remove tips and tails of peaks so that first and last peak scans are minima (ie so that there is no 'ski jump'
    shape to peak ends).

    """
    for peak, data in input_data.groupby("peak_id"):
        maximum_index_list = find_peaks(data.sort_values("scan")["intensity"].values)[0]
        minimum_index_list = find_peaks(data.sort_values("scan")["intensity"].values * -1)[0]

        if minimum_index_list.size > 0:

            # Test if there is a minimum between start of array and first maximum. If so, remove data that precedes
            # first minimum

            if minimum_index_list[0] < maximum_index_list[0]:
                input_data = input_data.drop(data.sort_values("scan").iloc[:minimum_index_list[0]].index.values)

            # Test if there is a minimum between last maximum and end of array. If so, remove data that follows
            # last minimum

            if minimum_index_list[-1] > maximum_index_list[-1]:
                input_data = input_data.drop(data.sort_values("scan").iloc[minimum_index_list[-1] + 1:].index.values)

    input_data = remove_small_peaks(input_data)

    return input_data


def peak_split(input_data):
    """Split peaks that have more than one maximum into individual peaks (separates isobaric species with similar
    retention times)

    **NOTE: THIS FUNCTION IS DEPRECATED** peak_split_max is more effective, and is the preferred tool.

    """
    next_peak_id = input_data["peak_id"].max() + 1

    # Count the number of maxima in the peak. If greater than 1 decide if peak separation is sufficient to split
    # into two peaks

    for peak, data in input_data.groupby("peak_id"):
        # Index position for start of new peak. Set initially at 0. If peak is split, gets set to new index position
        # for first data point of second peak (which may subsequently get split again)
        peak_start_index = 0

        maximum_index_list = find_peaks(data.sort_values("scan")["intensity"].values)[0]
        peak_maxima_count = maximum_index_list.size
        if peak_maxima_count > 1:
            minimum_index_list = find_peaks(data.sort_values("scan")["intensity"].values * -1)[0]
            scan_sorted_data = data.sort_values("scan")
            for maximum_index_list_index, maximum_index in enumerate(maximum_index_list[:-1]):

                # Test to see if minimum between each pair of maxima is low enough to split peak in two
                if scan_sorted_data.iloc[minimum_index_list[maximum_index_list_index]]["intensity"]/scan_sorted_data.iloc[maximum_index_list[maximum_index_list_index]]["intensity"] < config.peak_to_trough_split_ratio and scan_sorted_data.iloc[minimum_index_list[maximum_index_list_index]]["intensity"]/scan_sorted_data.iloc[maximum_index_list[maximum_index_list_index + 1]]["intensity"] < config.peak_to_trough_split_ratio:

                    # If peak is to be split, give first peak a new peak id number
                    new_peak_index_numbers = scan_sorted_data.iloc[peak_start_index:minimum_index_list[maximum_index_list_index]].index.tolist()
                    input_data.loc[new_peak_index_numbers, "peak_id"] = next_peak_id
                    next_peak_id += 1
                    peak_start_index = minimum_index_list[maximum_index_list_index]

    input_data = remove_small_peaks(input_data)

    return input_data


def peak_split_max(input_data):
    """Split peaks that have more than one maximum into individual peaks (separates isobaric species with similar
    retention times)

    Splits peaks based on the magnitude of the minimum between largest peak and any other maximum in the peak maximum
    list. Operates from the largest peak down, rather than iterating through the maxima in scan order

    """
    input_data["split_completed"] = False
    next_peak_id = input_data["peak_id"].max() + 1

    # Continue until all peaks have been annotated as fully split
    while not input_data["split_completed"].all():
        for peak, data in input_data.groupby("peak_id"):
            # print("Starting peak " + str(peak))

            # Check to see if peak has already been completed. If not, analyze
            if not data["split_completed"].all():

                # Count the number of maxima in the peak. If greater than 1 decide if peak separation is sufficient to
                # split into two peaks
                maximum_index_list = find_peaks(data.sort_values(by="scan")["intensity"].values)[0]
                peak_maxima_count = maximum_index_list.size

                if peak_maxima_count == 1:
                    input_data.loc[input_data["peak_id"] == peak, "split_completed"] = True
                    continue

                else:
                    split_performed = False

                    # Sort the find_peaks list (maximum_index_list) by peak intensity, then compare gap between max peak
                    # and every other peak (in decreasing intensity order) until you either find a gap that meets the
                    # split criterion, or complete the list. Either split, or pass.
                    minimum_index_list = find_peaks(data.sort_values("scan")["intensity"].values * -1)[0]
                    minimum_scan_list = []
                    for index in minimum_index_list:
                        minimum_scan_list.append(data.sort_values("scan")["scan"].values[index])
                    max_peaks_intensity_sorted = data.sort_values("scan").iloc[maximum_index_list].sort_values(by="intensity",
                                                                                                               ascending=False)
                    max_peak_1_intensity = max_peaks_intensity_sorted["intensity"].iloc[0]
                    max_peak_1_scan = max_peaks_intensity_sorted["scan"].iloc[0]
                    for peak2 in max_peaks_intensity_sorted.iloc[1:].itertuples():
                        max_peak_2_intensity = peak2.intensity
                        max_peak_2_scan = peak2.scan
                        if max_peak_1_scan < max_peak_2_scan:
                            start_scan = max_peak_1_scan
                            end_scan = max_peak_2_scan
                        else:
                            start_scan = max_peak_2_scan
                            end_scan = max_peak_1_scan

                        # Find intensity of minimum between largest two peaks
                        min_peaks_intensity_sorted = data[data["scan"].isin(np.array([scan for scan in minimum_scan_list
                                                                                      if start_scan < scan <
                                                                                      end_scan]))].sort_values(by="intensity")
                        min_peak_intensity = min_peaks_intensity_sorted["intensity"].iloc[0]

                        # Calculate intensity difference on both sides of minimum. If both pass split criterion,
                        # assign new peak id to
                        if min_peak_intensity/max_peak_1_intensity <= config.peak_to_trough_split_ratio and \
                                min_peak_intensity/max_peak_2_intensity <= config.peak_to_trough_split_ratio:
                            split_scan = min_peaks_intensity_sorted["scan"].iloc[0]

                            # if split_required, split peak in two, and give right hand peak a new peak id. This new
                            # peak may require splitting, but will be reevaluated once the function reaches the last
                            # peaks in the list.
                            input_data.loc[(input_data["scan"] > split_scan) &
                                           (input_data["peak_id"] == peak), ["peak_id"]] = next_peak_id
                            next_peak_id += 1
                            split_performed = True

                    if not split_performed:
                        input_data.loc[input_data["peak_id"] == peak, "split_completed"] = True

        input_data = remove_small_peaks(input_data)
        input_data = remove_no_maxima_peaks(input_data)
        print("Max peak id = " + str(next_peak_id - 1))

    input_data = input_data.drop(["split_completed"], axis=1)

    print("Peak shape peak split complete")

    return input_data
