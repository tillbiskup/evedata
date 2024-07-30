import datetime
import unittest

import numpy as np

import evedata.evefile.boundaries.evefile
import evedata.evefile.entities.file
import evedata.evefile.entities.data
from evedata.evefile.controllers import version_mapping


class MockHDF5Item:
    def __init__(self, name="", filename=""):
        self.filename = filename
        self.name = name
        self.attributes = {}


class MockHDF5Dataset(MockHDF5Item):
    def __init__(self, name="", filename=""):
        super().__init__(name=name, filename=filename)
        self.get_data_called = False
        self.dtype = np.dtype(
            [("PosCounter", "<i4"), ("A2980:23303chan1", "<f8")]
        )

    def get_data(self):
        self.get_data_called = True


class MockHDF5Group(MockHDF5Item):
    def __init__(self, name="", filename=""):
        super().__init__(name=name, filename=filename)
        self._items = {}

    def __iter__(self):
        for item in self._items.values():
            yield item

    def add_item(self, item):
        name = item.name.split("/")[-1]
        setattr(self, name, item)
        self._items[name] = item

    def item_names(self):
        return list(self._items.keys())


class MockEveH5(MockHDF5Group):

    # noinspection PyUnresolvedReferences
    def __init__(self):
        super().__init__()
        self.filename = "test.h5"
        self.name = "/"
        self.attributes = {
            "EVEH5Version": "7",
            "Location": "TEST",
            "Version": "2.0",
            "XMLversion": "9.2",
            "Comment": "",
            "Simulation": "no",
            "SCML-Author": "biskup02@a23bashful",
            "SCML-Name": "test.scml",
            "StartDate": "03.06.2024",
            "StartTime": "12:01:32",
            "StartTimeISO": "2024-06-03T12:01:32",
            "EndTimeISO": "2024-06-03T12:01:37",
        }
        self.add_item(MockHDF5Group(name="/c1", filename=self.filename))
        self.c1.attributes = {
            "EndTimeISO": "2024-06-03T12:01:37",
            "StartDate": "03.06.2024",
            "StartTime": "12:01:32",
            "StartTimeISO": "2024-06-03T12:01:32",
            "preferredAxis": "OMS58:io1501003",
            "preferredChannel": "A2980:22704chan1",
            "preferredNormalizationChannel": "A2980:22704chan1",
        }
        self.c1.add_item(
            MockHDF5Group(name="/c1/meta", filename=self.filename)
        )
        poscounttimer = MockHDF5Dataset(
            name="/c1/meta/PosCountTimer", filename=self.filename
        )
        poscounttimer.dtype = np.dtype(
            [("PosCounter", "<i4"), ("PosCountTimer", "<i4")]
        )
        poscounttimer.attributes = {"Unit": "msecs"}
        self.c1.meta.add_item(poscounttimer)


class MockEveH5v4(MockEveH5):

    # noinspection PyUnresolvedReferences
    def __init__(self):
        super().__init__()
        # Only starting with v4
        self.c1.add_item(
            MockHDF5Group(name="/c1/main", filename=self.filename)
        )

    # noinspection PyUnresolvedReferences
    def add_array_channel(self):
        # Fake array channel
        self.c1.main.add_item(
            MockHDF5Group(name="/c1/main/array", filename=self.filename)
        )
        self.c1.main.array.attributes = {
            "DeviceType": "Channel",
            "DetectorType": "Standard",
            "Access": "ca:BRQM1:mca08.VAL",
            "Name": "bsdd6_spectrum",
            "XML-ID": "BRQM1:mca08chan1",
        }
        for position in range(5, 20):
            self.c1.main.array.add_item(
                MockHDF5Dataset(
                    name=f"/c1/main/array/{position}", filename=self.filename
                )
            )
            getattr(self.c1.main.array, str(position)).dtype = np.dtype(
                [("0", "<i4")]
            )


class MockEveH5v5(MockEveH5v4):
    pass


class MockFile:
    pass


class TestVersionMapperFactory(unittest.TestCase):

    def setUp(self):
        self.factory = version_mapping.VersionMapperFactory()
        self.eveh5 = MockEveH5()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "eveh5",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.factory, attribute))

    def test_get_mapper_returns_mapper(self):
        self.factory.eveh5 = self.eveh5
        mapper = self.factory.get_mapper()
        self.assertIsInstance(mapper, version_mapping.VersionMapper)

    def test_get_mapper_with_eveh5_argument_sets_eveh5_property(self):
        self.factory.get_mapper(eveh5=self.eveh5)
        self.assertEqual(self.factory.eveh5, self.eveh5)

    def test_get_mapper_without_eveh5_raises(self):
        with self.assertRaises(ValueError):
            self.factory.get_mapper()

    def test_get_mapper_returns_correct_mapper(self):
        self.factory.eveh5 = self.eveh5
        mapper = self.factory.get_mapper()
        self.assertIsInstance(mapper, version_mapping.VersionMapperV5)

    def test_get_mapper_with_fractional_version_returns_correct_mapper(self):
        self.eveh5.attributes["EVEH5Version"] = "5.0"
        self.factory.eveh5 = self.eveh5
        mapper = self.factory.get_mapper()
        self.assertIsInstance(mapper, version_mapping.VersionMapperV5)

    def test_get_mapper_with_unknown_version_raises(self):
        self.eveh5.attributes["EVEH5Version"] = "0"
        self.factory.eveh5 = self.eveh5
        with self.assertRaises(AttributeError):
            self.factory.get_mapper()

    def test_get_mapper_sets_source_in_mapper(self):
        self.factory.eveh5 = self.eveh5
        mapper = self.factory.get_mapper()
        self.assertEqual(mapper.source, self.eveh5)


class TestVersionMapper(unittest.TestCase):
    def setUp(self):
        self.mapper = version_mapping.VersionMapper()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "source",
            "destination",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.mapper, attribute))

    def test_map_without_source_raises(self):
        self.mapper.source = None
        with self.assertRaises(ValueError):
            self.mapper.map()

    def test_map_without_destination_raises(self):
        self.mapper.source = MockEveH5()
        with self.assertRaises(ValueError):
            self.mapper.map()

    def test_map_with_source_and_destination_parameters(self):
        self.mapper.source = None
        self.mapper.map(source=MockEveH5(), destination=MockFile())

    def test_get_hdf5_dataset_importer_returns_importer(self):
        self.assertIsInstance(
            self.mapper.get_hdf5_dataset_importer(dataset=MockHDF5Dataset()),
            evedata.evefile.entities.data.HDF5DataImporter,
        )

    def test_get_hdf5_dataset_importer_sets_source_and_item(self):
        dataset = MockHDF5Dataset(filename="test.h5", name="/c1/main/foobar")
        importer = self.mapper.get_hdf5_dataset_importer(dataset=dataset)
        self.assertEqual(dataset.filename, importer.source)
        self.assertEqual(dataset.name, importer.item)

    def test_get_hdf5_dataset_importer_sets_mapping(self):
        dataset = MockHDF5Dataset(filename="test.h5", name="/c1/main/foobar")
        mapping = {0: "foobar", 1: "barbaz"}
        importer = self.mapper.get_hdf5_dataset_importer(
            dataset=dataset, mapping=mapping
        )
        mapping_dict = {
            dataset.dtype.names[0]: mapping[0],
            dataset.dtype.names[1]: mapping[1],
        }
        self.assertDictEqual(mapping_dict, importer.mapping)


class TestVersionMapperV5(unittest.TestCase):
    def setUp(self):
        self.mapper = version_mapping.VersionMapperV5()
        self.h5file = MockEveH5v5()

    def test_instantiate_class(self):
        pass

    def test_map_sets_main_dataset_name_lists(self):
        self.mapper.source = self.h5file
        device = MockHDF5Dataset(name="/c1/main/device")
        device.attributes = {
            "Name": "myaxis1",
            "Access": "ca:foobar",
            "DeviceType": "Device",
        }
        # noinspection PyUnresolvedReferences
        self.mapper.source.c1.main.add_item(device)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertTrue(self.mapper.datasets2map_in_main)

    def test_map_sets_snapshot_dataset_name_lists(self):
        self.mapper.source = self.h5file
        axis = MockHDF5Dataset(name="/c1/snapshot/axis1")
        axis.attributes = {
            "Name": "myaxis1",
            "Access": "ca:foobar",
            "DeviceType": "Axis",
        }
        # noinspection PyUnresolvedReferences
        self.mapper.source.c1.add_item(MockHDF5Group(name="/snapshot"))
        # noinspection PyUnresolvedReferences
        self.mapper.source.c1.snapshot.add_item(axis)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertTrue(self.mapper.datasets2map_in_snapshot)

    def test_map_sets_file_metadata_from_root_group(self):
        self.mapper.source = self.h5file
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        # destination: source
        root_mappings = {
            "eveh5_version": "EVEH5Version",
            "eve_version": "Version",
            "xml_version": "XMLversion",
            "measurement_station": "Location",
            "description": "Comment",
        }
        for key, value in root_mappings.items():
            with self.subTest(key=key, val=value):
                self.assertEqual(
                    getattr(evefile.metadata, key),
                    self.mapper.source.attributes[value],
                )

    def test_map_sets_file_metadata_from_c1_group(self):
        self.mapper.source = self.h5file
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        # destination: source
        c1_mappings = {
            "preferred_axis": "preferredAxis",
            "preferred_channel": "preferredChannel",
            "preferred_normalisation_channel": "preferredNormalizationChannel",
        }
        for key, value in c1_mappings.items():
            with self.subTest(key=key, val=value):
                # noinspection PyUnresolvedReferences
                self.assertEqual(
                    getattr(evefile.metadata, key),
                    self.mapper.source.c1.attributes[value],
                )

    def test_map_converts_date_to_datetime(self):
        self.mapper.source = self.h5file
        keys_to_drop = [
            key
            for key in self.mapper.source.attributes.keys()
            if "ISO" in key
        ]
        for key in keys_to_drop:
            self.mapper.source.attributes.pop(key)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertEqual(
            evefile.metadata.start,
            datetime.datetime.strptime(
                f"{self.mapper.source.attributes['StartDate']} "
                f"{self.mapper.source.attributes['StartTime']}",
                "%d.%m.%Y %H:%M:%S",
            ),
        )

    def test_map_sets_end_date_to_unix_start_time(self):
        self.mapper.source = self.h5file
        keys_to_drop = [
            key
            for key in self.mapper.source.attributes.keys()
            if "ISO" in key
        ]
        for key in keys_to_drop:
            self.mapper.source.attributes.pop(key)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertEqual(evefile.metadata.end, datetime.datetime(1970, 1, 1))

    def test_map_adds_log_messages(self):
        log_messages = [
            "2024-07-25T10:04:03: Lorem ipsum",
            "2024-07-25T10:05:23: dolor sit amet",
        ]
        self.mapper.source = self.h5file
        self.mapper.source.LiveComment = MockHDF5Dataset()
        self.mapper.source.LiveComment.data = np.asarray(log_messages)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertTrue(self.mapper.source.LiveComment.get_data_called)
        self.assertTrue(evefile.log_messages)
        self.assertIsInstance(
            evefile.log_messages[0], evedata.evefile.entities.file.LogMessage
        )
        timestamp, message = log_messages[0].split(": ", maxsplit=1)
        self.assertEqual(
            datetime.datetime.fromisoformat(timestamp),
            evefile.log_messages[0].timestamp,
        )
        self.assertEqual(message, evefile.log_messages[0].message)

    def test_map_adds_monitor_datasets(self):
        self.mapper.source = self.h5file
        monitor1 = MockHDF5Dataset(name="/device/monitor")
        monitor1.attributes = {"Name": "mymonitor", "Access": "ca:foobar"}
        monitor2 = MockHDF5Dataset(name="/device/monitor2")
        monitor2.attributes = {"Name": "mymonitor2", "Access": "ca:barbaz"}
        self.mapper.source.add_item(MockHDF5Group(name="/device"))
        # noinspection PyUnresolvedReferences
        self.mapper.source.device.add_item(monitor1)
        # noinspection PyUnresolvedReferences
        self.mapper.source.device.add_item(monitor2)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        for monitor in evefile.monitors.values():
            self.assertIsInstance(
                monitor,
                evedata.evefile.entities.data.MonitorData,
            )
        self.assertEqual(
            "monitor",
            evefile.monitors["monitor"].metadata.id,
        )
        self.assertEqual(
            monitor1.attributes["Name"],
            evefile.monitors["monitor"].metadata.name,
        )
        self.assertEqual(
            monitor1.attributes["Access"].split(":", maxsplit=1)[1],
            evefile.monitors["monitor"].metadata.pv,
        )
        self.assertEqual(
            monitor1.attributes["Access"].split(":", maxsplit=1)[0],
            evefile.monitors["monitor"].metadata.access_mode,
        )

    def test_monitor_datasets_contain_importer(self):
        self.mapper.source = self.h5file
        monitor = MockHDF5Dataset(name="/device/monitor")
        monitor.filename = "test.h5"
        monitor.attributes = {"Name": "mymonitor", "Access": "ca:foobar"}
        self.mapper.source.add_item(MockHDF5Group(name="/device"))
        # noinspection PyUnresolvedReferences
        self.mapper.source.device.add_item(monitor)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertEqual(
            "/device/monitor", evefile.monitors["monitor"].importer[0].item
        )
        self.assertEqual(
            monitor.filename, evefile.monitors["monitor"].importer[0].source
        )
        mapping_dict = {
            monitor.dtype.names[0]: "milliseconds",
            monitor.dtype.names[1]: "data",
        }
        self.assertDictEqual(
            mapping_dict, evefile.monitors["monitor"].importer[0].mapping
        )

    # noinspection PyUnresolvedReferences
    def test_map_adds_timestampdata_dataset(self):
        self.mapper.source = self.h5file
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertIsInstance(
            evefile.position_timestamps,
            evedata.evefile.entities.data.TimestampData,
        )
        self.assertEqual(
            self.mapper.source.c1.meta.PosCountTimer.attributes["Unit"],
            evefile.position_timestamps.metadata.unit,
        )
        self.assertEqual(
            self.mapper.source.c1.meta.PosCountTimer.name,
            evefile.position_timestamps.importer[0].item,
        )
        self.assertEqual(
            self.mapper.source.c1.meta.PosCountTimer.filename,
            evefile.position_timestamps.importer[0].source,
        )
        mapping_dict = {
            self.mapper.source.c1.meta.PosCountTimer.dtype.names[
                0
            ]: "positions",
            self.mapper.source.c1.meta.PosCountTimer.dtype.names[1]: "data",
        }
        self.assertDictEqual(
            mapping_dict, evefile.position_timestamps.importer[0].mapping
        )

    # noinspection PyUnresolvedReferences
    def test_map_adds_array_dataset(self):
        self.mapper.source = self.h5file
        self.mapper.source.add_array_channel()
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertIsInstance(
            evefile.data["array"],
            evedata.evefile.entities.data.ArrayChannelData,
        )
        self.assertEqual(
            "array",
            evefile.data["array"].metadata.id,
        )
        self.assertEqual(
            self.h5file.c1.main.array.attributes["Name"],
            evefile.data["array"].metadata.name,
        )
        self.assertEqual(
            self.h5file.c1.main.array.attributes["Access"].split(
                ":", maxsplit=1
            )[1],
            evefile.data["array"].metadata.pv,
        )
        self.assertEqual(
            self.h5file.c1.main.array.attributes["Access"].split(
                ":", maxsplit=1
            )[0],
            evefile.data["array"].metadata.access_mode,
        )
        positions = [int(i) for i in self.h5file.c1.main.array.item_names()]
        self.assertListEqual(positions, list(evefile.data["array"].positions))
        for idx, pos in enumerate(self.h5file.c1.main.array.item_names()):
            self.assertEqual(
                f"/c1/main/array/{pos}",
                evefile.data["array"].importer[idx].item,
            )

    # noinspection PyUnresolvedReferences
    def test_map_array_dataset_removes_dataset_from_list2map(self):
        self.mapper.source = self.h5file
        self.mapper.source.add_array_channel()
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertNotIn("array", self.mapper.datasets2map_in_main)

    def test_map_adds_axis_datasets(self):
        self.mapper.source = self.h5file
        axis1 = MockHDF5Dataset(name="/c1/main/axis1")
        axis1.attributes = {
            "Name": "myaxis1",
            "Access": "ca:foobar",
            "DeviceType": "Axis",
        }
        axis2 = MockHDF5Dataset(name="/c1/main/axis2")
        axis2.attributes = {
            "Name": "myaxis2",
            "Access": "ca:barbaz",
            "DeviceType": "Axis",
        }
        # noinspection PyUnresolvedReferences
        self.mapper.source.c1.main.add_item(axis1)
        # noinspection PyUnresolvedReferences
        self.mapper.source.c1.main.add_item(axis2)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        for axis in evefile.data.values():
            self.assertIsInstance(
                axis,
                evedata.evefile.entities.data.AxisData,
            )
        self.assertEqual(
            "axis1",
            evefile.data["axis1"].metadata.id,
        )
        self.assertEqual(
            axis1.attributes["Name"],
            evefile.data["axis1"].metadata.name,
        )
        self.assertEqual(
            axis1.attributes["Access"].split(":", maxsplit=1)[1],
            evefile.data["axis1"].metadata.pv,
        )
        self.assertEqual(
            axis1.attributes["Access"].split(":", maxsplit=1)[0],
            evefile.data["axis1"].metadata.access_mode,
        )

    def test_axis_datasets_contain_importer(self):
        self.mapper.source = self.h5file
        axis1 = MockHDF5Dataset(name="/c1/main/axis1")
        axis1.attributes = {
            "Name": "myaxis1",
            "Access": "ca:foobar",
            "DeviceType": "Axis",
        }
        axis2 = MockHDF5Dataset(name="/c1/main/axis2")
        axis2.attributes = {
            "Name": "myaxis2",
            "Access": "ca:barbaz",
            "DeviceType": "Axis",
        }
        # noinspection PyUnresolvedReferences
        self.mapper.source.c1.main.add_item(axis1)
        # noinspection PyUnresolvedReferences
        self.mapper.source.c1.main.add_item(axis2)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertEqual(
            "/c1/main/axis1", evefile.data["axis1"].importer[0].item
        )
        self.assertEqual(
            axis1.filename, evefile.data["axis1"].importer[0].source
        )
        mapping_dict = {
            axis1.dtype.names[0]: "positions",
            axis1.dtype.names[1]: "data",
        }
        self.assertDictEqual(
            mapping_dict, evefile.data["axis1"].importer[0].mapping
        )

    def test_map_axis_dataset_removes_dataset_from_list2map(self):
        self.mapper.source = self.h5file
        axis1 = MockHDF5Dataset(name="/c1/main/axis1")
        axis1.attributes = {
            "Name": "myaxis1",
            "Access": "ca:foobar",
            "DeviceType": "Axis",
        }
        # noinspection PyUnresolvedReferences
        self.mapper.source.c1.main.add_item(axis1)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertNotIn("axis1", self.mapper.datasets2map_in_main)


class TestVersionMapperV6(unittest.TestCase):
    def setUp(self):
        self.mapper = version_mapping.VersionMapperV6()

    def test_instantiate_class(self):
        pass

    def test_map_converts_date_to_datetime(self):
        self.mapper.source = MockEveH5()
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        date_mappings = {
            "start": "StartTimeISO",
            "end": "EndTimeISO",
        }
        for key, value in date_mappings.items():
            with self.subTest(key=key, val=value):
                self.assertEqual(
                    getattr(evefile.metadata, key),
                    datetime.datetime.fromisoformat(
                        self.mapper.source.attributes[value]
                    ),
                )


class TestVersionMapperV7(unittest.TestCase):
    def setUp(self):
        self.mapper = version_mapping.VersionMapperV7()

    def test_instantiate_class(self):
        pass

    def test_map_converts_simulation_flag_to_boolean(self):
        self.mapper.source = MockEveH5()
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.source.attributes["Simulation"] = "no"
        self.mapper.map(destination=evefile)
        self.assertIsInstance(evefile.metadata.simulation, bool)
        self.assertFalse(evefile.metadata.simulation)
        self.mapper.source.attributes["Simulation"] = "yes"
        self.mapper.map(destination=evefile)
        self.assertIsInstance(evefile.metadata.simulation, bool)
        self.assertTrue(evefile.metadata.simulation)
