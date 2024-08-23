import unittest

import numpy as np

from evedata.measurement.controllers import joining


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


class TestJoin(unittest.TestCase):
    def setUp(self):
        self.join = joining.Join()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "measurement",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.join, attribute))

    def test_initialise_with_measurement_sets_measurement(self):
        measurement = "foo"
        join = joining.Join(measurement=measurement)
        self.assertEqual(measurement, join.measurement)

    def test_join_without_measurement_raises(self):
        self.join.measurement = None
        with self.assertRaisesRegex(
            ValueError, "Need a measurement to join data."
        ):
            self.join.join()

    def test_join_without_data_raises(self):
        self.join.measurement = "foo"
        with self.assertRaisesRegex(ValueError, "Need data to join data."):
            self.join.join()

    def test_join_without_axes_raises(self):
        self.join.measurement = "foo"
        with self.assertRaisesRegex(ValueError, "Need axes to join data."):
            self.join.join(data="foo")

    def test_join_returns_list(self):
        self.join.measurement = "foo"
        result = self.join.join(data=("foo", None), axes=("bar", None))
        self.assertIsInstance(result, list)


class TestLastFill(unittest.TestCase):
    def setUp(self):
        self.join = joining.AxesLastFill()
        self.join.measurement = MockMeasurement()

    def test_instantiate_class(self):
        pass

    def test_join_returns_list_of_numpy_arrays(self):
        result = self.join.join(
            data=("SimChan:01", None), axes=(("SimMot:01", None),)
        )
        self.assertTrue(result)
        for element in result:
            self.assertIsInstance(element, np.ndarray)

    def test_join_returns_only_values_for_data_positions(self):
        self.join.measurement.devices = {
            "SimChan:01": MockDevice(
                data=np.random.random(5), positions=np.linspace(0, 4, 5)
            ),
            "SimMot:01": MockDevice(
                data=np.random.random(7), positions=np.linspace(0, 6, 7)
            ),
        }
        result = self.join.join(
            data=("SimChan:01", None), axes=(("SimMot:01", None),)
        )
        self.assertEqual(len(result[0]), len(result[1]))

    def test_join_returns_only_values_for_data_positions_with_gaps(self):
        self.join.measurement.devices = {
            "SimChan:01": MockDevice(
                data=np.random.random(4), positions=np.asarray([0, 2, 3, 4])
            ),
            "SimMot:01": MockDevice(
                data=np.random.random(7), positions=np.linspace(0, 6, 7)
            ),
        }
        result = self.join.join(
            data=("SimChan:01", None), axes=(("SimMot:01", None),)
        )
        self.assertEqual(len(result[0]), len(result[1]))

    def test_join_fills_axes_values(self):
        self.join.measurement.devices = {
            "SimChan:01": MockDevice(
                data=np.random.random(5), positions=np.linspace(0, 4, 5)
            ),
            "SimMot:01": MockDevice(
                data=np.random.random(4), positions=np.linspace(0, 3, 4)
            ),
        }
        result = self.join.join(
            data=("SimChan:01", None), axes=(("SimMot:01", None),)
        )
        self.assertEqual(len(result[0]), len(result[1]))
        np.testing.assert_array_equal(
            self.join.measurement.devices["SimMot:01"].data,
            result[1][:-1],
        )
        self.assertEqual(result[1][-2], result[1][-1])

    def test_join_fills_axes_values_with_gap_at_beginning(self):
        self.join.measurement.devices = {
            "SimChan:01": MockDevice(
                data=np.random.random(5), positions=np.linspace(0, 4, 5)
            ),
            "SimMot:01": MockDevice(
                data=np.random.random(3), positions=np.linspace(2, 4, 3)
            ),
        }
        result = self.join.join(
            data=("SimChan:01", None), axes=(("SimMot:01", None),)
        )
        self.assertEqual(len(result[0]), len(result[1]))
        np.testing.assert_array_equal(
            self.join.measurement.devices["SimMot:01"].data,
            result[1][2:],
        )
        self.assertEqual(0, result[1][0])

    def test_join_fills_axes_values_with_gaps(self):
        self.join.measurement.devices = {
            "SimChan:01": MockDevice(
                data=np.random.random(5), positions=np.linspace(0, 4, 5)
            ),
            "SimMot:01": MockDevice(
                data=np.random.random(4), positions=np.asarray([0, 2, 4])
            ),
        }
        result = self.join.join(
            data=("SimChan:01", None), axes=(("SimMot:01", None),)
        )
        self.assertEqual(len(result[0]), len(result[1]))
        self.assertEqual(result[1][0], result[1][1])
        self.assertEqual(result[1][2], result[1][3])

    def test_join_with_data_attribute_returns_correct_values(self):
        result = self.join.join(
            data=("SimChan:01", "positions"), axes=(("SimMot:01", None),)
        )
        np.testing.assert_array_equal(
            self.join.measurement.devices["SimChan:01"].positions,
            result[0],
        )

    def test_join_with_axes_attribute_returns_correct_values(self):
        result = self.join.join(
            data=("SimChan:01", None), axes=(("SimMot:01", "positions"),)
        )
        np.testing.assert_array_equal(
            self.join.measurement.devices["SimMot:01"].positions,
            result[1],
        )


class TestJoinFactory(unittest.TestCase):
    def setUp(self):
        self.factory = joining.JoinFactory()

    def test_instantiate_class(self):
        pass

    def test_get_join_returns_join(self):
        self.assertIsInstance(self.factory.get_join(), joining.Join)

    def test_get_join_with_type_returns_correct_join(self):
        self.assertIsInstance(
            self.factory.get_join(mode="AxesLastFill"),
            joining.Join,
        )

    def test_initialise_with_measurement_sets_measurement(self):
        measurement = "foo"
        factory = joining.JoinFactory(measurement=measurement)
        self.assertEqual(measurement, factory.measurement)

    def test_get_join_with_measurement_sets_measurement(self):
        self.factory.measurement = "foo"
        join = self.factory.get_join()
        self.assertEqual(self.factory.measurement, join.measurement)
