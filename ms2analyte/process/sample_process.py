#!/usr/bin/env python3

"""Process raw input data for individual files and create analytes from individual runs"""

import os
import sys
import pickle

from ms2analyte.converters import waters, thermo, agilent
from ms2analyte.process import filters, peak_create, analyte_create
from ms2analyte.output import tableau


def sample_process(input_file, input_structure, input_type):
    """Create analytes for a single data file
    Either sample or blank OK in this function

    """
    print("Starting processing for sample " + input_file[:-(len(input_structure.ms_data_file_suffix) + 1)])

    if input_structure.instrument_manufacturer == "Waters":
        if input_structure.ms_data_file_type == "func001":
            if input_type == "Samples":
                input_data = filters.intensity(waters.func001(os.path.join(input_structure.sample_directory,
                                                                           input_file)))
            elif input_type == "Blanks":
                input_data = filters.intensity(waters.func001(os.path.join(input_structure.blank_directory,
                                                                           input_file)))
            else:
                print("Input type not recognized. Options are 'Samples' or 'Blanks'")
                sys.exit()
        elif input_structure.ms_data_file_type == "mzML":
            if input_type == "Samples":
                input_data = filters.intensity(waters.mzml(os.path.join(input_structure.sample_directory, input_file)))
            elif input_type == "Blanks":
                input_data = filters.intensity(waters.mzml(os.path.join(input_structure.blank_directory, input_file)))
            else:
                print("Input type not recognized. Options are 'Samples' or 'Blanks'")
                sys.exit()
        else:
            print("File type not recognized. Options are: 'func001', 'mzML'")
            sys.exit()

    elif input_structure.instrument_manufacturer == "Thermo":
        if input_structure.ms_data_file_type == "mzML":
            if input_type == "Samples":
                input_data = filters.intensity(thermo.mzml(os.path.join(input_structure.sample_directory, input_file)))
            elif input_type == "Blanks":
                input_data = filters.intensity(thermo.mzml(os.path.join(input_structure.blank_directory, input_file)))
            else:
                print("Input type not recognized. Options are 'Samples' or 'Blanks'")
                sys.exit()
        elif input_structure.ms_data_file_type == "Proteowizard mzML":
            if input_type == "Samples":
                input_data = filters.intensity(thermo.proteowizard_mzml(os.path.join(input_structure.sample_directory,
                                                                                     input_file)))
            elif input_type == "Blanks":
                input_data = filters.intensity(thermo.proteowizard_mzml(os.path.join(input_structure.blank_directory,
                                                                                     input_file)))
            else:
                print("Input type not recognized. Options are 'Samples' or 'Blanks'")
                sys.exit()

        else:
            print("File type not recognized. Options are: 'mzML', 'Proteowizard mzML")
            sys.exit()
    elif input_structure.instrument_manufacturer == "Agilent":
        if input_structure.ms_data_file_type == "mzXML":
            if input_type == "Samples":
                input_data = filters.intensity(
                    agilent.mzxml_import(os.path.join(input_structure.sample_directory, input_file)))
            elif input_type == "Blanks":
                input_data = filters.intensity(
                    agilent.mzxml_import(os.path.join(input_structure.blank_directory, input_file)))
            else:
                print("Input type not recognized. Options are 'Samples' or 'Blanks'")
                sys.exit()
        else:
            print("File type not recognized. Options are: 'mzXML'")
            sys.exit()
    else:
        print("Manufacturer not recognized. Options are: 'Waters', 'Thermo', 'Agilent'")
        sys.exit()

    input_data = peak_create.mass_bin(input_data)
    tableau.full_export(input_file, input_data, input_structure, input_type, subname="massbin")
    input_data = peak_create.remove_small_peaks(input_data)
    input_data = peak_create.remove_no_maxima_peaks(input_data)
    input_data = peak_create.mass_range_check(input_data)
    # tableau.full_export(input_file, input_data, input_structure, input_type, subname="massrange")
    if not input_structure.ims_exists:
        if peak_create.find_scan_duplicates(input_data):
            input_data = peak_create.resolve_scan_duplicates(input_data)
    input_data = peak_create.isotope_filter(input_data)
    # tableau.full_export(input_file, input_data, input_structure, input_type, subname="isotopefilter")
    input_data = peak_create.scan_split(input_data)
    # tableau.full_export(input_file, input_data, input_structure, input_type, subname="scansplit")
    if input_structure.ims_exists:
        input_data = peak_create.drift_split(input_data)
        # tableau.full_export(input_file, input_data, input_structure, input_type, subname="driftsplit")
        input_data = peak_create.scan_split(input_data)
    input_data = peak_create.remove_no_maxima_peaks(input_data)
    input_data = peak_create.peak_minima_trim(input_data)
    input_data = peak_create.peak_split_max(input_data)
    # tableau.full_export(input_file, input_data, input_structure, input_type, subname="peaksplit")
    peak_list = analyte_create.peak_df_to_obj(input_data)
    analyte_list = analyte_create.peak_to_analyte(peak_list, input_data)
    # analyte_list = analyte_create.analyte_isotope_filter(analyte_list)
    input_data = analyte_create.analyte_id_append(input_data, analyte_list)
    tableau.full_export(input_file, input_data, input_structure, input_type)

    with open(os.path.join(input_structure.output_directory, input_type,
                           input_file[:-(len(input_structure.ms_data_file_suffix) + 1)] + "_analytes.pickle"), "wb") \
            as g:
        pickle.dump(analyte_list, g)

    with open(os.path.join(input_structure.output_directory, input_type,
                           input_file[:-(len(input_structure.ms_data_file_suffix) + 1)] + "_dataframe.pickle"), "wb") \
            as h:
        pickle.dump(input_data, h)
