import unittest

import numpy as np

from evedata.measurement.controllers import harmonising


class MockDevice:
    def __init__(
        self, data=np.random.random(5), positions=np.linspace(0, 4, 5)
    ):
        self.data = data
        self.positions = positions


class MockMeasurement:
    def __init__(self):
        self.devices = {
            "SimChan:01": MockDevice(),
            "SimMot:01": MockDevice(),
        }


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
        self.assertEqual(measurement, harmonisation.measurement)

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

    def test_harmonise_returns_list(self):
        self.harmonisation.measurement = "foo"
        result = self.harmonisation.harmonise(
            data=("foo", None), axes=("bar", None)
        )
        self.assertIsInstance(result, list)


class TestLastFill(unittest.TestCase):
    def setUp(self):
        self.harmonisation = harmonising.AxesLastFill()
        self.harmonisation.measurement = MockMeasurement()

    def test_instantiate_class(self):
        pass

    def test_harmonise_returns_list_of_numpy_arrays(self):
        result = self.harmonisation.harmonise(
            data=("SimChan:01", None), axes=(("SimMot:01", None),)
        )
        self.assertTrue(result)
        for element in result:
            self.assertIsInstance(element, np.ndarray)

    def test_harmonise_returns_only_values_for_data_positions(self):
        self.harmonisation.measurement.devices = {
            "SimChan:01": MockDevice(
                data=np.random.random(5), positions=np.linspace(0, 4, 5)
            ),
            "SimMot:01": MockDevice(
                data=np.random.random(7), positions=np.linspace(0, 6, 7)
            ),
        }
        result = self.harmonisation.harmonise(
            data=("SimChan:01", None), axes=(("SimMot:01", None),)
        )
        self.assertEqual(len(result[0]), len(result[1]))

    def test_harmonise_returns_only_values_for_data_positions_with_gaps(self):
        self.harmonisation.measurement.devices = {
            "SimChan:01": MockDevice(
                data=np.random.random(4), positions=np.asarray([0, 2, 3, 4])
            ),
            "SimMot:01": MockDevice(
                data=np.random.random(7), positions=np.linspace(0, 6, 7)
            ),
        }
        result = self.harmonisation.harmonise(
            data=("SimChan:01", None), axes=(("SimMot:01", None),)
        )
        self.assertEqual(len(result[0]), len(result[1]))

    def test_harmonise_fills_axes_values(self):
        self.harmonisation.measurement.devices = {
            "SimChan:01": MockDevice(
                data=np.random.random(5), positions=np.linspace(0, 4, 5)
            ),
            "SimMot:01": MockDevice(
                data=np.random.random(4), positions=np.linspace(0, 3, 4)
            ),
        }
        result = self.harmonisation.harmonise(
            data=("SimChan:01", None), axes=(("SimMot:01", None),)
        )
        self.assertEqual(len(result[0]), len(result[1]))
        np.testing.assert_array_equal(
            self.harmonisation.measurement.devices["SimMot:01"].data,
            result[1][:-1],
        )
        self.assertEqual(result[1][-2], result[1][-1])

    def test_harmonise_fills_axes_values_with_gaps(self):
        self.harmonisation.measurement.devices = {
            "SimChan:01": MockDevice(
                data=np.random.random(5), positions=np.linspace(0, 4, 5)
            ),
            "SimMot:01": MockDevice(
                data=np.random.random(4), positions=np.asarray([0, 2, 4])
            ),
        }
        result = self.harmonisation.harmonise(
            data=("SimChan:01", None), axes=(("SimMot:01", None),)
        )
        self.assertEqual(len(result[0]), len(result[1]))
        self.assertEqual(result[1][0], result[1][1])
        self.assertEqual(result[1][2], result[1][3])

    def test_harmonise_with_data_attribute_returns_correct_values(self):
        result = self.harmonisation.harmonise(
            data=("SimChan:01", "positions"), axes=(("SimMot:01", None),)
        )
        np.testing.assert_array_equal(
            self.harmonisation.measurement.devices["SimChan:01"].positions,
            result[0],
        )

    def test_harmonise_with_axes_attribute_returns_correct_values(self):
        result = self.harmonisation.harmonise(
            data=("SimChan:01", None), axes=(("SimMot:01", "positions"),)
        )
        np.testing.assert_array_equal(
            self.harmonisation.measurement.devices["SimMot:01"].positions,
            result[1],
        )


class TestHarmonisationFactory(unittest.TestCase):
    def setUp(self):
        self.factory = harmonising.HarmonisationFactory()

    def test_instantiate_class(self):
        pass

    def test_get_harmonisation_returns_harmonisation(self):
        self.assertIsInstance(
            self.factory.get_harmonisation(), harmonising.Harmonisation
        )

    def test_get_harmonisation_with_type_returns_correct_harmonisation(self):
        self.assertIsInstance(
            self.factory.get_harmonisation(mode="AxesLastFill"),
            harmonising.Harmonisation,
        )

    def test_initialise_with_measurement_sets_measurement(self):
        measurement = "foo"
        factory = harmonising.HarmonisationFactory(measurement=measurement)
        self.assertEqual(measurement, factory.measurement)

    def test_get_harmonisation_with_measurement_sets_measurement(self):
        self.factory.measurement = "foo"
        harmonisation = self.factory.get_harmonisation()
        self.assertEqual(self.factory.measurement, harmonisation.measurement)
