import unittest

from evedata.measurement.entities import metadata


class TestMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.Metadata()

    def test_instantiate_class(self):
        pass
