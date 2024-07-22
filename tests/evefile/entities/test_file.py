import unittest

from evedata.evefile.entities import file


class TestFile(unittest.TestCase):
    def setUp(self):
        self.file = file.File()

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
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.file, attribute))


class TestMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = file.Metadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "filename",
            "eveh5_version",
            "eve_version",
            "xml_version",
            "measurement_station",
            "start",
            "end",
            "description",
            "simulation",
            "preferred_axis",
            "preferred_channel",
            "preferred_normalisation_channel",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestScan(unittest.TestCase):
    def setUp(self):
        self.scan = file.Scan()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "author",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.scan, attribute))


class TestLogMessage(unittest.TestCase):
    def setUp(self):
        self.log_message = file.LogMessage()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = ["timestamp", "comment"]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.log_message, attribute))
