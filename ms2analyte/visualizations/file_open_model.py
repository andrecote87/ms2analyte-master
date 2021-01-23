#!/usr/bin/env python3

"""file open model for MS2Analyte"""

import os


class PathManager:
    def __init__(self):
        """Initialize directory paths held in class and name for MS2Analyte experiment. Used to name experiment level
        files in results output."""
        self.experiment_directory = None
        self.sample_directory = None
        self.blank_directory = None
        self.output_directory = None
        self.experiment_name = None

    def is_valid(self, dirname):
        """Examine whether directory exists"""
        if os.path.isdir(dirname):
            return True
        else:
            return False

    def set_experiment_dirname(self, dirname):
        """Set the experiment directory if the directory exists
        Set subdirectory paths based on experiment dirname. Otherwise resets the experiment_directory to None

        """
        if self.is_valid(dirname):
            self.experiment_directory = dirname
            self.sample_directory = os.path.join(dirname, "Samples")
            self.blank_directory = os.path.join(dirname, "Blanks")
            self.output_directory = os.path.join(dirname, "Output")
        else:
            self.experiment_directory = None
            self.sample_directory = None
            self.blank_directory = None
            self.output_directory = None

    def set_blanks_dirname(self, dirname):
        """Set the blanks directory if the directory exists
        Otherwise resets the blank_directory to None

        """
        if self.is_valid(dirname):
            self.blank_directory = dirname
        else:
            self.blank_directory = None

    def set_samples_dirname(self, dirname):
        """Set the samples directory if the directory exists
        Otherwise resets the sample_directory to None

        """
        if self.is_valid(dirname):
            self.sample_directory = dirname
        else:
            self.sample_directory = None

    def set_output_dirname(self, dirname):
        """Set the output directory if the directory exists
        Otherwise resets the output_directory to None

        """
        if self.is_valid(dirname):
            self.output_directory = dirname
        else:
            self.output_directory = None

    def get_dirname(self, target_directory):
        """Fetch directory name for target directory"""
        return target_directory

    def update_experiment_dirname(self):
        if self.experiment_directory:
            self.sample_directory = os.path.join(self.experiment_directory, "Samples")
            self.blank_directory = os.path.join(self.experiment_directory, "Blanks")
            self.output_directory = os.path.join(self.experiment_directory, "Output")

    def update_samples_dirname(self, dirname):
        if dirname:
            self.sample_directory = dirname

    def update_blanks_dirname(self, dirname):
        if dirname:
            self.blank_directory = dirname

    def update_output_dirname(self, dirname):
        if dirname:
            self.output_directory = dirname

    def update_experiment_name(self, experiment_name):
        if experiment_name:
            self.experiment_name = experiment_name
        else:
            self.experiment_name = None


class ExperimentParameters:
    def __init__(self):
        """
        Initialize the experiment parameters the class holds
        These are parameters from the mass spectrometry experiment. Specifically, details about the acquisition setup
        that are required to correctly configure MS2Analyte.

        """
        self.blanks_exist = None
        self.replicate_count = None
        self.ms2_exists = None
        self.ms2_type = None
        self.ims_exists = None

    def update_blanks_exist(self, state):
        self.blanks_exist = state

    def update_replicates_count(self, count):
        self.replicate_count = count

    def update_ms2_exists(self, state):
        self.ms2_exists = state

    def update_ms2_type(self, type):
        # WARNING: this assumes only two options for MS2 type. If more options are added, an new function will be
        # required
        if type:
            self.ms2_type = "DDA"
        else:
            self.ms2_type = "DIA"

    def update_ims_exists(self, state):
        self.ims_exists = state


class InstrumentParameters:
    def __init__(self):
        """Initialize the instrument parameters the class holds:
        These are details about the hardware used in the mass spectrometry experiment, as well as details about the
        output file format.

        """
        self.instrument_manufacturer = None
        self.instrument_model = None
        self.instrument_software = None
        self.ms_data_file_type = None
        self.ms_data_file_suffix = None

    def update_instrument_manufacturer(self, manufacturer):
        self.instrument_manufacturer = manufacturer

    def update_instrument_model(self, model):
        self.instrument_model = model

    def update_instrument_software(self, software):
        self.instrument_software = software

    def update_ms_data_file_type(self, file_type):
        self.ms_data_file_type = file_type
        if file_type == "func001":
            self.ms_data_file_suffix = "csv"
        elif file_type == "mzXML":
            self.ms_data_file_suffix = "mzXML"
        elif file_type == "mzML":
            self.ms_data_file_suffix = "mzML"


class ValidateSubmit:
    def __init__(self):
        self.validated = True

    def validate(self, path_manager, experiment_parameters):
        self.validated = True
        warnings_list = []

        # Validate path data
        if not path_manager.experiment_name:
            warnings_list.append("ERROR: Experiment name not provided. Please specify above")
            self.validated = False

        if not path_manager.sample_directory:
            warnings_list.append("ERROR: Samples directory not provided. Please specify above")
            self.validated = False
        elif not os.path.isdir(path_manager.sample_directory):
            warnings_list.append("ERROR: Samples directory does not exist. If you provided an experiment directory, "
                                 "make sure it contains the directory 'Samples' with your sample MS data inside")
            self.validated = False

        if experiment_parameters.blanks_exist:
            if not path_manager.blank_directory:
                warnings_list.append("ERROR: Blanks directory not provided. Please specify above")
                self.validated = False
            elif not os.path.isdir(path_manager.blank_directory):
                warnings_list.append("ERROR: Blanks directory does not exist. If you provided an experiment directory, "
                                     "make sure it contains the directory 'Blanks' with your blank MS data inside")
                self.validated = False

        if not path_manager.output_directory:
            # Note: Output directory is created in MS2Analyte, so os.path.isdir() test is not required here.
            warnings_list.append("ERROR: Output directory not provided. Please specify above")
            self.validated = False

        # Validate experiment data
        if not experiment_parameters.replicate_count:
            warnings_list.append("ERROR: Replicate count not provided. Either uncheck the 'Replicates' checkbox, "
                                 "or provide number of replicates (1 - 9) in the replicate count box above")
            self.validated = False

        return self.validated, warnings_list

    def submit(self, path_manager, experiment_parameters, instrument_parameters):
        input_data_structure = InputDataStructure(path_manager.sample_directory, path_manager.blank_directory,
                                                  path_manager.output_directory, experiment_parameters.blanks_exist,
                                                  experiment_parameters.replicate_count,
                                                  experiment_parameters.ms2_exists, experiment_parameters.ms2_type,
                                                  experiment_parameters.ims_exists,
                                                  instrument_parameters.instrument_manufacturer,
                                                  instrument_parameters.instrument_model,
                                                  instrument_parameters.instrument_software,
                                                  instrument_parameters.ms_data_file_type,
                                                  instrument_parameters.ms_data_file_suffix,
                                                  path_manager.experiment_name)

        return input_data_structure


class InputDataStructure:

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
