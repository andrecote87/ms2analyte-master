#!/usr/bin/env python3

"""Unit tests for the drift_features module"""

import unittest
from unittest.mock import patch

from ms2analyte.calculate import drift_features
from ms2analyte import config


class TestDriftFeatures(unittest.TestCase):
    """Class to test functions in the drift features module"""
    @patch.object(config, 'get', drift_time_error=5)
    def test_average_drift_validate(self):
        """Test that average drift function returns correct value"""
        drift_list = [10, 10, 10, 20, 20, 20]
        result = drift_features.average_drift(drift_list)
        self.assertEqual(result, 15.0, "Should be 15.0")

    def test_drift_match_validate(self):
        result = drift_features.drift_match(10, 12)
        self.assertTrue(result, "Config.drift_time_error patched to 5 in test. Drift 1 = 10, Drift 2 = 12. "
                                "Should be True")

    def test_drift_match_time_difference(self):
        result = drift_features.drift_match(10, 20)
        self.assertFalse(result, "Config.drift_time_error patched to 5 in test. Drift 1 = 10, Drift 2 = 20. "
                                 "Should be False")


if __name__ == "__main__":
    unittest.main()
