#!/usr/bin/env python3

"""tools for reviewing analyte and sample level output data from MS2Analyte"""


import os
import pickle
import csv
import pandas as pd

from ms2analyte.file_handling import data_import


def experiment_analyte_sample_review(file_path, experiment_name, input_type):
    """Print a list of all samples and their associated sample analyte ids and experiment analyte ids. Length of this
    list tells you how many analytes were found in this sample. Dict tells you what the corresponding experiment
    analyte id is for each sample analyte

    """
    with open(os.path.join(file_path, experiment_name + "_experiment_analyte_sample_list_" + input_type + ".pickle"),
              "rb") as f:
        input_data = pickle.load(f)

    print(len(input_data))
    for experiment in input_data:
        print(experiment.sample_name)
        print(experiment.sample_id_to_experiment_id)


def experiment_analyte_mass_spectra_review(file_path, input_type, experiment_name):
    """Print summary of peaks in averaged mass spectra for each experiment analyte"""
    with open(os.path.join(file_path, input_type, experiment_name + "_experiment_analyte_mass_spectra.pickle"), "rb") \
            as f:
        input_data = pickle.load(f)

    print(len(input_data))
    for experiment_analyte in input_data:
        print(experiment_analyte.experiment_analyte_id)
        for mass_peak in experiment_analyte.relative_experiment_mass_spectrum:
            print(mass_peak.average_mass)
            print(mass_peak.relative_intensity)
            print(mass_peak.contributing_peak_list)


def sample_analyte_review(file_path, input_type, sample_name):
    """Print all available data for each sample analyte in a given sample. Requires full sample name including
    replicate suffix

    """
    with open(os.path.join(file_path, input_type, sample_name + "_analytes.pickle"), "rb") as f:
        sample_analytes = pickle.load(f)

    print("Sample analyte data for " + sample_name)
    for analyte in sample_analytes:
        print("Analyte_id: " + str(analyte.analyte_id))
        print("Peak list: " + str(analyte.peak_list))
        print("Max peak id: " + str(analyte.max_peak_id))
        print("max peak intensity mass: " + str(analyte. max_peak_intensity_mass))
        print("Max peak intensity: " + str(analyte.max_peak_intensity))
        print("Analyte rt: " + str(analyte.analyte_rt))
        print("Replicate match: " + str(analyte.replicate_match))
        print("Replicate analyte id: " + str(analyte.replicate_analyte_id))
        print("Experiment match: " + str(analyte.experiment_match))
        print("Experiment analyte id: " + str(analyte.experiment_analyte_id))
        print("Blank match: " + str(analyte.blank_match))


def experiment_analyte_mass_spectra_csv(file_path, input_type, experiment_name):
    """Write summary of peaks for each experiment analyte mass spectrum to csv file"""
    with open(os.path.join(file_path, input_type, experiment_name + "_experiment_analyte_mass_spectra.pickle"), "rb") \
            as f:
        input_data = pickle.load(f)

    headers = [["experiment_analyte_id", "average_mass", "relative_intensity", "contributing_replicate",
               "contributing_replicate_sample_id"]]
    export_data = []

    for experiment_analyte in input_data:
        experiment_analyte_id = experiment_analyte.experiment_analyte_id
        for mass_peak in experiment_analyte.relative_experiment_mass_spectrum:
            average_mass = mass_peak.average_mass
            relative_intensity = mass_peak.relative_intensity
            for contributing_peak in mass_peak.contributing_peak_list:
                contributing_replicate = contributing_peak[0]
                contributing_replicate_sample_id = contributing_peak[1]
                export_data.append([experiment_analyte_id, average_mass, relative_intensity, contributing_replicate,
                                    contributing_replicate_sample_id])

    with open(os.path.join(file_path, input_type, experiment_name + "_experiment_analyte_mass_spectra.csv"), "w") as g:
        csv_g = csv.writer(g)
        csv_g.writerows(headers + export_data)


def experiment_analyte_review(file_path, input_type, experiment_name):
    """Print list of all experiment analyte ids and a list of the samples that contribute to each one, the replicate
    analyte id in each case, and the replicates and analyte ids from each replicate that contribute to each experiment
    analyte. This allows you to see which experiment analytes exist, which samples contain this analyte, and which
    replicates from each sample contribute to this analyte

    """
    with open(os.path.join(file_path, input_type, experiment_name + "_experiment_analyte_list.pickle"), "rb") as f:
        input_data = pickle.load(f)

    print("Experiment analyte list")
    print(input_data)

    for experiment in input_data:
        print(experiment)


def sample_mass_spectra_review(file_path, input_type, sample_name):
    """Print list of summary data for the mass spectrum for each sample analyte"""
    with open(os.path.join(file_path, input_type, sample_name + "_replicate_analyte_mass_spectra.pickle"), "rb") as f:
        input_data = pickle.load(f)

    for sample in input_data:
        print(sample.replicate_analyte_id)
        print(sample.max_intensity)
        print(sample.replicate_analyte_rt)


def replicate_peak_analyte_id_df(input_data_structure):
    """Create dataframe containing key information on every peak in every replicate that is part of an experiment
    analyte

    """

    # Create list of all sample names

    sample_name_list = data_import.name_extract(input_data_structure, "Samples")

    # Create empty dataframe to contain data for every mass peak found in every sample

    headers = ["sample_name", "replicate", "peak_id", "peak_rt", "peak_average_mz", "analyte_id", "analyte_rt",
               "analyte_blank_match", "replicate_analyte_id", "experiment_analyte_id"]
    all_analyte_data = pd.DataFrame(columns=headers)

    # Parse over all peaks in all samples, and add to df

    for sample in sample_name_list:
        for i in range(1, input_data_structure.replicate_count + 1, 1):
            sample_replicate_name = sample + "_R" + str(i)
            print("Starting " + sample_replicate_name)

            # Import full peak list after initial massbin step

            with open(os.path.join(input_data_structure.output_directory, "Samples", sample_replicate_name +
                                   "_massbin_tableau_output.csv")) as g:
                massbin_data = pd.read_csv(g)

            # Import full dataframe after sample processing step (end of sample_process.py)

            with open(os.path.join(input_data_structure.output_directory, "Samples", sample_replicate_name +
                                   "_dataframe.pickle"), "rb") as h:
                full_sample_data = pickle.load(h)

            # Create list of all peak ids present in full_sample_data

            full_sample_peak_ids = pd.unique(full_sample_data["peak_id"])

            # Examine every peak in massbin data. If not in full_sample_peak_ids then must have been dropped in peak
            # processing steps (probably in the isotope_filter step). Insert into full peak list in order to capture
            # all peaks for comparison to external peak lists

            print("Starting massbin insert")

            for peak, data in massbin_data.groupby("peak_id"):
                if peak not in full_sample_peak_ids:
                    peak_average_mz = round(data["mz"].mean(), 4)
                    peak_rt = round(data["rt"].mean(), 2)
                    all_analyte_data = all_analyte_data.append({"sample_name": sample, "replicate": i, "peak_id": peak,
                                                                "peak_rt": peak_rt, "peak_average_mz": peak_average_mz},
                                                               ignore_index=True)

            # Insert every peak that is associated with an analyte for each sample

            print("Starting analyte peaks insert")

            for peak, data in full_sample_data.groupby("peak_id"):
                peak_average_mz = round(data["mz"].mean(), 4)
                peak_rt = round(data["rt"].mean(), 2)
                all_analyte_data = all_analyte_data.append({"sample_name": sample, "replicate": i, "peak_id": peak,
                                                            "peak_rt": peak_rt, "peak_average_mz": peak_average_mz,
                                                            "analyte_id": pd.unique(data["analyte_id"])[0]},
                                                           ignore_index=True)

            # Import all analyte objects for this sample and replicate

            with open(os.path.join(input_data_structure.output_directory, "Samples", sample_replicate_name +
                                   "_analytes.pickle"), "rb") as k:
                analyte_data = pickle.load(k)

            # Insert additional missing data (i.e. replicate_analyte_id, experiment_analyte_id, blank_match etc)
            # for each peak

            print("Starting insert of replicate analyte ids and experiemnt analyte ids")

            for analyte in analyte_data:
                all_analyte_data.loc[(all_analyte_data["sample_name"] == sample) &
                                     (all_analyte_data["replicate"] == i) &
                                     (all_analyte_data["analyte_id"] == analyte.analyte_id), "replicate_analyte_id"]\
                    = analyte.replicate_analyte_id
                all_analyte_data.loc[(all_analyte_data["sample_name"] == sample) &
                                     (all_analyte_data["replicate"] == i) &
                                     (all_analyte_data["analyte_id"] == analyte.analyte_id), "analyte_rt"]\
                    = analyte.analyte_rt
                all_analyte_data.loc[(all_analyte_data["sample_name"] == sample) &
                                     (all_analyte_data["replicate"] == i) &
                                     (all_analyte_data["analyte_id"] == analyte.analyte_id), "analyte_blank_match"]\
                    = analyte.blank_match
                all_analyte_data.loc[(all_analyte_data["sample_name"] == sample) &
                                     (all_analyte_data["replicate"] == i) &
                                     (all_analyte_data["analyte_id"] == analyte.analyte_id), "experiment_analyte_id"]\
                    = analyte.experiment_analyte_id

    with open(os.path.join(input_data_structure.output_directory, input_data_structure.experiment_name +
                           "_full_peak_list_dataframe.pickle"), "wb") as n:
        pickle.dump(all_analyte_data, n)

    with open(os.path.join(input_data_structure.output_directory, input_data_structure.experiment_name +
                           "_full_peak_list_dataframe.csv"), "w") as m:
        all_analyte_data.to_csv(m, index=False, header=True)
