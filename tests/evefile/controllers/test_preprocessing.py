import unittest

import numpy as np

from evedata.evefile.controllers import preprocessing
from evedata.evefile.entities.data import ImporterPreprocessingStep


class TestSelectPositions(unittest.TestCase):
    def setUp(self):
        self.processing = preprocessing.SelectPositions()

    def test_instantiate_class(self):
        pass

    def test_is_preprocessing_step(self):
        self.assertIsInstance(self.processing, ImporterPreprocessingStep)

    def test_has_attributes(self):
        attributes = [
            "positions",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.processing, attribute))

    def test_extracts_matching_rows(self):
        raw_data = np.arange(12).reshape(2, -1).T
        dtype = np.dtype([("PosCounter", "<i4"), ("A2980:23303chan1", "<f8")])
        data = np.ndarray(raw_data.shape[0], dtype=dtype)
        for idx, name in enumerate(dtype.names):
            data[name] = raw_data[:, idx]
        positions = np.array([2, 3, 5])
        self.processing.positions = positions
        result = self.processing.process(data)
        np.testing.assert_array_equal(positions, result[dtype.names[0]])
        self.assertEqual(data.ndim, result.ndim)
