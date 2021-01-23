#!/usr/bin/env python3

"""Tool to convert Thermo source data in to MS2Analyte input format"""

import pandas as pd
import os
import glob
import csv
import pymzml
import xml.etree.ElementTree as ET

import ms2analyte.config as config


def orbitrap(file_path):
    """Import Orbitrap data from XCalibur export. Designed for scan by scan Orbitrap data.
    Original export of example data performed by Cech lab @ UNCG. Example data in MS_data external in Cech directory
    """
    headers = ["scan", "rt", "mz", "drift", "intensity"]
    input_data = []

    intensity_cutoff = config.intensity_cutoff

    for path_name in glob.glob(os.path.join(file_path, "*.mzML.binary.*.txt")):
        file_name = path_name.split("/")[-1]
        scan_number = int(file_name.split(".")[-2])

        with open(path_name) as f:
            for row in f:
                if row.startswith("# retentionTime:"):
                    retention_time = float(row.split(" ")[-1])
                    break

        with open(path_name) as f:
            csv_f = csv.reader(f, delimiter="\t")
            for row in csv_f:
                if not row[0].startswith("#"):
                    intensity = round(float(row[1]), 0)
                    mass = round(float(row[0]), 4)
                    if intensity >= intensity_cutoff:
                        input_data.append([scan_number, retention_time, mass, None, intensity])

    orbitrap_dataframe = pd.DataFrame.from_records(input_data, columns=headers, index=str)

    return orbitrap_dataframe


def mzml(file_path):
    """Read centroided mzML data"""
    headers = ["scan", "rt", "mz", "drift", "intensity"]
    input_data = []

    intensity_cutoff = config.intensity_cutoff

    run = pymzml.run.Reader(file_path, MS_precisions={1: 5e-6})

    for n, spec in enumerate(run):
        scan_number = spec.index
        # Print import progress. Useful because importing large mzML files can be slow.
        if scan_number > 0 and scan_number % 100 == 0:
            print("Completed import of scan " + str(scan_number))

        if spec.ms_level == 1:
            retention_time = round(spec.scan_time_in_minutes(), 2)
            drift_time = None
            for peak in spec.peaks('reprofiled'):
                print(peak)
                mz = round(peak[0], 4)
                intensity = int(peak[1])
                if intensity >= intensity_cutoff:
                    input_data.append([scan_number, retention_time, mz, drift_time, intensity])

    mzml_dataframe = pd.DataFrame.from_records(input_data, columns=headers)

    print("Complete mzML import")

    return mzml_dataframe


def proteowizard_mzml(file_path):
    """Read centroided mzML data from Proteowizard conversion.
    Includes tools to ignore non-MS spectra. For example, some mzML files include 'electromagnetic radiation spectrum'
    data, or PDA data.
    Works by parsing the 'id' spectrum tag. This is not incorporated in pymzml, so the XML tree must be parsed with
    ElementTree instead. Reviews the 'controllerType' value. If controllerType=0, this is MS data. Otherwise, it is
    some other (unwanted) spectrum type

    """
    headers = ["scan", "rt", "mz", "drift", "intensity"]
    input_data = []

    intensity_cutoff = config.intensity_cutoff

    # Parse over mzML file and temp mzML file that only contains MS data.
    mzml_tree = ET.parse(file_path)
    ms_spectrum_index_list = []
    mzml_root = mzml_tree.getroot()
    for base_mzml in mzml_root.findall("{http://psi.hupo.org/ms/mzml}mzML"):
        for mzml_run in base_mzml.findall("{http://psi.hupo.org/ms/mzml}run"):
            for mzml_spectrumList in mzml_run.findall("{http://psi.hupo.org/ms/mzml}spectrumList"):
                for mzml_spectrum in mzml_spectrumList.findall("{http://psi.hupo.org/ms/mzml}spectrum"):
                    if int(mzml_spectrum.attrib["id"].split()[0].split("=")[1]) != 0:
                        mzml_spectrumList.remove(mzml_spectrum)
                        # ms_spectrum_index_list.append(int(mzml_spectrum.attrib["index"]))

    # Create a temporary mzML file for pymzml to read (pymzml will only accept files as inputs, not objects)
    mzml_filename = str(os.path.basename(file_path))
    temp_mzml_filename = mzml_filename.rsplit(".")[0] + "_temp.mzML"
    temp_mzml_filepath = os.path.join(os.path.dirname(file_path), temp_mzml_filename)

    mzml_tree.write(temp_mzml_filepath)

    # Parse mzml and create dataframe
    mzml_dataframe = mzml(temp_mzml_filepath)

    # Delete temporary mzML file used for pymzml reader
    os.remove(temp_mzml_filepath)

    return mzml_dataframe
