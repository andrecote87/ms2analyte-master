#!/usr/bin/env python3

"""
Process raw ms2 input data for individual file and create ms2 spectra for each ms1 analyte

NOTE: This is a legacy module, and probably doesn't work

"""

import os
import sys
import pickle

from ms2analyte.converters import waters
from ms2analyte.process import filters, peak_create, analyte_create, ms2_create
from ms2analyte.output import tableau


def ms2_process(input_file, input_structure, input_type):
    """Create analytes for a single data file. Either sample or blank OK in this function"""
    print("Starting ms2 spectrum creation for sample " + input_file[:-(len(input_structure.ms_data_file_suffix) + 1)])

    if input_structure.instrument_manufacturer == "Waters":
        if input_structure.ms_data_file_type == "func001":
            if input_type == "Samples":
                ms2_input_data = filters.intensity(
                    waters.func001(os.path.join(input_structure.sample_directory, "func002", input_file)))
            elif input_type == "Blanks":
                ms2_input_data = filters.intensity(
                    waters.func001(os.path.join(input_structure.blank_directory, "func002", input_file)))
            else:
                print("Input type not recognized. Options are 'Samples' or 'Blanks'")
                sys.exit()
        else:
            print("File type not recognized. Options are: 'func001'")
            sys.exit()

    else:
        print("Manufacturer not recognized. MS2 options are: 'Waters'")
        sys.exit()

    ms2_input_data = peak_create.mass_bin(ms2_input_data)
    ms2_input_data = peak_create.mass_range_check(ms2_input_data)
    ms2_input_data = peak_create.isotope_filter(ms2_input_data)
    ms2_input_data = peak_create.scan_split(ms2_input_data)
    ms2_input_data = peak_create.drift_split(ms2_input_data)
    ms2_input_data = peak_create.scan_split(ms2_input_data)
    ms2_input_data = peak_create.remove_no_maxima_peaks(ms2_input_data)
    ms2_input_data = peak_create.peak_minima_trim(ms2_input_data)
    ms2_input_data = peak_create.peak_split(ms2_input_data)
    ms2_peak_list = analyte_create.peak_df_to_obj(ms2_input_data)
    analyte_ms2_peaks = ms2_create.ms2_peak_to_analyte(ms2_peak_list, ms2_input_data, input_structure, input_type,
                                                       input_file)
    ms2_input_data = ms2_create.ms2_analyte_id_append(ms2_input_data, analyte_ms2_peaks)
    tableau.full_export(input_file, ms2_input_data, input_structure, input_type, subname="ms2_data")

    with open(os.path.join(input_structure.output_directory, input_type,
                           input_file[:-(len(input_structure.ms_data_file_suffix) + 1)] + "_ms2_dataframe.pickle"),
              "wb") as g:
        pickle.dump(ms2_input_data, g)
