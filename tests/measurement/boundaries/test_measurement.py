import unittest

from evedata.measurement.boundaries import measurement


class TestMeasurement(unittest.TestCase):
    def setUp(self):
        self.measurement = measurement.Measurement()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "devices",
            "machine",
            "beamline",
            "metadata",
            "scan",
            "setup",
            "log_messages",
            "data",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.measurement, attribute))
