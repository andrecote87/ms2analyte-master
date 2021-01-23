#!/usr/bin/env python3

"""
Set of scripts for calculating mass spectral properties of peaks and analytes from mass spectrometry data

"""

import ms2analyte.config as config


def average_mass(mass_list):
    """Calculate average mass from list of masses"""
    average_mass_value = round(sum(mass_list)/len(mass_list), 4)
    return average_mass_value


def mass_match(mass1, mass2):
    """Determine whether two masses are within required mass error of one another"""
    mass_match_bool = False

    if mass1 - config.mass_error_da <= mass2 <= mass1 + config.mass_error_da:
        mass_match_bool = True

    return mass_match_bool


def isotope_match(mass1, mass2):
    """Determine whether a lower mass (mass1) has a 13C isotope partner (mass2)"""
    isotope_match_bool = False

    if mass1 - config.mass_error_da <= mass2 - config.carbon_isotope_offset <= mass1 + config.mass_error_da:
        isotope_match_bool = True

    return isotope_match_bool
