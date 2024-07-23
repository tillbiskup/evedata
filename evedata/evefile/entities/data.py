"""

*Entities representing an eveH5 file on the data level.*

Data are organised in "datasets" within HDF5, and the
:mod:`evedata.evefile.entities.data` module provides the relevant entities
to describe these datasets. Although currently (as of 06/2024, eve version
2.1) neither average nor interval detector channels save the individual
data points, at least the former is a clear need of the
engineers/scientists. Hence, the data model already respects this use
case. As per position (count) there can be a variable number of measured
points, the resulting array is no longer rectangular, but a "ragged
array". While storing such arrays is possible directly in HDF5,
the implementation within evedata is entirely independent of the actual
representation in the eveH5 file.


Overview
========

A first overview of the classes implemented in this module and their
hierarchy is given in the UML diagram below.

.. _fig-uml_evedata-evefile.data_api:

.. figure:: /uml/evedata.evefile.data.*
    :align: center
    :width: 750px

    Class hierarchy of the :mod:`evedata.evefile.entities.data` module.
    Each class has a corresponding metadata class in the
    :mod:`evedata.evefile.entities.metadata` module. While in this
    diagram, some child classes seem to be identical, they have a
    different type of metadata (see the
    :mod:`evedata.evefile.entities.metadata` module). Generally, having
    different types serves to discriminate where necessary between
    detector channels and motor axes.
    You may click on the image for a larger view.



Array channels
--------------

Array channels in their general form are channels collecting 1D data.
Typical devices used here are MCAs, but oscilloscopes and vector signal
analysers (VSA) would be other typical array channels. Hence, for these
quite different types of array channels, distinct subclasses of the
generic ``ArrayChannelData`` class exist, see
:numref:`Fig. %s <fig-uml_arraychannel_api>`.


.. _fig-uml_arraychannel_api:

.. figure:: /uml/arraychannel.*
    :align: center
    :width: 750px

    Preliminary data model for the ArrayChannelData classes. The basic
    hierarchy is identical to :numref:`Fig. %s
    <fig-uml_evedata-evefile.data_api>`. Details for the ``MCAChannelData``
    class can be found in :numref:`Fig. %s <fig-uml_mcachannel_api>`. The
    ``ScopeData`` class is a container for scopes with several channels
    read simultaneously. Further array detector channels can be added by
    subclassing ``ArrayChannelData``. Probably the next class will be
    ``VSAChannelData`` for Vector Signal Analyser (VSA) data.


Multi Channel Analysers (MCA) generally collect 1D data and typically have
separate regions of interest (ROI) defined, containing the sum of the
counts for the given region. For the EPICS MCA record,
see https://millenia.cars.aps.anl.gov/software/epics/mcaRecord.html.


.. _fig-uml_mcachannel_api:

.. figure:: /uml/mcachannel.*
    :align: center
    :width: 750px

    Preliminary data model for the MCAChannelData classes. The basic
    hierarchy is identical to :numref:`Fig. %s
    <fig-uml_evedata-evefile.data_api>`, and here, the relevant part of the
    metadata class hierarchy from :numref:`Fig. %s
    <fig-uml_evedata-evefile.metadata>` is shown as well. Separating the
    ``MCAChannelCalibration`` class from the ``ArrayChannelMetadata``
    allows to add distinct behaviour, *e.g.* creating calibration curves
    from the parameters.


Note: The scalar attributes for ArrayChannelROIs will currently be saved
as snapshots regardless of whether the actual ROI has been defined/used.
Hence, the evedata package needs to decide based on the existence of the
actual data whether to create a ROI object and attach it to
``ArrayChannelData``.

The calibration parameters are needed to convert the *x* axis of the MCA
spectrum into a real energy axis. Hence, the ``ArrayChannelCalibration``
class will have methods for performing exactly this conversion. The
relationship between calibrated units (cal) and channel number (chan) is
defined as cal=CALO + chan\*CALS + chan^2\*CALQ. The first channel in the
spectrum is defined as chan=0. However, not all MCAs/SDDs have these
calibration values: Ketek SDDs seem to not have these values (internal
calibration?).

The real_time and life_time values can be used to get an idea of the
amount of pile up occurring, *i.e.* having two photons with same energy
within a short time interval reaching the detector being detected as one
photon with twice the energy. Hence, latest in the radiometry package,
distinct methods for this kind of analysis should be implemented.


Area channels
-------------

Area channels are basically 2D channels, *i.e.*, cameras. There are (at
least) two distinct types of cameras in use, namely scientific cameras and
standard consumer digital cameras for taking pictures (of sample positions
in the setup). While scientific cameras usually record only greyscale
images, but have additional parameters and can define regions of interest (
ROI), consumer cameras are much simpler in terms of their data model and
typically record RGB images. These different types of images need to be
handled differently in the data processing and analysis pipeline.


.. _fig-uml_areachannel_api:

.. figure:: /uml/areachannel.*
    :align: center
    :width: 750px

    Preliminary data model for the AreaChannel class. The basic hierarchy
    is identical to :numref:`Fig. %s <fig-uml_evedata-evefile.data_api>`. As
    scientific cameras are quite different from standard consumer digital
    cameras for taking pictures, but both are used from within the
    measurement program, distinct subclasses of the basic ``AreaDetector``
    class exist. For details on the ``ScientificCamera`` classes,
    see :numref:`Fig. %s <fig-uml_scientificcamera_api>`.


.. _fig-uml_scientificcamera_api:

.. figure:: /uml/scientificcamera.*
    :align: center
    :width: 750px

    Preliminary data model for the ScientificCameraChannel classes. The
    basic hierarchy is identical to :numref:`Fig. %s
    <fig-uml_evedata-evefile.data_api>`, and here, the relevant part of the
    metadata class hierarchy from :numref:`Fig. %s
    <fig-uml_evedata-evefile.metadata>` is shown as well. As different
    area detectors (scientific cameras) have somewhat different options,
    probably there will appear a basic ``AreaChannel`` class with more
    specific subclasses.


Regarding file names/paths: Some of the scientific cameras are operated
from Windows, hence there is usually no unique mapping of paths to actual
places of the files, particularly given that Windows allows to map a drive
letter to arbitrary network paths. It seems as if these paths are quite
different for the different detectors, and therefore, some externally
configurable mapping should be used.

Note for Pilatus cameras: Those cameras seem to have three sensors each
for temperature and humidity. Probably the simplest solution would be to
store those values in an array rather than having three individual fields
each. In case of temperature (and humidity) readings for each individual
image, the array would become a 2D array.


Module documentation
====================

"""

import logging

import numpy as np

from evedata.evefile.entities import metadata

logger = logging.getLogger(__name__)


class Data:
    """
    Data recorded from the devices involved in a measurement.

    This is the base class for all data(sets) and not meant to be used
    directly. Rather, one of the individual subclasses should actually be
    used.

    When subclassing, make sure to create the corresponding metadata class
    in the :mod:`evedata.evefile.entities.metadata` module as well.

    Data are read from HDF5 files, and to save time and resources, actual
    data are only read upon request.

    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.metadata.Metadata`
        Relevant metadata for the individual device.

    options : :class:`dict`
        (Variable) options of the device.

        Devices can have options. Generally, there are two types of
        options: those whose values are *not* changing within a given scan
        module, and those whose values can potentially change for every
        individual position (count). The latter are stored here as
        key--value pairs with the key corresponding to the option name.
        The former are stored in the
        :attr:`evedata.evefile.entities.metadata.Metadata.options` attribute.

    Examples
    --------
    The :class:`Data` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.metadata = metadata.Metadata()
        self.options = {}
        self._data = None

    @property
    def data(self):
        """
        Actual data recorded from the device.

        Returns
        -------
        data : any
            Actual data recorded from the device.

        """
        return self._data


class MonitorData(Data):
    """
    Data from devices monitored, but not controlled by the eve engine.

    In contrast to :class:`MeasureData`, :class:`MonitorData` do not have
    a position as primary axis, but a timestamp in milliseconds, *i.e.*,
    the :attr:`milliseconds` attribute.


    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.metadata.MonitorMetadata`
        Relevant metadata for the individual device.

    milliseconds : :class:`numpy.ndarray`
        Time in milliseconds since start of the scan.


    Examples
    --------
    The :class:`MonitorData` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.metadata = metadata.MonitorMetadata()
        self.milliseconds = np.ndarray(shape=[], dtype=int)


class MeasureData(Data):
    """
    Base class for data from devices actually controlled by the eve engine.

    In contrast to :class:`MonitorData`, :class:`MeasureData` have a
    position as primary axis rather than a timestamp in milliseconds, *i.e.*,
    the :attr:`positions` attribute.


    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.metadata.MeasureMetadata`
        Relevant metadata for the individual device.

    positions : :class:`numpy.ndarray`
        Position values data are recorded for.

        Each data "point" corresponds to an overall position of all
        actuators (motor axes) of the setup and is assigned an individual
        "position count".


    Examples
    --------
    The :class:`MeasureData` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.metadata = metadata.MeasureMetadata()
        self.positions = np.ndarray(shape=[], dtype=int)


class DeviceData(MeasureData):
    """
    Data from (dumb) devices.

    Three types of devices are distinguished by the eve measurement
    program: (dumb) devices, motor axes, and detector channels.


    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.metadata.DeviceMetadata`
        Relevant metadata for the individual device.


    Examples
    --------
    The :class:`DeviceData` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.metadata = metadata.DeviceMetadata()


class AxisData(MeasureData):
    """
    Data from motor axes.

    Three types of devices are distinguished by the eve measurement
    program: (dumb) devices, motor axes, and detector channels.


    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.metadata.AxisMetadata`
        Relevant metadata for the individual device.

    set_values : None
        Values the axis should have been set to.

        While the :attr:`Data.data` attribute contains the actual
        positions of the axis, here, the originally intended positions are
        stored. This allows for easily checking whether the axis has been
        positioned within a scan as intended.


    Examples
    --------
    The :class:`AxisData` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.metadata = metadata.AxisMetadata()
        self.set_values = None


class ChannelData(MeasureData):
    """
    Data from detector channels.

    Three types of devices are distinguished by the eve measurement
    program: (dumb) devices, motor axes, and detector channels.


    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.metadata.ChannelMetadata`
        Relevant metadata for the individual device.


    Examples
    --------
    The :class:`ChannelData` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.metadata = metadata.ChannelMetadata()


class TimestampData(MeasureData):
    """
    Data correlating the positions to the time used for monitors.

    There are generally two different types of devices: those directly
    controlled by the eve engine, and those who are monitored. The former
    are instances of the :class:`MeasureData` class, the latter of the
    :class:`MonitorData` class.

    The :class:`TimestampData` class allows to map the time stamps (in
    milliseconds) of the :class:`MonitorData` data to positions of
    :class:`MeasureData` data. This is a necessary prerequisite to
    correlate monitored values to the data from controlled devices,
    such as motor axes and detector channels.


    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.metadata.TimestampMetadata`
        Relevant metadata for the individual device.


    Examples
    --------
    The :class:`TimestampData` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.metadata = metadata.TimestampMetadata()


class NonnumericChannelData(ChannelData):
    """
    Data for channels with non-numeric data.

    There are EPICS PVs returning non-numeric values that are stored in
    HDF5 datasets in eveH5 files. This class represents these read
    non-numeric values.


    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.metadata.NonnumericChannelMetadata`
        Relevant metadata for the individual device.


    Examples
    --------
    The :class:`NonnumericChannelData` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.metadata = metadata.NonnumericChannelMetadata()


class SinglePointChannelData(ChannelData):
    """
    Data for channels with numeric 0D data.

    Detector channels can be distinguished by the dimension of their data:

    0D
        scalar values per position, including average and interval channels
    1D
        array values, *i.e.* vectors, per position
    2D
        area values, *i.e.* images, per position

    This class represents 0D, scalar values.

    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.metadata.SinglePointChannelMetadata`
        Relevant metadata for the individual device.


    Examples
    --------
    The :class:`SinglePointChannelData` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.metadata = metadata.SinglePointChannelMetadata()


class AverageChannelData(ChannelData):
    """
    Data for channels with averaged numeric 0D data.

    Detector channels can be distinguished by the dimension of their data:

    0D
        scalar values per position, including average and interval channels
    1D
        array values, *i.e.* vectors, per position
    2D
        area values, *i.e.* images, per position

    This class represents 0D, scalar values that are averaged.


    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.metadata.AverageChannelMetadata`
        Relevant metadata for the individual device.

    raw_data : Any
        Short description

    attempts : numpy.ndarray
        Short description


    Examples
    --------
    The :class:`AverageChannelData` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.metadata = metadata.AverageChannelMetadata()
        self.raw_data = None
        self.attempts = np.ndarray(shape=[], dtype=int)


class IntervalChannelData(ChannelData):
    """
    Data for channels with numeric 0D data measured in a time interval.

    Detector channels can be distinguished by the dimension of their data:

    0D
        scalar values per position, including average and interval channels
    1D
        array values, *i.e.* vectors, per position
    2D
        area values, *i.e.* images, per position

    This class represents 0D, scalar values that are measured in a time
    interval.


    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.metadata.IntervalChannelMetadata`
        Relevant metadata for the individual device.

    raw_data : Any
        The raw individual values measured in the given time interval.

    counts : numpy.ndarray
        The number of values measured in the given time interval.

        Note that this value may change for each individual position.


    Examples
    --------
    The :class:`IntervalChannelData` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.metadata = metadata.IntervalChannelMetadata()
        self.raw_data = None
        self.counts = np.ndarray(shape=[], dtype=int)


class ArrayChannelData(ChannelData):
    """
    Metadata for channels with numeric 1D data.

    Detector channels can be distinguished by the dimension of their data:

    0D
        scalar values per position, including average and interval channels
    1D
        array values, *i.e.* vectors, per position
    2D
        area values, *i.e.* images, per position

    This class represents 1D array values.


    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.metadata.ArrayChannelMetadata`
        Relevant metadata for the individual device.


    Examples
    --------
    The :class:`ArrayChannelData` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.metadata = metadata.ArrayChannelMetadata()


class AreaChannelData(ChannelData):
    """
    Metadata for channels with numeric 2D data.

    Detector channels can be distinguished by the dimension of their data:

    0D
        scalar values per position, including average and interval channels
    1D
        array values, *i.e.* vectors, per position
    2D
        area values, *i.e.* images, per position

    This class represents 2D area values.


    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.metadata.AreaChannelMetadata`
        Relevant metadata for the individual device.


    Examples
    --------
    The :class:`AreaChannelData` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.metadata = metadata.AreaChannelMetadata()


class NormalizedChannelData:
    """
    Mixin class (interface) for normalized channel data.

    0D channels can be normalized by the data of another 0D channel,
    *i.e.* by dividing its values by the values of the normalizing channel.


    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.metadata.AreaChannelMetadata`
        Relevant metadata for normalization.

    normalized_data : Any
        Data that have been normalized.

        Normalization takes place by dividing by the values of the
        normalizing channel.

    normalizing_data : Any
        Data used for normalization.

    Raises
    ------
    exception
        Short description when and why raised


    Examples
    --------
    The :class:`AreaChannelData` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.metadata = metadata.NormalizedChannelMetadata()
        self.normalized_data = None
        self.normalizing_data = None


class SinglePointNormalizedChannelData(
    SinglePointChannelData, NormalizedChannelData
):
    """
    Data for channels with normalized numeric 0D data.

    Detector channels can be distinguished by the dimension of their data:

    0D
        scalar values per position, including average and interval channels
    1D
        array values, *i.e.* vectors, per position
    2D
        area values, *i.e.* images, per position

    This class represents 0D, scalar values that are normalized by the
    data of another 0D channel.


    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.metadata.SinglePointNormalizedChannelMetadata`
        Relevant metadata for the individual normalized device.


    Examples
    --------
    The :class:`SinglePointNormalizedChannelData` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.metadata = metadata.SinglePointNormalizedChannelMetadata()


class AverageNormalizedChannelData(AverageChannelData, NormalizedChannelData):
    """
    Data for channels with normalized averaged numeric 0D data.

    Detector channels can be distinguished by the dimension of their data:

    0D
        scalar values per position, including average and interval channels
    1D
        array values, *i.e.* vectors, per position
    2D
        area values, *i.e.* images, per position

    This class represents 0D, scalar values that are averaged and
    normalized by the data of another 0D channel.


    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.metadata.AverageNormalizedChannelMetadata`
        Relevant metadata for the individual normalized device.


    Examples
    --------
    The :class:`AverageNormalizedChannelData` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.metadata = metadata.AverageNormalizedChannelMetadata()


class IntervalNormalizedChannelData(
    IntervalChannelData, NormalizedChannelData
):
    """
    Data for channels with normalized interval-measured numeric 0D data.

    Detector channels can be distinguished by the dimension of their data:

    0D
        scalar values per position, including average and interval channels
    1D
        array values, *i.e.* vectors, per position
    2D
        area values, *i.e.* images, per position

    This class represents 0D, scalar values that are measured in a time
    interval and normalized by the data of another 0D channel.


    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.metadata.IntervalNormalizedChannelMetadata`
        Relevant metadata for the individual normalized device.

    Examples
    --------
    The :class:`IntervalNormalizedChannelData` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.metadata = metadata.IntervalNormalizedChannelMetadata()


class ScopeChannelData(ArrayChannelData):
    """
    Data for oscilloscope channels.

    Oscilloscope channel data are usually 1D data, *i.e.* arrays or vectors.


    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.metadata.ScopeChannelMetadata`
        Relevant metadata for the individual device.

    Raises
    ------
    exception
        Short description when and why raised


    Examples
    --------
    The :class:`ScopeChannelData` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.metadata = metadata.ScopeChannelMetadata()


class MCAChannelData(ArrayChannelData):
    """
    Data for multichannel analyzer (MCA) channels.

    MCA channel data are usually 1D data, *i.e.* arrays or vectors.


    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.metadata.MCAChannelMetadata`
        Relevant metadata for the individual device.

    roi : :class:`list`
        List of data for the individual ROIs defined.

        Individual items in the list are objects of class
        :class:`MCAChannelROIData`.

    life_time : :class:`numpy.ndarray`
        Short description

    real_time : :class:`numpy.ndarray`
        Short description

    preset_life_time : :class:`numpy.ndarray`
        Short description

    preset_real_time : :class:`numpy.ndarray`
        Short description


    Examples
    --------
    The :class:`MCAChannelData` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.metadata = metadata.MCAChannelMetadata()
        self.roi = []
        self.life_time = np.ndarray(shape=[])
        self.real_time = np.ndarray(shape=[])
        self.preset_life_time = np.ndarray(shape=[])
        self.preset_real_time = np.ndarray(shape=[])


class MCAChannelROIData(MeasureData):
    """
    Data for an individual ROI of an MCA detector channel.

    Many MCAs allow to define one or several regions of interest (ROI).
    This class contains the relevant data for an individual ROI.


    Attributes
    ----------
    label : :class:`str`
        Label for the ROI provided by the operator.

    marker : :class:`numpy.ndarray`
        Two-element vector of integer values containing the left and right
        boundary of the ROI.


    Examples
    --------
    The :class:`MCAChannelROIData` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.label = ""
        self.marker = np.asarray([0, 0], dtype=int)


class ScientificCameraData(AreaChannelData):
    """
    Data for scientific camera data.

    Scientific camera data are usually 2D data, *i.e.* images.

    Note, however, that typically the data column in the corresponding
    HDF5 dataset contains filenames rather than the actual data, as the
    data are *not* stored on the HDF5 level.


    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.metadata.ScientificCameraMetadata`
        Relevant metadata for the individual device.

    roi : :class:`list`
        List of data for the individual ROIs defined.

        Individual items in the list are objects of class
        :class:`ScientificCameraROIData`.

    acquire_time : any
        Short description

    temperature : :class:`numpy.ndarray`
        Short description

    humidity : :class:`numpy.ndarray`
        Short description


    Examples
    --------
    The :class:`ScientificCameraData` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.metadata = metadata.ScientificCameraMetadata()
        self.roi = []
        self.acquire_time = None
        self.temperature = np.ndarray(shape=[])
        self.humidity = np.ndarray(shape=[])


class ScientificCameraROIData(MeasureData):
    """
    Data for an individual ROI of a scientific camera.

    Many scientific cameras allow to define one or several regions of
    interest (ROI). This class contains the relevant data for an
    individual ROI.


    Attributes
    ----------
    label : :class:`str`
        Label for the ROI provided by the operator.

    marker : :class:`numpy.ndarray`
        Four-element vector of integer values containing the boundary of
        the ROI.

    background_width : :class:`int`
        Short description

    min_value : :class:`numpy.ndarray`
        Short description

    min_x : :class:`numpy.ndarray`
        Short description

    min_y : :class:`numpy.ndarray`
        Short description

    max_value : :class:`numpy.ndarray`
        Short description

    max_x : :class:`numpy.ndarray`
        Short description

    max_y : :class:`numpy.ndarray`
        Short description

    mean : :class:`numpy.ndarray`
        Short description

    total : :class:`numpy.ndarray`
        Short description

    net : :class:`numpy.ndarray`
        Short description

    sigma : :class:`numpy.ndarray`
        Short description

    centroid_threshold : :class:`numpy.ndarray`
        Short description

    centroid_x : :class:`numpy.ndarray`
        Short description

    centroid_y : :class:`numpy.ndarray`
        Short description

    centroid_sigma_x : :class:`numpy.ndarray`
        Short description

    centroid_sigma_y : :class:`numpy.ndarray`
        Short description

    centroid_sigma_xy : :class:`numpy.ndarray`
        Short description


    Examples
    --------
    The :class:`ScientificCameraROIData` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.label = ""
        self.marker = np.asarray([0, 0, 0, 0], dtype=int)
        self.background_width = 0
        self.min_value = np.ndarray(shape=[], dtype=float)
        self.min_x = np.ndarray(shape=[], dtype=float)
        self.min_y = np.ndarray(shape=[], dtype=float)
        self.max_value = np.ndarray(shape=[], dtype=float)
        self.max_x = np.ndarray(shape=[], dtype=float)
        self.max_y = np.ndarray(shape=[], dtype=float)
        self.mean = np.ndarray(shape=[], dtype=float)
        self.total = np.ndarray(shape=[], dtype=float)
        self.net = np.ndarray(shape=[], dtype=float)
        self.sigma = np.ndarray(shape=[], dtype=float)
        self.centroid_threshold = 0.0
        self.centroid_x = np.ndarray(shape=[], dtype=float)
        self.centroid_y = np.ndarray(shape=[], dtype=float)
        self.centroid_sigma_x = np.ndarray(shape=[], dtype=float)
        self.centroid_sigma_y = np.ndarray(shape=[], dtype=float)
        self.centroid_sigma_xy = np.ndarray(shape=[], dtype=float)


class SampleCameraData(AreaChannelData):
    """
    Data for consumer digital cameras used to take photos of samples.

    Consumer digital camera data are usually 2D data, *i.e.* images.

    Note, however, that typically the data column in the corresponding
    HDF5 dataset contains filenames rather than the actual data, as the
    data are *not* stored on the HDF5 level.


    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.metadata.SampleCameraMetadata`
        Relevant metadata for the individual device.


    Examples
    --------
    The :class:`SampleCameraData` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.metadata = metadata.SampleCameraMetadata()


class NonencodedAxisData(AxisData):
    """
    Data from motor axes without encoders.

    Three types of devices are distinguished by the eve measurement
    program: (dumb) devices, motor axes, and detector channels.

    Motor axes can have encoders that allow to read the real values back,
    while axes without encoders only report the value they should be
    arrived at.

    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.metadata.AxisMetadata`
        Relevant metadata for the individual device.

    set_values : None
        Values the axis should have been set to.

        While the :attr:`Data.data` attribute contains the actual
        positions of the axis, here, the originally intended positions are
        stored. This allows for easily checking whether the axis has been
        positioned within a scan as intended.


    Examples
    --------
    The :class:`NonencodedAxisData` class is not meant to be used directly,
    as any entities, but rather indirectly by means of the respective
    facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.metadata = metadata.NonencodedAxisMetadata()
        self._filled_data = None

    @property
    def filled_data(self):
        """
        Filled axis values.

        Depending on the detector channel the axis values should be
        plotted against, filling may change.

        Returns
        -------
        data : any
            Filled axis values.

        """
        return self._filled_data
