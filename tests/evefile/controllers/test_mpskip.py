import copy
import logging
import unittest

import numpy as np

from evedata.evefile.controllers import mpskip
from evedata.evefile.entities.data import ImporterPreprocessingStep


class MockSkipData:

    def __init__(self):
        self.data = np.array([])
        self.positions = np.array([])

    def get_parent_positions(self):
        return np.append(
            self.positions[0] - 1,
            self.positions[np.where(np.diff(self.positions) > 1)[0]] + 1,
        )


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


class MockEveFile:

    def __init__(self):
        self.scan = MockScanBoundary()
        self.scan_modules = {}

    def has_scan(self):
        return bool(self.scan)


class MockScanBoundary:

    def __init__(self):
        self.scan = MockScan()


class MockScan:

    def __init__(self):
        self.scan_modules = {}

    def add_scan_modules(self):
        outer_module = MockScanModule()
        outer_module.id = 1
        outer_module.name = "WL"
        outer_module.parent = 0
        outer_module.add_axis("nmEnerg:io2600wl2e.A")
        self.scan_modules.update({outer_module.id: outer_module})

        inner_module = MockScanModule()
        inner_module.id = 2
        inner_module.name = "Skip"
        inner_module.parent = 1
        channel_names = [
            "MPSKIP:euvr01chan1",
            "MPSKIP:euvr01skipcountchan1",
            "K0617:gw24126chan1",
            "A2980:gw24103chan1",
            "PPESM9:pi03500000.RBVchan1",
            "Energ:io2600e2wlchan1",
        ]
        for channel_name in channel_names:
            inner_module.add_channel(channel_name)
        inner_module.add_axis("Counter-mot")
        self.scan_modules.update({inner_module.id: inner_module})


class MockScanModule:

    def __init__(self):
        self.id = -1
        self.name = ""
        self.parent = -1
        self.axes = {}
        self.channels = {}

    def has_mpskip(self):
        return bool(
            [name for name in self.channels if name.startswith("MPSKIP")]
        )

    def add_axis(self, id=""):
        self.axes.update({id: MockAxisChannel(id=id)})

    def add_channel(self, id=""):
        self.channels.update({id: MockAxisChannel(id=id)})


class MockAxisChannel:

    def __init__(self, id=""):
        self.id = id


class TestMpskip(unittest.TestCase):
    def setUp(self):
        self.mapper = mpskip.Mpskip()
        self.logger = logging.getLogger(name="evedata")
        self.logger.setLevel(logging.WARNING)
        self.source = MockEveFile()
        self.source.scan.scan.add_scan_modules()
        self.source.scan_modules = copy.deepcopy(
            self.source.scan.scan.scan_modules
        )

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "source",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.mapper, attribute))

    def test_map_without_source_raises(self):
        self.mapper.source = None
        with self.assertRaises(ValueError):
            self.mapper.map()

    def test_map_with_source_sets_source(self):
        self.mapper.map(source=self.source)
        self.assertEqual(self.source, self.mapper.source)

    def test_map_without_scan_logs(self):
        source = MockEveFile()
        source.scan = None
        self.logger.setLevel(logging.DEBUG)
        with self.assertLogs(level=logging.DEBUG) as captured:
            self.mapper.map(source=source)
        self.assertEqual(len(captured.records), 1)
        self.assertEqual(
            captured.records[0].getMessage(),
            "No scan, hence no mpskip mapping.",
        )

    def test_map_removes_mpskip_module_from_scan_modules(self):
        self.mapper.map(source=self.source)
        self.assertNotIn(
            "Skip",
            [sm.name for sm in self.mapper.source.scan_modules.values()],
        )

    def test_map_adds_channels_to_parent_scan_module(self):
        self.mapper.map(source=self.source)
        self.assertTrue(self.mapper.source.scan_modules[1].channels)

    def test_map_does_not_add_mpskip_channels_to_parent_scan_module(self):
        self.mapper.map(source=self.source)
        self.assertFalse(
            [
                name
                for name in self.mapper.source.scan_modules[1].channels
                if name.startswith("MPSKIP")
            ]
        )
