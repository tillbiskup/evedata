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
    modules. Hint: For a larger view, you may open the image in a separate
    tab. As it is vectorised (SVG), it scales well.


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

    is_nested : :class:`bool`
        Whether the scan module itself is nested.

        A scan module can either be appended or nested. Given that the
        scan modules are unaware of the other scan modules and (currently)
        only contain IDs as references to their parent and appended or
        nested scan module, this information needs to be set from outside,
        *e.g.* during mapping by the :class:`VersionMapper
        <evedata.scan.controllers.version_mapping.VersionMapper>` class.

        Default: False

    number_of_positions : :class:`int`
        Number of positions created during the scan module.

        Positions are the fundamental quantisation of the data in eveH5
        files. Each position axes are moved to is assigned a "position
        count", *i.e.* a unique integer value. Furthermore, positionings
        of axes at the end of the scan module (in the "positioning phase")
        get their own position number.

        For snapshot modules, things are quite simple: Each snapshot
        module creates its own position, one per module.

        Default: 0

    number_of_positions_per_pass : :class:`int`
        Number of positions created during *one pass* of the scan module.

        Scan modules can be nested, and even though a given scan module
        is not nested itself, it can be in a chain of scan modules that
        are nested. Hence, the total number of positions created during a
        scan for a given scan module can be different from the number of
        positions during a single pass.

        Default: 0

    positions : :class:`numpy.array`
        Actual positions created during the scan module.

        These positions cannot necessarily be inferred from the definition
        of the scan module itself, but sometimes only be obtained from the
        actual measurement.


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
        self.is_nested = False
        self.number_of_positions = 0
        self.number_of_positions_per_pass = 0
        self.positions = None


class ScanModule(AbstractScanModule):
    """
    Representation of a "classical" scan module.

    This type of scan modules is the generic building block of all scans and
    very versatile. Mainly, it consists of detector channels and motor axes,
    as well as a series of events, pre- and post-scan options, positionings
    and plots.


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

    is_nested : :class:`bool`
        Whether the scan module itself is nested.

        A scan module can either be appended or nested. Given that the
        scan modules are unaware of the other scan modules and (currently)
        only contain IDs as references to their parent and appended or
        nested scan module, this information needs to be set from outside,
        *e.g.* during mapping by the :class:`VersionMapper
        <evedata.scan.controllers.version_mapping.VersionMapper>` class.

        Default: False

    number_of_positions : :class:`int`
        Number of positions created during the scan module.

        Positions are the fundamental quantisation of the data in eveH5
        files. Each position axes are moved to is assigned a "position
        count", *i.e.* a unique integer value. Furthermore, positionings
        of axes at the end of the scan module (in the "positioning phase")
        get their own position number.

        For snapshot modules, things are quite simple: Each snapshot
        module creates its own position, one per module.

        Default: 0

    number_of_positions_per_pass : :class:`int`
        Number of positions created during *one pass* of the scan module.

        Scan modules can be nested, and even though a given scan module
        is not nested itself, it can be in a chain of scan modules that
        are nested. Hence, the total number of positions created during a
        scan for a given scan module can be different from the number of
        positions during a single pass.

        Default: 0

    positions : :class:`numpy.array`
        Actual positions created during the scan module.

        These positions cannot necessarily be inferred from the definition
        of the scan module itself, but sometimes only be obtained from the
        actual measurement.

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

    positionings : :class:`list`
        Positionings for individual axes of the scan module.

        Optionally, at the end of a pass of a scan module, axes contained
        in this scan module can be positioned by calculating a new
        position using the values of a given (optionally normalised) detector
        channel.

        Each element in the list is a :obj:`Positioning` object.

    number_of_measurements : :class:`int`
        Number of measurements performed per axes position.

        Each measurement gets its individual position count.

        Default: 1


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
        self.positionings = []
        self.number_of_measurements = 1

    def has_mpskip(self):
        """
        Check whether a scan module uses the EPICS MPSKIP feature.

        The MPSKIP detector is a special EPICS workaround to, *i.a.*, store
        individual data points for an average channel. For details,
        see the :mod:`mpskip <evedata.evefile.controllers.mpskip>` module.

        To properly convert the datasets of the devices in a scan using
        the MPSKIP feature, we need to know which devices were part of the
        scan module containing the MPSKIP detector.

        This convenience method allows for easily checking whether the
        scan module contains the MPSKIP detector and allows the
        controllers handling the dataset conversion to do their work.

        Currently, the method checks for at least one detector channel
        whose ID starts with "MPSKIP".

        Returns
        -------
        has_mpskip : :class:`bool`
            Whether the scan module uses the EPICS MPSKIP feature

        """
        mpskip_channels = [
            item for item in self.channels if item.startswith("MPSKIP")
        ]
        return bool(mpskip_channels)


class Channel:
    """
    Representation of a channel used in a scan module.

    Scan modules use detector channels and motor axes in their main phase.
    All relevant information regarding a channel with respect to its use in
    a scan module is contained in this class and classes inheriting from it.

    To get further information on the channel in general, its :attr:`id` can
    be used to look up this information in the ``setup`` part of the SCML
    file.


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
    be used to look up this information in the ``setup`` part of the SCML
    file.


    Attributes
    ----------
    id : :class:`str`
        Unique ID of the axis.

        Each axis has a unique ID that is used internally to refer to it.
        The names displayed in the GUI are "given" names different from this
        ID, though. The HDF5 datasets in an eveH5 file use these UIDs as name.

    step_function : :class:`str`
        Name of the function used to determine the axis positions.

        Possible values are: "add", "multiply", "file", "plugin",
        "positionlist", "range"

    position_mode : :class:`str`
        Mode used for positioning the axis.

        Possible values are: "absolute", "relative"

        If "relative", the axis positions are understood as  relative to
        another position value.

        Default: "absolute"

    positions : :class:`numpy.array`
        Set values the axis should have been moved to.

        Whether the axis ever reached these positions is an entirely
        different matter that can be resolved by comparing these set
        values with the values recorded by the engine.

        If :attr:`step_function` is set to "file", no positions can be
        inferred from the SCML file, as they are simply not contained.

    is_main_axis : :class:`bool`
        Whether the axis is set as main axis.

        Only for axes with :attr:`step_function` in ["add", "multiply"]
        setting one of these axes as main axis defines the number of
        positions of the other axes in this group.


    Examples
    --------
    The :class:`Axis` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.scan` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self, sm_id=""):
        self.id = sm_id  # noqa
        self.step_function = ""
        self.position_mode = "absolute"
        self.positions = None
        self.is_main_axis = False


class SnapshotModule(AbstractScanModule):
    """
    Representation of snapshot scan modules.

    Snapshot scan modules are used to record the state of devices at a given
    point in time (an individual position count). Historically, there are
    four different types of such snapshot scan modules: motor axes and
    detector channels, and static and dynamic each.


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

    is_nested : :class:`bool`
        Whether the scan module itself is nested.

        A scan module can either be appended or nested. Given that the
        scan modules are unaware of the other scan modules and (currently)
        only contain IDs as references to their parent and appended or
        nested scan module, this information needs to be set from outside,
        *e.g.* during mapping by the :class:`VersionMapper
        <evedata.scan.controllers.version_mapping.VersionMapper>` class.

        Default: False

    number_of_positions : :class:`int`
        Number of positions created during the scan module.

        Positions are the fundamental quantisation of the data in eveH5
        files. Each position axes are moved to is assigned a "position
        count", *i.e.* a unique integer value. Furthermore, positionings
        of axes at the end of the scan module (in the "positioning phase")
        get their own position number.

        For snapshot modules, things are quite simple: Each snapshot
        module creates its own position, one per module.

        Default: 1

    number_of_positions_per_pass : :class:`int`
        Number of positions created during *one pass* of the scan module.

        Scan modules can be nested, and even though a given scan module
        is not nested itself, it can be in a chain of scan modules that
        are nested. Hence, the total number of positions created during a
        scan for a given scan module can be different from the number of
        positions during a single pass.

        Default: 1

    positions : :class:`list` | :class:`numpy.array`
        Actual positions created during the scan module.

        These positions cannot necessarily be inferred from the definition
        of the scan module itself, but sometimes only be obtained from the
        actual measurement.

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
    The :class:`SnapshotModule` class is not meant to be used directly,
    as any entities, but rather indirectly by means of the respective
    facades in the boundaries technical layer of the :mod:`evedata.scan`
    subpackage. Hence, for the time being, there are no dedicated examples
    how to use this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.number_of_positions = 1
        self.number_of_positions_per_pass = 1
        self.axes = {}
        self.channels = {}


class Positioning:
    """
    Representation of an axis positioning as optional step in a scan module.

    An axis can be positioned in several ways after a scan module has been
    executed. The position the axis should be positioned at is determined
    by analysing the data of a given detector channel. This allows to
    perform setup scans in scan modules that are prepended to the scan
    modules performing the actual measurement, and have both, setup and
    actual measurement in one scan.

    A positioning gets its separate position (count) in the eveH5 file,
    and all positionings for all axes are performed after the main phase
    of the scan module has finished.


    Attributes
    ----------
    axis_id : :class:`str`
        Unique ID of the axis that shall be positioned.

    channel_id : :class:`str`
        Unique ID of the channel analysed to determine the axis position.

    normalize_channel_id : :class:`str`
        Unique ID of the channel used for normalization.

        Often, channels are normalized, and this normalization is crucial
        for proper positioning of an axis.

    type : :class:`str`
        The way the (new) axis position is calculated from the channel data.

        Currently, the following types are available:

        ====== =======================================
        Type   Parameter
        ====== =======================================
        PEAK   --
        CENTER threshold
        MAX    --
        MIN    --
        EDGE   number from left
        ====== =======================================

        If parameters are available, they are stored in the
        :attr:`parameters` attribute.

    parameters : :class:`dict`
        Parameters used to calculate the new position.

        Whether a given :attr:`type` has parameters can be seen from the
        table above.

    position : :class:`int`
        Actual position created during the scan.

        Positions are the fundamental quantisation of the data in eveH5
        files. Each position axes are moved to is assigned a "position
        count", *i.e.* a unique integer value. Furthermore, positionings
        of axes at the end of the scan module (in the "positioning phase")
        get their own position number.


    Examples
    --------
    The :class:`Positioning` class is not meant to be used directly,
    as any entities, but rather indirectly by means of the respective
    facades in the boundaries technical layer of the :mod:`evedata.scan`
    subpackage. Hence, for the time being, there are no dedicated examples
    how to use this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        self.axis_id = None
        self.channel_id = None
        self.normalize_channel_id = None
        self.type = ""
        self.parameters = {}
        self.position = None
