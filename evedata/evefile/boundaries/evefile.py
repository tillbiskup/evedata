"""

*High-level Python object representation of eveH5 file contents.*

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 1

This module provides a high-level representation of the contents of an eveH5
file. Being a high-level, user-facing object representation, technically
speaking this module is a facade. The corresponding resource
(persistence-layer-facing interface) would be the :mod:`eveh5
<evedata.evefile.boundaries.eveh5>` module.

The big difference to the :mod:`evedata.measurement` subpackage: the
:mod:`evedata.evefile` subpackage still is rather close to the eveH5 files
and rather generic. Furthermore, some aspects such as "filling" (
*i.e.*, adding data points for axes datasets to be able to plot
arbitrary datasets against each other) are *not* performed within the
:mod:`evedata.evefile` subpackage. Additional abstractions, such as
instruments, will be implemented in the :mod:`evedata.measurement`
subpackage. However, each eveH5 file can be represented by an :obj:`EveFile`
object, and the :mod:`evedata.measurement` subpackage will make use of this
module.


Overview
========

A first overview of the classes implemented in this module and their
hierarchy is given in the UML diagram below.


.. figure:: /uml/evedata.evefile.boundaries.evefile.*
    :align: center

    Class hierarchy of the :mod:`evedata.evefile.boundaries.evefile` module,
    providing the facade (user-facing interface) for an eveH5 file.
    Basically, it inherits from :class:`evedata.evefile.entities.file.File`
    and adds behaviour. Most of this behaviour is contributed by the various
    modules of the :mod:`controllers <evedata.evefile.controllers>` subpackage.


Key aspects
===========

While the :mod:`evefile <evedata.evefile.boundaries.evefile>` module is the
high-level interface (facade) of the :mod:`evedata.evefile` subpackage,
it is still, from a functional viewpoint, close to the actual eveH5 files,
providing a faithful representation of all information contained in an eveH5
(and SCML) file. Nevertheless, it is clearly an abstraction from the actual
data files. Hence, the key characteristics of the module are:

* Stable interface to eveH5 files, regardless of their version.
* Powerful abstractions on the device level.

    * Options to devices appear as attributes of the device objects, not as
      separate datasets.
    * Devices have clear, recognisable types, such as "multimeter", "MCA",
      "scientific camera", to name but a few.

* Access to the complete information contained in an eveH5 (and SCML) file,
  *i.e.*, data and scan description.
* **No data filling**, *i.e.*, generally no ready-to-plot datasets.

    * Data filling functionality is provided by the
      :mod:`evedata.measurement` subpackage.
    * The reason to *not* automatically fill data: being able to tell which
      data (points) have actually been recorded.

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

    evefile = File()
    evefile.load(filename="my_measurement_file.h5")

Of course, you could alternatively set the filename first,
thus shortening the :meth:`load` method call:

.. code-block::

    evefile = File()
    evefile.filename = "my_measurement_file.h5"
    evefile.load()


Internals: What happens when reading an eveH5 file?
===================================================

Reading an eveH5 file is not as simple as reading contents of an HDF5 file
and present its contents as Python object hierarchy. At least, if you would
like to view, process, and analyse your data more conveniently, you should
not stop here. The idea behind the ``evedata`` package, an in parts behind
the :class:`EveFile` class, is to provide you as consumer of the data with
powerful abstractions and structured information. To this end, a series of
steps are necessary:

* Check whether the eveH5 file contains the scan description (SCML) file.

    * If so, extract (up to eveH5 v7) and import the scan description.
    * If not, we're probably doomed, as some of the mappings are hard to do
      otherwise.

* Read the eveH5 file (actually, an HDF5 file).
* Get the correct :class:`VersionMapper
  <evedata.evefile.controllers.version_mapping.VersionMapper>` class.
* Map the file contents to the proper data structures provided by the
  ``evedata`` package.


Module documentation
====================

"""

import logging

from evedata.evefile.entities.file import File
from evedata.evefile.boundaries.eveh5 import HDF5File
from evedata.evefile.controllers import version_mapping


logger = logging.getLogger(__name__)


class EveFile(File):
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

    data : :class:`dict`
        Data recorded from the devices involved in a measurement.

        Each item is an instance of
        :class:`evedata.evefile.entities.data.Data`.

    snapshots : :class:`dict`
        Device data recorded as snapshot during a measurement.

        Only those device data that are not options belonging to any of
        the devices in the :attr:`data` attribute are stored here.

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

    Raises
    ------
    exception
        Short description when and why raised


    Examples
    --------
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
        self._load_scml()
        self._read_and_map_eveh5_file()

    def _load_scml(self):
        pass

    def _read_and_map_eveh5_file(self):
        eveh5 = HDF5File()
        eveh5.read_attributes = True
        eveh5.read(filename=self.metadata.filename)
        mapper_factory = version_mapping.VersionMapperFactory()
        mapper = mapper_factory.get_mapper(eveh5)
        mapper.map(source=eveh5, destination=self)
