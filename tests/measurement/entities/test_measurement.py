import unittest

from evedata.measurement.entities import measurement


class TestMeasurement(unittest.TestCase):
    def setUp(self):
        self.measurement = measurement.Measurement()

    def test_instantiate_class(self):
        pass


class TestData(unittest.TestCase):
    def setUp(self):
        self.data = measurement.Data()

    def test_instantiate_class(self):
        pass


class TestAxis(unittest.TestCase):
    def setUp(self):
        self.axis = measurement.Axis()

    def test_instantiate_class(self):
        pass
