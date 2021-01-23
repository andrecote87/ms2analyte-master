#!/usr/bin/env python3

"""Tools to annotate analytes with blank information"""

import os
import pickle
import sys

from ms2analyte.calculate import analyte_match
from ms2analyte.output import tableau


def blank_annotate(input_structure):
    """Annotate experiment analytes as blank from basketed blank analyte data"""
    with open((os.path.join(input_structure.output_directory, "Samples", input_structure.experiment_name +
                            "_experiment_analyte_mass_spectra.pickle")), "rb") as pickle_file:
        samples_spectra = pickle.load(pickle_file)

    with open((os.path.join(input_structure.output_directory, "Blanks", input_structure.experiment_name +
                            "_experiment_analyte_mass_spectra.pickle")), "rb") as pickle_file:
        blanks_spectra = pickle.load(pickle_file)

    for sample in samples_spectra:
        for blank in blanks_spectra:
            if analyte_match.relative_intensity_match(sample.relative_experiment_mass_spectrum,
                                                      blank.relative_experiment_mass_spectrum):
                sample.experiment_analyte_is_blank = True
                break

    with open((os.path.join(input_structure.output_directory, "Samples", input_structure.experiment_name +
                            "_experiment_analyte_mass_spectra.pickle")), "wb") as pickle_file:
        pickle.dump(samples_spectra, pickle_file)

    print("Finished blank annotation for mass spectra")


def input_data_blank_annotate(input_structure, input_type, sample_list):
    """Add blank annotations to original input dataframes for samples. First create concatenated dataframe for all
    replicates from a sample and then append blank annotations to each experiment analyte id

    """

    # Check that this function is being performed on sample data only

    if input_type != "Samples":
        print("ERROR: Cannot perform blank annotation on this input type. Options are 'Samples' only")
        sys.exit()

    # Load the experiment analyte mass spectra for this experiment

    with open((os.path.join(input_structure.output_directory, input_type, input_structure.experiment_name +
                            "_experiment_analyte_mass_spectra.pickle")), "rb") as pickle_file:
        experiment_mass_spectra = pickle.load(pickle_file)

    # Load each sample and annotate the experiment_analytes in each sample as blank or not

    for sample_name in sample_list:
        with open((os.path.join(input_structure.output_directory, input_type, sample_name
                                + "_all_replicates_dataframe.pickle")), "rb") as pickle_file:
            input_data = pickle.load(pickle_file)

        if "blank_analyte" not in input_data.columns:
            input_data["blank_analyte"] = None

        for experiment_mass_spectrum in experiment_mass_spectra:
            if experiment_mass_spectrum.experiment_analyte_id in input_data["experiment_analyte_id"].unique():
                input_data.loc[input_data.experiment_analyte_id == experiment_mass_spectrum.experiment_analyte_id,
                               "blank_analyte"] = experiment_mass_spectrum.experiment_analyte_is_blank

        with open((os.path.join(input_structure.output_directory, input_type, sample_name
                                + "_all_replicates_blanked_dataframe.pickle")), "wb") as pickle_file:
            pickle.dump(input_data, pickle_file)

        tableau.experiment_blank_annotation_export(input_structure, input_type, sample_name)

    print("Finished blank annotation for dataframe")


def analyte_blank_annotate(input_structure, sample_names):
    """Annotate sample analytes as blanks from experiment analyte data"""

    # Import experiment_analyte_spectrum objects

    with open((os.path.join(input_structure.output_directory, "Samples", input_structure.experiment_name +
                            "_experiment_analyte_mass_spectra.pickle")), "rb") as f:
        experiment_analyte_spectra = pickle.load(f)

    # Create list of experiment analyte ids that are annotated as blank

    blank_experiment_analytes = []

    for experiment_analyte_spectrum in experiment_analyte_spectra:
        if experiment_analyte_spectrum.experiment_analyte_is_blank:
            blank_experiment_analytes.append(experiment_analyte_spectrum.experiment_analyte_id)

    for sample_name in sample_names:
        for i in range(1, input_structure.replicate_count + 1, 1):
            with open((os.path.join(input_structure.output_directory, "Samples", sample_name + "_R"
                                    + str(i) + "_analytes.pickle")),
                      "rb") as g:
                analyte_data = pickle.load(g)

            for analyte in analyte_data:
                if analyte.experiment_analyte_id in blank_experiment_analytes:
                    analyte.blank_match = True

            with open((os.path.join(input_structure.output_directory, "Samples", sample_name + "_R"
                                    + str(i) + "_analytes.pickle")),
                      "wb") as h:
                pickle.dump(analyte_data, h)

    print("Finished blank annotation for sample analyte objects")
