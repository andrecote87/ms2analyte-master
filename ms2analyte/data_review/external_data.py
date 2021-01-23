#!/usr/bin/env python3

"""
A suite of tools to compare MS2Analyte outputs to data from external sources
(e.g. peak lists from other data processing packages)

"""

import pickle
import numpy as np
import csv
import os
import sys

import ms2analyte.config as config


def peak_list_annotate(experiment_name, sample_name, replicate, ms2analyte_data_path, peak_list_full_path):
    """Compare peak list from external data processing tool with MS2Analyte output data, and annotate external peak list
    with the final assignment (i.e. present or not and, if so, is the peak excluded, or included as part of an analyte,
    or included as part of a blank?) for all matching peak features

    Requires data_review.data_review.replicate_peak_analyte_id_df to be run on experiment first in order to create
    required summary Dataframe

    Assumes peak list is a csv with headers and peak mz in column 1 and peak rt in column 2

    NOTE: paths are currently manually defined

"""
    with open(os.path.join(ms2analyte_data_path, experiment_name + "_full_peak_list_dataframe.pickle"), "rb") as f:
        ms2analyte_dataframe = pickle.load(f)

    external_peak_list = []     # [[mz, rt]]

    with open(peak_list_full_path) as g:
        csv_g = csv.reader(g)
        next(g)
        for row in csv_g:
            external_peak_list.append([round(float(row[0]), 4), round(float(row[1]), 2)])

    for row in external_peak_list:
        peak_match_df = ms2analyte_dataframe.loc[(ms2analyte_dataframe["sample_name"] == sample_name) &
                                                 (ms2analyte_dataframe["replicate"] == replicate) &
                                                 ms2analyte_dataframe["peak_rt"].between(row[1] - config.rt_error,
                                                                                         row[1] + config.rt_error) &
                                                 ms2analyte_dataframe["peak_average_mz"].between(row[0] -
                                                                                                 config.mass_error_da,
                                                                                                 row[0] +
                                                                                                 config.mass_error_da)]

        # If there are no matches, annotate peak list with this information
        if len(peak_match_df) == 0:
            # Append assignment
            row.append("Not found in MS2Analyte")
            # Append blank match bool
            row.append(False)

        # If there is exactly one match, insert the highest level of assignment, and annotate blank match
        elif len(peak_match_df) == 1:
            # Append assignment
            if not np.isnan(peak_match_df.iloc[0]["experiment_analyte_id"]):
                row.append("Experiment analyte id: " + str(peak_match_df.iloc[0]["experiment_analyte_id"]))
            elif not np.isnan(peak_match_df.iloc[0]["analyte_id"]):
                row.append("Analyte id: " + str(peak_match_df.iloc[0]["analyte_id"]))
            else:
                row.append("Dropped in peak create stage")
            # Append blank match bool
            row.append(peak_list_blank_annotate(peak_match_df))

        # If there is more than one candidate match within the tolerances, choose the one with the experiment_analyte_id
        # If there isn't an experiment_analyte_id, choose the one with the analyte_id
        # If there are still multiple candidates, choose the one with the lowest mass error.
        # If there are still multiple candidates, choose the one with the lowest rt error
        # If there are still multiple candidates, take the first in the list [NOTE: would perhaps be better to take
        # the one with the highest level of assignment, but this situation will be rare so hve not implemented this for
        # now.]
        else:
            if len(peak_match_df[peak_match_df["experiment_analyte_id"].notnull()]) == 1:
                row.append("Experiment analyte id: " + str(peak_match_df[peak_match_df["experiment_analyte_id"].notnull()].iloc[0]["experiment_analyte_id"]))
                row.append(peak_list_blank_annotate(peak_match_df[peak_match_df["experiment_analyte_id"].notnull()]))
            elif len(peak_match_df[peak_match_df["experiment_analyte_id"].notnull()]) > 1:
                annotation, blank_match = prioritize_match_list(peak_match_df[peak_match_df["experiment_analyte_id"].notnull()], row[0], row[1])
                row.append(annotation)
                row.append(blank_match)
            elif len(peak_match_df[peak_match_df["analyte_id"].notnull()]) == 1:
                row.append("Analyte id: " + str(peak_match_df[peak_match_df["analyte_id"].notnull()].iloc[0]["analyte_id"]))
                row.append(peak_list_blank_annotate(peak_match_df[peak_match_df["analyte_id"].notnull()]))
            elif len(peak_match_df[peak_match_df["analyte_id"].notnull()]) > 1:
                annotation, blank_match = prioritize_match_list(peak_match_df[peak_match_df["analyte_id"].notnull()],
                                                                row[0], row[1])
                row.append(annotation)
                row.append(blank_match)
            else:
                annotation, blank_match = prioritize_match_list(peak_match_df, row[0], row[1])
                row.append(annotation)
                row.append(blank_match)

    headers = [["mz", "rt", "MS2Analyte annotation", "MS2Analyte blank match"]]

    with open(peak_list_full_path[:-4] + "_annotated_R" + str(replicate) + ".csv", "w") as h:
        csv_h = csv.writer(h)
        csv_h.writerows(headers + external_peak_list)


def peak_list_blank_annotate(dataframe):
    """Blank annotation function for peak_list_annotate"""
    if dataframe.iloc[0]["analyte_blank_match"]:
        return True
    else:
        return False


def prioritize_match_list(dataframe, row_mz, row_rt):
    """Prioritize matched peaks for peak_list_annotate. Used in cases where matching by various criteria gives
    more thank one possible match in order to select the closest match based on mz and/or rt matching.

    """
    annotation = ""
    blank_match = False
    dataframe["mass_differences"] = dataframe.peak_average_mz - row_mz
    minimum_mz_error = dataframe.mass_differences.abs().min().item()

    # Make sure that you have the sign of the error correct
    if len(dataframe.loc[dataframe["mass_differences"] == minimum_mz_error]) == 0:
        minimum_mz_error = -minimum_mz_error
    mass_filtered_peak_match_df = dataframe.loc[dataframe["mass_differences"] == minimum_mz_error]

    # If no rows remain, print error and exit
    if len(mass_filtered_peak_match_df) == 0:
        print("ERROR: mass filtered df length = 0")
        sys.exit()

    # If only one row remains, add data
    if len(mass_filtered_peak_match_df) == 1:
        if not np.isnan(mass_filtered_peak_match_df.iloc[0]["experiment_analyte_id"]):
            annotation = ("Experiment analyte id: " +
                          str(mass_filtered_peak_match_df.iloc[0]["experiment_analyte_id"]))
        elif not np.isnan(mass_filtered_peak_match_df.iloc[0]["analyte_id"]):
            annotation = ("Analyte id: " + str(mass_filtered_peak_match_df.iloc[0]["analyte_id"]))
        else:
            annotation = "Dropped in peak create stage"
        # Append blank match bool
        blank_match = (peak_list_blank_annotate(mass_filtered_peak_match_df))

    # If more than one option, compare rt errors and pick lowest error match(es)
    else:
        mass_filtered_peak_match_df["rt_differences"] = mass_filtered_peak_match_df.peak_rt - row_rt
        minimum_rt_error = mass_filtered_peak_match_df.rt_differences.abs().min().item()
        # Make sure that you have the sign of the error correct
        if len(mass_filtered_peak_match_df.loc[mass_filtered_peak_match_df["rt_differences"] == minimum_rt_error]) == 0:
            minimum_rt_error = -minimum_rt_error
        mass_rt_filtered_peak_match_df = mass_filtered_peak_match_df.loc[mass_filtered_peak_match_df["rt_differences"]
                                                                         == minimum_rt_error]
        # If no rows remain, print error and exit
        if len(mass_rt_filtered_peak_match_df) == 0:
            print("ERROR: mass rt filtered df length = 0")
            sys.exit()
        # Otherwise, add data from first row. In most cases, results will only have one row. In cases where
        # more than one row exists, pick first row arbitrarily. Justification is that this will be very rare,
        # and doesn't justify effort of more complex solution (RGL).
        else:
            if not np.isnan(mass_rt_filtered_peak_match_df.iloc[0]["experiment_analyte_id"]):
                annotation = ("Experiment analyte id: " +
                              str(mass_rt_filtered_peak_match_df.iloc[0]["experiment_analyte_id"]))
            elif not np.isnan(mass_rt_filtered_peak_match_df.iloc[0]["analyte_id"]):
                annotation = ("Analyte id: " + str(mass_rt_filtered_peak_match_df.iloc[0]["analyte_id"]))
            else:
                annotation = "Dropped in peak create stage"
            # Append blank match bool
            blank_match = (peak_list_blank_annotate(mass_rt_filtered_peak_match_df))

    return annotation, blank_match
