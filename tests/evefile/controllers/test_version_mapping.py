import datetime
import logging
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
        self.data = None
        self.get_data_called = False
        self.dtype = np.dtype(
            [("PosCounter", "<i4"), (name.split("/")[-1], "<f8")]
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

    def remove_item(self, item):
        name = item.name.split("/")[-1]
        delattr(self, name)
        self._items.pop(name)

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
        self.attributes.update(
            {
                "EVEH5Version": "4",
                "Location": "TEST",
                "Version": "1.27",
                "XMLversion": "5.0",
            }
        )
        # Only starting with v4
        self.c1.add_item(
            MockHDF5Group(name="/c1/main", filename=self.filename)
        )
        self.c1.add_item(
            MockHDF5Group(name="/c1/snapshot", filename=self.filename)
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
            "Access": "ca:array.VAL",
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
        for option in ["ELTM", "ERTM", "PLTM", "PRTM", "R0", "R1"]:
            dataset = MockHDF5Dataset(
                name=f"/c1/main/array.{option}", filename=self.filename
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:array.{option}",
            }
            self.c1.main.add_item(dataset)
        for option in [
            "CALO",
            "CALQ",
            "CALS",
        ]:
            dataset = MockHDF5Dataset(
                name=f"/c1/snapshot/array.{option}", filename=self.filename
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:array.{option}",
            }
            data_ = np.ndarray(
                [2],
                dtype=np.dtype(
                    [("PosCounter", "<i4"), (f"array.{option}", "f8")]
                ),
            )
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"array.{option}"] = np.random.random(2)
            dataset.data = data_
            self.c1.snapshot.add_item(dataset)
        for option in [
            "R0LO",
            "R0HI",
            "R1LO",
            "R1HI",
        ]:
            dataset = MockHDF5Dataset(
                name=f"/c1/snapshot/array.{option}", filename=self.filename
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:array.{option}",
            }
            data_ = np.ndarray(
                [2],
                dtype=np.dtype(
                    [("PosCounter", "<i4"), (f"array.{option}", "<i4")]
                ),
            )
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"array.{option}"] = [-1, -1]
            dataset.data = data_
            self.c1.snapshot.add_item(dataset)
        for option in [
            "R0NM",
            "R1NM",
        ]:
            dataset = MockHDF5Dataset(
                name=f"/c1/snapshot/array.{option}", filename=self.filename
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:array.{option}",
            }
            data_ = np.ndarray(
                [2],
                dtype=np.dtype(
                    [("PosCounter", "<i4"), (f"array.{option}", "S3")]
                ),
            )
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"array.{option}"] = ["foo", "foo"]
            dataset.data = data_
            self.c1.snapshot.add_item(dataset)

    # noinspection PyUnresolvedReferences
    def add_scientific_camera(self, camera="GREYQMP02", n_roi=4, n_stats=5):
        # Fake scientific camera channels
        for name in [
            "TIFF1:chan1",
            "cam1:AcquireTime_RBV",
            "cam1:Gain_RBV",
            "cam1:Temperature_RBV",
            "cam1:Time",
            "cam1:greatEyesCooler",
        ]:
            dataset = MockHDF5Dataset(
                name=f"/c1/main/{camera}:{name}", filename=self.filename
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{camera}:{name}",
            }
            self.c1.main.add_item(dataset)
        for idx, name in enumerate(
            [
                "MinX_RBV",
                "MinY_RBV",
                "SizeX_RBV",
                "SizeY_RBV",
            ]
        ):
            for roi in range(1, n_roi + 1):
                dataset = MockHDF5Dataset(
                    name=f"/c1/main/{camera}:ROI{roi}:{name}",
                    filename=self.filename,
                )
                dataset.attributes = {
                    "DeviceType": "Channel",
                    "Access": f"ca:{camera}:ROI{roi}:{name}",
                }
                data_ = np.ndarray(
                    [2],
                    dtype=np.dtype(
                        [
                            ("PosCounter", "<i4"),
                            (f"{camera}:ROI{roi}:{name}", "<i4"),
                        ]
                    ),
                )
                data_["PosCounter"] = np.asarray([2, 5])
                data_[f"{camera}:ROI{roi}:{name}"] = [100 * idx, 100 * idx]
                dataset.data = data_
                self.c1.main.add_item(dataset)
        for name in [
            "BgdWidth_RBV",
            "CentroidThreshold_RBV",
            "CentroidX_RBV",
            "CentroidY_RBV",
            "MaxValue_RBV",
            "MaxX_RBV",
            "MaxY_RBV",
            "MeanValue_RBV",
            "MinValue_RBV",
            "MinX_RBV",
            "MinY_RBV",
            "SigmaXY_RBV",
            "SigmaX_RBV",
            "SigmaY_RBV",
            "Sigma_RBV",
            "Total_RBV",
            "chan1",
        ]:
            for stats in range(1, n_stats + 1):
                dataset = MockHDF5Dataset(
                    name=f"/c1/main/{camera}:Stats{stats}:{name}",
                    filename=self.filename,
                )
                dataset.attributes = {
                    "DeviceType": "Channel",
                    "Access": f"ca:{camera}:Stats{stats}:{name}",
                }
                self.c1.main.add_item(dataset)

        for name in [
            "TIFF1:FileName",
            "cam1:ReverseX_RBV",
            "cam1:ReverseY_RBV",
            "cam1:Temperature",
            "cam1:TemperatureActual",
        ]:
            dataset = MockHDF5Dataset(
                name=f"/c1/snapshot/{camera}:{name}", filename=self.filename
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{camera}:{name}",
            }
            self.c1.snapshot.add_item(dataset)

    # noinspection PyUnresolvedReferences
    def add_sample_camera(self, camera="fcm"):
        # Fake sample camera channels
        dataset = MockHDF5Dataset(
            name=f"/c1/main/{camera}:uvc1:chan1", filename=self.filename
        )
        dataset.attributes = {
            "DeviceType": "Channel",
            "Access": f"ca:{camera}:uvc1:chan1",
        }
        self.c1.main.add_item(dataset)
        for name in [
            "uvc1:BeamX",
            "uvc1:BeamY",
            "uvc1:FileNumberRBV",
        ]:
            dataset = MockHDF5Dataset(
                name=f"/c1/main/{camera}:{name}", filename=self.filename
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{camera}:{name}",
            }
            data_ = np.ndarray(
                [2],
                dtype=np.dtype(
                    [
                        ("PosCounter", "<i4"),
                        (f"{camera}:{name}", "<i4"),
                    ]
                ),
            )
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{camera}:{name}"] = [42, 42]
            dataset.data = data_
            self.c1.main.add_item(dataset)
        for name in [
            "uvc1:BeamX",
            "uvc1:BeamY",
            "uvc1:BeamXfrac",
            "uvc1:BeamYfrac",
            "uvc1:SkipFrames",
            "uvc1:AvgFrames",
        ]:
            dataset = MockHDF5Dataset(
                name=f"/c1/snapshot/{camera}:{name}", filename=self.filename
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{camera}:{name}",
            }
            data_ = np.ndarray(
                [2],
                dtype=np.dtype(
                    [
                        ("PosCounter", "<i4"),
                        (f"{camera}:{name}", "<i4"),
                    ]
                ),
            )
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{camera}:{name}"] = [21, 21]
            dataset.data = data_
            self.c1.snapshot.add_item(dataset)

    # noinspection PyUnresolvedReferences
    def add_singlepoint_detector_data(self, normalized=False):
        names = [
            "A2980:gw24103chan1",
            "K0617:gw24126chan1",
            "mlsCurrent:Mnt1chan1",
        ]
        for name in names:
            dataset = MockHDF5Dataset(
                name=f"/c1/main/{name}", filename=self.filename
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{name}",
                "Name": name,
                "Unit": "mA",
                "Detectortype": "Standard",
            }
            data_ = np.ndarray(
                [2],
                dtype=np.dtype(
                    [
                        ("PosCounter", "<i4"),
                        (f"{name}", "f8"),
                    ]
                ),
            )
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{name}"] = [42.0, 42.0]
            dataset.data = data_
            # noinspection PyUnresolvedReferences
            self.c1.main.add_item(dataset)
        if normalized:
            name = "K0617:gw24126chan1"
            normalized = "A2980:gw24103chan1"
            dataset = MockHDF5Dataset(
                name=f"/c1/main/normalized/{name}__{normalized}",
                filename=self.filename,
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{name}",
                "Name": name,
                "Unit": "mA",
                "Detectortype": "Standard",
                "channel": name,
                "normalizeId": normalized,
            }
            data_ = np.ndarray(
                [2],
                dtype=np.dtype(
                    [
                        ("PosCounter", "<i4"),
                        (f"{name}", "f8"),
                    ]
                ),
            )
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{name}"] = [42.0, 42.0]
            dataset.data = data_
            self.c1.main.add_item(MockHDF5Group(name="/c1/main/normalized"))
            self.c1.main.normalized.add_item(dataset)
        return names

    # noinspection PyUnresolvedReferences
    def add_interval_detector_data(self, normalized=False):
        self.c1.main.add_item(MockHDF5Group(name="/c1/main/standarddev"))
        if normalized:
            basename = "bIICurrent:Mnt1chan1"
            name = f"{basename}__bIICurrent:Mnt1lifeTimechan1"
            dataset = MockHDF5Dataset(
                name=f"/c1/main/normalized/{name}",
                filename=self.filename,
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{basename}",
                "Name": basename,
                "Detectortype": "Interval",
                "channel": basename,
                "normalizeId": name.split("__")[1],
            }
            dtype = np.dtype(
                [
                    ("PosCounter", "<i4"),
                    (f"{basename}", "f8"),
                ]
            )
            data_ = np.ndarray([2], dtype=dtype)
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{basename}"] = [42.0, 42.0]
            dataset.data = data_
            self.c1.main.add_item(MockHDF5Group(name="/c1/main/normalized"))
            self.c1.main.normalized.add_item(dataset)
            # Non-normalized dataset
            dataset = MockHDF5Dataset(
                name=f"/c1/main/{basename}",
                filename=self.filename,
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{basename}",
                "Name": basename,
                "Detectortype": "Standard",
            }
            dtype = np.dtype(
                [
                    ("PosCounter", "<i4"),
                    (f"{basename}", "f8"),
                ]
            )
            data_ = np.ndarray([2], dtype=dtype)
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{basename}"] = [42.0, 42.0]
            dataset.data = data_
            self.c1.main.add_item(dataset)
        else:
            name = "mlsCurrent:Mnt1chan1"
            dataset = MockHDF5Dataset(
                name=f"/c1/main/{name}", filename=self.filename
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{name}",
                "Name": name,
                "Detectortype": "Interval",
            }
            data_ = np.ndarray(
                [2],
                dtype=np.dtype(
                    [
                        ("PosCounter", "<i4"),
                        (f"{name}", "f8"),
                    ]
                ),
            )
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{name}"] = [42.0, 42.0]
            dataset.data = data_
            # noinspection PyUnresolvedReferences
            self.c1.main.add_item(dataset)
        metadata = "Count"
        dataset = MockHDF5Dataset(
            name=f"/c1/main/standarddev/{name}__{metadata}",
            filename=self.filename,
        )
        dataset.attributes = {
            "Name": name,
            "channel": name,
        }
        dtype = np.dtype(
            [
                ("PosCounter", "<i4"),
                (f"{metadata}", "f8"),
            ]
        )
        data_ = np.ndarray([2], dtype=dtype)
        data_["PosCounter"] = np.asarray([2, 5])
        data_[f"{metadata}"] = [42.0, 42.0]
        dataset.data = data_
        dataset.dtype = dtype
        # noinspection PyUnresolvedReferences
        self.c1.main.standarddev.add_item(dataset)
        metadata = "TrigIntv-StdDev"
        dataset = MockHDF5Dataset(
            name=f"/c1/main/standarddev/{name}__{metadata}",
            filename=self.filename,
        )
        dataset.attributes = {
            "Name": name,
            "channel": name,
        }
        dtype = np.dtype(
            [
                ("PosCounter", "<i4"),
                ("TriggerIntv", "f8"),
                ("StandardDeviation", "f8"),
            ]
        )
        data_ = np.ndarray([2], dtype=dtype)
        data_["PosCounter"] = np.asarray([2, 5])
        data_["TriggerIntv"] = [0.1, 0.1]
        data_["StandardDeviation"] = [42.21, 42.21]
        dataset.data = data_
        dataset.dtype = dtype
        # noinspection PyUnresolvedReferences
        self.c1.main.standarddev.add_item(dataset)
        return name

    # noinspection PyUnresolvedReferences
    def add_average_detector_data(self, maxdev=False, normalized=False):
        self.c1.main.add_item(MockHDF5Group(name="/c1/main/averagemeta"))
        if normalized:
            basename = "bIICurrent:Mnt1chan1"
            normalize_name = "bIICurrent:Mnt1lifeTimechan1"
            name = f"{basename}__{normalize_name}"
            dataset = MockHDF5Dataset(
                name=f"/c1/main/normalized/{name}",
                filename=self.filename,
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{basename}",
                "Name": basename,
                "Detectortype": "Standard",
                "channel": basename,
                "normalizeId": normalized,
            }
            dtype = np.dtype(
                [
                    ("PosCounter", "<i4"),
                    (f"{basename}", "f8"),
                ]
            )
            data_ = np.ndarray([2], dtype=dtype)
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{basename}"] = [42.0, 42.0]
            dataset.data = data_
            self.c1.main.add_item(MockHDF5Group(name="/c1/main/normalized"))
            self.c1.main.normalized.add_item(dataset)
            # Non-normalized dataset
            dataset = MockHDF5Dataset(
                name=f"/c1/main/{basename}",
                filename=self.filename,
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{basename}",
                "Name": basename,
                "Detectortype": "Standard",
            }
            dtype = np.dtype(
                [
                    ("PosCounter", "<i4"),
                    (f"{basename}", "f8"),
                ]
            )
            data_ = np.ndarray([2], dtype=dtype)
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{basename}"] = [42.0, 42.0]
            dataset.data = data_
            self.c1.main.add_item(dataset)
            # Normalizing dataset
            dataset = MockHDF5Dataset(
                name=f"/c1/main/{normalize_name}",
                filename=self.filename,
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{normalize_name}",
                "Name": normalize_name,
                "Detectortype": "Standard",
            }
            dtype = np.dtype(
                [
                    ("PosCounter", "<i4"),
                    (f"{normalize_name}", "f8"),
                ]
            )
            data_ = np.ndarray([2], dtype=dtype)
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{normalize_name}"] = [42.0, 42.0]
            dataset.data = data_
            self.c1.main.add_item(dataset)
        else:
            name = "mlsCurrent:Mnt1chan1"
            dataset = MockHDF5Dataset(
                name=f"/c1/main/{name}", filename=self.filename
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{name}",
                "Name": name,
                "Detectortype": "Standard",
            }
            data_ = np.ndarray(
                [2],
                dtype=np.dtype(
                    [
                        ("PosCounter", "<i4"),
                        (f"{name}", "f8"),
                    ]
                ),
            )
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{name}"] = [42.0, 42.0]
            dataset.data = data_
            # noinspection PyUnresolvedReferences
            self.c1.main.add_item(dataset)
        metadata = "AverageCount"
        dataset = MockHDF5Dataset(
            name=f"/c1/main/averagemeta/{name}__{metadata}",
            filename=self.filename,
        )
        dataset.attributes = {
            "Name": name,
            "channel": name,
        }
        dtype = np.dtype(
            [
                ("PosCounter", "<i4"),
                ("AverageCount", "<i4"),
                ("Preset", "<i4"),
            ]
        )
        data_ = np.ndarray([2], dtype=dtype)
        data_["PosCounter"] = np.asarray([2, 5])
        data_["AverageCount"] = [3, 3]
        data_["Preset"] = [3, 3]
        dataset.data = data_
        dataset.dtype = dtype
        # noinspection PyUnresolvedReferences
        self.c1.main.averagemeta.add_item(dataset)
        if maxdev:
            metadata = "Attempts"
            dataset = MockHDF5Dataset(
                name=f"/c1/main/averagemeta/{name}__{metadata}",
                filename=self.filename,
            )
            dataset.attributes = {
                "Name": name,
                "channel": name,
            }
            dtype = np.dtype(
                [
                    ("PosCounter", "<i4"),
                    ("Attempts", "<i4"),
                    ("MaxAttempts", "<i4"),
                ]
            )
            data_ = np.ndarray([2], dtype=dtype)
            data_["PosCounter"] = np.asarray([2, 5])
            data_["Attempts"] = [1, 1]
            data_["MaxAttempts"] = [4, 4]
            dataset.data = data_
            dataset.dtype = dtype
            # noinspection PyUnresolvedReferences
            self.c1.main.averagemeta.add_item(dataset)
            metadata = "Limit-MaxDev"
            dataset = MockHDF5Dataset(
                name=f"/c1/main/averagemeta/{name}__{metadata}",
                filename=self.filename,
            )
            dataset.attributes = {
                "Name": name,
                "channel": name,
            }
            dtype = np.dtype(
                [
                    ("PosCounter", "<i4"),
                    ("Limit", "f8"),
                    ("maxDeviation", "f8"),
                ]
            )
            data_ = np.ndarray([2], dtype=dtype)
            data_["PosCounter"] = np.asarray([2, 5])
            data_["Limit"] = [21.42, 21.42]
            data_["maxDeviation"] = [0.21, 0.21]
            dataset.data = data_
            dataset.dtype = dtype
            # noinspection PyUnresolvedReferences
            self.c1.main.averagemeta.add_item(dataset)
        return name

    # noinspection PyUnresolvedReferences
    def add_axes_snapshot_data(self):
        # Axes have a unit attribute
        axes_names = [
            "SimMt:testrack01000",
            "SimMt:testrack01001",
            "SimMt:testrack01002",
            "SimMt:testrack01003",
            "SimMt:testrack01004",
            "SimMt:testrack01005",
        ]
        # Nonnumeric axes have no unit attribute
        nonnumeric_axes_names = [
            "DiscPosSimMt:testrack01000",
            "DiscPosSimMt:testrack01001",
        ]
        for name in [*axes_names, *nonnumeric_axes_names]:
            dataset = MockHDF5Dataset(
                name=f"/c1/snapshot/{name}",
                filename=self.filename,
            )
            dataset.attributes = {
                "DeviceType": "Axis",
                "Access": f"ca:{name}",
                "Name": name,
            }
            if name not in nonnumeric_axes_names:
                dataset.attributes["Unit"] = "degrees"
            dtype = np.dtype(
                [
                    ("PosCounter", "<i4"),
                    (f"{name}", "f8"),
                ]
            )
            data_ = np.ndarray([2], dtype=dtype)
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{name}"] = [42.0, 42.0]
            dataset.data = data_
            self.c1.snapshot.add_item(dataset)
        return [*axes_names, *nonnumeric_axes_names]

    # noinspection PyUnresolvedReferences
    def add_channel_snapshot_data(self):
        # Channels need not have a unit attribute, example: SmCounter-det
        channel_names = [
            "SmCounter-det",
            "U125P:ioIDB00GapMotchan1",
            "bIICurrent:Mnt1chan1",
            "bIICurrent:Mnt1lifeTimechan1",
        ]
        # Nonnumeric channels definitely have no unit attribute
        nonnumeric_channel_names = [
            "bIICurrent:Mnt1topupStatechan1",
            "wftest:filenamechan1",
        ]
        for name in [*channel_names, *nonnumeric_channel_names]:
            dataset = MockHDF5Dataset(
                name=f"/c1/snapshot/{name}",
                filename=self.filename,
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{name}",
                "Name": name,
            }
            if name not in ["SmCounter-det", *nonnumeric_channel_names]:
                dataset.attributes["Unit"] = "mA"
            dtype = np.dtype(
                [
                    ("PosCounter", "<i4"),
                    (f"{name}", "f8"),
                ]
            )
            data_ = np.ndarray([2], dtype=dtype)
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{name}"] = [42.0, 42.0]
            dataset.data = data_
            self.c1.snapshot.add_item(dataset)
        return [*channel_names, *nonnumeric_channel_names]

    def add_mpskip(self):
        channel_names = {
            "MPSKIP:sx70001chan1": "SkipDetektorSX700",
            "MPSKIP:sx70001counterchan1": "SX700-Scounter",
            "MPSKIP:sx70001skipcountchan1": "SX700-Skipcount",
        }
        for uid, name in channel_names.items():
            dataset = MockHDF5Dataset(
                name=f"/c1/main/{uid}",
                filename=self.filename,
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Detectortype": "Standard",
                "Access": f"ca:{uid}",
                "Name": name,
            }
            dtype = np.dtype(
                [
                    ("PosCounter", "<i4"),
                    (f"{uid}", "f8"),
                ]
            )
            data_ = np.ndarray([6], dtype=dtype)
            data_["PosCounter"] = np.arange(3, 9)
            data_[f"{uid}"] = np.ones(6) * 42.0
            dataset.data = data_
            self.c1.main.add_item(dataset)
            self.c1.snapshot.add_item(dataset)
        monitor_names = [
            "detector",
            "limit",
            "maxdev",
            "reset",
            "skipcount",
        ]
        self.add_item(MockHDF5Group(name="/device", filename=self.filename))
        for name in monitor_names:
            dataset = MockHDF5Dataset(
                name=f"/device/MPSKIP:sx70001{name}",
                filename=self.filename,
            )
            dataset.attributes = {
                "Access": f"ca:MPSKIP:sx70001{name}",
                "Name": name,
            }
            dtype = np.dtype(
                [
                    ("mSecsSinceStart", "<i4"),
                    (f"MPSKIP:sx70001{name}", "f8"),
                ]
            )
            data_ = np.ndarray([1], dtype=dtype)
            data_["mSecsSinceStart"] = -1
            data_[f"MPSKIP:sx70001{name}"] = 42.0
            dataset.data = data_
            self.device.add_item(dataset)
        return list(channel_names.keys()), monitor_names


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
        self.logger = logging.getLogger(name="evedata")
        self.logger.setLevel(logging.ERROR)

    def test_instantiate_class(self):
        pass

    @unittest.skip
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

    @unittest.skip
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

    def test_map_sets_file_metadata_from_root_group_without_comment(self):
        self.mapper.source = self.h5file
        self.mapper.source.attributes.pop("Comment")
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        # destination: source
        root_mappings = {
            "eveh5_version": "EVEH5Version",
            "eve_version": "Version",
            "xml_version": "XMLversion",
            "measurement_station": "Location",
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
            b"2024-07-25T10:04:03: Lorem ipsum",
            b"2024-07-25T10:05:23: dolor sit amet",
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
        timestamp, message = log_messages[0].decode().split(": ", maxsplit=1)
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

    # noinspection PyUnresolvedReferences
    def test_map_array_dataset_adds_importers_for_options(self):
        self.mapper.source = self.h5file
        self.mapper.source.add_array_channel()
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        offset = 15
        pv_attributes = ["ELTM", "ERTM", "PLTM", "PRTM"]
        for idx, option in enumerate(pv_attributes):
            self.assertEqual(
                f"/c1/main/array.{option}",
                evefile.data["array"].importer[idx + offset].item,
            )
        attribute_names = [
            "life_time",
            "real_time",
            "preset_life_time",
            "preset_real_time",
        ]
        for idx, attribute in enumerate(attribute_names):
            self.assertEqual(
                attribute,
                evefile.data["array"]
                .importer[idx + offset]
                .mapping[f"array.{pv_attributes[idx]}"],
            )

    def test_map_array_adds_mca_roi_objects(self):
        self.mapper.source = self.h5file
        self.mapper.source.add_array_channel()
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        # Assuming two ROI datasets to be added
        self.assertEqual(2, len(evefile.data["array"].roi))

    def test_map_array_adds_importers_to_mca_roi_objects(self):
        self.mapper.source = self.h5file
        self.mapper.source.add_array_channel()
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        for roi in evefile.data["array"].roi:
            self.assertTrue(roi.importer)

    def test_map_array_set_mca_roi_marker(self):
        self.mapper.source = self.h5file
        self.mapper.source.add_array_channel()
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        for roi in evefile.data["array"].roi:
            self.assertListEqual([-1, -1], list(roi.marker))

    def test_map_array_set_mca_roi_label(self):
        self.mapper.source = self.h5file
        self.mapper.source.add_array_channel()
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        for roi in evefile.data["array"].roi:
            self.assertEqual("foo", roi.label)

    def test_map_array_dataset_calibration_has_correct_values(self):
        self.mapper.source = self.h5file
        self.mapper.source.add_array_channel()
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        mapping_table = {
            "CALO": "offset",
            "CALQ": "quadratic",
            "CALS": "slope",
        }
        for key, value in mapping_table.items():
            # noinspection PyUnresolvedReferences
            self.assertEqual(
                getattr(self.mapper.source.c1.snapshot, f"array.{key}").data[
                    f"array.{key}"
                ][0],
                getattr(evefile.data["array"].metadata.calibration, value),
            )

    def test_map_mca_dataset_with_unknown_options_logs_warning(self):
        self.mapper.source = self.h5file
        self.mapper.source.add_array_channel()
        option = "UNKNOWN"
        dataset = MockHDF5Dataset(
            name=f"/c1/snapshot/array.{option}",
            filename=self.mapper.source.filename,
        )
        dataset.attributes = {
            "DeviceType": "Channel",
            "Access": f"ca:array.{option}",
        }
        # noinspection PyUnresolvedReferences
        self.mapper.source.c1.snapshot.add_item(dataset)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.logger.setLevel(logging.WARN)
        with self.assertLogs(level=logging.WARN) as captured:
            self.mapper.map(destination=evefile)
        self.assertEqual(len(captured.records), 1)
        self.assertEqual(
            captured.records[0].getMessage(), f"Option {option} " f"unmapped"
        )

    # noinspection PyUnresolvedReferences
    def test_map_array_dataset_removes_options_from_list2map(self):
        self.mapper.source = self.h5file
        self.mapper.source.add_array_channel()
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        array_datasets_in_main = [
            item
            for item in self.mapper.datasets2map_in_main
            if item.startswith("array")
        ]
        self.assertFalse(array_datasets_in_main)
        array_datasets_in_snapshot = [
            item
            for item in self.mapper.datasets2map_in_snapshot
            if item.startswith("array")
        ]
        self.assertFalse(array_datasets_in_snapshot)

    def test_map_adds_axis_datasets(self):
        self.mapper.source = self.h5file
        axis1 = MockHDF5Dataset(name="/c1/main/axis1")
        axis1.attributes = {
            "Name": "myaxis1",
            "Unit": "eV",
            "Access": "ca:foobar",
            "DeviceType": "Axis",
        }
        axis2 = MockHDF5Dataset(name="/c1/main/axis2")
        axis2.attributes = {
            "Name": "myaxis2",
            "Unit": "nm",
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
            axis1.attributes["Unit"],
            evefile.data["axis1"].metadata.unit,
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

    # noinspection PyUnresolvedReferences
    def test_map_scientific_camera_dataset_adds_dataset(self):
        self.mapper.source = self.h5file
        camera_name = "GREYQMP02"
        self.mapper.source.add_scientific_camera(camera=camera_name)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertIn(camera_name, evefile.data)
        self.assertIsInstance(
            evefile.data[camera_name],
            evedata.evefile.entities.data.ScientificCameraData,
        )

    # noinspection PyUnresolvedReferences
    def test_map_scientific_camera_dataset_adds_importer(self):
        self.mapper.source = self.h5file
        camera_name = "GREYQMP02"
        self.mapper.source.add_scientific_camera(camera=camera_name)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertEqual(
            getattr(
                self.mapper.source.c1.main, f"{camera_name}:TIFF1:chan1"
            ).filename,
            evefile.data[camera_name].importer[0].source,
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main, f"{camera_name}:TIFF1:chan1"
            ).dtype.names[0]: "positions",
            getattr(
                self.mapper.source.c1.main, f"{camera_name}:TIFF1:chan1"
            ).dtype.names[1]: "data",
        }
        self.assertDictEqual(
            mapping_dict, evefile.data[camera_name].importer[0].mapping
        )

    # noinspection PyUnresolvedReferences
    def test_scientific_camera_dataset_has_correct_number_of_rois(self):
        self.mapper.source = self.h5file
        camera_name = "GREYQMP02"
        n_roi = 4
        self.mapper.source.add_scientific_camera(
            camera=camera_name, n_roi=n_roi
        )
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertEqual(n_roi, len(evefile.data[camera_name].roi))

    # noinspection PyUnresolvedReferences
    def test_scientific_camera_dataset_has_correct_roi_marker(self):
        self.mapper.source = self.h5file
        camera_name = "GREYQMP02"
        n_roi = 4
        self.mapper.source.add_scientific_camera(
            camera=camera_name, n_roi=n_roi
        )
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        for roi in evefile.data[camera_name].roi:
            self.assertListEqual([0, 100, 200, 300], list(roi.marker))

    # noinspection PyUnresolvedReferences
    def test_scientific_camera_dataset_has_correct_number_of_stats(self):
        self.mapper.source = self.h5file
        camera_name = "GREYQMP02"
        n_stats = 5
        self.mapper.source.add_scientific_camera(
            camera=camera_name, n_stats=n_stats
        )
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertEqual(n_stats, len(evefile.data[camera_name].statistics))

    def test_scientific_camera_dataset_statistics_have_importers(self):
        self.mapper.source = self.h5file
        camera_name = "GREYQMP02"
        n_stats = 5
        self.mapper.source.add_scientific_camera(
            camera=camera_name, n_stats=n_stats
        )
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        for statistic in evefile.data[camera_name].statistics:
            self.assertGreater(len(statistic.importer), 0)

    # noinspection PyUnresolvedReferences
    def test_map_scientific_camera_dataset_removes_options_from_list2map(
        self,
    ):
        self.mapper.source = self.h5file
        camera_name = "GREYQMP02"
        self.mapper.source.add_scientific_camera(camera=camera_name)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        camera_datasets_in_main = [
            item
            for item in self.mapper.datasets2map_in_main
            if item.startswith(camera_name)
        ]
        self.assertFalse(camera_datasets_in_main)
        camera_datasets_in_snapshot = [
            item
            for item in self.mapper.datasets2map_in_snapshot
            if item.startswith(camera_name)
        ]
        self.assertFalse(camera_datasets_in_snapshot)

    def test_map_scientific_camera_w_unknown_options_logs_warning(self):
        self.mapper.source = self.h5file
        camera_name = "GREYQMP02"
        self.mapper.source.add_scientific_camera(camera=camera_name)
        option = "cam1:UNKNOWN"
        dataset = MockHDF5Dataset(
            name=f"/c1/main/{camera_name}:{option}",
            filename=self.mapper.source.filename,
        )
        dataset.attributes = {
            "DeviceType": "Channel",
            "Access": f"ca:{camera_name}:{option}",
        }
        # noinspection PyUnresolvedReferences
        self.mapper.source.c1.main.add_item(dataset)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.logger.setLevel(logging.WARN)
        with self.assertLogs(level=logging.WARN) as captured:
            self.mapper.map(destination=evefile)
        messages = [record.getMessage() for record in captured.records]
        self.assertGreaterEqual(len(captured.records), 1)
        self.assertIn(f"Option {option} unmapped", messages)

    def test_map_scientific_camera_w_unknown_snapshot_options_logs_warning(
        self,
    ):
        self.mapper.source = self.h5file
        camera_name = "GREYQMP02"
        self.mapper.source.add_scientific_camera(camera=camera_name)
        option = "cam1:UNKNOWN2"
        dataset = MockHDF5Dataset(
            name=f"/c1/snapshot/{camera_name}:{option}",
            filename=self.mapper.source.filename,
        )
        dataset.attributes = {
            "DeviceType": "Channel",
            "Access": f"ca:{camera_name}:{option}",
        }
        # noinspection PyUnresolvedReferences
        self.mapper.source.c1.snapshot.add_item(dataset)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.logger.setLevel(logging.WARN)
        with self.assertLogs(level=logging.WARN) as captured:
            self.mapper.map(destination=evefile)
        messages = [record.getMessage() for record in captured.records]
        self.assertGreaterEqual(len(captured.records), 1)
        self.assertIn(f"Option {option} unmapped", messages)

    # noinspection PyUnresolvedReferences
    def test_map_sample_camera_dataset_removes_options_from_list2map(self):
        self.mapper.source = self.h5file
        camera_name = "fcm"
        self.mapper.source.add_sample_camera(camera=camera_name)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        camera_datasets_in_main = [
            item
            for item in self.mapper.datasets2map_in_main
            if item.startswith(camera_name)
        ]
        self.assertFalse(camera_datasets_in_main)
        camera_datasets_in_snapshot = [
            item
            for item in self.mapper.datasets2map_in_snapshot
            if item.startswith(camera_name)
        ]
        self.assertFalse(camera_datasets_in_snapshot)

    # noinspection PyUnresolvedReferences
    def test_map_sample_camera_dataset_adds_dataset(self):
        self.mapper.source = self.h5file
        camera_name = "fcm"
        self.mapper.source.add_sample_camera(camera=camera_name)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertIn(camera_name, evefile.data)
        self.assertIsInstance(
            evefile.data[camera_name],
            evedata.evefile.entities.data.SampleCameraData,
        )

    # noinspection PyUnresolvedReferences
    def test_map_sample_camera_dataset_adds_importer(self):
        self.mapper.source = self.h5file
        camera_name = "fcm"
        self.mapper.source.add_sample_camera(camera=camera_name)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertEqual(
            getattr(
                self.mapper.source.c1.main, f"{camera_name}:uvc1:chan1"
            ).filename,
            evefile.data[camera_name].importer[0].source,
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main, f"{camera_name}:uvc1:chan1"
            ).dtype.names[0]: "positions",
            getattr(
                self.mapper.source.c1.main, f"{camera_name}:uvc1:chan1"
            ).dtype.names[1]: "data",
        }
        self.assertDictEqual(
            mapping_dict, evefile.data[camera_name].importer[0].mapping
        )

    def test_map_sample_camera_sets_correct_option_values_from_main(self):
        self.mapper.source = self.h5file
        camera_name = "fcm"
        self.mapper.source.add_sample_camera(camera=camera_name)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        mapping_table = {
            "BeamX": "beam_x",
            "BeamY": "beam_y",
        }
        for key, value in mapping_table.items():
            # noinspection PyUnresolvedReferences
            self.assertEqual(
                getattr(
                    self.mapper.source.c1.main, f"{camera_name}:uvc1:{key}"
                ).data[f"{camera_name}:uvc1:{key}"][0],
                getattr(evefile.data[camera_name].metadata, value),
            )

    def test_map_sample_camera_sets_correct_option_values_from_snapshot(self):
        self.mapper.source = self.h5file
        camera_name = "fcm"
        self.mapper.source.add_sample_camera(camera=camera_name)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        mapping_table = {
            "BeamXfrac": "fractional_x_position",
            "BeamYfrac": "fractional_y_position",
            "SkipFrames": "skip_frames",
            "AvgFrames": "average_frames",
        }
        for key, value in mapping_table.items():
            # noinspection PyUnresolvedReferences
            self.assertEqual(
                getattr(
                    self.mapper.source.c1.snapshot,
                    f"{camera_name}:uvc1:{key}",
                ).data[f"{camera_name}:uvc1:{key}"][0],
                getattr(evefile.data[camera_name].metadata, value),
            )

    def test_map_sample_camera_prefers_option_values_from_main(self):
        self.mapper.source = self.h5file
        camera_name = "fcm"
        self.mapper.source.add_sample_camera(camera=camera_name)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        mapping_table = {
            "BeamX": "beam_x",
            "BeamY": "beam_y",
        }
        for key, value in mapping_table.items():
            # noinspection PyUnresolvedReferences
            self.assertEqual(
                getattr(
                    self.mapper.source.c1.main, f"{camera_name}:uvc1:{key}"
                ).data[f"{camera_name}:uvc1:{key}"][0],
                getattr(evefile.data[camera_name].metadata, value),
            )

    def test_map_sample_camera_with_unmapped_options_logs_info(self):
        self.mapper.source = self.h5file
        camera_name = "fcm"
        self.mapper.source.add_sample_camera(camera=camera_name)
        option = "FileNumberRBV"
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.logger.setLevel(logging.INFO)
        with self.assertLogs(level=logging.INFO) as captured:
            self.mapper.map(destination=evefile)
        self.assertEqual(len(captured.records), 1)
        self.assertEqual(
            captured.records[0].getMessage(),
            f"Option {option} " f"unmapped " f"for camera {camera_name}",
        )

    # noinspection PyUnresolvedReferences
    def test_map_singlepoint_datasets_removes_from_list2map(self):
        self.mapper.source = self.h5file
        self.mapper.source.add_singlepoint_detector_data(normalized=False)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertFalse(self.mapper.datasets2map_in_main)

    # noinspection PyUnresolvedReferences
    def test_map_singlepoint_datasets_adds_datasets(self):
        self.mapper.source = self.h5file
        datasets = self.mapper.source.add_singlepoint_detector_data(
            normalized=False
        )
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        for dataset in datasets:
            h5_dataset = getattr(self.mapper.source.c1.main, dataset)
            self.assertIn(dataset, evefile.data.keys())
            self.assertIsInstance(
                evefile.data[dataset],
                evedata.evefile.entities.data.SinglePointChannelData,
            )
            self.assertEqual(
                dataset,
                evefile.data[dataset].metadata.id,
            )
            self.assertEqual(
                h5_dataset.attributes["Name"],
                evefile.data[dataset].metadata.name,
            )
            self.assertEqual(
                h5_dataset.attributes["Unit"],
                evefile.data[dataset].metadata.unit,
            )
            self.assertEqual(
                h5_dataset.attributes["Access"].split(":", maxsplit=1)[1],
                evefile.data[dataset].metadata.pv,
            )
            self.assertEqual(
                h5_dataset.attributes["Access"].split(":", maxsplit=1)[0],
                evefile.data[dataset].metadata.access_mode,
            )

    # noinspection PyUnresolvedReferences
    def test_map_singlepoint_datasets_adds_importer(self):
        self.mapper.source = self.h5file
        datasets = self.mapper.source.add_singlepoint_detector_data(
            normalized=False
        )
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        for dataset in datasets:
            self.assertEqual(
                getattr(self.mapper.source.c1.main, dataset).filename,
                evefile.data[dataset].importer[0].source,
            )
            mapping_dict = {
                getattr(self.mapper.source.c1.main, dataset).dtype.names[
                    0
                ]: "positions",
                getattr(self.mapper.source.c1.main, dataset).dtype.names[
                    1
                ]: "data",
            }
            self.assertDictEqual(
                mapping_dict, evefile.data[dataset].importer[0].mapping
            )

    # noinspection PyUnresolvedReferences
    def test_map_normalized_singlepoint_datasets_adds_datasets(self):
        self.mapper.source = self.h5file
        self.mapper.source.add_singlepoint_detector_data(normalized=True)
        dataset = "K0617:gw24126chan1"
        normalizing = "K0617:gw24126chan1__A2980:gw24103chan1"
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertIn(dataset, evefile.data.keys())
        self.assertIsInstance(
            evefile.data[dataset],
            evedata.evefile.entities.data.SinglePointNormalizedChannelData,
        )
        h5_dataset = getattr(
            self.mapper.source.c1.main.normalized, normalizing
        )
        self.assertEqual(
            h5_dataset.attributes["normalizeId"],
            evefile.data[dataset].metadata.normalize_id,
        )

    # noinspection PyUnresolvedReferences
    def test_map_normalized_singlepoint_datasets_adds_importer(self):
        self.mapper.source = self.h5file
        self.mapper.source.add_singlepoint_detector_data(normalized=True)
        dataset = "K0617:gw24126chan1"
        normalizing = "K0617:gw24126chan1__A2980:gw24103chan1"
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        for importer in evefile.data[dataset].importer:
            self.assertEqual(
                getattr(self.mapper.source.c1.main, dataset).filename,
                importer.source,
            )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main.normalized, normalizing
            ).dtype.names[1]: "normalized_data",
        }
        self.assertDictEqual(
            mapping_dict, evefile.data[dataset].importer[1].mapping
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main, normalizing.split("__")[1]
            ).dtype.names[1]: "normalizing_data",
        }
        self.assertDictEqual(
            mapping_dict, evefile.data[dataset].importer[2].mapping
        )

    # noinspection PyUnresolvedReferences
    def test_map_interval_dataset_removes_from_list2map(self):
        self.mapper.source = self.h5file
        self.mapper.source.add_interval_detector_data(normalized=False)
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertFalse(self.mapper.datasets2map_in_main)

    # noinspection PyUnresolvedReferences
    def test_map_interval_dataset_adds_dataset(self):
        self.mapper.source = self.h5file
        dataset = self.mapper.source.add_interval_detector_data(
            normalized=False
        )
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        h5_dataset = getattr(self.mapper.source.c1.main, dataset)
        self.assertIn(dataset, evefile.data.keys())
        self.assertIsInstance(
            evefile.data[dataset],
            evedata.evefile.entities.data.IntervalChannelData,
        )
        self.assertEqual(
            dataset,
            evefile.data[dataset].metadata.id,
        )
        self.assertEqual(
            h5_dataset.attributes["Name"],
            evefile.data[dataset].metadata.name,
        )
        self.assertEqual(
            h5_dataset.attributes["Access"].split(":", maxsplit=1)[1],
            evefile.data[dataset].metadata.pv,
        )
        self.assertEqual(
            h5_dataset.attributes["Access"].split(":", maxsplit=1)[0],
            evefile.data[dataset].metadata.access_mode,
        )

    def test_map_interval_channel_sets_trigger_interval(self):
        self.mapper.source = self.h5file
        dataset = self.mapper.source.add_interval_detector_data(
            normalized=False
        )
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        # noinspection PyUnresolvedReferences
        self.assertEqual(
            getattr(
                self.mapper.source.c1.main.standarddev,
                f"{dataset}__TrigIntv-StdDev",
            ).data["TriggerIntv"][0],
            evefile.data[dataset].metadata.trigger_interval,
        )

    # noinspection PyUnresolvedReferences
    def test_map_interval_dataset_adds_importer(self):
        self.mapper.source = self.h5file
        dataset = self.mapper.source.add_interval_detector_data(
            normalized=False
        )
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        for importer in evefile.data[dataset].importer:
            self.assertEqual(
                getattr(self.mapper.source.c1.main, dataset).filename,
                importer.source,
            )
        mapping_dict = {
            getattr(self.mapper.source.c1.main, dataset).dtype.names[
                0
            ]: "positions",
            getattr(self.mapper.source.c1.main, dataset).dtype.names[
                1
            ]: "data",
        }
        self.assertDictEqual(
            mapping_dict, evefile.data[dataset].importer[0].mapping
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main.standarddev, f"{dataset}__Count"
            ).dtype.names[1]: "counts",
        }
        self.assertDictEqual(
            mapping_dict, evefile.data[dataset].importer[1].mapping
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main.standarddev,
                f"{dataset}__TrigIntv-StdDev",
            ).dtype.names[2]: "std",
        }
        self.assertDictEqual(
            mapping_dict, evefile.data[dataset].importer[2].mapping
        )

    # noinspection PyUnresolvedReferences
    def test_map_normalized_interval_dataset_adds_dataset(self):
        self.mapper.source = self.h5file
        dataset = self.mapper.source.add_interval_detector_data(
            normalized=True
        )
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        h5_dataset = getattr(self.mapper.source.c1.main.normalized, dataset)
        self.assertIn(dataset, evefile.data.keys())
        self.assertIsInstance(
            evefile.data[dataset],
            evedata.evefile.entities.data.IntervalNormalizedChannelData,
        )
        self.assertEqual(
            dataset,
            evefile.data[dataset].metadata.id,
        )
        self.assertEqual(
            h5_dataset.attributes["Name"],
            evefile.data[dataset].metadata.name,
        )
        self.assertEqual(
            h5_dataset.attributes["Access"].split(":", maxsplit=1)[1],
            evefile.data[dataset].metadata.pv,
        )
        self.assertEqual(
            h5_dataset.attributes["Access"].split(":", maxsplit=1)[0],
            evefile.data[dataset].metadata.access_mode,
        )

    # noinspection PyUnresolvedReferences
    def test_map_normalized_interval_dataset_adds_importer(self):
        self.mapper.source = self.h5file
        dataset = self.mapper.source.add_interval_detector_data(
            normalized=True
        )
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        for importer in evefile.data[dataset].importer:
            self.assertEqual(
                getattr(
                    self.mapper.source.c1.main.normalized, dataset
                ).filename,
                importer.source,
            )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main.normalized, dataset
            ).dtype.names[0]: "positions",
            getattr(
                self.mapper.source.c1.main.normalized, dataset
            ).dtype.names[1]: "data",
        }
        self.assertDictEqual(
            mapping_dict, evefile.data[dataset].importer[0].mapping
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main.standarddev, f"{dataset}__Count"
            ).dtype.names[1]: "counts",
        }
        self.assertDictEqual(
            mapping_dict, evefile.data[dataset].importer[1].mapping
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main.standarddev,
                f"{dataset}__TrigIntv-StdDev",
            ).dtype.names[2]: "std",
        }
        self.assertDictEqual(
            mapping_dict, evefile.data[dataset].importer[2].mapping
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main.normalized, dataset
            ).dtype.names[1]: "normalized_data",
        }
        self.assertDictEqual(
            mapping_dict, evefile.data[dataset].importer[3].mapping
        )

    # noinspection PyUnresolvedReferences
    def test_map_average_dataset_removes_from_list2map(self):
        self.mapper.source = self.h5file
        self.mapper.source.add_average_detector_data(
            normalized=False, maxdev=False
        )
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertFalse(self.mapper.datasets2map_in_main)

    # noinspection PyUnresolvedReferences
    def test_map_average_dataset_adds_dataset(self):
        self.mapper.source = self.h5file
        dataset = self.mapper.source.add_average_detector_data(
            normalized=False, maxdev=False
        )
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        h5_dataset = getattr(self.mapper.source.c1.main, dataset)
        self.assertIn(dataset, evefile.data.keys())
        self.assertIsInstance(
            evefile.data[dataset],
            evedata.evefile.entities.data.AverageChannelData,
        )
        self.assertEqual(
            dataset,
            evefile.data[dataset].metadata.id,
        )
        self.assertEqual(
            h5_dataset.attributes["Name"],
            evefile.data[dataset].metadata.name,
        )
        self.assertEqual(
            h5_dataset.attributes["Access"].split(":", maxsplit=1)[1],
            evefile.data[dataset].metadata.pv,
        )
        self.assertEqual(
            h5_dataset.attributes["Access"].split(":", maxsplit=1)[0],
            evefile.data[dataset].metadata.access_mode,
        )

    # noinspection PyUnresolvedReferences
    def test_map_average_dataset_adds_importer(self):
        self.mapper.source = self.h5file
        dataset = self.mapper.source.add_average_detector_data(
            normalized=False, maxdev=False
        )
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        for importer in evefile.data[dataset].importer:
            self.assertEqual(
                getattr(self.mapper.source.c1.main, dataset).filename,
                importer.source,
            )
        mapping_dict = {
            getattr(self.mapper.source.c1.main, dataset).dtype.names[
                0
            ]: "positions",
            getattr(self.mapper.source.c1.main, dataset).dtype.names[
                1
            ]: "data",
        }
        self.assertDictEqual(
            mapping_dict, evefile.data[dataset].importer[0].mapping
        )

    # noinspection PyUnresolvedReferences
    def test_map_average_dataset_with_maxdev_adds_additional_importer(self):
        self.mapper.source = self.h5file
        dataset = self.mapper.source.add_average_detector_data(
            normalized=False, maxdev=True
        )
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        for importer in evefile.data[dataset].importer:
            self.assertEqual(
                getattr(self.mapper.source.c1.main, dataset).filename,
                importer.source,
            )
        mapping_dict = {
            getattr(self.mapper.source.c1.main, dataset).dtype.names[
                0
            ]: "positions",
            getattr(self.mapper.source.c1.main, dataset).dtype.names[
                1
            ]: "data",
        }
        self.assertDictEqual(
            mapping_dict, evefile.data[dataset].importer[0].mapping
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main.averagemeta, f"{dataset}__Attempts"
            ).dtype.names[1]: "attempts",
        }
        self.assertDictEqual(
            mapping_dict, evefile.data[dataset].importer[1].mapping
        )

    def test_map_average_channel_sets_metadata(self):
        self.mapper.source = self.h5file
        dataset = self.mapper.source.add_average_detector_data(
            normalized=False, maxdev=False
        )
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        # noinspection PyUnresolvedReferences
        self.assertEqual(
            getattr(
                self.mapper.source.c1.main.averagemeta,
                f"{dataset}__AverageCount",
            ).data["AverageCount"][0],
            evefile.data[dataset].metadata.n_averages,
        )

    # noinspection PyUnresolvedReferences
    def test_map_average_channel_with_maxdev_sets_metadata(self):
        self.mapper.source = self.h5file
        dataset = self.mapper.source.add_average_detector_data(
            normalized=False, maxdev=True
        )
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertEqual(
            getattr(
                self.mapper.source.c1.main.averagemeta,
                f"{dataset}__Attempts",
            ).data["MaxAttempts"][0],
            evefile.data[dataset].metadata.max_attempts,
        )
        self.assertEqual(
            getattr(
                self.mapper.source.c1.main.averagemeta,
                f"{dataset}__Limit-MaxDev",
            ).data["Limit"][0],
            evefile.data[dataset].metadata.low_limit,
        )
        self.assertEqual(
            getattr(
                self.mapper.source.c1.main.averagemeta,
                f"{dataset}__Limit-MaxDev",
            ).data["maxDeviation"][0],
            evefile.data[dataset].metadata.max_deviation,
        )

    # noinspection PyUnresolvedReferences
    def test_map_normalized_average_dataset_adds_dataset(self):
        self.mapper.source = self.h5file
        dataset = self.mapper.source.add_average_detector_data(
            normalized=True, maxdev=False
        )
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        h5_dataset = getattr(self.mapper.source.c1.main.normalized, dataset)
        dataset = dataset.split("__")[0]
        self.assertIn(dataset, evefile.data.keys())
        self.assertIsInstance(
            evefile.data[dataset],
            evedata.evefile.entities.data.AverageNormalizedChannelData,
        )
        self.assertEqual(
            dataset,
            evefile.data[dataset].metadata.id,
        )
        self.assertEqual(
            h5_dataset.attributes["Name"],
            evefile.data[dataset].metadata.name,
        )
        self.assertEqual(
            h5_dataset.attributes["Access"].split(":", maxsplit=1)[1],
            evefile.data[dataset].metadata.pv,
        )
        self.assertEqual(
            h5_dataset.attributes["Access"].split(":", maxsplit=1)[0],
            evefile.data[dataset].metadata.access_mode,
        )

    # noinspection PyUnresolvedReferences
    def test_map_normalized_average_dataset_adds_importer(self):
        self.mapper.source = self.h5file
        dataset = self.mapper.source.add_average_detector_data(
            normalized=True, maxdev=False
        )
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        base_dataset = dataset.split("__")[0]
        for importer in evefile.data[base_dataset].importer:
            self.assertEqual(
                getattr(self.mapper.source.c1.main, base_dataset).filename,
                importer.source,
            )
        mapping_dict = {
            getattr(self.mapper.source.c1.main, base_dataset).dtype.names[
                0
            ]: "positions",
            getattr(self.mapper.source.c1.main, base_dataset).dtype.names[
                1
            ]: "data",
        }
        self.assertDictEqual(
            mapping_dict, evefile.data[base_dataset].importer[0].mapping
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main.normalized, dataset
            ).dtype.names[1]: "normalized_data",
        }
        self.assertDictEqual(
            mapping_dict, evefile.data[base_dataset].importer[1].mapping
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main, dataset.split("__")[1]
            ).dtype.names[1]: "normalizing_data",
        }
        self.assertDictEqual(
            mapping_dict, evefile.data[base_dataset].importer[2].mapping
        )

    # noinspection PyUnresolvedReferences
    def test_map_norm_avg_dataset_with_maxdev_adds_additional_importer(self):
        self.mapper.source = self.h5file
        dataset = self.mapper.source.add_average_detector_data(
            normalized=True, maxdev=True
        )
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        base_dataset = dataset.split("__")[0]
        for importer in evefile.data[base_dataset].importer:
            self.assertEqual(
                getattr(self.mapper.source.c1.main, base_dataset).filename,
                importer.source,
            )
        mapping_dict = {
            getattr(self.mapper.source.c1.main, base_dataset).dtype.names[
                0
            ]: "positions",
            getattr(self.mapper.source.c1.main, base_dataset).dtype.names[
                1
            ]: "data",
        }
        self.assertDictEqual(
            mapping_dict, evefile.data[base_dataset].importer[0].mapping
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main.averagemeta, f"{dataset}__Attempts"
            ).dtype.names[1]: "attempts",
        }
        self.assertDictEqual(
            mapping_dict, evefile.data[base_dataset].importer[1].mapping
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main.normalized, dataset
            ).dtype.names[1]: "normalized_data",
        }
        self.assertDictEqual(
            mapping_dict, evefile.data[base_dataset].importer[2].mapping
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main, dataset.split("__")[1]
            ).dtype.names[1]: "normalizing_data",
        }
        self.assertDictEqual(
            mapping_dict, evefile.data[base_dataset].importer[3].mapping
        )

    def test_map_axes_snapshot_datasets(self):
        self.mapper.source = self.h5file
        datasets = self.mapper.source.add_axes_snapshot_data()
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertTrue(evefile.snapshots)
        for dataset in datasets:
            self.assertIsInstance(
                evefile.snapshots[dataset],
                evedata.evefile.entities.data.AxisData,
            )

    def test_map_axes_snapshot_datasets_removes_from_2map(self):
        self.mapper.source = self.h5file
        datasets = self.mapper.source.add_axes_snapshot_data()
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        for dataset in datasets:
            self.assertNotIn(dataset, self.mapper.datasets2map_in_snapshot)

    def test_map_channel_snapshot_datasets(self):
        self.mapper.source = self.h5file
        datasets = self.mapper.source.add_channel_snapshot_data()
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        self.assertTrue(evefile.snapshots)
        for dataset in datasets:
            self.assertIsInstance(
                evefile.snapshots[dataset],
                evedata.evefile.entities.data.AxisData,
            )

    def test_map_channel_snapshot_datasets_removes_from_2map(self):
        self.mapper.source = self.h5file
        datasets = self.mapper.source.add_channel_snapshot_data()
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        for dataset in datasets:
            self.assertNotIn(dataset, self.mapper.datasets2map_in_snapshot)

    def test_map_mpskip(self):
        self.mapper.source = self.h5file
        self.mapper.source.add_mpskip()
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        dataset = "MPSKIP:sx70001"
        dataset_id = f"{dataset}counterchan1"
        h5_dataset = getattr(self.mapper.source.c1.main, dataset_id)
        self.assertIn(dataset, evefile.data)
        self.assertIsInstance(
            evefile.data[dataset],
            evedata.evefile.entities.data.SkipData,
        )
        self.assertEqual(
            dataset_id,
            evefile.data[dataset].metadata.id,
        )
        self.assertEqual(
            h5_dataset.attributes["Name"],
            evefile.data[dataset].metadata.name,
        )
        self.assertEqual(
            h5_dataset.attributes["Access"].split(":", maxsplit=1)[1],
            evefile.data[dataset].metadata.pv,
        )
        self.assertEqual(
            h5_dataset.attributes["Access"].split(":", maxsplit=1)[0],
            evefile.data[dataset].metadata.access_mode,
        )

    # noinspection PyUnresolvedReferences
    def test_map_mpskip_adds_importer(self):
        self.mapper.source = self.h5file
        self.mapper.source.add_mpskip()
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        dataset = "MPSKIP:sx70001"
        dataset_id = f"{dataset}counterchan1"
        self.assertEqual(
            getattr(self.mapper.source.c1.main, dataset_id).filename,
            evefile.data[dataset].importer[0].source,
        )
        mapping_dict = {
            getattr(self.mapper.source.c1.main, dataset_id).dtype.names[
                0
            ]: "positions",
            getattr(self.mapper.source.c1.main, dataset_id).dtype.names[
                1
            ]: "data",
        }
        self.assertDictEqual(
            mapping_dict, evefile.data[dataset].importer[0].mapping
        )

    def test_map_mpskip_sets_metadata(self):
        self.mapper.source = self.h5file
        self.mapper.source.add_mpskip()
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        dataset = "MPSKIP:sx70001"
        mapping_table = {
            "detector": "channel",
            "limit": "low_limit",
            "maxdev": "max_deviation",
            "skipcount": "n_averages",
        }
        for key, value in mapping_table.items():
            # print(f"{dataset}{key}")
            # noinspection PyUnresolvedReferences
            self.assertEqual(
                getattr(self.mapper.source.device, f"{dataset}{key}").data[
                    f"{dataset}{key}"
                ][0],
                getattr(evefile.data[dataset].metadata, value),
            )

    def test_map_mpskip_with_missing_metadata_logs(self):
        self.mapper.source = self.h5file
        self.mapper.source.add_mpskip()
        monitor2remove = "MPSKIP:sx70001maxdev"
        self.mapper.source.device.remove_item(
            getattr(self.mapper.source.device, monitor2remove)
        )
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        with self.assertLogs(version_mapping.logger) as cm:
            self.mapper.map(destination=evefile)
        self.assertIn(
            f"Could not find monitor dataset {monitor2remove}",
            cm.output[0],
        )

    def test_map_mpskip_removes_from_2map(self):
        self.mapper.source = self.h5file
        datasets, monitors = self.mapper.source.add_mpskip()
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.map(destination=evefile)
        for dataset in datasets[1:]:
            self.assertNotIn(dataset, evefile.snapshots)
            self.assertNotIn(dataset, evefile.data)
        for monitor in monitors:
            self.assertNotIn(f"MPSKIP:sx70001{monitor}", evefile.monitors)


class TestVersionMapperV6(unittest.TestCase):
    def setUp(self):
        self.mapper = version_mapping.VersionMapperV6()

    def test_instantiate_class(self):
        pass

    def test_map_converts_date_to_datetime(self):
        self.mapper.source = MockEveH5v5()
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
        self.mapper.source = MockEveH5v5()
        evefile = evedata.evefile.boundaries.evefile.EveFile()
        self.mapper.source.attributes["Simulation"] = "no"
        self.mapper.map(destination=evefile)
        self.assertIsInstance(evefile.metadata.simulation, bool)
        self.assertFalse(evefile.metadata.simulation)
        self.mapper.source.attributes["Simulation"] = "yes"
        self.mapper.map(destination=evefile)
        self.assertIsInstance(evefile.metadata.simulation, bool)
        self.assertTrue(evefile.metadata.simulation)
