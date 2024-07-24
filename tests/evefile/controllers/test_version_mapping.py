import datetime
import unittest

import evedata.evefile.boundaries.evefile
from evedata.evefile.controllers import version_mapping


class MockHDF5Item:
    def __init__(self):
        self.attributes = {}


class MockEveH5:

    def __init__(self):
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
        self.c1 = MockHDF5Item()
        self.c1.attributes = {
            "EndTimeISO": "2024-06-03T12:01:37",
            "StartDate": "03.06.2024",
            "StartTime": "12:01:32",
            "StartTimeISO": "2024-06-03T12:01:32",
            "preferredAxis": "OMS58:io1501003",
            "preferredChannel": "A2980:22704chan1",
            "preferredNormalizationChannel": "A2980:22704chan1",
        }


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

    def test_get_mapper_with_fractoinal_version_returns_correct_mapper(self):
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


class TestVersionMapperV5(unittest.TestCase):
    def setUp(self):
        self.mapper = version_mapping.VersionMapperV5()

    def test_instantiate_class(self):
        pass

    def test_map_sets_file_metadata_from_root_group(self):
        self.mapper.source = MockEveH5()
        evefile = evedata.evefile.boundaries.evefile.File()
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
        self.mapper.source = MockEveH5()
        evefile = evedata.evefile.boundaries.evefile.File()
        self.mapper.map(destination=evefile)
        # destination: source
        c1_mappings = {
            "preferred_axis": "preferredAxis",
            "preferred_channel": "preferredChannel",
            "preferred_normalisation_channel": "preferredNormalizationChannel",
        }
        for key, value in c1_mappings.items():
            with self.subTest(key=key, val=value):
                self.assertEqual(
                    getattr(evefile.metadata, key),
                    self.mapper.source.c1.attributes[value],
                )

    def test_map_converts_date_to_datetime(self):
        self.mapper.source = MockEveH5()
        evefile = evedata.evefile.boundaries.evefile.File()
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
        self.mapper.source = MockEveH5()
        evefile = evedata.evefile.boundaries.evefile.File()
        self.mapper.map(destination=evefile)
        self.assertEqual(evefile.metadata.end, datetime.datetime(1970, 1, 1))


class TestVersionMapperV6(unittest.TestCase):
    def setUp(self):
        self.mapper = version_mapping.VersionMapperV6()

    def test_instantiate_class(self):
        pass

    def test_map_converts_date_to_datetime(self):
        self.mapper.source = MockEveH5()
        evefile = evedata.evefile.boundaries.evefile.File()
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
        evefile = evedata.evefile.boundaries.evefile.File()
        self.mapper.source.attributes["Simulation"] = "no"
        self.mapper.map(destination=evefile)
        self.assertIsInstance(evefile.metadata.simulation, bool)
        self.assertFalse(evefile.metadata.simulation)
        self.mapper.source.attributes["Simulation"] = "yes"
        self.mapper.map(destination=evefile)
        self.assertIsInstance(evefile.metadata.simulation, bool)
        self.assertTrue(evefile.metadata.simulation)
