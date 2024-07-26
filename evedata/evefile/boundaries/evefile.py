"""

*High-level Python object representation of eveH5 file contents.*

The aim of this module is to provide a high-level representation of
the contents of an eveH5 file.


Module documentation
====================

"""

import logging

from evedata.evefile.entities.file import File as FileEntity


logger = logging.getLogger(__name__)


class File(FileEntity):
    """
    High-level Python object representation of eveH5 file contents.

    This class serves as facade to the entire :mod:`evedata.evefile`
    subpackage and provides a rather high-level representation of the
    contents of an individual eveH5 file.

    Individual measurements are saved in HDF5 files using a particular
    schema (eveH5). Besides file-level metadata, there are log messages,
    a scan description (originally an XML/SCML file), and the actual data.

    The data are organised in three functionally different sections: data,
    snapshots, and monitors.


    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.file.Metadata`
        File metadata

    log_messages : :class:`list`
        Log messages from an individual measurement

        Each item in the list is an instance of
        :class:`evedata.evefile.entities.file.LogMessage`.

    scan : :class:`Scan`
        Description of the actual scan.

    data : :class:`list`
        Data recorded from the devices involved in a measurement.

        Each item in the list is an instance of
        :class:`evedata.evefile.entities.data.Data`.

    snapshots : :class:`list`
        Device data recorded as snapshot during a measurement.

        Only those device data that are not options belonging to any of
        the devices in the :attr:`data` attribute are stored here.

        Each item in the list is an instance of
        :class:`evedata.evefile.entities.data.Data`.

    monitors : :class:`list`
        Device data monitored during a measurement.

        Each item in the list is an instance of
        :class:`evedata.evefile.entities.data.Data`.

    position_timestamps : :class:`evedata.evefile.entities.data.TimestampData`
        Timestamps for each individual position.

        Monitors have timestamps (milliseconds since start of the scan)
        rather than positions as primary quantisation axis. This object
        provides a mapping between timestamps and positions and can be used
        to map monitor data to positions.

    Raises
    ------
    exception
        Short description when and why raised


    Examples
    --------
    It is always nice to give some examples how to use the class. Best to do
    that with code examples:

    Loading the contents of a data file of a measurement may be as simple as:

    .. code-block::

        evefile = File()
        evefile.load(filename="my_measurement_file.h5")

    Of course, you could alternatively set the filename first,
    thus shortening the :meth:`load` method call:

    .. code-block::

        evefile = File()
        evefile.filename = "my_measurement_file.h5"
        evefile.load()


    """

    @property
    def filename(self):
        """
        Name of the file to be loaded.

        Returns
        -------
        filename : :class:`str`
            Name of the file to be loaded.

        """
        return self.metadata.filename

    @filename.setter
    def filename(self, filename=""):
        self.metadata.filename = filename

    def load(self, filename=""):
        """
        Load contents of an eveH5 file containing data.

        Parameters
        ----------
        filename : :class:`str`
            Name of the file to load.

        """
        if filename:
            self.metadata.filename = filename
