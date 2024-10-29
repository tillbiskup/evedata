import logging
import unittest

import numpy as np

from evedata.scan.entities import scan


class TestScan(unittest.TestCase):
    def setUp(self):
        self.scan = scan.Scan()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "repeat_count",
            "comment",
            "description",
            "scan_modules",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.scan, attribute))


class TestAbstractScanModule(unittest.TestCase):
    def setUp(self):
        self.module = scan.AbstractScanModule()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "id",
            "name",
            "parent",
            "appended",
            "nested",
            "is_nested",
            "number_of_positions",
            "number_of_positions_per_pass",
            "positions",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.module, attribute))


class TestScanModule(unittest.TestCase):
    def setUp(self):
        self.module = scan.ScanModule()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "id",
            "name",
            "parent",
            "appended",
            "nested",
            "axes",
            "channels",
            "positionings",
            "pre_scan_settings",
            "post_scan_settings",
            "number_of_measurements",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.module, attribute))

    def test_has_mpskip_without_mpskip(self):
        self.assertIsInstance(self.module.has_mpskip(), bool)
        self.assertFalse(self.module.has_mpskip())

    def test_has_mpskip_with_mpskip(self):
        self.module.channels["MPSKIP:euvr01chan1"] = scan.Channel()
        self.module.channels["MPSKIP:euvr01skipcountchan1"] = scan.Channel()
        self.assertTrue(self.module.has_mpskip())

    def test_has_device_with_channel(self):
        device_name = "SimChan01"
        self.module.channels[device_name] = scan.Channel()
        self.assertTrue(self.module.has_device(device_name))

    def test_has_device_with_axis(self):
        device_name = "SimMot01"
        self.module.axes[device_name] = scan.Axis()
        self.assertTrue(self.module.has_device(device_name))


class TestChannel(unittest.TestCase):
    def setUp(self):
        self.channel = scan.Channel()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "id",
            "normalize_id",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.channel, attribute))


class TestAxis(unittest.TestCase):
    def setUp(self):
        self.axis = scan.Axis()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "id",
            "step_function",
            "position_mode",
            "positions",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.axis, attribute))


class TestSnapshotModule(unittest.TestCase):
    def setUp(self):
        self.module = scan.StaticSnapshotModule()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "id",
            "name",
            "parent",
            "appended",
            "nested",
            "axes",
            "channels",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.module, attribute))

    def test_default_setting_of_some_attributes(self):
        self.assertEqual(1, self.module.number_of_positions)
        self.assertEqual(1, self.module.number_of_positions_per_pass)


class TestPositioning(unittest.TestCase):
    def setUp(self):
        self.positioning = scan.Positioning()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "axis_id",
            "channel_id",
            "normalize_channel_id",
            "type",
            "parameters",
            "position",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.positioning, attribute))


class TestDynamicSnapshotModule(unittest.TestCase):
    def setUp(self):
        self.module = scan.DynamicSnapshotModule()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "id",
            "name",
            "parent",
            "appended",
            "nested",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.module, attribute))

    def test_default_setting_of_some_attributes(self):
        self.assertEqual(1, self.module.number_of_positions)
        self.assertEqual(1, self.module.number_of_positions_per_pass)


class TestAverageChannel(unittest.TestCase):
    def setUp(self):
        self.channel = scan.AverageChannel()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "id",
            "normalize_id",
            "n_averages",
            "low_limit",
            "max_attempts",
            "max_deviation",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.channel, attribute))


class TestIntervalChannel(unittest.TestCase):
    def setUp(self):
        self.channel = scan.IntervalChannel()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "id",
            "normalize_id",
            "trigger_interval",
            "stopped_by",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.channel, attribute))


class TestPreScan(unittest.TestCase):
    def setUp(self):
        self.pre_scan = scan.PreScan()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "id",
            "value",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.pre_scan, attribute))


class TestPostScan(unittest.TestCase):
    def setUp(self):
        self.post_scan = scan.PostScan()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = ["id", "value", "reset_original_value"]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.post_scan, attribute))


class TestStepFunction(unittest.TestCase):
    def setUp(self):
        self.step_function = scan.StepFunction()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "positions",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.step_function, attribute))

    def test_has_calculate_positions_method(self):
        self.step_function.calculate_positions()


class TestStepRange(unittest.TestCase):
    def setUp(self):
        self.step_function = scan.StepRange()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "positions",
            "mode",
            "start",
            "stop",
            "step_width",
            "is_main_axis",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.step_function, attribute))

    def test_calculate_positions_sets_positions(self):
        self.step_function.start = 1
        self.step_function.stop = 5
        self.step_function.step_width = 2
        self.step_function.calculate_positions()
        np.testing.assert_array_equal(
            np.asarray([1.0, 3.0, 5.0]),
            self.step_function.positions,
        )
        self.assertEqual("float64", self.step_function.positions.dtype.name)

    def test_stepwidth_zero_does_not_raise(self):
        self.step_function.start = 1
        self.step_function.stop = 1
        self.step_function.step_width = 0
        self.step_function.calculate_positions()
        np.testing.assert_array_equal(
            np.asarray([1.0]),
            self.step_function.positions,
        )
        self.assertEqual("float64", self.step_function.positions.dtype.name)


class TestStepRanges(unittest.TestCase):
    def setUp(self):
        self.step_function = scan.StepRanges()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "positions",
            "expression",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.step_function, attribute))

    def test_set_positions(self):
        self.step_function.positions = np.asarray([1.0, 3.0, 5.0])

    def test_calculate_positions(self):
        self.step_function.calculate_positions()


class TestStepReference(unittest.TestCase):
    def setUp(self):
        self.step_function = scan.StepReference()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "positions",
            "mode",
            "parameter",
            "axis_id",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.step_function, attribute))


class TestStepFile(unittest.TestCase):
    def setUp(self):
        self.step_function = scan.StepFile()
        self.logger = logging.getLogger(name="evedata")
        self.logger.setLevel(logging.ERROR)

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "positions",
            "filename",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.step_function, attribute))

    def test_calculate_positions_sets_empty_array(self):
        self.logger.setLevel(logging.ERROR)
        self.step_function.calculate_positions()
        self.assertIsInstance(self.step_function.positions, np.ndarray)
        np.testing.assert_array_equal(
            np.asarray([]), self.step_function.positions
        )

    def test_calculate_positions_logs_warning(self):
        self.logger.setLevel(logging.WARN)
        with self.assertLogs(level=logging.WARN) as captured:
            self.step_function.calculate_positions()
        self.assertEqual(len(captured.records), 1)
        self.assertEqual(
            captured.records[0].getMessage(),
            "Step function 'file' does not allow to obtain positions.",
        )
