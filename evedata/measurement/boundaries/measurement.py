"""
*High-level Python object representation of a measurement.*

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 1

This module provides a high-level representation of a measurement as
manifested in an eveH5 file. Being a high-level, user-facing object
representation, technically speaking this module is a facade.

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
    the ``data`` attribute. This contains the actual data that should be
    plotted or processed further. Thus, the :class:`Measurement
    <evedata.measurement.boundaries.measurement.Measurement>` facade
    resembles the dataset concept known from the ASpecD framework and
    underlying, *i.a.*, the ``radiometry`` package. The
    :meth:`Measurement.set_data()
    <evedata.measurement.boundaries.measurement.Measurement.set_data>` method
    takes care of filling (of the axes) if necessary. Furthermore, you can
    set the attribute of the underlying data object to obtain the data from,
    if it is not ``data``, but, *e.g.*, ``std`` or an option.


Key aspects
===========


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

* Move all data objects from the :attr:`EveFile.data
  <evedata.evefile.boundaries.evefile.EveFile.data>` attribute to the
  :attr:`Measurement.devices` attribute.

  * Is this entirely true? How to deal with things such as current and
    lifetime that technically speaking belong to the machine section?

* Populate the :attr:`Measurement.machine` and :attr:`Measurement.beamline`
  attributes.

* Set the :attr:`Measurement.data` attribute with the data from the
  :attr:`Evefile.metadata.preferred_axis
  <evedata.evefile.entities.file.Metadata.preferred_axis>` and
  :attr:`EveFile.metadata.preferred_channel
  <evedata.evefile.entities.file.Metadata.preferred_channel>`
  attributes of the eveH5 file, if present.


Module documentation
====================

"""

import logging

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

    def __init__(self):
        super().__init__()
        self.data = entities.Data()
