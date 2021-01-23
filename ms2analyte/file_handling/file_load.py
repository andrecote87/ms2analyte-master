#!/usr/bin/env python3

"""Tools to load files for MS2Analyte analysis"""

import os
import pickle
import pandas as pd


def sample_dataframe_concat(input_structure, input_type, sample_name):
    """Load pickle files for a sample, and create concatenated dataframe for all replicates"""
    sample_replicate_data = []
    for i in range(1, input_structure.replicate_count + 1):
        with open(os.path.join(input_structure.output_directory, input_type, sample_name + "_R" + str(i)
                               + "_dataframe.pickle"), "rb") as pickle_file:
            replicate_data = pickle.load(pickle_file)
        sample_replicate_data.append(replicate_data)
    sample_input_data = pd.concat(sample_replicate_data)

    return sample_input_data
