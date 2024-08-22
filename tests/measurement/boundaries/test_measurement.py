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
            simmot2 = main.create_dataset(
                "SimMot:02",
                data=np.ndarray(
                    [5],
                    dtype=np.dtype(
                        [("PosCounter", "<i4"), ("SimMot:02", "<f8")]
                    ),
                ),
            )
            simmot2["PosCounter"] = np.linspace(6, 10, 5)
            simmot2["SimMot:02"] = np.random.random(5)
            simmot2.attrs["Name"] = np.bytes_(["baf"])
            simmot2.attrs["Unit"] = np.bytes_(["nm"])
            simmot2.attrs["Access"] = np.bytes_(["ca:foobaz"])
            simmot2.attrs["DeviceType"] = np.bytes_(["Axis"])
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
            simchan2 = main.create_dataset(
                "SimChan:02",
                data=np.ndarray(
                    [5],
                    dtype=np.dtype(
                        [("PosCounter", "<i4"), ("SimChan:02", "<f8")]
                    ),
                ),
            )
            simchan2["PosCounter"] = np.linspace(6, 10, 5)
            simchan2["SimChan:02"] = np.random.random(5)
            simchan2.attrs["Name"] = np.bytes_(["baz"])
            simchan2.attrs["Unit"] = np.bytes_(["mA"])
            simchan2.attrs["Access"] = np.bytes_(["ca:bazfoo"])
            simchan2.attrs["DeviceType"] = np.bytes_(["Channel"])
            simchan2.attrs["Detectortype"] = np.bytes_(["Standard"])
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

    def test_load_sets_device_names(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        self.assertTrue(self.measurement.device_names)
        device_names = {
            value.metadata.name: key
            for key, value in self.measurement.devices.items()
        }
        self.assertDictEqual(device_names, self.measurement.device_names)

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
        self.assertEqual(
            self.measurement.devices[
                self.measurement.metadata.preferred_axis
            ].metadata.name,
            self.measurement.data.axes[0].quantity,
        )
        self.assertEqual(
            self.measurement.devices[
                self.measurement.metadata.preferred_axis
            ].metadata.unit,
            self.measurement.data.axes[0].unit,
        )
        self.assertEqual(
            self.measurement.devices[
                self.measurement.metadata.preferred_channel
            ].metadata.name,
            self.measurement.data.axes[1].quantity,
        )
        self.assertEqual(
            self.measurement.devices[
                self.measurement.metadata.preferred_channel
            ].metadata.unit,
            self.measurement.data.axes[1].unit,
        )

    def test_preferred_data_sets_current_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        self.assertEqual("SimChan:01", self.measurement.current_data)

    def test_preferred_data_sets_current_axes(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        self.assertListEqual(["SimMot:01"], self.measurement.current_axes)

    def test_set_data_sets_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        name = "SimChan:02"
        self.measurement.set_data(name=name)
        np.testing.assert_array_equal(
            self.measurement.data.data,
            self.measurement.devices[name].data,
        )

    def test_set_data_sets_current_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        name = "SimChan:02"
        self.measurement.set_data(name=name)
        self.assertEqual(name, self.measurement.current_data)

    def test_current_data_is_read_only(self):
        with self.assertRaises(AttributeError):
            self.measurement.current_data = "foo"  # noqa

    def test_set_data_sets_axis_metadata(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        name = "SimChan:02"
        self.measurement.set_data(name=name)
        self.assertEqual(
            self.measurement.devices[name].metadata.name,
            self.measurement.data.axes[1].quantity,
        )
        self.assertEqual(
            self.measurement.devices[name].metadata.unit,
            self.measurement.data.axes[1].unit,
        )

    def test_set_data_with_name_sets_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        dataset_id = "SimChan:02"
        name = self.measurement.devices[dataset_id].metadata.name
        self.measurement.set_data(name=name)
        np.testing.assert_array_equal(
            self.measurement.data.data,
            self.measurement.devices[dataset_id].data,
        )

    def test_set_axes_sets_axes(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        name = "SimMot:02"
        self.measurement.set_axes(names=[name])
        np.testing.assert_array_equal(
            self.measurement.data.axes[0].values,
            self.measurement.devices[name].data,
        )

    def test_set_axes_sets_current_axes(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        name = "SimMot:02"
        self.measurement.set_axes(names=[name])
        self.assertListEqual([name], self.measurement.current_axes)

    def test_current_axes_is_read_only(self):
        with self.assertRaises(AttributeError):
            self.measurement.current_axes = ["foo"]  # noqa

    def test_set_axes_sets_axis_metadata(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        name = "SimMot:02"
        self.measurement.set_axes(names=[name])
        self.assertEqual(
            self.measurement.devices[name].metadata.name,
            self.measurement.data.axes[0].quantity,
        )
        self.assertEqual(
            self.measurement.devices[name].metadata.unit,
            self.measurement.data.axes[0].unit,
        )

    def test_set_axes_with_name_sets_axes(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        dataset_id = "SimMot:02"
        name = self.measurement.devices[dataset_id].metadata.name
        self.measurement.set_axes(names=[name])
        np.testing.assert_array_equal(
            self.measurement.data.axes[0].values,
            self.measurement.devices[dataset_id].data,
        )

    def test_get_name_returns_name(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        dataset_id = "SimMot:02"
        name = self.measurement.devices[dataset_id].metadata.name
        self.assertEqual(name, self.measurement.get_name(dataset_id))

    def test_get_name_with_list_returns_list_of_names(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        dataset_id = ["SimMot:02", "SimChan:01"]
        names = [
            self.measurement.devices[device].metadata.name
            for device in dataset_id
        ]
        self.assertListEqual(names, self.measurement.get_name(dataset_id))

    def test_set_data_if_no_preferred_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(set_preferred=False)
        self.measurement.load(filename=self.filename)
        name = "SimChan:01"
        self.measurement.set_data(name=name)
        np.testing.assert_array_equal(
            self.measurement.data.data,
            self.measurement.devices[name].data,
        )

    def test_set_axes_if_no_preferred_data_raises(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(set_preferred=False)
        self.measurement.load(filename=self.filename)
        name = "SimMot:01"
        with self.assertRaisesRegex(ValueError, "No data to set axes for"):
            self.measurement.set_axes(names=[name])

    def test_set_data_with_field_name(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        name = "SimChan:01"
        field = "positions"
        self.measurement.set_data(name=name, field=field)
        np.testing.assert_array_equal(
            self.measurement.data.data,
            getattr(self.measurement.devices[name], field),
        )

    def test_set_axes_with_field_name(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        name = "SimMot:01"
        field = "positions"
        self.measurement.set_axes(names=[name], fields=[field])
        np.testing.assert_array_equal(
            self.measurement.data.axes[0].values,
            getattr(self.measurement.devices[name], field),
        )

    def test_set_axes_with_different_length_of_names_and_fields_raises(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        names = ["SimMot:01"]
        fields = ["positions", "data"]
        with self.assertRaisesRegex(
            IndexError, "Names and fields need to " "be of same length"
        ):
            self.measurement.set_axes(names=names, fields=fields)
