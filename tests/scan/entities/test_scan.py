import unittest

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
            "is_main_axis",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.axis, attribute))


class TestSnapshotModule(unittest.TestCase):
    def setUp(self):
        self.module = scan.SnapshotModule()

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
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.positioning, attribute))
