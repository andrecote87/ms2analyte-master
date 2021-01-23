#!/usr/bin/env python3

"""
Processing software to identify analytes from mass spectrometry data. Excludes processing of individual samples,
which is the slowest step. This module is mostly used for debugging of later processes.

"""

from ms2analyte.file_handling import data_import
from ms2analyte.process import replicate_compare, basket, blank_annotate


def run_analysis(input_structure):

    # Extract sample names for sample set and, if present, blanks

    sample_list = data_import.name_extract(input_structure, "Samples")
    blank_list = data_import.name_extract(input_structure, "Blanks")

    # If there are replicates then replicate compare samples, otherwise append replicate notations for the
    # analyte ids from the single replicate data

    if input_structure.replicate_count > 1:
        replicate_compare.sample_consensus_analytes(input_structure, "Samples")
    else:
        replicate_compare.sample_consensus_analytes_no_replicates(input_structure, "Samples")

    # basket sample set

    basket.sample_set_basket(input_structure, "Samples", sample_list)
    experiment_analyte_sample_list = basket.experiment_analyte_sample_analyte_dict(input_structure, "Samples")
    basket.input_data_sample_annotate(input_structure, "Samples", sample_list, experiment_analyte_sample_list)
    basket.create_experiment_analyte_spectra(input_structure, "Samples", sample_list, experiment_analyte_sample_list)

    # If there are blanks then replicate compare blanks and basket blanks

    if input_structure.blanks_exist:
        if input_structure.replicate_count > 1:
            replicate_compare.sample_consensus_analytes(input_structure, "Blanks")
        else:
            replicate_compare.sample_consensus_analytes_no_replicates(input_structure, "Blanks")

        basket.sample_set_basket(input_structure, "Blanks", blank_list)
        experiment_analyte_sample_list = basket.experiment_analyte_sample_analyte_dict(input_structure, "Blanks")
        basket.create_experiment_analyte_spectra(input_structure, "Blanks", blank_list, experiment_analyte_sample_list)

    # Annotate experiment analytes as blank or not

    if input_structure.blanks_exist:
        blank_annotate.blank_annotate(input_structure)
        blank_annotate.input_data_blank_annotate(input_structure, "Samples", sample_list)


if __name__ == "__main__":

    # Acquire the directories and experimental details for the experiment from input_data_structure

    input_structure = data_import.input_data_structure()
    run_analysis(input_structure)
