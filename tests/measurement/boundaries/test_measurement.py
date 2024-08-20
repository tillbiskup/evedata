import os
import unittest

import h5py
import numpy as np

import evedata.evefile.entities.data
from evedata.measurement.boundaries import measurement


class DummyHDF5File:
    def __init__(self, filename=""):
        self.filename = filename

    def create(self, set_preferred=True):
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
            if set_preferred:
                c1.attrs["preferredAxis"] = np.bytes_(["SimMot:01"])
                c1.attrs["preferredChannel"] = np.bytes_(["SimChan:01"])
            main = c1.create_group("main")
            meta = c1.create_group("meta")
            simmot = main.create_dataset(
                "SimMot:01",
                data=np.ndarray(
                    [5],
                    dtype=np.dtype(
                        [("PosCounter", "<i4"), ("SimMot:01", "<f8")]
                    ),
                ),
            )
            simmot["PosCounter"] = np.linspace(1, 5, 5)
            simmot["SimMot:01"] = np.random.random(5)
            simmot.attrs["Name"] = np.bytes_(["foo"])
            simmot.attrs["Unit"] = np.bytes_(["eV"])
            simmot.attrs["Access"] = np.bytes_(["ca:foobar"])
            simmot.attrs["DeviceType"] = np.bytes_(["Axis"])
            simchan = main.create_dataset(
                "SimChan:01",
                data=np.ndarray(
                    [5],
                    dtype=np.dtype(
                        [("PosCounter", "<i4"), ("SimChan:01", "<f8")]
                    ),
                ),
            )
            simchan["PosCounter"] = np.linspace(1, 5, 5)
            simchan["SimChan:01"] = np.random.random(5)
            simchan.attrs["Name"] = np.bytes_(["bar"])
            simchan.attrs["Unit"] = np.bytes_(["A"])
            simchan.attrs["Access"] = np.bytes_(["ca:barbaz"])
            simchan.attrs["DeviceType"] = np.bytes_(["Channel"])
            simchan.attrs["Detectortype"] = np.bytes_(["Standard"])
            data = np.ndarray(
                [5],
                dtype=np.dtype(
                    [("PosCounter", "<i4"), ("PosCountTimer", "<i4")]
                ),
            )
            data["PosCounter"] = np.linspace(1, 5, 5)
            data["PosCountTimer"] = np.linspace(42, 814, 5)
            poscounttimer = meta.create_dataset("PosCountTimer", data=data)
            poscounttimer.attrs["Unit"] = np.bytes_(["msecs"])

            log_messages = [
                b"2024-07-25T10:04:03: Lorem ipsum",
                b"2024-07-25T10:05:23: dolor sit amet",
            ]
            LiveComment = file.create_dataset(
                "LiveComment", data=np.asarray(log_messages)
            )


class TestMeasurement(unittest.TestCase):
    def setUp(self):
        self.measurement = measurement.Measurement()
        self.filename = "file.h5"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

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

    def test_setting_filename_sets_metadata_filename(self):
        self.measurement.filename = self.filename
        self.assertEqual(self.measurement.metadata.filename, self.filename)

    def test_load_with_filename_sets_metadata_filename(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        self.assertEqual(self.filename, self.measurement.metadata.filename)

    def test_load_without_filename_but_filename_set_keeps_filename(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.filename = self.filename
        self.measurement.load()
        self.assertEqual(self.filename, self.measurement.metadata.filename)

    def test_load_sets_file_metadata(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        root_mappings = {
            "eveh5_version": "7",
            "measurement_station": "Unittest",
        }
        for key, value in root_mappings.items():
            with self.subTest(key=key, val=value):
                self.assertEqual(
                    getattr(self.measurement.metadata, key), value
                )

    def test_init_with_filename_sets_metadata_filename(self):
        file = measurement.Measurement(filename=self.filename)
        self.assertEqual(self.filename, file.metadata.filename)

    def test_load_sets_log_messages(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        self.assertTrue(self.measurement.log_messages)

    def test_load_sets_device_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        self.assertTrue(self.measurement.devices)
        for item in self.measurement.devices.values():
            self.assertIsInstance(
                item, evedata.evefile.entities.data.MeasureData
            )

    def test_load_sets_data_to_preferred_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        np.testing.assert_array_equal(
            self.measurement.data.data,
            self.measurement.devices["SimChan:01"].data,
        )
        np.testing.assert_array_equal(
            self.measurement.data.axes[0].values,
            self.measurement.devices["SimMot:01"].data,
        )

    def test_load_does_not_set_data_if_no_preferred_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(set_preferred=False)
        self.measurement.load(filename=self.filename)
        self.assertEqual(0, len(self.measurement.data.data))
        self.assertEqual(0, len(self.measurement.data.axes[0].values))

    def test_load_with_preferred_data_sets_axis_metadata(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        self.assertEqual("foo", self.measurement.data.axes[0].quantity)
        self.assertEqual("eV", self.measurement.data.axes[0].unit)
        self.assertEqual("bar", self.measurement.data.axes[1].quantity)
        self.assertEqual("A", self.measurement.data.axes[1].unit)
