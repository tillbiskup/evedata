"""

*Ensure data and axes values are commensurate and compatible.*

For each motor axis and detector channel, in the original eveH5 file only
those values appear---together with a "position counter" (PosCount)
value---that have actually been set or measured. Hence, the number of
values (*i.e.*, the length of the data vector) will generally be different
for different devices. To be able to plot arbitrary data against each other,
the corresponding data vectors need to be commensurate. If this is not the
case, they need to be brought to the same dimensions (*i.e.*, "harmonised",
originally somewhat misleadingly termed "filled").

To be exact, being commensurate is only a necessary, but not a sufficient
criterion, as not only the shape needs to be commensurate, but the indices
(in this case the positions) be identical.

"""

import logging

import numpy as np

logger = logging.getLogger(__name__)


class Harmonisation:
    """
    Base class for harmonisation of data.

    For each motor axis and detector channel, in the original eveH5 file only
    those values appear---together with a "position counter" (PosCount)
    value---that have actually been set or measured. Hence, the number of
    values (*i.e.*, the length of the data vector) will generally be different
    for different devices. To be able to plot arbitrary data against each
    other, the corresponding data vectors need to be commensurate. If this
    is not the case, they need to be brought to the same dimensions (*i.e.*,
    "harmonised", originally somewhat misleadingly termed "filled").

    The main "quantisation" axis of the values for a device and the
    common reference is the list of positions. Hence, to harmonise,
    first of all the lists of positions are compared, and gaps handled
    accordingly.

    As there are different strategies how to deal with gaps in the
    positions list, generally, there will be different subclasses of the
    :class:`Harmonisation` class dealing each with a particular strategy.


    Attributes
    ----------
    measurement : :class:`evedata.measurement.boundaries.measurement.Measurement`
        Measurement the harmonisation should be performed for.

        Although harmonisation is carried out for a small subset of the
        device data of a measurement, additional information from the
        measurement may be necessary to perform the task.

    Parameters
    ----------
    measurement : :class:`evedata.measurement.boundaries.measurement.Measurement`
        Measurement the harmonisation should be performed for.


    Examples
    --------
    Usually, harmonisation takes place in the :meth:`set_data()
    <evedata.measurement.boundaries.measurement.Measurement.set_data>` and
    :meth:`set_axes()
    <evedata.measurement.boundaries.measurement.Measurement.set_axes>`
    methods. Furthermore, a :obj:`Measurement
    <evedata.measurement.boundaries.measurement.Measurement>` object will
    have a :class:`Harmonisation` instance of the appropriate type. To
    harmonise data, in this case of a detector channel and a motor axis,
    call :meth:`harmonise` with the respective parameters:

    .. code-block::

        harmonisation = Harmonisation(measurement=my_measurement)
        data, *axes = harmonisation.harmonise(
            data=("SimChan:01", None),
            axes=(("SimMot:02", None)),
        )

    Note the use of two variables for the return of the method, and in
    particular the use of ``*axes`` ensuring that ``axes`` is always a list
    and takes all remaining return arguments, regardless of their count.

    .. important::
        While it may be tempting to use this class on your own and work
        further with the returned arrays, you will lose all metadata and
        context. Hence, simply *don't*. Just use the interface provided by
        :class:`Measurement
        <evedata.measurement.boundaries.measurement.Measurement>` instead.

    """

    def __init__(self, measurement=None):
        self.measurement = measurement

    def harmonise(self, data=None, axes=None):
        """
        Harmonise data.

        The main "quantisation" axis of the values for a device and the
        common reference is the list of positions. Hence, to harmonise,
        first of all the lists of positions are compared, and gaps handled
        accordingly.

        As there are different strategies how to deal with gaps in the
        positions list, generally, there will be different subclasses of the
        :class:`Harmonisation` class dealing each with a particular strategy.

        Parameters
        ----------
        data : :class:`tuple` | :class:`list`
            Name of the device and its attribute data are taken from.

            If the attribute is set to None, ``data`` will be used instead.

        axes : :class:`tuple` | :class:`list`
            Names of the devices and their attribute axes values are taken from.

            If an attribute is set to None, ``data`` will be used instead.

            Each element of the tuple/list is itself a two-element
            tuple/list with name and attribute.

        Returns
        -------
        data : :class:`list`
            Homogenised data and axes values.

            The first element is always the data, the following the
            (variable number of) axes. To separate the two and always get a
            list of axes, you may call it like this:

            .. code-block::

                data, *axes = harmonisation.harmonise(...)

        Raises
        ------
        ValueError
            Raised if no measurement is present
        ValueError
            Raised if no data are provided
        ValueError
            Raised if no axes are provided

        """
        if not self.measurement:
            raise ValueError("Need a measurement to harmonise data.")
        if not data:
            raise ValueError("Need data to harmonise data.")
        if not axes:
            raise ValueError("Need axes to harmonise data.")
        return self._harmonise(data=data, axes=axes)

    def _harmonise(self, data=None, axes=None):  # noqa
        return []


class AxesLastFill(Harmonisation):
    # noinspection PyUnresolvedReferences
    """
    Inflate axes to data dimensions using last for missing value.

    This was previously known as "LastFill" mode and was described as "Use
    all channel data and fill in the last known position for all axes
    without values."

    While the terms "channel" and "axis" have different meanings than in
    context of the :mod:`harmonising
    <evedata.measurement.controllers.harmonising>` module, the behaviour is
    qualitatively similar:

    * The device used as "data" is taken as reference and its values are
      *not* changed.
    * The values of  devices used as "axes" are inflated to the same
      dimension as the data.
    * For values originally missing for an axis, the last value of the
      previous position is used.

    Of course, as in all cases, the (integer) positions are used as common
    reference for the values of all devices.

    .. todo::
        Currently, the class does *not* handle snapshot values, as snapshots
        are not yet present in the Measurement object.


    Attributes
    ----------
    measurement : :class:`evedata.measurement.boundaries.measurement.Measurement`
        Measurement the harmonisation should be performed for.

        Although harmonisation is carried out for a small subset of the
        device data of a measurement, additional information from the
        measurement may be necessary to perform the task.

    Parameters
    ----------
    measurement : :class:`evedata.measurement.boundaries.measurement.Measurement`
        Measurement the harmonisation should be performed for.


    Examples
    --------
    See the :class:`Harmonisation` base class for examples -- and replace
    the class name accordingly.

    """

    def _harmonise(self, data=None, axes=None):
        result = []
        data_device = self.measurement.devices[data[0]]
        axes_devices = [self.measurement.devices[axis[0]] for axis in axes]
        if data[1]:
            data_attribute = data[1]
        else:
            data_attribute = "data"
        data_values = getattr(data_device, data_attribute)
        result.append(data_values)
        for idx, axes_device in enumerate(axes_devices):
            if axes[idx][1]:
                axes_attribute = axes[idx][1]
            else:
                axes_attribute = "data"
            values = getattr(axes_device, axes_attribute)
            positions = (
                np.digitize(data_device.positions, axes_device.positions) - 1
            )
            values = values[positions]
            result.append(values)
        return result
