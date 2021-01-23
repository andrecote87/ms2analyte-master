#!/usr/bin/env python3

"""Tools to import sample data and create output directory structure for MS2Analyte"""

import os
import sys
import glob
from collections import defaultdict


class InputDataStructure:
    """Class for input data for MS2Analyte analysis. Includes key experiment details and data paths"""
    def __init__(self, sample_directory, blank_directory, output_directory, blanks_exist, replicate_count, ms2_exists,
                 ms2_type, ims_exists, instrument_manufacturer, instrument_model, instrument_software,
                 ms_data_file_type, ms_data_file_suffix, experiment_name):
        self.sample_directory = sample_directory
        self.blank_directory = blank_directory
        self.output_directory = output_directory
        self.blanks_exist = blanks_exist
        self.replicate_count = replicate_count
        self.ms2_exists = ms2_exists
        self.ms2_type = ms2_type
        self.ims_exists = ims_exists
        self.instrument_manufacturer = instrument_manufacturer
        self.instrument_model = instrument_model
        self.instrument_software = instrument_software
        self.ms_data_file_type = ms_data_file_type
        self.ms_data_file_suffix = ms_data_file_suffix
        self.experiment_name = experiment_name


def input_data_structure():
    """Determine location of sample and blank input files, number of replicates, instrument type, and desired output
    directory
    """
    # Mevers data local

    # "/Volumes/Macintosh HD/Users/roger/Documents/Collaborators/Mevers/Clardy/Metabolomics/Full_dataset/Samples"
    # "/Volumes/RGL_MS_data/Mevers_JP_input_data/JP_Box_mzXML/Samples"
    # sample_directory = "/Volumes/RGL_MS_data/Mevers_JP_input_data/JP_Box_mzXML/Centroid/Media_blanks/Samples"
    # blank_directory = "/Volumes/RGL_MS_data/Mevers_JP_input_data/JP_Box_mzXML/Centroid/Media_blanks/Blanks"
    # output_directory = "/Volumes/RGL_MS_data/Mevers_JP_input_data/JP_Box_mzXML/Centroid/Media_blanks/Output"
    # blanks_exist = True
    # replicate_count = 1
    # ms2_exists = False
    # ms2_type = "DIA"
    # ims_exists = False
    # instrument_manufacturer = "Agilent"
    # instrument_model = "Unknown"
    # instrument_software = "Unknown"
    # ms_data_file_type = "mzXML"
    # ms_data_file_suffix = "mzXML"
    # experiment_name = "Mevers_JP_centroid_mzXML_media_blanks"

    # Fausto data

    # sample_directory = "/Volumes/Macintosh HD/Users/roger/Documents/Chemistry/MS2Analyte/MS2Analyte_python_scripts/" \
    #                    "test_data/Temp_Fausto/Samples"
    # blank_directory = "/Volumes/Macintosh HD/Users/roger/Documents/Chemistry/MS2Analyte/MS2Analyte_python_scripts/" \
    #                   "test_data/Temp_Fausto/Blanks"
    # output_directory = "/Volumes/Macintosh HD/Users/roger/Documents/Chemistry/MS2Analyte/MS2Analyte_python_scripts/" \
    #                    "test_data/Temp_Fausto/Output"
    # blanks_exist = False
    # replicate_count = 1
    # ms2_exists = False
    # ms2_type = "DIA"
    # ims_exists = True
    # instrument_manufacturer = "Waters"
    # instrument_model = "Synapt"
    # instrument_software = "MassLynx"
    # ms_data_file_type = "func001"
    # ms_data_file_suffix = "csv"
    # experiment_name = "Fausto_test_data"

    # BKD plate 001 data

    # sample_directory = "/Volumes/RGL_MS_data/MS2Analyte_source_data/MS2Analyte_source_data_BKD_001/" \
    #                    "MS2Analyte_Rx_filenames/Samples"
    # blank_directory = "/Volumes/RGL_MS_data/MS2Analyte_source_data/MS2Analyte_source_data_BKD_001/" \
    #                   "MS2Analyte_Rx_filenames/Blanks"
    # output_directory = "/Volumes/RGL_MS_data/MS2Analyte_source_data/MS2Analyte_source_data_BKD_001/" \
    #                    "MS2Analyte_Rx_filenames/Output"
    # blanks_exist = True
    # replicate_count = 3
    # ms2_exists = False
    # ms2_type = "DIA"
    # ims_exists = True
    # instrument_manufacturer = "Waters"
    # instrument_model = "Synapt"
    # instrument_software = "MassLynx"
    # ms_data_file_type = "func001"
    # ms_data_file_suffix = "csv"
    # experiment_name = "BKD_001"

    # Trevor data

    sample_directory = "/Volumes/Macintosh HD/Users/roger/Documents/Chemistry/MS2Analyte/MS2Analyte_python_scripts/" \
                       "test_data/Green_tea_GT26/DIA_data/Positive/peak_split_max/Samples"
    blank_directory = "/Volumes/Macintosh HD/Users/roger/Documents/Chemistry/MS2Analyte/MS2Analyte_python_scripts/" \
                      "test_data/Green_tea_GT26/DIA_data/Positive/peak_split_max/Blanks"
    output_directory = "/Volumes/Macintosh HD/Users/roger/Documents/Chemistry/MS2Analyte/MS2Analyte_python_scripts/" \
                       "test_data/Green_tea_GT26/DIA_data/Positive/peak_split_max/Output_20201110"
    blanks_exist = True
    replicate_count = 3
    ms2_exists = False
    ms2_type = "DIA"
    ims_exists = True
    instrument_manufacturer = "Waters"
    instrument_model = "Synapt"
    instrument_software = "MassLynx"
    ms_data_file_type = "func001"
    ms_data_file_suffix = "csv"
    experiment_name = "GreenTea26_basket_test"

    # Trevor data MSConvert

    # sample_directory = "/Volumes/Macintosh HD/Users/roger/Documents/Chemistry/MS2Analyte/MS2Analyte_python_scripts/" \
    #                    "test_data/Green_tea_GT26/Thermo_centroid/Positive/Samples"
    # blank_directory = "/Volumes/Macintosh HD/Users/roger/Documents/Chemistry/MS2Analyte/MS2Analyte_python_scripts/" \
    #                   "test_data/Green_tea_GT26/Thermo_centroid/Positive/Blanks"
    # output_directory = "/Volumes/Macintosh HD/Users/roger/Documents/Chemistry/MS2Analyte/MS2Analyte_python_scripts/" \
    #                    "test_data/Green_tea_GT26/Thermo_centroid/Positive/Output"
    # blanks_exist = False
    # replicate_count = 1
    # ms2_exists = True
    # ms2_type = "DDA"
    # ims_exists = False
    # instrument_manufacturer = "Thermo"
    # instrument_model = "Orbitrap"
    # instrument_software = "Xcalibur"
    # ms_data_file_type = "Proteowizard mzML"
    # ms_data_file_suffix = "mzML"
    # experiment_name = "Thermo_mzml_test"

    # Nick data

    # sample_directory = "/Volumes/RGL_MS_data/UNB_Moorehouse/Test_func001_input/Samples"
    # blank_directory = "/Volumes/RGL_MS_data/UNB_Moorehouse/Test_func001_input/Blanks"
    # output_directory = "/Volumes/RGL_MS_data/UNB_Moorehouse/Test_func001_input/Output"
    # blanks_exist = False
    # replicate_count = 3
    # ms2_exists = False
    # ms2_type = "DIA"
    # ims_exists = True
    # instrument_manufacturer = "Waters"
    # instrument_model = "Synapt"
    # instrument_software = "MassLynx"
    # ms_data_file_type = "func001"
    # ms_data_file_suffix = "csv"
    # experiment_name = "Moorehose_test_output"

    # IsoTracer test data

    # sample_directory = "../test_data/Isotracer_data/1353_D0_12C/Samples"
    # blank_directory = "../test_data/Isotracer_data/1353_D0_12C/Blanks"
    # output_directory = "../test_data/Isotracer_data/1353_D0_12C/Output"
    # blanks_exist = True
    # replicate_count = 4
    # ms2_exists = True
    # ms2_type = "DIA"
    # ims_exists = False
    # instrument_manufacturer = "Waters"
    # instrument_model = "Synapt"
    # instrument_software = "MassLynx"
    # ms_data_file_type = "func001"
    # ms_data_file_suffix = "csv"
    # experiment_name = "1353_C12"

    return InputDataStructure(sample_directory, blank_directory, output_directory, blanks_exist, replicate_count,
                              ms2_exists, ms2_type, ims_exists, instrument_manufacturer, instrument_model,
                              instrument_software, ms_data_file_type, ms_data_file_suffix, experiment_name)


def directory_check(input_structure):
    """Check for presence of input and output directories, and if output subdirectories are missing, create"""
    if not os.path.exists(input_structure.sample_directory):
        print("ERROR - data_import.directory_check: Sample directory not found")
        sys.exit()

    if input_structure.blanks_exist and not os.path.exists(input_structure.blank_directory):
        print("ERROR - data_import.directory_check: Blank directory not found")
        sys.exit()

    if not os.path.exists(input_structure.output_directory):
        os.makedirs(input_structure.output_directory)

    if not os.path.exists(os.path.join(input_structure.output_directory, "Samples")):
        os.makedirs(os.path.join(input_structure.output_directory, "Samples"))

    if input_structure.blanks_exist and not os.path.exists(os.path.join(input_structure.output_directory, "Blanks")):
        os.makedirs(os.path.join(input_structure.output_directory, "Blanks"))


def replicate_check(input_structure, input_type):
    """Check both blanks and samples for the correct number of replicate files.
    Note that the glob statement assumes that there will be no more than 9 replicates

    """
    sample_dict = defaultdict(int)
    error_found = False

    if input_type == "Samples":
        base_directory = input_structure.sample_directory
    elif input_type == "Blanks":
        base_directory = input_structure.blank_directory
    else:
        print("ERROR - data_import.replicate_check: Sample input type not valid. Must be 'Samples' or 'Blanks'")
        sys.exit()

    for sample in glob.glob(os.path.join(base_directory, "*_R[0-9]." + input_structure.ms_data_file_suffix)):
        sample_dict[os.path.basename(sample).rsplit("_", maxsplit=1)[0]] += 1

    for key, value in sample_dict.items():
        if value != input_structure.replicate_count:
            print("ERROR - data_import.directory_check: incorrect number of replicates for " + str(key) + ". Expecting "
                  + str(input_structure.replicate_count) + " replicates, found " + str(value))
            error_found = True

    if error_found:
        sys.exit()

    else:
        print("Replicate check for " + input_type + " passed")


def name_extract(input_structure, input_type):
    """Generate a list of unique sample names for any directory. You should use this function twice if you want lists of
    blank names and sample names.

    """
    sample_name_list = []

    if input_type == "Samples":
        base_input_directory = input_structure.sample_directory
    elif input_type == "Blanks":
        base_input_directory = input_structure.blank_directory
    else:
        print("ERROR - data_import.name_extract: Replicate compare. Sample input type not valid. Must be 'Samples' or "
              "'Blanks'")
        sys.exit()

    # Create list of sample names to analyze
    for sample in glob.glob(os.path.join(base_input_directory, "*_R[0-9]." + input_structure.ms_data_file_suffix)):
        sample_name = str(os.path.basename(sample).rsplit("_", maxsplit=1)[0])
        if sample_name not in sample_name_list:
            sample_name_list.append(sample_name)

    return sample_name_list
