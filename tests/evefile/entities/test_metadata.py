import unittest

from evedata.evefile.entities import metadata


class TestMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.Metadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestAbstractDeviceMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.AbstractDeviceMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "id",
            "pv",
            "access_mode",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestMeasureMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.MeasureMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestMonitorMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.MonitorMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "id",
            "pv",
            "access_mode",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestDeviceMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.DeviceMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestAxisMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.AxisMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "deadband",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.ChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestTimestampMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.TimestampMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestNonnumericChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.NonnumericChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestSinglePointChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.SinglePointChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestAverageChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.AverageChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "n_averages",
            "low_limit",
            "max_attempts",
            "max_deviation",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestIntervalChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.IntervalChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "trigger_interval",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestArrayChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.ArrayChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestAreaChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.AreaChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "file_type",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestNormalizedChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.NormalizedChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "normalize_id",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestSinglePointNormalizedChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.SinglePointNormalizedChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "normalize_id",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestAverageNormalizedChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.AverageNormalizedChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "normalize_id",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestIntervalNormalizedChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.IntervalNormalizedChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "normalize_id",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestScopeChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.ScopeChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestMCAChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.MCAChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "calibration",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestMCAChannelCalibration(unittest.TestCase):
    def setUp(self):
        self.calibration = metadata.MCAChannelCalibration()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "offset",
            "slope",
            "quadratic",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.calibration, attribute))


class TestScientificCameraMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.ScientificCameraMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "gain",
            "reverse_x",
            "reverse_y",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestSampleCameraMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.SampleCameraMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "beam_x",
            "beam_y",
            "fractional_x_position",
            "fractional_y_position",
            "skip_frames",
            "average_frames",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestNonencodedAxisMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.NonencodedAxisMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "deadband",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))
