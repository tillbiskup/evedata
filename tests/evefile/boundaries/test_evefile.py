import unittest

from evedata.evefile.boundaries import evefile


class TestFile(unittest.TestCase):
    def setUp(self):
        self.evefile = evefile.EveFile()
        self.filename = "file.h5"

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
        self.evefile.load(filename=self.filename)
        self.assertEqual(self.filename, self.evefile.metadata.filename)

    def test_load_without_filename_but_filename_set_keeps_filename(self):
        self.evefile.filename = self.filename
        self.evefile.load()
        self.assertEqual(self.filename, self.evefile.metadata.filename)
