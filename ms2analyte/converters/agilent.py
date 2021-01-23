#!/usr/bin/env python3

"""Tool to convert Agilent source data in to MS2Analyte input format"""

import pandas as pd
from pyteomics import mzxml

import ms2analyte.config as config


def mzxml_import(file_path):
    """Read centroided mzXML data"""
    headers = ["scan", "rt", "mz", "drift", "intensity"]
    input_data = []

    intensity_cutoff = config.intensity_cutoff

    reader = mzxml.MzXML(file_path)
    for index, spectrum in enumerate(reader):
        if len(spectrum["m/z array"]) != len(spectrum["intensity array"]):
            print("ERROR: mzXML import; m/z and intensity arrays different lengths")
        if spectrum["msLevel"] == 1:
            rt = round(spectrum["retentionTime"], 2)
            for j in range(len(spectrum["m/z array"])):
                intensity = spectrum["intensity array"][j]
                mz = spectrum["m/z array"][j]
                if intensity >= intensity_cutoff:
                    input_data.append([index, rt, mz, None, int(intensity)])

    if len(input_data) > 0:
        mzxml_dataframe = pd.DataFrame.from_records(input_data, columns=headers)
        print("Completed mzXML import")
        return mzxml_dataframe

    else:
        print("No mass peaks found for " + file_path)
