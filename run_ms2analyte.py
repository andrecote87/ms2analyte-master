#!/usr/bin/env python3

"""A Dev tool to run MS2Analyte, either with the GUI or without, and either with full sample processing, or bypassing
the slow individual sample processing steps if testing downstream tools.

"""

import ms2analyte.file_open_dialogue
from ms2analyte.file_handling import data_import
import ms2analyte.ms2analyte_sample_process
import ms2analyte.ms2analyte_no_sample_process


def main():

    use_gui = False
    process_samples = True

    if use_gui:
        ms2analyte.file_open_dialogue.launch_gui()
    else:
        input_structure = data_import.input_data_structure()
        if process_samples:
            ms2analyte.ms2analyte_sample_process.run_analysis(input_structure)
        else:
            ms2analyte.ms2analyte_no_sample_process.run_analysis(input_structure)


main()
