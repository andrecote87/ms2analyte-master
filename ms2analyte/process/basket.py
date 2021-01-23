#!/usr/bin/env python3

"""Tools to basket replicate_analytes from replicate_compare.py"""

import os
import pickle
from operator import attrgetter

from ms2analyte.calculate import rt_features, analyte_match, mass_features
from ms2analyte.file_handling import file_load
from ms2analyte.output import tableau
import ms2analyte.config as config


class ExperimentAnalyte:
    """Class for experiment analytes (i.e. an analyte found across a set of samples)"""
    def __init__(self, experiment_analyte_id, experiment_analyte_members, rt, experiment_analyte_spectrum):
        self.experiment_analyte_id = experiment_analyte_id
        self.experiment_analyte_members = experiment_analyte_members
        self.rt = rt
        self.experiment_analyte_spectrum = experiment_analyte_spectrum  # [ExperimentAnalyteMassPeak list]
        self.experiment_analyte_is_blank = False


class ExperimentAnalyteMassPeak:
    """Class for mass peaks for each experiment analyte (i.e. average relative intensities and masses)"""
    def __init__(self, average_mass, relative_intensity, contributing_peak_list):
        self.average_mass = average_mass
        self.relative_intensity = relative_intensity
        self.contributing_peak_list = contributing_peak_list    # (sample_name, replicatemasspeak)


class SampleExperimentId:
    """Class that defines the experiment analyte ids for each sample by sample analyte id. Used in
    input_data_sample_annotate

    """
    def __init__(self, sample_name, replicate_analyte_id_to_experiment_id):
        self.sample_name = sample_name
        self.replicate_analyte_id_to_experiment_id = replicate_analyte_id_to_experiment_id


class ExperimentAnalyteSpectrum:
    """Class for relative intensity spectra for experiment analyte id (averaged from all contributing sample analytes
    in that experiment analyte

    """
    def __init__(self, experiment_analyte_id, relative_experiment_mass_spectrum, experiment_analyte_is_blank):
        self.experiment_analyte_id = experiment_analyte_id
        self.relative_experiment_mass_spectrum = relative_experiment_mass_spectrum  # [ExperimentMassPeak list]
        self.experiment_analyte_is_blank = experiment_analyte_is_blank


def sample_set_basket(input_structure, input_type, sample_name_list):
    """Compare replicate analytes from each sample in experiment, identify all unique analytes found in experiment set,
    and determine distribution of these analytes across sample set. Return a list of ExperimentAnalytes

    """
    print("Starting sample set basketing")

    experiment_analyte_id = 1
    experiment_analytes = []

    # Import the replicate analyte mass spectra for each sample in the experiment

    sample_mass_spectra = []

    for sample_name in sample_name_list:
        with open((os.path.join(input_structure.output_directory, input_type,
                                sample_name + "_replicate_analyte_mass_spectra.pickle")), "rb") as pickle_file:
            sample_replicate_analytes = pickle.load(pickle_file)

        sample_mass_spectra.append([sample_name, sorted(sample_replicate_analytes, key=attrgetter("max_intensity"),
                                                    reverse=True)])

    # If there is more than one sample, compare. Otherwise, assign an experiment analyte id to each replicate analyte

    if len(sample_mass_spectra) > 1:

        # Take each sample and compare the unassigned analytes in that sample against all analytes in subsequent samples
        # to create new sample analytes, and assign experiment analyte ids
        # Note that a different strategy is required for the last sample in the list (see below)

        for index, sample in enumerate(sample_mass_spectra[:-1]):
            for sample_replicate_analyte in sample[1]:
                if not sample_replicate_analyte.is_basketed:
                    experiment_analyte_replicate_analytes = [sample_replicate_analyte]

                    # For each new sample, look for matches for replicate analyte of interest. Create new experiment
                    # analyte with all matches

                    for sample_data in sample_mass_spectra[index + 1:]:
                        for compare_replicate_analyte in sample_data[1]:
                            if not compare_replicate_analyte.is_basketed:
                                if rt_features.rt_match(sample_replicate_analyte.replicate_analyte_rt,
                                                        compare_replicate_analyte.replicate_analyte_rt):
                                    if analyte_match.relative_intensity_match(sample_replicate_analyte.replicate_analyte_spectrum,
                                                                          compare_replicate_analyte.replicate_analyte_spectrum):
                                        compare_replicate_analyte.is_basketed = True
                                        experiment_analyte_replicate_analytes.append(compare_replicate_analyte)
                                        break

                    experiment_analytes.append(create_experiment_analyte(experiment_analyte_id,
                                                                         experiment_analyte_replicate_analytes))
                    experiment_analyte_id += 1

        # For the last sample in the list, add each unassigned replicate analyte as a new experiment analyte

        for sample_replicate_analyte in sample_mass_spectra[-1][1]:
            if not sample_replicate_analyte.is_basketed:
                sample_replicate_analyte.is_basketed = True
                experiment_analytes.append(create_experiment_analyte(experiment_analyte_id,
                                                                     [sample_replicate_analyte]))
                experiment_analyte_id += 1

    # If there is only one sample in the experiment then there will be no basketing, so add all analytes

    elif len(sample_mass_spectra) == 1:
        for sample_replicate_analyte in sample_mass_spectra[0][1]:
            sample_replicate_analyte.is_basketed = True
            experiment_analytes.append(create_experiment_analyte(experiment_analyte_id,
                                                                 [sample_replicate_analyte]))
            experiment_analyte_id += 1

    else:
        print("ERROR: No sample analyte data provided. Basketing failed")

    with open((os.path.join(input_structure.output_directory, input_type, input_structure.experiment_name +
                            "_experiment_analytes.pickle")), "wb") as pickle_file:
        pickle.dump(experiment_analytes, pickle_file)

    print("Finished sample set basketing")


def create_experiment_analyte(experiment_analyte_id, replicate_analyte_list):
    """Tool to create experiment analytes from a set of replicate analytes. Calculates average values including
    retention times etc. """

    rt_list = []
    for replicate_analyte in replicate_analyte_list:
        rt_list.append(replicate_analyte.replicate_analyte_rt)

    experiment_analyte_mass_spectrum = create_experiment_analyte_mass_spectrum(replicate_analyte_list)

    return ExperimentAnalyte(experiment_analyte_id,
                             replicate_analyte_list,
                             rt_features.average_rt(rt_list),
                             experiment_analyte_mass_spectrum)


def create_experiment_analyte_mass_spectrum(replicate_analyte_list):
    """Create averaged mass spectrum for experiment analyte. Currently this retains all mass peaks that appear at least
    n times, and takes the average relative intensity for all the cases where it appears. Be careful about setting n
    greater than 1, as this can remove all peaks for analytes that only appear once in the experiment.

    """

    experiment_analyte_mass_spectrum = []
    for replicate_analyte in replicate_analyte_list:
        for replicate_mass_peak in replicate_analyte.replicate_analyte_spectrum:
            peak_match = False
            for experiment_mass_peak in experiment_analyte_mass_spectrum:
                if mass_features.mass_match(replicate_mass_peak.average_mass, experiment_mass_peak.average_mass):
                    experiment_mass_peak.contributing_peak_list.append((replicate_analyte.sample_name,
                                                                        replicate_mass_peak))
                    new_average_mass = experiment_mass_peak.average_mass + \
                                       (replicate_mass_peak.average_mass - experiment_mass_peak.average_mass)/\
                                       len(experiment_mass_peak.contributing_peak_list)
                    experiment_mass_peak.average_mass = new_average_mass
                    new_relative_intensity = experiment_mass_peak.relative_intensity + \
                                       (replicate_mass_peak.relative_intensity -
                                        experiment_mass_peak.relative_intensity)/\
                                       len(experiment_mass_peak.contributing_peak_list)
                    experiment_mass_peak.relative_intensity = new_relative_intensity
                    peak_match = True
                    break
            if not peak_match:
                experiment_analyte_mass_spectrum.append(ExperimentAnalyteMassPeak(replicate_mass_peak.average_mass,
                                                                                  replicate_mass_peak.relative_intensity,
                                                                                  [(replicate_analyte.sample_name,
                                                                                    replicate_mass_peak)]))

    # scan experiment_analyte_mass_spectrum and only retain peaks that appear at least the minimum number of times
    final_experiment_analyte_mass_spectrum = []
    for peak in experiment_analyte_mass_spectrum:
        if len(peak.contributing_peak_list) >= config.minimum_experiment_analyte_mass_peak_count:
            final_experiment_analyte_mass_spectrum.append(peak)

    return final_experiment_analyte_mass_spectrum


def create_experiment_analyte_spectra(input_structure, input_type, sample_name_list, experiment_analyte_sample_list):
    """Create averaged mass spectra for each experiment analyte. NOTE: Not complete"""

    experiment_analyte_spectra = []

    with open((os.path.join(input_structure.output_directory, input_type, input_structure.experiment_name +
                            "_experiment_analytes.pickle")), "rb") as pickle_file:
        experiment_analytes = pickle.load(pickle_file)

    for experiment_analyte in experiment_analytes:

        # Check that the max peak is 100% and, if not, fix.

        max_relative_intensity = 0

        for replicate_mass_peak in experiment_analyte.experiment_analyte_spectrum:
            if replicate_mass_peak.relative_intensity > max_relative_intensity:
                max_relative_intensity = replicate_mass_peak.relative_intensity

        if max_relative_intensity != 100:
            for replicate_mass_peak in experiment_analyte.experiment_analyte_spectrum:
                replicate_mass_peak.relative_intensity = round((replicate_mass_peak.relative_intensity /
                                                                max_relative_intensity) * 100, 1)

        experiment_analyte_spectra.append(ExperimentAnalyteSpectrum(experiment_analyte.experiment_analyte_id,
                                                                    experiment_analyte.experiment_analyte_spectrum,
                                                                    False))

    with open((os.path.join(input_structure.output_directory, input_type, input_structure.experiment_name +
                            "_experiment_analyte_mass_spectra.pickle")), "wb") as pickle_file:
        pickle.dump(experiment_analyte_spectra, pickle_file)


def experiment_analyte_sample_analyte_dict(input_structure, input_type):
    """Create dictionary that connects experiment analyte ids to the replicate analyte ids for each sample"""

    # First load list of replicate analyte ids, and the experiment analyte ids these refer to

    with open((os.path.join(input_structure.output_directory, input_type, input_structure.experiment_name +
                            "_experiment_analytes.pickle")), "rb") as pickle_file:
        experiment_analytes = pickle.load(pickle_file)

    # Resort these data so that you have a dict of replicate analyte id to experiment analyte id for each sample

    experiment_analyte_sample_list = []

    for experiment_analyte in experiment_analytes:
        for replicate_analyte in experiment_analyte.experiment_analyte_members:
            if len(experiment_analyte_sample_list) > 0:
                sample_match = False
                for entry in experiment_analyte_sample_list:
                    if entry.sample_name == replicate_analyte.sample_name:
                        entry.replicate_analyte_id_to_experiment_id[replicate_analyte.replicate_analyte_id] = \
                            experiment_analyte.experiment_analyte_id
                        sample_match = True
                        break
                if not sample_match:
                    experiment_analyte_sample_list.append(
                        SampleExperimentId(replicate_analyte.sample_name,
                                           {replicate_analyte.replicate_analyte_id:
                                            experiment_analyte.experiment_analyte_id}))
            else:
                experiment_analyte_sample_list.append(SampleExperimentId(replicate_analyte.sample_name,
                                                                         {replicate_analyte.replicate_analyte_id:
                                                                          experiment_analyte.experiment_analyte_id}))

    with open((os.path.join(input_structure.output_directory, input_structure.experiment_name +
                            "_experiment_analyte_sample_list_" + input_type + ".pickle")), "wb") as pickle_file:
        pickle.dump(experiment_analyte_sample_list, pickle_file)

    return experiment_analyte_sample_list


def input_data_sample_annotate(input_structure, input_type, sample_list, experiment_analyte_sample_list):
    """Annotate sample analyte id numbers to original input dataframe. First create concatenated dataframe for all
    replicates from a sample and then append experiment analyte ids to each replicate analyte id

    """
    for sample_name in sample_list:
        sample_dataframe = file_load.sample_dataframe_concat(input_structure, input_type, sample_name)

        if input_type == "Samples":
            if "experiment_analyte_id" not in sample_dataframe.columns:
                sample_dataframe["experiment_analyte_id"] = None
        elif input_type == "Blanks":
            if "experiment_blank_id" not in sample_dataframe.columns:
                sample_dataframe["experiment_blank_id"] = None

        sample_to_experiment_id_dict = {}
        sample_analyte_id_list = []

        for sample_data in experiment_analyte_sample_list:
            if sample_data.sample_name == sample_name:
                sample_to_experiment_id_dict = sample_data.replicate_analyte_id_to_experiment_id
                break

        for sample_analyte_id in sample_to_experiment_id_dict:
            sample_analyte_id_list.append(sample_analyte_id)

        if input_type == "Samples":
            for sample_analyte_id in sample_analyte_id_list:
                sample_dataframe.loc[sample_dataframe.replicate_analyte_id == sample_analyte_id,
                                     "experiment_analyte_id"] = sample_to_experiment_id_dict[sample_analyte_id]
        elif input_type == "Blanks":
            for sample_analyte_id in sample_analyte_id_list:
                sample_dataframe.loc[sample_dataframe.replicate_analyte_id == sample_analyte_id, "experiment_blank_id"]\
                    = sample_to_experiment_id_dict[sample_analyte_id]

        with open((os.path.join(input_structure.output_directory, input_type, sample_name
                                + "_all_replicates_dataframe.pickle")), "wb") as pickle_file:
            pickle.dump(sample_dataframe, pickle_file)

        tableau.experiment_analyte_export(input_structure, input_type, sample_name)


def analyte_update_experiment_analyte_data(input_structure, input_type, sample_names):
    """Update analyte objects (analyte_create.Analyte) with experiment_analyte_id + experiment_match"""

    # Import experiment analyte list

    with open((os.path.join(input_structure.output_directory, input_type, input_structure.experiment_name +
                            "_experiment_analytes.pickle")), "rb") as f:
        experiment_analytes = pickle.load(f)

    # Create dict providing experiment analyte id for each analyte from each replicate.

    sample_analyte_id_names = []
    sample_analyte_id_dict = {}

    for experiment_analyte in experiment_analytes:
        for replicate_analyte in experiment_analyte.experiment_analyte_members:
            for replicate in replicate_analyte.analyte_list:
                sample_analyte_id_name = replicate_analyte.sample_name + "_R" + str(replicate[0]) + "_" + \
                                         str(replicate[1])
                sample_analyte_id_names.append(sample_analyte_id_name)
                sample_analyte_id_dict[sample_analyte_id_name] = experiment_analyte.experiment_analyte_id

    # Open each list of analytes from a particular replicate. If that analyte has an experiment analyte id, add, and
    # update experiment_match

    for sample_name in sample_names:
        for i in range(1, input_structure.replicate_count + 1, 1):
            with open((os.path.join(input_structure.output_directory, input_type, sample_name + "_R"
                                    + str(i) + "_analytes.pickle")), "rb") as g:
                analyte_data = pickle.load(g)

            for analyte in analyte_data:
                analyte_id_name = sample_name + "_R" + str(i) + "_" + str(analyte.analyte_id)
                if analyte_id_name in sample_analyte_id_names:
                    analyte.experiment_analyte_id = sample_analyte_id_dict[analyte_id_name]
                    analyte.experiment_match = True

            with open((os.path.join(input_structure.output_directory, input_type, sample_name + "_R"
                                    + str(i) + "_analytes.pickle")), "wb") as h:
                pickle.dump(analyte_data, h)
