import unittest

from evedata.measurement.controllers import harmonising


class TestHarmonisation(unittest.TestCase):
    def setUp(self):
        self.harmonisation = harmonising.Harmonisation()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "measurement",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.harmonisation, attribute))

    def test_initialise_with_measurement_sets_measurement(self):
        measurement = "foo"
        harmonisation = harmonising.Harmonisation(measurement=measurement)
        self.assertEqual(measurement, harmonisation.measurementgit)

    def test_harmonise_without_measurement_raises(self):
        self.harmonisation.measurement = None
        with self.assertRaisesRegex(
            ValueError, "Need a measurement to harmonise data."
        ):
            self.harmonisation.harmonise()

    def test_harmonise_without_data_raises(self):
        self.harmonisation.measurement = "foo"
        with self.assertRaisesRegex(
            ValueError, "Need data to harmonise data."
        ):
            self.harmonisation.harmonise()

    def test_harmonise_without_axes_raises(self):
        self.harmonisation.measurement = "foo"
        with self.assertRaisesRegex(
            ValueError, "Need axes to harmonise data."
        ):
            self.harmonisation.harmonise(data="foo")
