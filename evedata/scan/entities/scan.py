"""

*Entities representing a scan performed by the eve engine.*

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 2

Scans are defined in XML files using a schema called Scan Markup Language
(SCML). While these scan descriptions can be conveniently be modified using
the eve GUI, eventually the eve engine receives an SCML file with a scan
description that it executes.

The idea behind this module and the entire :mod:`scan <evedata.scan>`
subpackage is *not* to really parse the SCML file and provide means to
modify the scan description, but rather to represent those aspects important
for interpreting the resulting eveH5 files, besides all the relevant
metadata for the individual devices used.

An SCML file usually contains a scan block defining the actual scan, and the
entities of such a scan is what this module is concerned with. Other parts
of the SCML file are a setup part (not yet a block, as of SCML schema v9.2)
containing the description of the devices (detectors, motors, devices)
explicitly used in the scan, and a plugins section.


Overview
========

A first overview of the classes implemented in this module and their
hierarchy is given in the UML diagram below, :numref:`Fig. %s
<fig-uml_evedata-scan.scan_api>`.


.. _fig-uml_evedata-scan.scan_api:

.. figure:: /uml/evedata.scan.entities.scan.*
    :align: center
    :width: 750px

    Class hierarchy of the :mod:`scan.entities.scan
    <evedata.scan.entities.scan>` module, closely resembling the schema of
    the SCML file. As the scan module is already quite complicated,
    event and plot-related classes have been separated into their own
    modules and are described below. Hint: For a larger view, you may open
    the image in a separate tab. As it is vectorised (SVG), it scales well.


.. important::

    Note that for the time being, only a subset of the classes shown in the
    above UML diagram are implemented, and only the most relevant attributes
    of these classes.


Module documentation
====================

"""

import logging


logger = logging.getLogger(__name__)


class Scan:
    """
    Representation of all information available for a given scan.

    A scan consists of scan modules, a series of metadata, and different
    types of events.


    Attributes
    ----------
    repeat_count : :class:`int`
        Short description

    comment : :class:`str`
        Short description

    description : :class:`str`
        Short description

    scan_modules : :class:`dict`
        Scan modules the scan consists of.

        The keys are the unique IDs (UID) of the respective scan module,
        and the values :obj:`AbstractScanModule` objects. This allows for easy
        access of a given scan module given its UID.


    Examples
    --------
    The :class:`Scan` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.scan` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        self.repeat_count = 1
        self.comment = ""
        self.description = ""
        self.scan_modules = {}


class AbstractScanModule:
    r"""
    Abstract base class for scan modules.

    A scan consists of 1..\ *n* scan modules. Each scan module has a parent
    (the first defined scan module has the root node with 0 as its parent)
    and 0..1 appended and 0..1 nested scan modules.

    An appended scan module is executed once the current scan module is
    finished, while nested scan modules are executed for each position of
    the current scan module.


    Attributes
    ----------
    id : :class:`int`
        Unique ID of the scan module.

        The IDs are numeric and start with 1, as the root node is always 0.
        Hence, the first scan module defined will have 0 as its parent.

        Default: 1

    name : :class:`str`
        Name of the scan module.

        The scan module appears in the graphical representation eve GUI with
        this name. Hence, providing good names can be very valuable.

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


    Examples
    --------
    The :class:`AbstractScanModule` class is not meant to be used directly, as
    any entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.scan` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        self.id = 1  # noqa
        self.name = ""
        self.parent = 0
        self.appended = None
        self.nested = None


class ScanModule(AbstractScanModule):
    """
    One sentence (on one line) describing the class.

    More description comes here...


    Attributes
    ----------
    id : :class:`int`
        Unique ID of the scan module.

        The IDs are numeric and start with 1, as the root node is always 0.
        Hence, the first scan module defined will have 0 as its parent.

        Default: 1

    name : :class:`str`
        Name of the scan module.

        The scan module appears in the graphical representation eve GUI with
        this name. Hence, providing good names can be very valuable.

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

    axes : :class:`dict`
        Motor axes actively being used in the scan module.

        The keys are the unique IDs (UID) of the axis, while the values are
        :obj:`Axis` objects. This allows for easy access of a given axis
        given its UID.

    channels : :class:`dict`
        Detector channels actively being used in the scan module.

        The keys are the unique IDs (UID) of the channel, while the values are
        :obj:`Channel` objects. This allows for easy access of a given channel
        given its UID.


    Examples
    --------
    The :class:`ScanModule` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.scan` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.axes = {}
        self.channels = {}


class Channel:
    """
    Representation of a channel used in a scan module.

    Scan modules use detector channels and motor axes in their main phase.
    All relevant information regarding a channel with respect to its use in
    a scan module is contained in this class and classes inheriting from it.

    To get further information on the channel in general, its :attr:`id` can
    be used to look up this information in the ``setup`` part of the SCML file.


    Attributes
    ----------
    id : :class:`str`
        Unique ID of the channel.

        Each channel has a unique ID that is used internally to refer to it.
        The names displayed in the GUI are "given" names different from this
        ID, though. The HDF5 datasets in an eveH5 file use these UIDs as name.

    normalize_id : :class:`str`
        Unique ID of the channel used for normalization.

        Channels can be normalized by other channels, *i.e.* the values
        divided by the values obtained from the normalizing channel.


    Examples
    --------
    The :class:`Channel` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.scan` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        self.id = ""  # noqa
        self.normalize_id = ""


class Axis:
    """
    Representation of an axis used in a scan module.

    Scan modules use detector channels and motor axes in their main phase.
    All relevant information regarding an axis with respect to its use in
    a scan module is contained in this class.

    To get further information on the axis in general, its :attr:`id` can
    be used to look up this information in the ``setup`` part of the SCML file.


    Attributes
    ----------
    id : :class:`str`
        Unique ID of the axis.

        Each axis has a unique ID that is used internally to refer to it.
        The names displayed in the GUI are "given" names different from this
        ID, though. The HDF5 datasets in an eveH5 file use these UIDs as name.


    Examples
    --------
    The :class:`Axis` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.scan` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        self.id = ""  # noqa
