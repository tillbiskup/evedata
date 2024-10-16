import unittest

import numpy as np

from evedata.evefile.controllers import mpskip
from evedata.evefile.entities.data import ImporterPreprocessingStep


class MockSkipData:

    def __init__(self):
        self.data = np.array([])
        self.positions = np.array([])


class TestRearrangeRawValues(unittest.TestCase):
    def setUp(self):
        self.processing = mpskip.RearrangeRawValues()
        self.data = np.ndarray(
            [12],
            dtype=np.dtype(
                [
                    ("PosCounter", "<i4"),
                    ("foo", "f8"),
                ]
            ),
        )
        self.data["PosCounter"] = np.array(
            [5, 6, 8, 9, 10, 12, 13, 14, 15, 17, 18, 19]
        )
        self.data["foo"] = np.arange(12)
        self.skip_data = MockSkipData()
        self.skip_data.positions = self.data["PosCounter"]
        self.skip_data.data = np.array([1, 2, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3])

    def test_instantiate_class(self):
        pass

    def test_is_preprocessing_step(self):
        self.assertIsInstance(self.processing, ImporterPreprocessingStep)

    def test_has_attributes(self):
        attributes = [
            "skip_data",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.processing, attribute))

    def test_splits_raw_values(self):
        self.processing.skip_data = self.skip_data
        result = self.processing.process(self.data)
        self.assertEqual(4, len(result))

    def test_sets_correct_positions(self):
        self.processing.skip_data = self.skip_data
        result = self.processing.process(self.data)
        self.assertListEqual([4, 7, 11, 16], list(result["PosCounter"]))
