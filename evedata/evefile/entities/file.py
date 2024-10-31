"""

*Entities representing an eveH5 file on the entire file level.*

While the entities in this module represent the contents of an eveH5 file,
they clearly abstract from the internal structure of these files.
Furthermore, there are different versions of the underlying schema
(*i.e.*, organisation) of these files, and the entities abstract away from
these differences as well. The key concept is to provide users of the
``evedata`` interface with useful abstractions allowing to conveniently
access all the data present in an eveH5 file.


Overview
========

A first overview of the classes implemented in this module and their
hierarchy is given in the UML diagram below.


.. figure:: /uml/evedata.evefile.entities.file.*
    :align: center

    Class hierarchy of the :mod:`evedata.evefile.entities.file` module. The
    :class:`File` class is sort of the central interface to the entire
    subpackage, as this class provides a faithful representation of all
    information available from a given eveH5 file. To this end,
    it incorporates instances of classes of the other modules of the
    subpackage. Furthermore, "Scan" inherits from the identically named
    facade of the scan functional layer and contains the full information
    of the SCML file (if the SCML file is present in the eveH5 file).


Module documentation
====================

"""

import datetime
import logging

import evedata.scan.boundaries.scan

logger = logging.getLogger(__name__)


class File:
    """
    Representation of all information available from a given eveH5 file.

    Individual measurements are saved in HDF5 files using a particular
    schema (eveH5). Besides file-level metadata, there are log messages,
    a scan description (originally an XML/SCML file), and the actual data.

    The data are organised in three functionally different sections: data,
    snapshots, and monitors.


    Attributes
    ----------
    metadata : :class:`Metadata`
        File metadata

    log_messages : :class:`list`
        Log messages from an individual measurement

        Each item in the list is an instance of :class:`LogMessage`.

    scan : :class:`Scan`
        Description of the actual scan.

    scan_modules : :class:`dict`
        Modules the scan consists of.

        Each item is an instance of :class:`ScanModule` and contains the
        data recorded within the given scan module.

        In case of no scan description present, a "dummy" scan module will
        be created containing *all* data.

    snapshots : :class:`dict`
        Device data recorded as snapshot during a measurement.

        Each item is an instance of
        :class:`evedata.evefile.entities.data.Data`.

    monitors : :class:`dict`
        Device data monitored during a measurement.

        Each item is an instance of
        :class:`evedata.evefile.entities.data.Data`.

    position_timestamps : :class:`evedata.evefile.entities.data.TimestampData`
        Timestamps for each individual position.

        Monitors have timestamps (milliseconds since start of the scan)
        rather than positions as primary quantisation axis. This object
        provides a mapping between timestamps and positions and can be used
        to map monitor data to positions.


    Examples
    --------
    The :class:`File` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        self.metadata = Metadata()
        self.log_messages = []
        self.scan = Scan()
        self.scan_modules = {}
        self.data = {}
        self.snapshots = {}
        self.monitors = {}
        self.position_timestamps = None


class Metadata:
    """
    Metadata of a given eveH5 file.

    As measurements result in individual files, there is a series of
    crucial metadata of such a measurement on this global level.


    Attributes
    ----------
    filename : :class:`str`
        Name (full path) of the eveH5 file.

    eveh5_version : :class:`str`
        Version of the eveH5 schema.

    eve_version : :class:`str`
        Version of the eve engine used to record the data.

    xml_version : :class:`str`
        Version of the schema used for the scan description (SCML/XML)

    measurement_station : :class:`str`
        Name of the measurement station used to record the data.

    start : :class:`datetime.datetime`
        Timestamp of the start of the measurement

    end : :class:`datetime.datetime`
        Timestamp of the end of the measurement

    description : :class:`str`
        User-entered description of the entire scan.

    simulation : :class:`bool`
        Flag signalling whether the measurement was a simulation.

        Default: ``False``

    preferred_axis : :class:`string`
        Name of the axis marked as preferred in the scan description.

        Default: ""

    preferred_channel : :class:`string`
        Name of the channel marked as preferred in the scan description.

        Default: ""

    preferred_normalisation_channel : :class:`string`
        Name of the channel marked as preferred for normalising.

        Default: ""

    Examples
    --------
    The :class:`Metadata` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        self.filename = ""
        self.eveh5_version = ""
        self.eve_version = ""
        self.xml_version = ""
        self.measurement_station = ""
        self.start = datetime.datetime.now()
        self.end = datetime.datetime.now()
        self.description = ""
        self.simulation = False
        self.preferred_axis = ""
        self.preferred_channel = ""
        self.preferred_normalisation_channel = ""


class Scan(evedata.scan.boundaries.scan.Scan):
    """
    Description of a scan used to record data.

    Measurements are described and defined as scans using a special XML
    schema termed Scan Markup Language (SCML).


    Attributes
    ----------
    author : :class:`str`
        Author of a given scan description, as set in the SCML file.

    filename : :class:`str`
        Name of the SCML file containing the scan description.


    Examples
    --------
    The :class:`Scan` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.author = ""
        self.filename = ""


class LogMessage:
    """
    Log message from an individual measurement.

    Operators can enter log messages during a measurement using the
    eve-gui. In such case, the respective message appears in the eveH5
    file together with a timestamp.


    Attributes
    ----------
    timestamp : :class:`datetime.datetime`
        Timestamp of the log message

    message : :class:`str`
        Actual content of the log message.


    Examples
    --------
    The :class:`Scan` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        self.timestamp = datetime.datetime.now()
        self.message = ""

    def from_string(self, string=""):
        """
        Set attributes from string.

        In eveH5 files up to v7, the log messages are single strings with
        the ISO timestamp at the beginning, followed by the actual message.
        Timestamp and message are separated by ": ".

        This method separates both parts and converts the timestamp into an
        actual :obj:`datetime.datetime` object, consistent with the
        :attr:`timestamp` attribute.

        Parameters
        ----------
        string : :class:`str`
            Log message consisting of timestamp and actual message.

        """
        timestamp, message = string.split(": ", maxsplit=1)
        self.timestamp = datetime.datetime.fromisoformat(timestamp)
        self.message = message


class ScanModule:
    """
    Representation of a scan module, containing the corresponding data.

    Scans are organised in scan modules, and despite the flat organisation of
    the data files up to eveH5 v7, organising the data according to the
    scan modules they are recorded in is not only sensible, but sometimes
    necessary to properly deal with the data.

    How does this class differ from
    :class:`evedata.scan.entities.scan.ScanModule` having the same name?
    Both represent scan modules as building blocks of a scan/measurement,
    but serve different purposes on different abstraction layers. While
    :class:`evedata.scan.entities.scan.ScanModule` represents the scan
    modules as defined in a scan (in an SCML file) quite closely,
    the present class provides the organisation layer for the representation
    of the actual data, be it in the :class:`EveFile
    <evedata.evefile.boundaries.evefile.EveFile>` or :class:`Measurement
    <evedata.measurement.boundaries.measurement.Measurement>` interfaces.

    Attributes
    ----------
    name : :class:`str`
        Given name of the scan module, as displayed in the eve GUI.

    id : :class:`int`
        Unique (numeric) ID of the scan module.

        Typically, when a scan gets created using the eve GUI, a unique ID
        will automatically be assigned to each individual scan module.

        IDs are required to be unique.

    parent : :class:`id`
        Unique ID of the parent scan module.

        In case of the first scan module, this is 0.

        Default: 0

    appended : :class:`int`
        Unique ID of the appended scan module.

        A scan module can have 0..1 appended and 0..1 nested scan modules.

        Default: None

    nested : :class:`int`
        Unique ID of the nested scan module.

        A scan module can have 0..1 appended and 0..1 nested scan modules.

        Default: None

    data : :class:`dict`
        Data recorded from the devices involved in the scan module.

        Each item is an instance of
        :class:`evedata.evefile.entities.data.Data`.

    positions : :class:`numpy.array`
        Actual positions created during the scan module.

        These positions cannot necessarily be inferred from the definition
        of the scan module itself, but sometimes only be obtained from the
        actual measurement.


    Examples
    --------
    The :class:`ScanModule` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        self.name = "main"
        self.id = 1  # noqa
        self.parent = 0
        self.appended = None
        self.nested = None
        self.data = {}
        self.positions = None

    @property
    def device_names(self):
        """
        Name of the devices contained in :attr:`data`.

        The keys used in :attr:`data` are the XML-IDs and names of the
        HDF5 datasets. However, usually each device has a more readable
        and pronounceable name that it is known by.

        Note that device names are not guaranteed to be unique. For all
        devices in the :attr:`data` attribute, this should be the case,
        though.

        Returns
        -------
        device_names : :class:`dict`
            Names of the devices contained in :attr:`data`.

            The keys are the readable and pronounceable names of the
            devices, the values are the corresponding XML-IDs.

        """
        return {
            device.metadata.name: device_id
            for device_id, device in self.data.items()
        }
