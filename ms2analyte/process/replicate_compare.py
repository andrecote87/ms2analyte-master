#!/usr/bin/env python3

"""Tools to replicate compare analytes from analyte_create.py"""

import os
import pickle
from operator import attrgetter

from ms2analyte.calculate import analyte_match
from ms2analyte.file_handling import data_import, file_load
from ms2analyte.output import tableau
import ms2analyte.config as config


class ReplicateMaxMassData:
    """Class containing all mass data from maximum intensity scan for one analyte from one replicate"""
    def __init__(self, replicate_number, sample_name, max_scan, max_intensity, normalized_mass_data):
        self.replicate_number = replicate_number
        self.sample_name = sample_name
        self.max_scan = max_scan
        self.max_intensity = max_intensity
        self.normalized_mass_data = normalized_mass_data


class ReplicateMassPeak:
    """Class containing data about each mass peak in a replicate analyte"""
    def __init__(self, mass_peak_data, average_mass, average_intensity, relative_intensity):
        self.mass_peak_data = mass_peak_data    # [[mz, intensity, replicate number]]
        self.average_mass = average_mass
        self.average_intensity = average_intensity
        self.relative_intensity = relative_intensity


class ReplicateAnalyte:
    """Class containing data on analyte ids for each assigned replicate analyte (i.e. analytes that pass replicate
    comparison)

    """
    def __init__(self, replicate_analyte_id, analyte_list, max_peak_intensity_mass, max_intensity, replicate_analyte_rt,
                 replicate_analyte_spectrum, sample_name, is_basketed):
        self.replicate_analyte_id = replicate_analyte_id
        self.analyte_list = analyte_list                                # [[replicate, analyte id]]
        self.max_peak_intensity_mass = max_peak_intensity_mass
        self.max_intensity = max_intensity
        self.replicate_analyte_rt = replicate_analyte_rt
        self.replicate_analyte_spectrum = replicate_analyte_spectrum    # [ReplicateMassPeak list]
        self.sample_name = sample_name
        self.is_basketed = is_basketed   # This is used in basketing step to remove matched analytes from available pool


def sample_consensus_analytes(input_structure, input_type):
    """Open sample files for all sample replicates, find consensus analytes and write to consensus list"""
    sample_name_list = data_import.name_extract(input_structure, input_type)

    # For each sample, import the analyte objects for each replicate
    for sample_name in sample_name_list:
        replicate_analyte_id = 1
        sample_replicate_data = []
        for i in range(1, input_structure.replicate_count + 1):
            with open((os.path.join(input_structure.output_directory, input_type, sample_name + "_R"
                                    + str(i) + "_analytes.pickle")), "rb") as pickle_file:
                replicate_data = pickle.load(pickle_file)
            sample_replicate_data.append(sorted(replicate_data, key=attrgetter("max_peak_intensity"), reverse=True))

        # For each replicate, look all analytes and, for those not assigned to replicate analytes, look at subsequent
        # replicates for matches. Append replicate_analyte_ids to all matching replicate analytes
        for j, sample_replicate in enumerate(sample_replicate_data[:-1]):
            for analyte in sample_replicate:
                if not analyte.replicate_match:
                    for compare_replicate in sample_replicate_data[j + 1:]:
                        for compare_analyte in compare_replicate:
                            if not compare_analyte.replicate_match:
                                if analyte_match.max_peak_match(analyte, compare_analyte) \
                                        and analyte_match.rt_match(analyte, compare_analyte):
                                    if analyte_match.bidirectional_match(analyte, compare_analyte):
                                        analyte.replicate_match = True
                                        analyte.replicate_analyte_id = replicate_analyte_id
                                        compare_analyte.replicate_match = True
                                        compare_analyte.replicate_analyte_id = replicate_analyte_id
                    if analyte.replicate_match:
                        replicate_analyte_id += 1

        print("Finished sample " + sample_name + " Number of replicate analytes = " + str(replicate_analyte_id))

        for index, replicate_analytes in enumerate(sample_replicate_data):
            input_data_replicate_annotate(input_structure, input_type, sample_name, index + 1, replicate_analytes)

        tableau.replicate_analyte_export(input_structure, input_type, sample_name)

        replicate_analyte_objects(input_structure, input_type, sample_name)


def sample_consensus_analytes_no_replicates(input_structure, input_type):
    """Create required output files from replicate comparison stage if there is only a single replicate"""
    sample_name_list = data_import.name_extract(input_structure, input_type)

    # For each sample, import the analyte objects for each replicate
    for sample_name in sample_name_list:
        with open((os.path.join(input_structure.output_directory, input_type, sample_name + "_R1_analytes.pickle")),
                  "rb") as pickle_file:
            replicate_data = pickle.load(pickle_file)
        sample_replicate_data = sorted(replicate_data, key=attrgetter("max_peak_intensity"), reverse=True)

        for analyte in sample_replicate_data:
            analyte.replicate_match = True
            analyte.replicate_analyte_id = analyte.analyte_id

        input_data_replicate_annotate(input_structure, input_type, sample_name, 1, sample_replicate_data)

        tableau.replicate_analyte_export(input_structure, input_type, sample_name)

        replicate_analyte_objects(input_structure, input_type, sample_name)


def input_data_replicate_annotate(input_structure, input_type, sample_name, replicate_number, analyte_list):
    """Add replicate analyte id and replicate number to main dataframe"""
    with open((os.path.join(input_structure.output_directory, input_type, sample_name + "_R" + str(replicate_number)
              + "_dataframe.pickle")), "rb") as pickle_file:
        input_data = pickle.load(pickle_file)

    if "replicate_analyte_id" not in input_data.columns:
        input_data["replicate_analyte_id"] = None

    if "replicate" not in input_data.columns:
        input_data["replicate"] = replicate_number

    for analyte in analyte_list:
        input_data.loc[input_data.analyte_id == analyte.analyte_id, "replicate_analyte_id"] = \
            analyte.replicate_analyte_id

    with open((os.path.join(input_structure.output_directory, input_type, sample_name + "_R" + str(replicate_number)
              + "_dataframe.pickle")), "wb") as pickle_file:
        pickle.dump(input_data, pickle_file)


def replicate_analyte_objects(input_structure, input_type, sample_name):
    """Create replicate analyte objects containing consensus mass spectrum from sample_consensus_analytes data.
    Can only be run after input_data_replicate_annotate.

    """

    # Load dataframes for all replicates for a sample, and concatenate into one dataframe
    sample_input_data = file_load.sample_dataframe_concat(input_structure, input_type, sample_name)

    sample_replicate_data = []

    # For each replicate analyte, find mass features from max intensity scan from each replicate, then determine
    # the relative activities (100%) for each replicate, and determine average values for each peak.
    for replicate_analyte_id, replicate_analyte_data in sample_input_data.groupby("replicate_analyte_id"):

        replicate_max_mass_data = []
        analyte_list = []
        rt_list = []

        # Find scan for maximum intensity peak, and create list of all mass features in that scan for each replicate
        for replicate, analyte_data in replicate_analyte_data.groupby("replicate"):
            max_scan = analyte_data[analyte_data["intensity"] == analyte_data["intensity"].max()].iloc[0]["scan"]
            max_intensity = analyte_data["intensity"].max()
            insert_data = []
            for index, row in analyte_data[analyte_data.scan == max_scan].iterrows():
                insert_data.append([round(row["mz"], 4), row["intensity"]])
            replicate_max_mass_data.append(ReplicateMaxMassData(replicate, sample_name, max_scan, max_intensity,
                                                                insert_data))
            analyte_list.append([replicate, int(analyte_data["analyte_id"].max())])
            rt_list.append(analyte_data["rt"].max())

        # Calculate relative intensity of each mass peak within each replicate
        for replicate_data in replicate_max_mass_data:
            for mass_data in replicate_data.normalized_mass_data:
                percent_intensity = round((mass_data[1]/replicate_data.max_intensity) * 100, 2)
                mass_data.append(percent_intensity)

        # Align mass peaks between replicates
        # replicate_mass_peak_list is [[data for each peak as [mz, intensity, relative percentage, replicate number]]]
        replicate_mass_peak_list = []

        for replicate_data in replicate_max_mass_data:
            for mass_peak in replicate_data.normalized_mass_data:
                mass_match_difference = 1000
                mass_match_index = None
                for index, replicate_mass_peak in enumerate(replicate_mass_peak_list):
                    mass_difference = abs(mass_peak[0] - replicate_mass_peak[0][0])
                    if mass_difference < mass_match_difference:
                        mass_match_difference = mass_difference
                        mass_match_index = index
                if mass_match_difference <= config.mass_error_da:
                    mass_peak.append(replicate_data.replicate_number)
                    replicate_mass_peak_list[mass_match_index].append(mass_peak)
                else:
                    mass_peak.append(replicate_data.replicate_number)
                    replicate_mass_peak_list.append([mass_peak])

        # If experiment has replicates, calculate average intensity of mass peaks for masses that appear at least twice.
        if input_structure.replicate_count > 1:
            replicate_mass_peak_data = []
            for mass_peak_list in replicate_mass_peak_list:
                intensity_list = []
                if len(mass_peak_list) > 1:
                    sum_mass = 0
                    sum_relative_intensity = 0
                    for mass_peak in mass_peak_list:
                        intensity_list.append(mass_peak[1])
                        sum_mass += mass_peak[0]
                        sum_relative_intensity += mass_peak[2]
                    average_mass = round(sum_mass/len(mass_peak_list), 4)
                    average_intensity = int(sum(intensity_list)/len(intensity_list))
                    average_relative_intensity = round(sum_relative_intensity/len(mass_peak_list), 1)
                    replicate_mass_peak_data.append(ReplicateMassPeak(mass_peak_list, average_mass, average_intensity,
                                                                      average_relative_intensity))
        else:
            replicate_mass_peak_data = []
            for mass_peak_list in replicate_mass_peak_list:
                average_mass = mass_peak_list[0][0]
                average_intensity = mass_peak_list[0][1]
                average_relative_intensity = mass_peak_list[0][2]
                replicate_mass_peak_data.append(ReplicateMassPeak(mass_peak_list, average_mass, average_intensity,
                                                                  average_relative_intensity))

        # Check that the max peak is 100% and, if not, fix.
        max_average_relative_intensity = 0
        max_intensity_mass = 0
        max_intensity = 0

        for replicate_mass_peak in replicate_mass_peak_data:
            if replicate_mass_peak.average_intensity > max_intensity:
                max_intensity = replicate_mass_peak.average_intensity
            if replicate_mass_peak.relative_intensity > max_average_relative_intensity:
                max_average_relative_intensity = replicate_mass_peak.relative_intensity
                max_intensity_mass = replicate_mass_peak.average_mass

        if max_average_relative_intensity != 100:
            for replicate_mass_peak in replicate_mass_peak_data:
                replicate_mass_peak.relative_intensity = round((replicate_mass_peak.relative_intensity /
                                                                max_average_relative_intensity) * 100, 1)

        replicate_analyte_rt = round(sum(rt_list)/len(rt_list), 2)

        sample_replicate_data.append(ReplicateAnalyte(replicate_analyte_id, analyte_list, max_intensity_mass,
                                                      max_intensity, replicate_analyte_rt, replicate_mass_peak_data,
                                                      sample_name, False))

    with open((os.path.join(input_structure.output_directory, input_type,
                            sample_name + "_replicate_analyte_mass_spectra.pickle")), "wb") as pickle_file:
        pickle.dump(sample_replicate_data, pickle_file)

    print("Finished creating mass spectra for replicated analytes for " + sample_name)


def analyte_update_replicate_analyte_data(input_structure, input_type, sample_names):
    """Update analyte objects (analyte_create.Analyte) with replicate_analyte_id + replicate_match"""
    for sample_name in sample_names:

        # import replicate_analytes
        with open((os.path.join(input_structure.output_directory, input_type,
                                sample_name + "_replicate_analyte_mass_spectra.pickle")), "rb") as f:
            replicate_analytes = pickle.load(f)

        sample_analyte_id_names = []
        sample_analyte_id_dict = {}

        # Reformat replicate analyte data to afford replicate analyte ids for every analyte from every replicate for
        # each sample
        for replicate_analyte in replicate_analytes:
            for analyte in replicate_analyte.analyte_list:
                sample_analyte_id_name = sample_name + "_R" + str(analyte[0]) + "_" + str(analyte[1])
                sample_analyte_id_names.append(sample_analyte_id_name)
                sample_analyte_id_dict[sample_analyte_id_name] \
                    = replicate_analyte.replicate_analyte_id

        # Open each list of analytes from a particular replicate. If that analyte has a replicate analyte id, add, and
        # update replicate_match
        for i in range(1, input_structure.replicate_count + 1, 1):
            with open((os.path.join(input_structure.output_directory, input_type, sample_name + "_R"
                                    + str(i) + "_analytes.pickle")), "rb") as g:
                analyte_data = pickle.load(g)

            for analyte in analyte_data:
                analyte_id_name = sample_name + "_R" + str(i) + "_" + str(analyte.analyte_id)
                if analyte_id_name in sample_analyte_id_names:
                    analyte.replicate_analyte_id = sample_analyte_id_dict[analyte_id_name]
                    analyte.replicate_match = True

            with open((os.path.join(input_structure.output_directory, input_type, sample_name + "_R"
                                    + str(i) + "_analytes.pickle")), "wb") as h:
                pickle.dump(analyte_data, h)
