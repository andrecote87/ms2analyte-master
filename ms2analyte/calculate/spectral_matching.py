#!/usr/bin/env python3

"""
Set of scripts for calculating similarities of analytes based on mass spectral features
Loosely based on script from https://doi.org/10.1021/pr070361e

"""

import numpy as np
import networkx as nx
import os
import pickle

import ms2analyte.config as config


def deisotoped_mass_list(spectrum):
    """Create deisotoped mass list from spectrum object"""
    sorted_mass_list = spectrum
    sorted_mass_list.sort(key=lambda x: x.average_mass)
    mass_reference_list = []
    mass_list = []
    for mass_peak in sorted_mass_list:
        mass_reference_list.append(mass_peak.average_mass)
    for mass_peak in sorted_mass_list:
        insert_peak = True
        for refrence_peak in mass_reference_list:
            # Look for isotope peaks at all charge states
            for i in range(1, config.allowed_charge_values + 1, 1):
                if refrence_peak - 0.1 < mass_peak.average_mass - (1/i) < refrence_peak + 0.1:
                    insert_peak = False
                    break
        if insert_peak:
            mass_list.append(mass_peak)
    return mass_list


def cosine_score(vector1, vector2):
    """Calculate cosine cosine score between two spectral vectors."""
    return np.dot(vector1, vector2)/np.sqrt(np.dot(np.dot(vector1, vector1), np.dot(vector2, vector2)))


def weighted_match_score(vector1, vector2):
    """Calculate matching score that considers both the relative intensities of the matching peaks
    (i.e. is is 100 vs 98, or 100 vs 2?) and also the number of matches versus the total number of peaks in each vector

    """
    vector1_weighted_pairwise_match = 0
    vector2_weighted_pairwise_match = 0
    for i in range(len(vector1)):
        if vector1[i] > 0 and vector2[i] > 0:
            weighting_factor = vector1[i]/vector2[i]
            if weighting_factor > 1:
                weighting_factor = 1/weighting_factor
            vector1_weighted_pairwise_match += vector1[i] * weighting_factor
            vector2_weighted_pairwise_match += vector2[i] * weighting_factor

    vector1_score = vector1_weighted_pairwise_match/sum(vector1)
    vector2_score = vector2_weighted_pairwise_match/sum(vector2)

    if vector1_score < vector2_score:
        return vector1_score
    else:
        return vector2_score


def select_closest_mass_offset(max_counts, unique_elements_with_count):
    """Select select the mass offset closest to zero if several mass offsets occur the same number of times

    """
    mass_offset = None

    for unique_element in unique_elements_with_count:
        if unique_element[1] == max_counts and unique_element != 0:
            if not mass_offset:
                mass_offset = unique_element[0]
            elif abs(unique_element[0]) < abs(mass_offset):
                mass_offset = unique_element[0]

    return mass_offset


def find_mass_offset(analyte1, analyte2):
    """Find mass offset between spectra. Uses deisotoped data so that there is no interference between isotope peaks
    from different isotope sub-peaks in the spectrum

    """
    deisotoped_spectrum1 = deisotoped_mass_list(analyte1.relative_experiment_mass_spectrum)
    deisotoped_spectrum2 = deisotoped_mass_list(analyte2.relative_experiment_mass_spectrum)

    # Create array of peak mass differences, where each peak from analyte 1 is a row, and each peak from analyte 2 is
    # a column. Calculate the mass differences between all peaks

    mass_difference_list = []
    for mass_peak1 in deisotoped_spectrum1:
        mass_differences = []
        for mass_peak2 in deisotoped_spectrum2:
            mass_difference = round(mass_peak1.average_mass, 1) - round(mass_peak2.average_mass, 1)
            mass_differences.append(mass_difference)
        mass_difference_list.append(mass_differences)
    mass_difference_array = np.array(mass_difference_list)

    # Generate a list of all unique mass differences, and count the number of instances for each mass difference.
    # Find the mass difference with the highest count, excluding 0 and set this as the allowed mass offset for peak
    # matching.

    unique_elements, counts_elements = np.unique(mass_difference_array, return_counts=True)
    counts_elements_values, counts_counts_elements = np.unique(counts_elements, return_counts=True)
    counts_elements_count_dict = dict(zip(counts_elements_values, counts_counts_elements))
    unique_elements_with_count = []
    for i in range(len(unique_elements)):
        unique_elements_with_count.append([unique_elements[i], counts_elements[i]])
    max_counts = np.amax(counts_elements)
    mass_offset = None
    # Only assign a mass offset if more than the minimum set number of peak pairs have the same offset
    if max_counts >= config.minimum_mass_offset_instances:
        count_of_max_counts = counts_elements_count_dict[max_counts]
        # If several mass offsets occur the same number of times, select the one closest to zero that is not zero itself
        if count_of_max_counts > 1:
            mass_offset = select_closest_mass_offset(max_counts, unique_elements_with_count)
        # Else if there is only one maximum count, if this is not a count of zero, set offset to this value.
        else:
            for unique_element in unique_elements_with_count:
                if unique_element[1] == max_counts and unique_element[0] != 0:
                    mass_offset = unique_element[0]
                # Otherwise, if top count is of zero, set offset to next highest count, provided it still meets the
                # minimum peak match threshold.
                else:
                    max_counts = sorted(counts_elements, reverse=True)[1]
                    if max_counts >= config.minimum_mass_offset_instances:
                        count_of_max_counts = counts_elements_count_dict[max_counts]
                        # If several mass offsets occur the same number of times, select the one closest to zero
                        if count_of_max_counts > 1:
                            mass_offset = select_closest_mass_offset(max_counts, unique_elements_with_count)
                    else:
                        break

    return mass_offset


def similarity_score(analyte1, analyte2, mass_offset):
    """Determine similarity score between two mass spectra. Accepts peak lists from either MS1 or MS2 spectra as inputs
    Each spectrum input is a list of tuples [(mass, relative intensity)]
    Evaluates the peak list from analyte1 against the peak list from analyte2 and creates a
    consensus peak list between the two spectra. Importantly, this includes either peaks that are exact mass matches
    between the two spectra, or sets of peaks that all differ by the same mass offset. So, for example, there might be
    some in-source fragments that are identical, but then some larger fragments that are all 14 Da higher in one analyte
    than the other. Both the matching smaller fragments and the larger signals that are offset will both be included as
    matches.

    """
    spectrum1 = analyte1.relative_experiment_mass_spectrum
    spectrum2 = analyte2.relative_experiment_mass_spectrum

    # Create list of 'consensus' masses, including both exact masses, and masses that match with the mass offset

    consensus_mass_list = []        # [[analyte1 mass, analyte2 mass, analyte1 mass intensity, analyte2 mass intensity]]
    analyte1_mass_completed_list = []
    analyte2_mass_completed_list = []

    # First find all the exact matches

    for mass_peak1 in spectrum1:
        for mass_peak2 in spectrum2:
            if round(mass_peak1.average_mass, 1) == round(mass_peak2.average_mass, 1):
                consensus_mass_list.append([round(mass_peak1.average_mass, 1),
                                            round(mass_peak2.average_mass, 1),
                                            mass_peak1.relative_intensity,
                                            mass_peak2.relative_intensity])
                analyte1_mass_completed_list.append(round(mass_peak1.average_mass, 1))
                analyte2_mass_completed_list.append(round(mass_peak2.average_mass, 1))
                break

    # Next find all the mass offset matches as long as the mass offset is not 'None' (which is true if the same mass
    # offset doesn't occur a defined number of times (set in config file) between peaks in the two spectra)

    if mass_offset:
        for mass_peak1 in spectrum1:
            if round(mass_peak1.average_mass, 1) not in analyte1_mass_completed_list:
                for mass_peak2 in spectrum2:
                    if round(mass_peak2.average_mass, 1) not in analyte2_mass_completed_list:
                        if round(mass_peak1.average_mass, 1) == round(mass_peak2.average_mass, 1) + mass_offset:
                            consensus_mass_list.append([round(mass_peak1.average_mass, 1),
                                                        round(mass_peak2.average_mass, 1),
                                                        mass_peak1.relative_intensity,
                                                        mass_peak2.relative_intensity])
                            analyte1_mass_completed_list.append(round(mass_peak1.average_mass, 1))
                            analyte2_mass_completed_list.append(round(mass_peak2.average_mass, 1))
                            break

    # Next add all analyte 1 peaks that have no match

    for mass_peak1 in spectrum1:
        if round(mass_peak1.average_mass, 1) not in analyte1_mass_completed_list:
            consensus_mass_list.append([round(mass_peak1.average_mass, 1),
                                        None,
                                        mass_peak1.relative_intensity,
                                        0])

    # Next add all analyte 2 peaks that have no match

    for mass_peak2 in spectrum2:
        if round(mass_peak2.average_mass, 1) not in analyte2_mass_completed_list:
            consensus_mass_list.append([None,
                                        round(mass_peak2.average_mass, 1),
                                        0,
                                        mass_peak2.relative_intensity])

    consensus_mass_array = np.array(consensus_mass_list)
    analyte1_vector_array = consensus_mass_array[:, 2]
    analyte2_vector_array = consensus_mass_array[:, 3]

    # Return match score
    # return round(cosine_score(analyte1_vector_array, analyte2_vector_array), 3)
    return round(weighted_match_score(analyte1_vector_array, analyte2_vector_array), 3)


def similarity_matrix(analyte_list):
    """Create similarity matrix for all analytes in a list"""
    similarity_data = []

    for analyte1 in analyte_list:
        insert_data = []
        for analyte2 in analyte_list:
            mass_offset = find_mass_offset(analyte1, analyte2)
            similarity_value = similarity_score(analyte1, analyte2, mass_offset)
            insert_data.append(similarity_value)
        similarity_data.append(insert_data)

    return similarity_data


def similarity_network_graph(input_structure):
    """Create network graph for all analytes from list, based on similarity matrix"""
    print("Starting creation of network similarity graph")

    # Load experiment analyte mass spectra
    with open(os.path.join(input_structure.output_directory,
                           "Samples",
                           input_structure.experiment_name + "_experiment_analyte_mass_spectra.pickle"), "rb") as f:
        analyte_list = pickle.load(f)

    # Create similarity matrix between all analytes
    similarity_data = similarity_matrix(analyte_list)

    # Create similarity network for analyte set.
    similarity_graph = nx.Graph()

    analyte_position_dict = {}
    for index, analyte in enumerate(analyte_list):
        analyte_position_dict[index] = analyte.experiment_analyte_id
        similarity_graph.add_node(analyte.experiment_analyte_id,
                                  blank_match=analyte.experiment_analyte_is_blank)

    for i, row in enumerate(similarity_data):
        for j, data in enumerate(row):
            if data > config.spectral_matching_minimum_cosine_score:
                similarity_graph.add_edge(analyte_position_dict[i], analyte_position_dict[j])

    with open(os.path.join(input_structure.output_directory,
                           input_structure.experiment_name + "_experiment_analyte_molecular_network_weighted.graphML"),
              "wb") as g:
        nx.write_graphml(similarity_graph, g)

    print("Network similarity graph complete")
