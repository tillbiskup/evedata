import os
import unittest

import h5py
import numpy as np

from evedata.evefile.boundaries import evefile


class DummyHDF5File:
    def __init__(self, filename=""):
        self.filename = filename

    def create(self):
        with h5py.File(self.filename, "w") as file:
            file.attrs["EVEH5Version"] = np.bytes_(["7"])
            file.attrs["Version"] = np.bytes_(["2.0"])
            file.attrs["XMLversion"] = np.bytes_(["9.2"])
            file.attrs["Comment"] = np.bytes_([""])
            file.attrs["Location"] = np.bytes_(["Unittest"])
            file.attrs["StartTimeISO"] = np.bytes_(["2024-06-03T12:01:32"])
            file.attrs["EndTimeISO"] = np.bytes_(["2024-06-03T12:01:37"])
            file.attrs["Simulation"] = np.bytes_(["no"])
            c1 = file.create_group("c1")
            main = c1.create_group("main")
            meta = c1.create_group("meta")
            test = main.create_dataset(
                "test",
                data=np.ones(
                    [5, 2],
                    dtype=np.dtype([("PosCounter", "<i4"), ("fooo", "<f8")]),
                ),
            )
            test.attrs["Name"] = np.bytes_(["foo"])
            test.attrs["Access"] = np.bytes_(["ca:foobar"])
            test.attrs["DeviceType"] = np.bytes_(["Axis"])
            data = np.ndarray(
                [],
                dtype=np.dtype(
                    [("PosCounter", "<i4"), ("PosCountTimer", "<i4")]
                ),
            )
            poscounttimer = meta.create_dataset("PosCountTimer", data=data)
            poscounttimer.attrs["Unit"] = np.bytes_(["msecs"])


class TestEveFile(unittest.TestCase):
    def setUp(self):
        self.evefile = evefile.EveFile()
        self.filename = "file.h5"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "log_messages",
            "scan",
            "data",
            "snapshots",
            "monitors",
            "position_timestamps",
            "filename",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.evefile, attribute))

    def test_setting_filename_sets_metadata_filename(self):
        self.evefile.filename = self.filename
        self.assertEqual(self.evefile.metadata.filename, self.filename)

    def test_load_with_filename_sets_metadata_filename(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile.load(filename=self.filename)
        self.assertEqual(self.filename, self.evefile.metadata.filename)

    def test_load_without_filename_but_filename_set_keeps_filename(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile.filename = self.filename
        self.evefile.load()
        self.assertEqual(self.filename, self.evefile.metadata.filename)

    def test_load_sets_file_metadata(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile.load(filename=self.filename)
        root_mappings = {
            "eveh5_version": "7",
            "measurement_station": "Unittest",
        }
        for key, value in root_mappings.items():
            with self.subTest(key=key, val=value):
                self.assertEqual(getattr(self.evefile.metadata, key), value)
