import os
import unittest

import h5py
import numpy as np

from evedata.evefile.entities import data, metadata


class DummyHDF5File:
    def __init__(self, filename=""):
        self.filename = filename

    def create(self):
        with h5py.File(self.filename, "w") as file:
            c1 = file.create_group("c1")
            meta = c1.create_group("meta")
            data_ = np.ndarray(
                [4],
                dtype=np.dtype(
                    [("PosCounter", "<i4"), ("PosCountTimer", "<i4")]
                ),
            )
            data_["PosCounter"] = np.asarray([1, 2, 3, 4])
            data_["PosCountTimer"] = np.asarray([2, 4, 6, 8])
            poscounttimer = meta.create_dataset("PosCountTimer", data=data_)
            poscounttimer.attrs["Unit"] = np.bytes_(["msecs"])


class TestData(unittest.TestCase):
    def setUp(self):
        self.data = data.Data()

        class MockData(data.Data):

            def __init__(self):
                super().__init__()
                self.get_data_called = False

            def get_data(self):
                super().get_data()
                self.get_data_called = True

        self.mock_data = MockData()
        self.filename = "test.h5"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "importer",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_setting_data_sets_data(self):
        self.data.data = np.random.random(5)
        self.assertTrue(self.data)

    def test_accessing_data_calls_get_data_if_data_not_loaded(self):
        _ = self.mock_data.data
        self.assertTrue(self.mock_data.get_data_called)

    def test_accessing_data_with_data_does_not_call_get_data(self):
        self.mock_data.data = np.random.random(5)
        _ = self.mock_data.data
        self.assertFalse(self.mock_data.get_data_called)

    def test_get_data_loads_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        importer = data.HDF5DataImporter(source=self.filename)
        importer.item = "/c1/meta/PosCountTimer"
        importer.mapping = {
            "PosCounter": "positions",
            "PosCountTimer": "data",
        }
        self.data.importer.append(importer)
        self.data.get_data()
        self.assertTrue(self.data.data.any())


class TestMonitorData(unittest.TestCase):
    def setUp(self):
        self.data = data.MonitorData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "milliseconds",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(self.data.metadata, metadata.MonitorMetadata)


class TestMeasureData(unittest.TestCase):
    def setUp(self):
        self.data = data.MeasureData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "positions",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(self.data.metadata, metadata.MeasureMetadata)


class TestDeviceData(unittest.TestCase):
    def setUp(self):
        self.data = data.DeviceData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "positions",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(self.data.metadata, metadata.DeviceMetadata)


class TestAxisData(unittest.TestCase):
    def setUp(self):
        self.data = data.AxisData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "positions",
            "set_values",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(self.data.metadata, metadata.AxisMetadata)


class TestChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.ChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "positions",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(self.data.metadata, metadata.ChannelMetadata)


class TestTimestampData(unittest.TestCase):
    def setUp(self):
        self.data = data.TimestampData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "positions",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(self.data.metadata, metadata.TimestampMetadata)


class TestNonnumericChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.NonnumericChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "positions",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.NonnumericChannelMetadata
        )


class TestSinglePointChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.SinglePointChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "positions",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.SinglePointChannelMetadata
        )


class TestAverageChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.AverageChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "positions",
            "raw_data",
            "attempts",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.AverageChannelMetadata
        )


class TestIntervalChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.IntervalChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "positions",
            "raw_data",
            "counts",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.IntervalChannelMetadata
        )


class TestArrayChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.ArrayChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "positions",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.ArrayChannelMetadata
        )


class TestAreaChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.AreaChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "positions",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.AreaChannelMetadata
        )


class TestNormalizedChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.NormalizedChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "normalized_data",
            "normalizing_data",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.NormalizedChannelMetadata
        )


class TestSinglePointNormalizedChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.SinglePointNormalizedChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "positions",
            "normalized_data",
            "normalizing_data",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.SinglePointNormalizedChannelMetadata
        )


class TestAverageNormalizedChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.AverageNormalizedChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "positions",
            "raw_data",
            "attempts",
            "normalized_data",
            "normalizing_data",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.AverageNormalizedChannelMetadata
        )


class TestIntervalNormalizedChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.IntervalNormalizedChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "positions",
            "raw_data",
            "counts",
            "normalized_data",
            "normalizing_data",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.IntervalNormalizedChannelMetadata
        )


class TestScopeChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.ScopeChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "positions",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.ScopeChannelMetadata
        )


class TestMCAChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.MCAChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "positions",
            "roi",
            "life_time",
            "real_time",
            "preset_life_time",
            "preset_real_time",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(self.data.metadata, metadata.MCAChannelMetadata)


class TestMCAChannelROIData(unittest.TestCase):
    def setUp(self):
        self.data = data.MCAChannelROIData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "positions",
            "label",
            "marker",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))


class TestScientificCameraData(unittest.TestCase):
    def setUp(self):
        self.data = data.ScientificCameraData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "positions",
            "roi",
            "acquire_time",
            "temperature",
            "humidity",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.ScientificCameraMetadata
        )


class TestScientificCameraROIData(unittest.TestCase):
    def setUp(self):
        self.data = data.ScientificCameraROIData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "positions",
            "label",
            "marker",
            "background_width",
            "min_value",
            "min_x",
            "min_y",
            "max_value",
            "max_x",
            "max_y",
            "mean",
            "total",
            "net",
            "sigma",
            "centroid_x",
            "centroid_y",
            "centroid_sigma_x",
            "centroid_sigma_y",
            "centroid_sigma_xy",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))


class TestSampleCameraData(unittest.TestCase):
    def setUp(self):
        self.data = data.SampleCameraData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "positions",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.SampleCameraMetadata
        )


class TestNonencodedAxisData(unittest.TestCase):
    def setUp(self):
        self.data = data.NonencodedAxisData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "positions",
            "set_values",
            "filled_data",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.NonencodedAxisMetadata
        )


class TestDataImporter(unittest.TestCase):
    def setUp(self):
        self.importer = data.DataImporter()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "source",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.importer, attribute))

    def test_load_without_source_raises(self):
        self.importer.source = ""
        with self.assertRaises(ValueError):
            self.importer.load()

    def test_load_with_source_as_parameter(self):
        self.importer.source = ""
        self.importer.load(source="foo")

    def test_load_returns_data(self):

        class MockDataImporter(data.DataImporter):
            def _load(self):
                return "foo"

        importer = MockDataImporter()
        importer.source = "baz"
        self.assertTrue(importer.load())

    def test_instantiate_with_source_sets_source(self):
        source = "baz"
        importer = data.DataImporter(source=source)
        self.assertEqual(source, importer.source)


class TestHDF5DataImporter(unittest.TestCase):
    def setUp(self):
        self.importer = data.HDF5DataImporter()
        self.filename = "test.h5"
        self.item = "/c1/main/test"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def create_hdf5_file(self):
        with h5py.File(self.filename, "w") as file:
            c1 = file.create_group("c1")
            main = c1.create_group("main")
            main.create_dataset("test", data=np.ones([5, 2]))

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "source",
            "item",
            "mapping",
            "data",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.importer, attribute))

    def test_load_without_item_raises(self):
        self.importer.source = "foo"
        with self.assertRaises(ValueError):
            self.importer.load()

    def test_load_with_item_as_parameter(self):
        self.create_hdf5_file()
        self.importer.source = self.filename
        self.importer.load(item=self.item)

    def test_load_returns_HDF5_dataset_data(self):
        self.create_hdf5_file()
        self.importer.source = self.filename
        self.importer.item = self.item
        np.testing.assert_array_equal(np.ones([5, 2]), self.importer.load())

    def test_load_sets_data_attribute(self):
        self.create_hdf5_file()
        self.importer.source = self.filename
        self.importer.item = self.item
        self.importer.load()
        np.testing.assert_array_equal(np.ones([5, 2]), self.importer.data)
