import unittest

import numpy as np

from evedata.evefile.controllers import info
from evedata.evefile.entities.file import ScanModule


class TestScanModuleStructure(unittest.TestCase):
    def setUp(self):
        self.scan_module_structure = info.ScanModuleStructure()

    def test_instantiate_class(self):
        pass

    def test_create_sets_structure(self):
        scan_module = ScanModule()
        scan_module.id = 1
        scan_module.name = "Diodes"
        scan_module.positions = np.asarray([1])
        self.scan_module_structure.scan_modules = {1: scan_module}
        self.scan_module_structure.create()
        self.assertTrue(self.scan_module_structure.structure)

    def test_create_without_scan_modules_raises(self):
        self.scan_module_structure.scan_modules = None
        with self.assertRaisesRegex(ValueError, "No scan modules"):
            self.scan_module_structure.create()

    def test_create_sets_metadata_of_scan_module(self):
        scan_module = ScanModule()
        scan_module.id = 1
        scan_module.name = "Diodes"
        scan_module.positions = np.asarray([1])
        self.scan_module_structure.scan_modules = {1: scan_module}
        self.scan_module_structure.create()
        self.assertIn(
            f"{self.scan_module_structure.scan_module_marker}"
            f" {scan_module.id}:"
            f" {scan_module.name}",
            self.scan_module_structure.structure[0],
        )

    def test_create_sets_metadata_of_scan_modules(self):
        scan_module1 = ScanModule()
        scan_module1.id = 1
        scan_module1.name = "Diodes"
        scan_module1.positions = np.asarray([1, 2, 3])
        self.scan_module_structure.scan_modules[scan_module1.id] = (
            scan_module1
        )
        scan_module2 = ScanModule()
        scan_module2.id = 2
        scan_module2.name = "MB"
        scan_module2.positions = np.asarray([4, 5, 6, 7, 8])
        self.scan_module_structure.scan_modules[scan_module2.id] = (
            scan_module2
        )
        self.scan_module_structure.create()
        self.assertIn(
            f"{self.scan_module_structure.scan_module_marker} "
            f"{scan_module1.id}: {scan_module1.name} - #"
            f"{scan_module1.positions[0]} ["
            f"{scan_module1.positions[0]}..{scan_module1.positions[-1]}]",
            self.scan_module_structure.structure[0],
        )
        self.assertIn(
            f"{self.scan_module_structure.scan_module_marker} "
            f"{scan_module2.id}: {scan_module2.name} - #"
            f"{scan_module2.positions[0]} ["
            f"{scan_module2.positions[0]}..{scan_module2.positions[-1]}]",
            self.scan_module_structure.structure[1],
        )
