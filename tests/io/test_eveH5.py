import os
import unittest

import h5py
import numpy as np

from evedata.io import eveH5


class DummyHDF5File:
    def __init__(self, filename=""):
        self.filename = filename

    def create(self):
        with h5py.File(self.filename, "w") as file:
            file.attrs["Version"] = np.bytes_(["0.1.0"])
            file.attrs["Location"] = np.bytes_(["Unittest"])
            c1 = file.create_group("c1")
            main = c1.create_group("main")
            meta = c1.create_group("meta")
            main.create_dataset("test", (1, 1))
            meta.create_dataset("PosCountTimer", (1, 1))


class TestHDF5Item(unittest.TestCase):
    def setUp(self):
        self.hdf5_item = eveH5.HDF5Item()
        self.filename = "test.h5"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = ["filename", "name", "attributes"]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.hdf5_item, attribute))

    def test_set_filename_on_init(self):
        filename = "foo"
        hdf5_item = eveH5.HDF5Item(filename=filename)
        self.assertEqual(filename, hdf5_item.filename)

    def test_set_name_on_init(self):
        name = "bar"
        hdf5_item = eveH5.HDF5Item(name=name)
        self.assertEqual(name, hdf5_item.name)

    def test_get_attributes_without_filename_raises(self):
        with self.assertRaisesRegex(ValueError, "Missing attribute filename"):
            self.hdf5_item.get_attributes()

    def test_get_attributes_without_name_raises(self):
        self.hdf5_item.filename = "foo"
        with self.assertRaisesRegex(ValueError, "Missing attribute name"):
            self.hdf5_item.get_attributes()

    def test_get_attributes_reads_attributes(self):
        DummyHDF5File(filename=self.filename).create()
        self.hdf5_item.filename = self.filename
        self.hdf5_item.name = "/"
        self.hdf5_item.get_attributes()
        self.assertTrue(self.hdf5_item.attributes)

    def test_attribute_values_are_strings(self):
        DummyHDF5File(filename=self.filename).create()
        self.hdf5_item.filename = self.filename
        self.hdf5_item.name = "/"
        self.hdf5_item.get_attributes()
        for value in self.hdf5_item.attributes.values():
            with self.subTest(value=value):
                self.assertIsInstance(value, str)
