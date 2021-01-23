#!/usr/bin/env python3

"""Tools to export data from MS2Analyte as flat files for viewing in Tableau"""

import os
import pickle
import pandas as pd
import sys
import csv

from ms2analyte.file_handling import file_load


def full_export(input_file, input_data, input_structure, input_type, **kwargs):
    """Export data at analyte stage (with peaks, but no replicate comparisons). Input type = 'Samples' or 'Blanks'"""
    subname = kwargs.get("subname", None)

    root_filename = input_file[:-(len(input_structure.ms_data_file_suffix) + 1)]
    if subname:
        output_filename = os.path.join(input_structure.output_directory, input_type, root_filename + "_" + subname
                                       + "_tableau_output.csv")
    else:
        output_filename = os.path.join(input_structure.output_directory, input_type, root_filename
                                       + "_tableau_output.csv")
    input_data.to_csv(output_filename, index=False, header=True)


def replicate_analyte_export(input_structure, input_type, sample_name, **kwargs):
    """Export data at replicate comparison stage"""
    subname = kwargs.get("subname", None)

    output_data = file_load.sample_dataframe_concat(input_structure, input_type, sample_name)

    if subname:
        output_filename = os.path.join(input_structure.output_directory, input_type, sample_name + "_" + subname
                                       + "_replicated_tableau_output.csv")
    else:
        output_filename = os.path.join(input_structure.output_directory, input_type, sample_name
                                       + "_replicated_tableau_output.csv")

    output_data.to_csv(output_filename, index=False, header=True)


def experiment_analyte_export(input_structure, input_type, sample_name, **kwargs):
    """Export data at experiment comparison stage"""
    subname = kwargs.get("subname", None)

    with open((os.path.join(input_structure.output_directory, input_type, sample_name
                            + "_all_replicates_dataframe.pickle")), "rb") as pickle_file:
        output_data = pickle.load(pickle_file)

    if subname:
        output_filename = os.path.join(input_structure.output_directory, input_type, sample_name + "_" + subname
                                       + "_experiment_ids_tableau_output.csv")
    else:
        output_filename = os.path.join(input_structure.output_directory, input_type, sample_name
                                       + "_experiment_ids_tableau_output.csv")

    output_data.to_csv(output_filename, index=False, header=True)


def experiment_blank_annotation_export(input_structure, input_type, sample_name, **kwargs):
    """Export data at experiment blank annotation stage"""
    subname = kwargs.get("subname", None)

    with open((os.path.join(input_structure.output_directory, input_type, sample_name
                            + "_all_replicates_blanked_dataframe.pickle")), "rb") as pickle_file:
        output_data = pickle.load(pickle_file)

    if subname:
        output_filename = os.path.join(input_structure.output_directory, input_type, sample_name + "_" + subname
                                       + "_experiment_ids_blanked_tableau_output.csv")
    else:
        output_filename = os.path.join(input_structure.output_directory, input_type, sample_name
                                       + "_experiment_ids_blanked_tableau_output.csv")

    output_data.to_csv(output_filename, index=False, header=True)


def ms1_ms2_combined_export(input_structure, input_type, sample_name, **kwargs):
    """Combine data from ms1 experiment and ms2 data in to a single file"""
    subname = kwargs.get("subname", None)

    with open((os.path.join(input_structure.output_directory, input_type, sample_name
                            + "_dataframe.pickle")), "rb") as pickle_file:
        ms1_data = pickle.load(pickle_file)

    with open((os.path.join(input_structure.output_directory, input_type, sample_name
                            + "_ms2_dataframe.pickle")), "rb") as pickle_file:
        ms2_data = pickle.load(pickle_file)

    ms1_data["ms_level"] = "ms1"
    ms2_data["ms_level"] = "ms2"

    output_data = pd.concat([ms1_data, ms2_data])

    if subname:
        output_filename = os.path.join(input_structure.output_directory, input_type, sample_name + "_" + subname
                                       + "_ms1_ms2_combined_tableau_output.csv")
    else:
        output_filename = os.path.join(input_structure.output_directory, input_type, sample_name
                                       + "_ms1_ms2_combined_tableau_output.csv")

    output_data.to_csv(output_filename, index=False, header=True)


def experiment_analyte_overview_export(input_structure, input_type, sample_list):
    """Create summary file the presents overview information on all the analytes found in all the samples of an
    experiment
    Useful for presenting a global view of which analytes have been found, and how these analytes are distributed
    across the sample set.

    """
    try:
        with open(os.path.join(input_structure.output_directory, input_type, input_structure.experiment_name +
                               "_experiment_analytes.pickle"), "rb") as analyte_pickle:
            experiment_analytes = pickle.load(analyte_pickle)
    except FileNotFoundError as fnf_error:
        print(fnf_error)
        print("Error: No experiment analyte data for this experiment. Make sure data were basketed")
        sys.exit()

    try:
        with open(os.path.join(input_structure.output_directory, input_type, input_structure.experiment_name +
                               "_experiment_analyte_mass_spectra.pickle"), "rb") as mass_pickle:
            experiment_mass_data = pickle.load(mass_pickle)
    except FileNotFoundError as fnf_error:
        print(fnf_error)
        print("Error: No experiment analyte mass spectra for this experiment. Make sure data were basketed")
        sys.exit()

    # Convert experiment mass data into dict

    experiment_analyte_mass_dict = {}
    experiment_analyte_is_blank = {}
    for experiment_analyte_spectrum in experiment_mass_data:
        experiment_analyte_mass_dict[experiment_analyte_spectrum.experiment_analyte_id] \
            = experiment_analyte_spectrum.relative_experiment_mass_spectrum
        experiment_analyte_is_blank[experiment_analyte_spectrum.experiment_analyte_id] = \
            experiment_analyte_spectrum.experiment_analyte_is_blank

    # Create dict for mass data from each sample

    sample_mass_data = {}

    for sample in sample_list:
        with open(os.path.join(input_structure.output_directory, input_type, sample +
                               "_replicate_analyte_mass_spectra.pickle"), "rb") as g:
            input_data = pickle.load(g)
            sample_mass_data[sample] = input_data

    headers = [["experiment_analyte_id", "experiment_analyte_max_mass", "experiment_analyte_count", "sample_name",
                "sample_analyte_id", "sample_analyte_max_intensity", "sample_analyte_rt", "experiment_analyte_is_blank"]]

    output_data = []

    for experiment_analyte in experiment_analytes:
        experiment_analyte_mass_spectrum = experiment_analyte_mass_dict[experiment_analyte.experiment_analyte_id]
        # NOTE: method below is a poor way to assign max mass- will provide max 13C peak of max signal rather than the
        # all 12C mass
        experiment_analyte_max_mass = 0
        for mass_peak in experiment_analyte_mass_spectrum:
            if mass_peak.relative_intensity > experiment_analyte_max_mass:
                experiment_analyte_max_mass = mass_peak.average_mass
        experiment_analyte_count = len(experiment_analyte.experiment_analyte_members)
        for replicate_analyte in experiment_analyte.experiment_analyte_members:
            replicate_analyte_max_intensity = None
            replicate_analyte_rt = None
            for replicate_analyte_mass_data in sample_mass_data[replicate_analyte.sample_name]:
                if replicate_analyte_mass_data.replicate_analyte_id == replicate_analyte.replicate_analyte_id:
                    replicate_analyte_max_intensity = replicate_analyte_mass_data.max_intensity
                    replicate_analyte_rt = replicate_analyte_mass_data.replicate_analyte_rt

            output_data.append([experiment_analyte.experiment_analyte_id,
                                experiment_analyte_max_mass,
                                experiment_analyte_count,
                                replicate_analyte.sample_name,
                                replicate_analyte.replicate_analyte_id,
                                replicate_analyte_max_intensity,
                                replicate_analyte_rt,
                                experiment_analyte_is_blank[experiment_analyte.experiment_analyte_id]])

    output_filename = os.path.join(input_structure.output_directory, input_structure.experiment_name +
                                   "_experiment_analyte_overview_tableau_output.csv")

    with open(output_filename, "w") as h:
        csv_h = csv.writer(h)
        csv_h.writerows(headers + output_data)
