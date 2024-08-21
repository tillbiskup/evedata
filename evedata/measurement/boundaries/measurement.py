r"""
.. include:: <isopub.txt>

*High-level Python object representation of a measurement.*

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 1

This module provides a high-level representation of a measurement as
manifested in an eveH5 file. Being a high-level, user-facing object
representation, technically speaking this module is a facade.

A measurement generally reflects all the data obtained during a
measurement. However, to plot data or to perform some analysis, usually we
need data together with an axis (or multiple axes for *n*\D data),
where data ("intensity values") and axis values come from different HDF5
datasets. Furthermore, there may generally be the need/interest to plot
arbitrary data against each other, *i.e.* channel data *vs.* channel data
and axis data *vs.* axis data, not only channel data *vs.* axis data. This
is the decisive difference between the :class:`Measurement entity
<evedata.measurement.entities.measurement.Measurement>` and the
:class:`Measurement facade
<evedata.measurement.boundaries.measurement.Measurement>`, with the latter
having the additional attributes for storing the data to work on.

The big difference to the :mod:`evedata.evefile` subpackage: the
:mod:`evedata.measurement` subpackage abstracts from the underlying eveH5
file and its structure and provides aspects such as "filling" (*i.e.*, adding
data points for axes datasets to be able to plot arbitrary datasets against
each other).


Overview
========

A first overview of the classes implemented in this module and their
hierarchy is given in the UML diagram below.


.. figure:: /uml/evedata.measurement.boundaries.measurement.*
    :align: center

    Class hierarchy of the :mod:`measurement.boundaries.measurement
    <evedata.measurement.entities.measurement>` module. The
    :class:`Measurement
    <evedata.measurement.boundaries.measurement.Measurement>` facade inherits
    directly from its entities counterpart. The crucial extension here is
    the :attr:`data <Measurement.data>` attribute. This contains the actual
    data that should be plotted or processed further. Thus, the
    :class:`Measurement
    <evedata.measurement.boundaries.measurement.Measurement>` facade
    resembles the dataset concept known from the ASpecD framework and
    underlying, *i.a.*, the ``radiometry`` package. The
    :meth:`Measurement.set_axes() <Measurement.set_axes>` method
    takes care of "filling" (of the axes) if necessary. Furthermore, you can
    set the attribute of the underlying data object to obtain the data from,
    if it is not ``data``, but, *e.g.*, ``std`` or an option.


Key aspects
===========

The :mod:`measurement <evedata.measurement.boundaries.measurement>` module
is the high-level interface (facade) of the :mod:`evedata.measurement`
subpackage, abstracting much further away from the actual eveH5 files than
the :mod:`evefile <evedata.evefile.boundaries.evefile>` module in the
:mod:`evedata.evefile` subpackage. Hence, the key characteristics of the
module are:

* Stable interface to eveH5 files, regardless of their version.

  * Some features may only be available for newer eveH5 versions, though.

* Powerful abstractions on and beyond the device level.

  * Options to devices appear as attributes of the device objects, not as
    separate datasets.
  * Devices have clear, recognisable types, such as "multimeter", "MCA",
    "scientific camera", to name but a few.

* Access to the complete information contained in an eveH5 (and SCML) file,
  *i.e.*, data and scan description.
* Distinction between :attr:`data <Measurement.data>` and :attr:`devices
  <Measurement.devices>`:

  * Devices are all available devices used in the scan modules that
    produced some data.
  * Data is the current selection of devices to plot, process, or analyse
    data for.
  * Data always contains a *n*\D array with intensity values and
    corresponding axes.

* Distinction between :attr:`devices <Measurement.devices>` (setup),
  :attr:`beamline <Measurement.beamline>`, and :attr:`machine
  <Measurement.machine>`:

  * Devices are all available devices used in the scan modules that
    produced some data.
  * Beamline contains information from all devices that are part of the
    beamline, such as shutters, valves, and alike. Usually, only a few
    data points per scan are recorded for those devices, typically by
    means of snapshots.
  * Machine contains information regarding the actual synchrotron. These
    are "read-only" devices, and they may not be controlled by the
    measurement program, *i.e.* be actual monitors with time stamps rather
    than positions.

* **Data "filling"** for ready-to-plot datasets.

  * "Filling" is only carried out for the currently selected devices in
    the "data" attribute.

* Actual **data are loaded on demand**, not when loading the file.

  * This does *not* apply to the metadata of the individual datasets.
    Those are read upon reading the file.
  * Reading data on demand should save time and resources, particularly
    for larger files.
  * Often, you are only interested in a subset of the available data.


Usage
=====

Loading the contents of a data file of a measurement may be as simple as:

.. code-block::

    from evedata.measurement.boundaries.measurement import Measurement

    measurement = Measurement()
    measurement.load(filename="my_measurement_file.h5")

Of course, you could alternatively set the filename first,
thus shortening the :meth:`load` method call:

.. code-block::

    measurement = Measurement()
    measurement.filename = "my_measurement_file.h5"
    measurement.load()

There is even a third way now: Instantiating the class already with a
given filename:

.. code-block::

    measurement = Measurement(filename="my_measurement_file.h5")
    measurement.load()

And yes, you can of course chain the object creation and loading the file
if you like. However, this leads to harder to read code and is therefore
*not* suggested.


Internals: What happens when reading an eveH5 file?
===================================================

Reading an eveH5 file is not as simple as reading contents of an HDF5 file
and present its contents as Python object hierarchy. At least, if you would
like to view, process, and analyse your data more conveniently, you should
not stop here. The idea behind the ``evedata`` package, and in parts behind
the :class:`Measurement` class, is to provide you as consumer of the data
with powerful abstractions and structured information. To this end,
a series of steps are necessary. Besides those described for the
underlying :class:`EveFile <evedata.evefile.boundaries.evefile.EveFile>`
class, these are:

* Copy all attributes from the :attr:`EveFile.metadata
  <evedata.evefile.boundaries.evefile.EveFile.metadata>` attribute to the
  :attr:`Measurement.metadata` attribute. |check|

* Copy the :attr:`EveFile.log_messages
  <evedata.evefile.boundaries.evefile.EveFile.log_messages>` attribute to the
  :attr:`Measurement.log_messages` attribute. |check|

* Move all data objects from the :attr:`EveFile.data
  <evedata.evefile.boundaries.evefile.EveFile.data>` attribute to the
  :attr:`Measurement.devices` attribute. |check|

  * Is this entirely true? How to deal with things such as current and
    lifetime that technically speaking belong to the machine section?

* Populate the :attr:`Measurement.machine` and :attr:`Measurement.beamline`
  attributes. |cross|

* Set the :attr:`Measurement.data` attribute with the data from the
  :attr:`EveFile.metadata.preferred_axis
  <evedata.evefile.entities.file.Metadata.preferred_axis>` and
  :attr:`EveFile.metadata.preferred_channel
  <evedata.evefile.entities.file.Metadata.preferred_channel>`
  attributes of the eveH5 file, if present. |check|

  * Set axis metadata (measure, unit). |check|
  * Fill data accordingly if necessary. |cross|

* Copy the :attr:`EveFile.scan
  <evedata.evefile.boundaries.evefile.EveFile.setup>` attribute to the
  :attr:`Measurement.scan` attribute. |cross|

* Copy the :attr:`EveFile.setup
  <evedata.evefile.boundaries.evefile.EveFile.setup>` attribute to the
  :attr:`Measurement.setup` attribute. |cross|


Questions to address
====================

* How to deal with snapshots?

  * Currently, all devices from the snapshot section that are *not* as
    well part of the main section will end up in either
    :attr:`Measurement.machine` or :attr:`Measurement.beamline`.
  * What about those snapshot devices that are part of the main section?
    They may be relevant for the filling, hence most possibly need to be
    retained somewhere.

* How to sensibly distinguish which of the datasets originally in the
  snapshot and monitor section belong to :attr:`Measurement.machine` and
  which to :attr:`Measurement.beamline`?

* How to deal with the :attr:`EveFile.position_timestamps
  <evedata.evefile.boundaries.evefile.EveFile.position_timestamps>` dataset?

  * This one is necessary for mapping monitor timestamps to positions.
  * Could we deal with it internally, as we have a representation of the
    :obj:`EveFile <evedata.evefile.boundaries.evefile.EveFile>` object?

* Where to get metadata for machine, beamline, and samples from?


Module documentation
====================

"""

import logging

from evedata.evefile.boundaries.evefile import EveFile
from evedata.measurement.entities import measurement as entities


logger = logging.getLogger(__name__)


class Measurement(entities.Measurement):
    """
    High-level Python object representation of a measurement.

    This class serves as facade to the entire :mod:`evedata.measurement`
    subpackage and provides a rather high-level representation of the
    contents of an individual measurement, whose contents are stored in an
    eveH5 file.

    Individual measurements are saved in HDF5 files using a particular
    schema (eveH5). Besides file-level metadata, there are log messages,
    a scan description (originally an XML/SCML file), and the actual data.

    The data are organised in three functionally different sections: devices,
    machine, and beamline.


    Attributes
    ----------
    devices : :class:`dict`
        Data recorded from the devices involved in a measurement.

        Each item is an instance of either
        :class:`evedata.evefile.entities.data.ChannelData` or
        :class:`evedata.evefile.entities.data.AxisData`.

    machine : :class:`dict`
        Data recorded from the machine involved in a measurement.

        Each item is an instance of
        :class:`evedata.evefile.entities.data.Data`.

    beamline : :class:`dict`
        Data recorded from the beamline involved in a measurement.

        Each item is an instance of
        :class:`evedata.evefile.entities.data.Data`.

    metadata : :class:`evedata.measurement.entities.metadata.Metadata`
        Measurement metadata

    log_messages : :class:`list`
        Log messages from an individual measurement

        Each item in the list is an instance of
        :class:`evedata.evefile.entities.file.LogMessage`.

    scan : :class:`Scan`
        Description of the actual scan.

    setup : :class:`Setup`
        Description of the actual setup.

    data : :class:`evedata.measurement.entities.measurement.Data`
        Actual data that should be plotted or processed further.

        The attribute will usually be pre-filled with the data from the
        :attr:`Evefile.metadata.preferred_axis
        <evedata.evefile.entities.file.Metadata.preferred_axis>` and
        :attr:`EveFile.metadata.preferred_channel
        <evedata.evefile.entities.file.Metadata.preferred_channel>`
        attributes of the eveH5 file, if present. They can be set/changed
        using the :meth:`set_data` and :meth:`set_axes` methods.

    Raises
    ------
    exception
        Short description when and why raised


    Examples
    --------
    It is always nice to give some examples how to use the class. Best to do
    that with code examples:

    .. code-block::

        obj = Measurement()
        ...



    """

    def __init__(self, filename=""):
        super().__init__()
        self.data = entities.Data()
        self.filename = filename
        self._evefile = None

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
        self._load_evefile()
        self._map_metadata()
        self._map_log_messages()
        self._map_devices()
        self._set_data()

    def _load_evefile(self):
        self._evefile = EveFile(filename=self.metadata.filename)
        self._evefile.load()

    def _map_metadata(self):
        attributes = [
            attribute
            for attribute in list(self._evefile.metadata.__dict__.keys())
            if not str(attribute).startswith("_")
        ]
        for attribute in attributes:
            setattr(
                self.metadata,
                attribute,
                getattr(self._evefile.metadata, attribute),
            )

    def _map_log_messages(self):
        self.log_messages = self._evefile.log_messages

    def _map_devices(self):
        for key, value in self._evefile.data.items():
            self.devices[key] = value

    def _set_data(self):
        if self.metadata.preferred_axis and self.metadata.preferred_channel:
            self.data.data = self.devices[
                self.metadata.preferred_channel
            ].data
            self.data.axes[0].values = self.devices[
                self.metadata.preferred_axis
            ].data
            self._set_axis_metadata_from_device(
                self.data.axes[0], self.metadata.preferred_axis
            )
            self._set_axis_metadata_from_device(
                self.data.axes[1], self.metadata.preferred_channel
            )

    def _set_axis_metadata_from_device(self, axis=None, device=""):
        axis.quantity = self.devices[device].metadata.name
        axis.unit = self.devices[device].metadata.unit
