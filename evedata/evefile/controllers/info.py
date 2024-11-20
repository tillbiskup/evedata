"""
*Information on scans, often relevant for debugging purposes.*

"""

import logging


logger = logging.getLogger(__name__)


class ScanModuleStructure:
    """
    One sentence (on one line) describing the class.

    More description comes here...


    Attributes
    ----------
    attr : :class:`None`
        Short description

    Raises
    ------
    exception
        Short description when and why raised


    Examples
    --------
    It is always nice to give some examples how to use the class. Best to do
    that with code examples:

    .. code-block::

        obj = ScanModuleStructure()
        ...



    """

    def __init__(self):
        self.scan_modules = {}
        self.structure = []
        self.scan_module_marker = "+"

    def create(self):
        if not self.scan_modules:
            raise ValueError("No scan modules")
        for scan_module in self.scan_modules.values():
            self.structure.append(
                f"{self.scan_module_marker} "
                f"{scan_module.id}: {scan_module.name} - #"
                f"{scan_module.positions[0]} [{scan_module.positions[0]}.."
                f"{scan_module.positions[-1]}]"
            )
