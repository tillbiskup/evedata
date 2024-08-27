"""

*Ensure data and axes values are commensurate and compatible.*

For each motor axis and detector channel, in the original eveH5 file only
those values appear---together with a "position" (PosCount) value---that
have actually been set or measured. Hence, the number of values (*i.e.*,
the length of the data vector) will generally be different for different
devices. To be able to plot arbitrary data against each other,
the corresponding data vectors need to be commensurate. If this is not the
case, they need to be brought to the same dimensions (*i.e.*, "joined",
originally somewhat misleadingly termed "filled").

To be exact, being commensurate is only a necessary, but not a sufficient
criterion, as not only the shape needs to be commensurate, but the indices
(in this case the positions) be identical.


A bit of history
================

In the previous inerface (``EveFile``), there are four "fill modes" available
for data: NoFill, LastFill, NaNFill, LastNaNFill. From the `documentation of
eveFile <https://www.ahf.ptb.de/messpl/sw/python/common/eveFile/doc/html
/Section-Fillmode.html#evefile.Fillmode>`_:


NoFill
    "Use only data from positions where at least one axis and one channel
    have values."

    Actually, not a filling, but mathematically an intersection, or,
    in terms of relational databases, an ``SQL INNER JOIN``. In any case,
    data are *reduced*.

LastFill
    "Use all channel data and fill in the last known position for all axes
    without values."

    Similar to an ``SQL LEFT JOIN`` with data left and axes right,
    but additionally explicitly setting the missing axes values in the join
    to the last known axis value.

NaNFill
    "Use all axis data and fill in NaN for all channels without values."

    Similar to an ``SQL LEFT JOIN`` with axes left and data right. To be
    exact, the ``NULL`` values of the join operation will be replaced by
    ``NaN``.

LastNaNFill
    "Use all data and fill in NaN for all channels without values and fill
    in the last known position for all axes without values."

    Similar to an ``SQL OUTER JOIN``, but additionally explicitly setting
    the missing axes values in the join to the last known axis value and
    replacing the ``NULL`` values of the join operation by ``NaN``.


Furthermore, for the Last*Fill modes, snapshots are inspected for axes
values that are newer than the last recorded axis in the main/standard section.

Note that none of the fill modes guarantees that there are no NaNs (or
comparable null values) in the resulting data.


.. important::

    The IDL Cruncher seems to use LastNaNFill combined with applying some
    "dirty" fixes to account for scans using MPSKIP and those scans
    "monitoring" a motor position via a pseudo-detector. The ``EveHDF``
    class (DS) uses LastNaNFill as a default as well but does *not* apply
    some additional post-processing.


Join modes currently implemented
================================

Currently, there is exactly one join mode implemented:

* :class:`AxesLastFill`

  Inflate axes to data dimensions using last for missing value.

  This mode is equivalent to the "LastFill" mode described above.


For developers
==============

To implement additional join modes, create a class inheriting from the
:class:`Join` base class and implement the actual joining in the private
method ``_join()``.

There is a factory class :class:`JoinFactory` that you can ask to get a
:class:`Join` object:

.. code-block::

    factory = JoinFactory()
    join = factory.get_join(mode="AxesLastFill")

This would return an :obj:`AxesLastFill` object. For further details,
see the :class:`JoinFactory` documentation.


Module documentation
====================

"""

import logging

import numpy as np
import numpy.ma as ma

logger = logging.getLogger(__name__)


class Join:
    """
    Base class for joining data.

    For each motor axis and detector channel, in the original eveH5 file only
    those values appear---together with a "position counter" (PosCount)
    value---that have actually been set or measured. Hence, the number of
    values (*i.e.*, the length of the data vector) will generally be different
    for different devices. To be able to plot arbitrary data against each
    other, the corresponding data vectors need to be commensurate. If this
    is not the case, they need to be brought to the same dimensions (*i.e.*,
    "joined", originally somewhat misleadingly termed "filled").

    The main "quantisation" axis of the values for a device and the
    common reference is the list of positions. Hence, to join,
    first of all the lists of positions are compared, and gaps handled
    accordingly.

    As there are different strategies how to deal with gaps in the
    positions list, generally, there will be different subclasses of the
    :class:`Join` class dealing each with a particular strategy.


    Attributes
    ----------
    measurement : :class:`evedata.measurement.boundaries.measurement.Measurement`
        Measurement the Join should be performed for.

        Although joining is carried out for a small subset of the
        device data of a measurement, additional information from the
        measurement may be necessary to perform the task.

    Parameters
    ----------
    measurement : :class:`evedata.measurement.boundaries.measurement.Measurement`
        Measurement the join should be performed for.


    Examples
    --------
    Usually, joining takes place in the :meth:`set_data()
    <evedata.measurement.boundaries.measurement.Measurement.set_data>` and
    :meth:`set_axes()
    <evedata.measurement.boundaries.measurement.Measurement.set_axes>`
    methods. Furthermore, a :obj:`Measurement
    <evedata.measurement.boundaries.measurement.Measurement>` object will
    have a :class:`Join` instance of the appropriate type. To
    join data, in this case of a detector channel and a motor axis,
    call :meth:`join` with the respective parameters:

    .. code-block::

        join = Join(measurement=my_measurement)
        data, *axes = join.join(
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

    def join(self, data=None, axes=None):
        """
        Harmonise data.

        The main "quantisation" axis of the values for a device and the
        common reference is the list of positions. Hence, to join,
        first of all the lists of positions are compared, and gaps handled
        accordingly.

        As there are different strategies how to deal with gaps in the
        positions list, generally, there will be different subclasses of the
        :class:`Join` class dealing each with a particular strategy.

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
            Joined data and axes values.

            The first element is always the data, the following the
            (variable number of) axes. To separate the two and always get a
            list of axes, you may call it like this:

            .. code-block::

                data, *axes = join.join(...)

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
            raise ValueError("Need a measurement to join data.")
        if not data:
            raise ValueError("Need data to join data.")
        if not axes:
            raise ValueError("Need axes to join data.")
        return self._join(data=data, axes=axes)

    def _join(self, data=None, axes=None):  # noqa
        return []


class AxesLastFill(Join):
    # noinspection PyUnresolvedReferences
    """
    Inflate axes to data dimensions using last for missing value.

    This was previously known as "LastFill" mode and was described as "Use
    all channel data and fill in the last known position for all axes
    without values." In SQL terms (relational database), this would be
    similar to a left join with data left and axes right, but additionally
    explicitly setting the missing axes values in the join to the last
    known axis value.

    While the terms "channel" and "axis" have different meanings than in
    context of the :mod:`joining
    <evedata.measurement.controllers.joining>` module, the behaviour is
    qualitatively similar:

    * The device used as "data" is taken as reference and its values are
      *not* changed.
    * The values of  devices used as "axes" are inflated to the same
      dimension as the data.
    * For values originally missing for an axis, the last value of the
      previous position is used.
    * If no previous value exists for a missing value, the value of
      :attr:`missing_value` is used.
    * The snapshots are checked for values corresponding to the axis,
      and if present, are taken into account.

    Of course, as in all cases, the (integer) positions are used as common
    reference for the values of all devices.


    Attributes
    ----------
    measurement : :class:`evedata.measurement.boundaries.measurement.Measurement`
        Measurement the join should be performed for.

        Although joining is carried out for a small subset of the
        device data of a measurement, additional information from the
        measurement may be necessary to perform the task, *e.g.*,
        the snapshots.

    missing_value : :attr:`numpy.ma.masked` | :class:`float`
        Value used if no previous axis value is available.

        Default: :attr:`numpy.ma.masked`

    Parameters
    ----------
    measurement : :class:`evedata.measurement.boundaries.measurement.Measurement`
        Measurement the join should be performed for.


    Examples
    --------
    See the :class:`Join` base class for examples -- and replace
    the class name accordingly.

    """

    def __init__(self, measurement=None):
        super().__init__(measurement=measurement)
        self.missing_value = ma.masked

    def _join(self, data=None, axes=None):
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
            if axes[idx][0] in self.measurement.device_snapshots:
                axes_positions = np.searchsorted(
                    axes_device.positions,
                    self.measurement.device_snapshots[axes[idx][0]].positions,
                )
                snapshot_values = getattr(
                    self.measurement.device_snapshots[axes[idx][0]],
                    axes_attribute,
                )
                values = np.insert(values, axes_positions, snapshot_values)
            else:
                axes_positions = axes_device.positions
            positions = np.digitize(data_device.positions, axes_positions) - 1
            values = values[positions]
            # Set values to special value where no previous axis values exist
            if np.any(np.where(positions < 0)):
                values = ma.masked_array(values)
                values[np.where(positions < 0)] = self.missing_value
            result.append(values)
        return result


class JoinFactory:
    """
    Factory for getting the correct join object.

    For background on the need for joining, see the documentation of the
    entire :mod:`joining <evedata.measurement.controllers.joining>` module, and
    of the :class:`Join <evedata.measurement.controllers.joining.Join>` class.

    Given a decision which type of join you would like to apply to
    your data, this factory class allows you to get the correct
    join instance without hassle. And you can even change your mind
    in between and don't have to change any code---the whole idea behind
    factories.

    Attributes
    ----------
    measurement : :class:`evedata.measurement.boundaries.measurement.Measurement`
        Measurement the join should be performed for.


    Parameters
    ----------
    measurement : :class:`evedata.measurement.boundaries.measurement.Measurement`
        Measurement the join should be performed for.


    Examples
    --------
    Getting a join object is as simple as calling a single method
    on the factory object:

    .. code-block::

        factory = JoinFactory()
        join = factory.get_join(mode="AxesLastFill")

    This will provide you with the appropriate :obj:`AxesLastFill` instance.

    As joins need a :class:`Measurement
    <evedata.measurement.boundaries.measurement.Measurement>` object,
    you can set one to the factory, and it will get added automatically to
    the join instance for you:

    .. code-block::

        factory = JoinFactory(measurement=my_measurement)
        join = factory.get_join(mode="AxesLastFill")

    Thus, when used from within a :class:`Measurement
    <evedata.measurement.boundaries.measurement.Measurement>` object,
    set the :attr:`measurement` attribute to ``self``.

    """

    def __init__(self, measurement=None):
        self.measurement = measurement

    def get_join(self, mode="Join"):
        """
        Obtain a :class:`Join` instance for a particular mode.

        If no mode is provided, this defaults to the base class. As the
        :class:`Join` does not implement any functionality, this is
        rather useless.

        If the :attr:`measurement` attribute is set, it is automatically set
        in the :obj:`Join` instance returned.

        Parameters
        ----------
        mode : :class:`str`
            Join mode to return a :class:`Join` instance for.

            Default: "Join"

        Returns
        -------
        join : :class:`Join`
            Join instance

        """
        instance = globals()[mode](measurement=self.measurement)
        return instance
