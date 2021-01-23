#!/usr/bin/env python3

"""
file open dialogue window for MS2Analyte
"""

import sys

from PyQt5 import QtWidgets

from ms2analyte.Qt_Designer_templates.File_Dialogue.mainwindow_v2 import Ui_MainWindow
from ms2analyte.visualizations.file_open_model import PathManager, ExperimentParameters, InstrumentParameters, \
    ValidateSubmit
from ms2analyte.ms2analyte_sample_process import run_analysis


class MainWindowUIClass(Ui_MainWindow):
    def __init__(self):
        """ Initialize the super class"""
        super(MainWindowUIClass, self).__init__()
        self.path_manager = PathManager()
        self.experiment_parameters = ExperimentParameters()
        self.instrument_parameters = InstrumentParameters()
        self.validate_submit = ValidateSubmit()
        self.input_data_structure = None

    def setupUi(self, MW):
        super(MainWindowUIClass, self).setupUi(MW)
        # Define initial values for instrument dropdowns
        self.ManufacturerComboBox.addItem("Waters")
        self.ManufacturerComboBox.addItem("Thermo")
        self.ManufacturerComboBox.addItem("Agilent")
        self.InstrumentComboBox.addItem("SYNAPT")
        self.InstrumentComboBox.addItem("Xevo")
        self.SoftwareComboBox.addItem("MassLynx")
        self.FileTypeComboBox.addItem("func001")
        self.FileTypeComboBox.addItem("mzML")
        self.FileTypeComboBox.addItem("Proteowizard mzML")

        # Capture initial states for all experiment check boxes
        self.experiment_parameters.update_blanks_exist(self.BlanksCheckBox.isChecked())
        self.experiment_parameters.update_ms2_exists(self.MS2CheckBox.isChecked())
        self.experiment_parameters.update_ms2_type(self.DDARadioButton.isChecked())
        self.experiment_parameters.update_ims_exists(self.IonMobilityCheckBox.isChecked())
        if self.ReplicateCountLineEdit.text():
            validated, count = self.validate_replicates_count(self.ReplicateCountLineEdit.text())
            if validated:
                self.experiment_parameters.update_replicates_count(count)

        # Capture initial states for all instrument dropdowns
        self.instrument_parameters.update_instrument_manufacturer(self.ManufacturerComboBox.currentText())
        self.instrument_parameters.update_instrument_model(self.InstrumentComboBox.currentText())
        self.instrument_parameters.update_instrument_software(self.SoftwareComboBox.currentText())
        self.instrument_parameters.update_ms_data_file_type(self.FileTypeComboBox.currentText())

    # These functions handle actions associated with the directory selection section

    def refresh_paths(self):
        """Update the path manager widgets after an interaction."""
        self.ExperimentLineEdit.setText(self.path_manager.experiment_directory)
        self.SampleLineEdit.setText(self.path_manager.sample_directory)
        self.BlankLineEdit.setText(self.path_manager.blank_directory)
        self.OutputLineEdit.setText(self.path_manager.output_directory)

    def experiment_browse_slot(self):
        """Called when the user presses the experiment browse button"""
        flags = QtWidgets.QFileDialog.ShowDirsOnly
        dirname = QtWidgets.QFileDialog.getExistingDirectory(
            None,
            "Select directory",
            "",
            flags)
        if dirname:
            self.path_manager.set_experiment_dirname(dirname)
            self.path_manager.update_experiment_dirname()
            self.refresh_paths()

    def sample_browse_slot(self):
        """Called when the user presses the sample browse button"""
        flags = QtWidgets.QFileDialog.ShowDirsOnly
        dirname = QtWidgets.QFileDialog.getExistingDirectory(
            None,
            "Select directory",
            "",
            flags)
        if dirname:
            self.path_manager.set_samples_dirname(dirname)
            self.refresh_paths()

    def blank_browse_slot(self):
        """Called when the user presses the blanks browse button"""
        flags = QtWidgets.QFileDialog.ShowDirsOnly
        dirname = QtWidgets.QFileDialog.getExistingDirectory(
            None,
            "Select directory",
            "",
            flags)
        if dirname:
            self.path_manager.set_blanks_dirname(dirname)
            self.refresh_paths()

    def output_browse_slot(self):
        """Called when the user presses the output browse button"""
        flags = QtWidgets.QFileDialog.ShowDirsOnly
        dirname = QtWidgets.QFileDialog.getExistingDirectory(
            None,
            "Select directory",
            "",
            flags)
        if dirname:
            self.path_manager.set_output_dirname(dirname)
            self.refresh_paths()

    def directory_check_changed(self):
        """Update the enabled and disabled status of directory options, depending on whether standard structure
        (global directory for all sub-directories) is checked or not and updates directory path variables in model

        """
        if self.StandardDirectoryCheckBox.isChecked():
            self.ExperimentPushButton.setEnabled(True)
            self.ExperimentDirectoryLabel.setEnabled(True)
            self.ExperimentLineEdit.setEnabled(True)
            self.BlankPushButton.setEnabled(False)
            self.BlankDirectoryLabel.setEnabled(False)
            self.BlankLineEdit.setEnabled(False)
            self.SamplePushButton.setEnabled(False)
            self.SampleDirectoryLabel.setEnabled(False)
            self.SampleLineEdit.setEnabled(False)
            self.OutputPushButton.setEnabled(False)
            self.OutputDirectoryLabel.setEnabled(False)
            self.OutputLineEdit.setEnabled(False)
            self.path_manager.update_experiment_dirname()
            self.refresh_paths()
        else:
            self.ExperimentPushButton.setEnabled(False)
            self.ExperimentDirectoryLabel.setEnabled(False)
            self.ExperimentLineEdit.setEnabled(False)
            self.BlankPushButton.setEnabled(True)
            self.BlankDirectoryLabel.setEnabled(True)
            self.BlankLineEdit.setEnabled(True)
            self.SamplePushButton.setEnabled(True)
            self.SampleDirectoryLabel.setEnabled(True)
            self.SampleLineEdit.setEnabled(True)
            self.OutputPushButton.setEnabled(True)
            self.OutputDirectoryLabel.setEnabled(True)
            self.OutputLineEdit.setEnabled(True)

    def experiment_name_changed(self):
        """Update the experiment name variable on text change"""
        self.path_manager.update_experiment_name(self.ExperimentNameLineEdit.text())

    # These functions handle actions with the experiment parameters section

    def blanks_check_changed(self):
        """Update blanks exist bool"""
        self.experiment_parameters.update_blanks_exist(self.BlanksCheckBox.isChecked())

    def validate_replicates_count(self, replicates_value):
        try:
            count = int(replicates_value)
            if 1 <= count < 10:
                return True, count
            else:
                self.textBrowser.append("ERROR: Replicate count must be an integer between 1 and 9")
                return False, None
        except:
            if replicates_value:
                self.textBrowser.append("ERROR: Replicate count must be an integer between 1 and 9")
                return False, None
            else:
                return True, None

    def replicates_check_changed(self):
        """Update the replicates exist bool, and changes the enabled/ disabled status of replicate count, depending
        on whether replicates check is checked or not"""

        if self.ReplicatesCheckBox.isChecked():
            self.ReplicateCountLineEdit.setEnabled(True)
            self.ReplicateCountLabel.setEnabled(True)
            if self.ReplicateCountLineEdit.text():
                validated, count = self.validate_replicates_count(self.ReplicateCountLineEdit.text())
                if validated:
                    self.experiment_parameters.update_replicates_count(count)

        else:
            self.ReplicateCountLineEdit.setEnabled(False)
            self.ReplicateCountLabel.setEnabled(False)
            self.experiment_parameters.update_replicates_count(1)

    def replicate_count_changed(self):
        validated, count = self.validate_replicates_count(self.ReplicateCountLineEdit.text())
        if validated:
            self.experiment_parameters.update_replicates_count(count)

    def ms2_check_changed(self):
        """Update the enabled and disabled status of MS2 type (DDA or DIA) radio buttons, depending on whether MS2 data
         check is checked or not"""
        if self.MS2CheckBox.isChecked():
            self.DDARadioButton.setEnabled(True)
            self.DIARadioButton.setEnabled(True)
        else:
            self.DDARadioButton.setEnabled(False)
            self.DIARadioButton.setEnabled(False)

        self.experiment_parameters.update_ms2_exists(self.MS2CheckBox.isChecked())

    def ms2_method_changed(self):
        # WARNING: Assumes only two options for MS2 method. See comments in file_open_model.py
        self.experiment_parameters.update_ms2_type(self.DDARadioButton.isChecked())

    def ion_mobility_check_changed(self):
        self.experiment_parameters.update_ims_exists(self.IonMobilityCheckBox.isChecked())

    # These functions handle actions associated with the instrument parameters section

    def instrument_combo_boxes_clear(self):
        self.InstrumentComboBox.clear()
        self.SoftwareComboBox.clear()
        self.FileTypeComboBox.clear()

    def manufacturer_dropdown_changed(self):
        """Populate the Instrument, Software and File Type ComboBoxes with appropriate options
        depending on selected manufacturer.

        """
        if str(self.ManufacturerComboBox.currentText()) == "Waters":
            self.instrument_combo_boxes_clear()
            self.InstrumentComboBox.addItem("SYNAPT")
            self.InstrumentComboBox.addItem("Xevo")
            self.SoftwareComboBox.addItem("MassLynx")
            self.FileTypeComboBox.addItem("func001")
            self.FileTypeComboBox.addItem("mzML")
        elif str(self.ManufacturerComboBox.currentText()) == "Thermo":
            self.instrument_combo_boxes_clear()
            self.InstrumentComboBox.addItem("Orbitrap")
            self.SoftwareComboBox.addItem("XCaliber")
            self.FileTypeComboBox.addItem("mzML")
        elif str(self.ManufacturerComboBox.currentText()) == "Agilent":
            self.instrument_combo_boxes_clear()
            self.InstrumentComboBox.addItem("qTOF")
            self.SoftwareComboBox.addItem("Mass Hunter")
            self.FileTypeComboBox.addItem("mzXML")
        self.instrument_parameters.update_instrument_manufacturer(self.ManufacturerComboBox.currentText())
        self.instrument_parameters.update_instrument_model(self.InstrumentComboBox.currentText())
        self.instrument_parameters.update_instrument_software(self.SoftwareComboBox.currentText())
        self.instrument_parameters.update_ms_data_file_type(self.FileTypeComboBox.currentText())

    def instrument_dropdown_changed(self):
        self.instrument_parameters.update_instrument_model(self.InstrumentComboBox.currentText())

    def software_dropdown_changed(self):
        self.instrument_parameters.update_instrument_software(self.SoftwareComboBox.currentText())

    def file_type_dropdown_changed(self):
        self.instrument_parameters.update_ms_data_file_type(self.FileTypeComboBox.currentText())

    # These functions handle actions with the submit button to first validate that the input data are suitable,
    # and then to run the analysis

    def submit_slot(self):
        validated, warnings_list = self.validate_submit.validate(self.path_manager, self.experiment_parameters)
        if validated:
            self.textBrowser.append("Validation complete")
            self.input_data_structure = self.validate_submit.submit(self.path_manager, self.experiment_parameters,
                                                                    self.instrument_parameters)
            run_analysis(self.input_data_structure)
        else:
            for warning in warnings_list:
                self.textBrowser.append(warning)


# Temporarily disabled 'main()' in order to run GUI selectively via run_ms2analyte.py

def launch_gui():
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = MainWindowUIClass()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


# def main():
#     app = QtWidgets.QApplication(sys.argv)
#     MainWindow = QtWidgets.QMainWindow()
#     ui = MainWindowUIClass()
#     ui.setupUi(MainWindow)
#     MainWindow.show()
#     sys.exit(app.exec_())
#
#
# main()


