"""

*Metadata classes corresponding to the data entities.*

Data without context (*i.e.* metadata) are mostly useless. Hence, to every
class (type) of data in the :mod:`evedata.evefile.entities.data` module,
there exists a corresponding metadata class in this module.


Overview
========

A first overview of the classes implemented in this module and their
hierarchy is given in the UML diagram below.

.. figure:: /uml/evedata.evefile.metadata.*
    :align: center
    :width: 750px

    Class hierarchy of the :mod:`evedata.evefile.entities.metadata` module.
    Each concrete class in the :mod:`evedata.evefile.entities.data` module
    has a corresponding metadata class in this module.
    You may click on the image for a larger view.


A note on the :class:`AbstractDeviceMetadata` interface class: The eveH5
dataset corresponding to the :class:`TimestampMetadata` class is special in
sense of having no PV and transport type nor an id. Several options have been
considered to address this problem:

#. Moving these three attributes down the line and copying them multiple
   times (feels bad).
#. Leaving the attributes blank for the "special" dataset (feels bad, too).
#. Introduce another class in the hierarchy, breaking the parallel to the
   Data class hierarchy (potentially confusing).
#. Create a mixin class (abstract interface) with the three attributes and
   use multiple inheritance/implements.

As obvious from the UML diagram, the last option has been chosen. The name
"DeviceMetadata" resembles the hierarchy in the ``scml.setup`` module and
clearly distinguishes actual devices from datasets not containing data
read from some instrument.



Module documentation
====================

"""

import logging

import numpy as np

logger = logging.getLogger(__name__)


class Metadata:
    """
    Metadata for the devices involved in a measurement.

    This is the base class for all data(sets) and not meant to be used
    directly. Rather, one of the individual subclasses should actually be
    used.

    This class complements the class
    :class:`evedata.evefile.entities.data.Data`.

    Attributes
    ----------
    name : :class:`str`
        Name of the device.

        Devices are uniquely identified by an ID that usually corresponds
        to the EPICS process variable (PV). However, most devices have
        "given" names as well that provide a more human-readable alternative.

    options : :class:`dict`
        (Scalar) options of the device.

        Devices can have options. Generally, there are two types of
        options: those whose values are *not* changing within a given scan
        module, and those whose values can potentially change for every
        individual position (count). The former are stored here as
        key--value pairs with the key corresponding to the option name.
        The latter are stored in the
        :attr:`evedata.evefile.entities.data.Data.options` attribute.

    Examples
    --------
    The :class:`Metadata` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.name = ""
        self.options = {}


class AbstractDeviceMetadata:
    """
    Mixin class (interface) for metadata of actual physical devices.

    Each physical device has a unique ID and can be accessed by an EPICS
    process variable (PV).


    Attributes
    ----------
    id : :class:`str`
        Unique ID of the device.

    pv : :class:`str`
        EPICS process variable (PV) used to access the physical device.

    access_mode : :class:`str`
        Method used to access the EPICS PV.

    Examples
    --------
    The :class:`AbstractDeviceMetadata` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.id = ""  # pylint: disable=invalid-name
        self.pv = ""  # pylint: disable=invalid-name
        self.access_mode = ""


class MonitorMetadata(Metadata, AbstractDeviceMetadata):
    """
    Metadata for monitor data.

    This class complements the class
    :class:`evedata.evefile.entities.data.MonitorData`.


    Examples
    --------
    The :class:`MonitorMetadata` class is not meant to be used directly,
    as any entities, but rather indirectly by means of the respective
    facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """


class MeasureMetadata(Metadata):
    """
    Metadata for data that are actually measured.

    This class complements the class
    :class:`evedata.evefile.entities.data.MeasureData`.


    Attributes
    ----------
    unit : :class:`string`
        Name of the unit corresponding to the data.


    Examples
    --------
    The :class:`MeasureMetadata` class is not meant to be used directly,
    as any entities, but rather indirectly by means of the respective
    facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.unit = ""


class DeviceMetadata(MeasureMetadata, AbstractDeviceMetadata):
    """
    Metadata for device data.

    This class complements the class
    :class:`evedata.evefile.entities.data.DeviceData`.


    Examples
    --------
    The :class:`DeviceMetadata` class is not meant to be used directly,
    as any entities, but rather indirectly by means of the respective
    facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """


class AxisMetadata(MeasureMetadata, AbstractDeviceMetadata):
    """
    Metadata for axis data.

    This class complements the class
    :class:`evedata.evefile.entities.data.AxisData`.


    Examples
    --------
    The :class:`AxisMetadata` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.deadband = 0.0


class ChannelMetadata(MeasureMetadata, AbstractDeviceMetadata):
    """
    Metadata for channel data.

    This class complements the class
    :class:`evedata.evefile.entities.data.ChannelData`.


    Examples
    --------
    The :class:`ChannelMetadata` class is not meant to be used directly,
    as any entities, but rather indirectly by means of the respective
    facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """


class TimestampMetadata(MeasureMetadata):
    """
    Metadata for the special dataset mapping timestamps to positions.

    This class complements the class
    :class:`evedata.evefile.entities.data.TimestampData`.


    Examples
    --------
    The :class:`TimestampMetadata` class is not meant to be used directly,
    as any entities, but rather indirectly by means of the respective
    facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """


class NonnumericChannelMetadata(ChannelMetadata):
    """
    Metadata for channels with non-numeric data.

    This class complements the class
    :class:`evedata.evefile.entities.data.NonnumericChannelData`.


    Examples
    --------
    The :class:`NonnumericChannelMetadata` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """


class SinglePointChannelMetadata(ChannelMetadata):
    """
    Metadata for channels with numeric 0D data.

    This class complements the class
    :class:`evedata.evefile.entities.data.SinglePointChannelData`.


    Examples
    --------
    The :class:`SinglePointChannelMetadata` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """


class AverageChannelMetadata(ChannelMetadata):
    """
    Metadata for channels with averaged numeric 0D data.

    This class complements the class
    :class:`evedata.evefile.entities.data.AverageChannelData`.


    Attributes
    ----------
    n_averages : :class:`int`
        Short description

    low_limit : :class:`float`
        Short description

    max_attempts : :class:`float`
        Short description

    max_deviation : :class:`float`
        Short description


    Examples
    --------
    The :class:`AverageChannelMetadata` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.n_averages = 0
        self.low_limit = 0.0
        self.max_attempts = 0
        self.max_deviation = 0.0


class IntervalChannelMetadata(ChannelMetadata):
    """
    Metadata for channels with numeric 0D data measured in a time interval.

    This class complements the class
    :class:`evedata.evefile.entities.data.IntervalChannelData`.


    Attributes
    ----------
    trigger_interval : :class:`float`
        Short description


    Examples
    --------
    The :class:`IntervalChannelMetadata` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.trigger_interval = 0.0


class ArrayChannelMetadata(ChannelMetadata):
    """
    Metadata for channels with numeric 1D data.

    This class complements the class
    :class:`evedata.evefile.entities.data.ArrayChannelData`.


    Examples
    --------
    The :class:`ArrayChannelMetadata` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """


class AreaChannelMetadata(ChannelMetadata):
    """
    Metadata for channels with numeric 2D data.

    This class complements the class
    :class:`evedata.evefile.entities.data.AreaChannelData`.


    Examples
    --------
    The :class:`AreaChannelMetadata` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.file_type = str


class NormalizedChannelMetadata:
    """
    Mixin class (interface) for metadata of normalized channel data.

    Attributes
    ----------
    normalize_id : :class:`str`
        Unique ID of the channel used to normalize the data


    Examples
    --------
    The :class:`NormalizedChannelMetadata` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.normalize_id = str


class SinglePointNormalizedChannelMetadata(
    ChannelMetadata, NormalizedChannelMetadata
):
    """
    Metadata for channels with normalized numeric 0D data.

    This class complements the class
    :class:`evedata.evefile.entities.data.SinglePointNormalizedChannelData`.


    Examples
    --------
    The :class:`SinglePointNormalizedChannelMetadata` class is not meant
    to be used directly, as any entities, but rather indirectly by means
    of the respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """


class AverageNormalizedChannelMetadata(
    ChannelMetadata, NormalizedChannelMetadata
):
    """
    Metadata for channels with normalized averaged numeric 0D data.

    This class complements the class
    :class:`evedata.evefile.entities.data.AverageNormalizedChannelData`.


    Examples
    --------
    The :class:`AverageNormalizedChannelMetadata` class is not meant
    to be used directly, as any entities, but rather indirectly by means
    of the respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """


class IntervalNormalizedChannelMetadata(
    ChannelMetadata, NormalizedChannelMetadata
):
    """
    Metadata for channels with normalized interval-measured numeric 0D data.

    This class complements the class
    :class:`evedata.evefile.entities.data.IntervalNormalizedChannelData`.


    Examples
    --------
    The :class:`IntervalNormalizedChannelMetadata` class is not meant
    to be used directly, as any entities, but rather indirectly by means
    of the respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """


class ScopeChannelMetadata(ArrayChannelMetadata):
    """
    Metadata for oscilloscope channels.

    This class complements the class
    :class:`evedata.evefile.entities.data.ScopeChannelData`.


    Examples
    --------
    The :class:`ScopeChannelMetadata` class is not meant
    to be used directly, as any entities, but rather indirectly by means
    of the respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """


class MCAChannelMetadata(ArrayChannelMetadata):
    """
    Metadata for multichannel analyzer (MCA) channels.

    This class complements the class
    :class:`evedata.evefile.entities.data.MCAChannelData`.


    Attributes
    ----------
    calibration : :class:`MCAChannelCalibration`
        Metadata for the calibration of the MCA channel.


    Examples
    --------
    The :class:`MCAChannelMetadata` class is not meant
    to be used directly, as any entities, but rather indirectly by means
    of the respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.calibration = MCAChannelCalibration()


class MCAChannelCalibration:
    """
    Metadata for MCA channel calibration.

    Many MCA channels need to be calibrated (with a second-order
    polynomial) to convert the channel numbers to actual energies.

    From the `EPICS MCA Record description
    <https://millenia.cars.aps.anl.gov/software/epics/mcaRecord.html>`_:
    "The relationship between calibrated units (cal) and channel number
    (chan) is defined as ``cal=CALO + chan*CALS + chan^2*CALQ``. The first
    channel in the spectrum is defined as chan=0." Here, ``CALO`` is the
    offset, ``CALS`` the slope, and ``CALQ`` the quadratic term of the
    polynomial.

    Attributes
    ----------
    offset : :class:`float`
        Calibration offset, *i.e.* 0th order coefficient of the polynomial.

    slope : :class:`float`
        Calibration slope, *i.e.* 1st order coefficient of the polynomial.

    quadratic : :class:`float`
        2nd order coefficient of the polynomial.


    Examples
    --------
    To calibrate your MCA with a number of channels with the given
    calibration parameters (offset, slope, quadratic term), use:

    .. code-block::

        calibration = MCAChannelCalibration()
        # Set the calibration parameters
        calibrated_values = calibration.calibrate(n_channels=4096)

    The :obj:`MCAChannelData <evedata.evefile.entities.data.MCAChannelData>`
    object will usually perform the calibration transparently for you if
    necessary. Even better, this object knows how many channels the MCA has.

    """

    def __init__(self):
        self.offset = 0.0
        self.slope = 1.0
        self.quadratic = 0.0

    def calibrate(self, n_channels=0):
        """
        Return calibrated values for given number of channels.

        From the `EPICS MCA Record description
        <https://millenia.cars.aps.anl.gov/software/epics/mcaRecord.html>`_:
        "The relationship between calibrated units (cal) and channel number
        (chan) is defined as ``cal=CALO + chan*CALS + chan^2*CALQ``. The first
        channel in the spectrum is defined as chan=0." Here, ``CALO`` is the
        offset, ``CALS`` the slope, and ``CALQ`` the quadratic term of the
        polynomial.

        Parameters
        ----------
        n_channels : :class:`int`
            Number of channels of the MCA

        Returns
        -------
        calibrated_values : :class:`numpy.ndarray`
            Calibrated values for the given number of channels.

        """
        channels = np.arange(n_channels)
        calibrated_values = (
            self.offset + channels * self.slope + channels**2 * self.quadratic
        )
        return calibrated_values


class ScientificCameraMetadata(AreaChannelMetadata):
    """
    Metadata for scientific camera data.

    This class complements the class
    :class:`evedata.evefile.entities.data.ScientificCameraData`.


    Attributes
    ----------
    gain : :class:`float`
        Short description

    reverse_x : :class:`bool`
        Short description

    reverse_y : :class:`bool`
        Short description


    Examples
    --------
    The :class:`ScientificCameraMetadata` class is not meant
    to be used directly, as any entities, but rather indirectly by means
    of the respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.gain = float()
        self.reverse_x = bool()
        self.reverse_y = bool()


class SampleCameraMetadata(AreaChannelMetadata):
    """
    Metadata for consumer digital cameras used to take photos of samples.

    This class complements the class
    :class:`evedata.evefile.entities.data.SampleCameraData`.


    Attributes
    ----------
    beam_x : :class:`int`
        Position of the beam in *x* direction in image coordinates

    beam_y : :class:`int`
        Position of the beam in *y* direction in image coordinates

    fractional_x_position : :class:`float`
        Fractional position of the beam in *x* direction in image coordinates

        The fractional position allows to specify the beam position
        independent of the image resolution.

    fractional_y_position : :class:`float`
        Fractional position of the beam in *y* direction in image coordinates

        The fractional position allows to specify the beam position
        independent of the image resolution.

    skip_frames : :class:`int`
        Number of frames skipped

    average_frames : :class:`int`
        Number of frames averaged

        .. note::

            May currently not be implemented in the EPICS IOC.


    Examples
    --------
    The :class:`SampleCameraMetadata` class is not meant
    to be used directly, as any entities, but rather indirectly by means
    of the respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.beam_x = int()
        self.beam_y = int()
        self.fractional_x_position = float()
        self.fractional_y_position = float()
        self.skip_frames = int()
        self.average_frames = int()


class NonencodedAxisMetadata(AxisMetadata):
    """
    Metadata for data of axes without encoders.

    This class complements the class
    :class:`evedata.evefile.entities.data.NonencodedAxisData`.


    Examples
    --------
    The :class:`NonencodedAxisMetadata` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.evefile` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """
