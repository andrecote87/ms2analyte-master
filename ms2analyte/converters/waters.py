#!/usr/bin/env python3

"""Tool to convert Waters source data in to MS2Analyte input format"""

import pandas as pd
import pymzml
import xml.etree.ElementTree as ET

import ms2analyte.config as config


def func001(file_path):
    """Import MS data from func001 files derived from MSeXpress"""
    input_data = pd.read_csv(file_path)
    reformatted_data = input_data[["ScanIndex", "ScanTimeMin", "Mz", "Drift", "Intensity"]]
    reformatted_data = reformatted_data.rename(index=str, columns={"ScanIndex": "scan", "ScanTimeMin": "rt", "Mz": "mz",
                                                "Drift": "drift", "Intensity": "intensity"})

    return reformatted_data


def mzml(file_path):
    """Import mzML files derived from applying MSConvert to .raw files.
    Tested with DDA data. Not tested with DIA data

    """
    headers = ["scan", "rt", "mz", "drift", "intensity"]
    input_data = []

    intensity_cutoff = config.intensity_cutoff

    # Waters data includes the lockspray internal calibrant scans as 'MS1' data. These are differentiated from true
    # MS1 data by the 'function' attribute in the spectrum element. Data MS1 scans are function 1. Lockspray scans are
    # assigned the highest possible function number (floating, depends on how many DDA scans were permitted during
    # acquisition setup). Commonly lockspray function=5. This is always 3 for MSe (DIA) data. pymzml doesn't incorporate
    # attribute data for the spectrum element. In order to filter out the lockspray data it is therefore necessary to
    # parse the XML file in ElemenTree and make a list of scan index numbers where ms level = 1 and function = 1.
    # This list is then used in the pymzml step to only incorporate true MS1 data.
    # NOTE: When MS2 functionality is added, this is not an issue, because all MS2 data have ms level = 2, and are
    # therefore all legitimate for inclusion.

    mzml_tree = ET.parse(file_path)
    ms1_spectrum_index_list = []

    mzml_root = mzml_tree.getroot()
    for base_mzml in mzml_root.findall("{http://psi.hupo.org/ms/mzml}mzML"):
        for mzml_run in base_mzml.findall("{http://psi.hupo.org/ms/mzml}run"):
            for mzml_spectrumList in mzml_run.findall("{http://psi.hupo.org/ms/mzml}spectrumList"):
                for mzml_spectrum in mzml_spectrumList.findall("{http://psi.hupo.org/ms/mzml}spectrum"):
                    for mzml_cvparam in mzml_spectrum.findall("{http://psi.hupo.org/ms/mzml}cvParam"):
                        if mzml_cvparam.attrib["name"] == "ms level":
                            if int(mzml_cvparam.attrib["value"]) == 1:
                                if int(mzml_spectrum.attrib["id"].split()[0].split("=")[1]) == 1:
                                    ms1_spectrum_index_list.append(int(mzml_spectrum.attrib["index"]))

    # Parse mzML file and format appropriate scan data as Dataframe

    run = pymzml.run.Reader(file_path)

    for n, spec in enumerate(run):
        if spec.index in ms1_spectrum_index_list:
            scan_number = spec.ID
            retention_time = round(spec.scan_time_in_minutes(), 2)
            drift_time = None
            for peak in spec.peaks('raw'):
                mz = round(peak[0], 4)
                intensity = int(peak[1])
                if intensity >= intensity_cutoff:
                    input_data.append([scan_number, retention_time, mz, drift_time, intensity])

        # Print import progress. Useful because importing large mzML files can be slow.
        if spec.index > 0:
            if spec.index % 100 == 0:
                print("Completed import of scan " + str(spec.index))

    mzml_dataframe = pd.DataFrame.from_records(input_data, columns=headers)

    return mzml_dataframe
