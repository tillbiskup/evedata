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
        data = np.arange(12).reshape(2, -1).T
        positions = np.array([2, 3, 5])
        self.processing.positions = positions
        result = self.processing.process(data)
        self.assertListEqual(list(positions), list(result[:, 0]))
        self.assertEqual(data.ndim, result.ndim)
