import unittest

from evedata.measurement.boundaries import measurement


class TestMeasurement(unittest.TestCase):
    def setUp(self):
        self.measurement = measurement.Measurement()

    def test_instantiate_class(self):
        pass
