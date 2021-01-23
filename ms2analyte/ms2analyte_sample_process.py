#!/usr/bin/env python3

"""
Processing software to identify analytes from mass spectrometry data

"""

import os
import glob
import pickle
import json

from ms2analyte.file_handling import data_import
from ms2analyte.process import sample_process, replicate_compare, basket, blank_annotate
from ms2analyte.output import tableau
from ms2analyte.calculate import spectral_matching


def run_analysis(input_structure):

    """Main engine for MS2Analyte. Manages the following steps:
    processes individual samples
    optionally performs replicate comparison
    baskets sample set
    optionally processes, replicate compares and annotates blanks
    creates mass spectra for analytes
    creates similarity network for all analytes in the dataset

    """

    # Check that the required directories exist and, if not, create

    data_import.directory_check(input_structure)

    # Check that the samples contain the correct number of replicates. If not, exit so that users can fix this issue

    data_import.replicate_check(input_structure, "Samples")

    # If the experiment includes blanks first check that the correct number of replicates exists. If not, exit so that
    # users can fix this issue.

    if input_structure.blanks_exist:
        data_import.replicate_check(input_structure, "Blanks")

    # Write input_structure to output directory in both pickle and json formats

    with open(os.path.join(input_structure.output_directory, input_structure.experiment_name +
                           "_experiment_import_parameters.pickle"), "wb") as f:
        pickle.dump(input_structure, f)

    json_input_structure = json.dumps(input_structure.__dict__)
    with open(os.path.join(input_structure.output_directory, input_structure.experiment_name +
                           "_experiment_import_parameters.json"), "w") as g:
        json.dump(json_input_structure, g)

    # If blanks exist, run analysis on individual blank files

    if input_structure.blanks_exist:
        for blank in glob.glob(os.path.join(input_structure.blank_directory, "*_R[0-9]."
                                            + input_structure.ms_data_file_suffix)):
            sample_process.sample_process(os.path.basename(blank), input_structure, "Blanks")

    # Run analysis on individual sample files

    for sample in glob.glob(os.path.join(input_structure.sample_directory, "*_R[0-9]."
                                                                           + input_structure.ms_data_file_suffix)):
        sample_process.sample_process(os.path.basename(sample), input_structure, "Samples")

    # Extract sample names for sample set and, if present, blanks

    sample_list = data_import.name_extract(input_structure, "Samples")

    if input_structure.blanks_exist:
        blank_list = data_import.name_extract(input_structure, "Blanks")

    # If there are replicates then replicate compare samples, otherwise append replicate notations for the
    # analyte ids from the single replicate data

    if input_structure.replicate_count > 1:
        replicate_compare.sample_consensus_analytes(input_structure, "Samples")
    else:
        replicate_compare.sample_consensus_analytes_no_replicates(input_structure, "Samples")

    # update the analyte objects from each individual sample replicate to include replicate analyte ids

    replicate_compare.analyte_update_replicate_analyte_data(input_structure, "Samples", sample_list)

    # basket sample set

    basket.sample_set_basket(input_structure, "Samples", sample_list)
    experiment_analyte_sample_list = basket.experiment_analyte_sample_analyte_dict(input_structure, "Samples")
    basket.input_data_sample_annotate(input_structure, "Samples", sample_list, experiment_analyte_sample_list)
    basket.create_experiment_analyte_spectra(input_structure, "Samples", sample_list, experiment_analyte_sample_list)

    # update the analyte objects from each individual sample replicate to include experiment analyte ids

    basket.analyte_update_experiment_analyte_data(input_structure, "Samples", sample_list)

    # If there are blanks then replicate compare blanks, update blank analytes with replicate analyte ids,
    # and basket blanks

    if input_structure.blanks_exist:
        if input_structure.replicate_count > 1:
            replicate_compare.sample_consensus_analytes(input_structure, "Blanks")
        else:
            replicate_compare.sample_consensus_analytes_no_replicates(input_structure, "Blanks")

        replicate_compare.analyte_update_replicate_analyte_data(input_structure, "Blanks", blank_list)
        basket.sample_set_basket(input_structure, "Blanks", blank_list)
        experiment_analyte_sample_list = basket.experiment_analyte_sample_analyte_dict(input_structure, "Blanks")
        basket.create_experiment_analyte_spectra(input_structure, "Blanks", blank_list, experiment_analyte_sample_list)

        # update the analyte objects from each individual blank replicate to include experiment analyte ids

        basket.analyte_update_experiment_analyte_data(input_structure, "Blanks", blank_list)

    # Annotate experiment analytes and sample analytes as blank or not

    if input_structure.blanks_exist:
        blank_annotate.blank_annotate(input_structure)
        blank_annotate.input_data_blank_annotate(input_structure, "Samples", sample_list)
        blank_annotate.analyte_blank_annotate(input_structure, sample_list)

    tableau.experiment_analyte_overview_export(input_structure, "Samples", sample_list)
    spectral_matching.similarity_network_graph(input_structure)


if __name__ == "__main__":

    # Acquire the directories and experimental details for the experiment from input_data_structure

    input_structure = data_import.input_data_structure()
    run_analysis(input_structure)
