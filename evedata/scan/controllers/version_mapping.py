"""
.. include:: <isopub.txt>

*Mapping SCML contents to the entities of the scan subpackage.*

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 2

There are different versions of the schema underlying the SCML files.
Hence, mapping the contents of an SCML file to the data model of the
evedata package requires to get the correct mapper for the specific
version. This is the typical use case for the factory pattern.

Users of the module hence will typically only obtain a
:obj:`VersionMapperFactory` object to get the correct mappers for individual
files. Furthermore, "users" basically boils down to the :class:`Scan
<evedata.scan.boundaries.scan.Scan>` class. Therefore, users of
the `evedata` package usually do not interact directly with any of the
classes provided by this module.


Overview
========

Being version agnostic with respect to eveH5 and SCML schema versions is a
central aspect of the evedata package. This requires facilities mapping
the actual SCML files to the data model provided by the :mod:`entities
<evedata.scan.entities>` technical layer of the :mod:`scan <evedata.scan>`
subpackage. The :class:`File <evedata.evefile.boundaries.evefile.File>`
facade obtains the correct :obj:`VersionMapper` object via the
:class:`VersionMapperFactory`, providing a :class:`SCML
<evedata.scan.boundaries.scml.SCML>` resource object to the factory. It is
the duty of the factory to obtain the "version" attribute from the
:obj:`SCML <evedata.scan.boundaries.scml.SCML>` object.


.. figure:: /uml/evedata.scan.controllers.version_mapping.*
    :align: center

    Class hierarchy of the :mod:`evedata.scan.controllers.version_mapping`
    module, providing the functionality to map different SCML file
    schemas to the data structure provided by the :class:`Scan
    <evedata.scan.boundaries.scan.Scan>` and :class:`Station
    <evedata.scan.boundaries.scan.Station>` classes. The factory
    will be used to get the correct mapper for a given SCML file.
    For each SCML schema version, there exists an individual
    ``VersionMapperVxmy`` class dealing with the version-specific mapping.
    The idea behind the ``Mapping`` class is to provide simple mappings for
    attributes and alike that need not be hard-coded and can be stored
    externally, *e.g.* in YAML files. This would make it easier to account
    for (simple) changes.


For each SCML schema version, there exists an individual
``VersionMapperVxmy`` class dealing with the version-specific mapping.
Currently, we assume major and minor version numbers to be relevant. Hence
the ``xmy`` suffix for the individual mapper classes. That
part of the mapping common to all versions of the SCML schema takes place
in the :class:`VersionMapper` parent class. The idea behind the ``Mapping``
class is to provide simple mappings for attributes and alike that can be
stored externally, *e.g.* in YAML files. This would make it easier to
account for (simple) changes.


Mapping tasks for SCML schema up to v9.2
========================================

Currently, the structure of the entities in the :mod:`evedata.scan.entities`
subpackage is not stable, and furthermore, there is no overview how much the
SCML schema has changed for the different versions. Hence, the tasks
described here will definitely change and evolve over time.

* Map SCML metadata (version, location) |check|
* Map scan -- if it exists

  * Map scan metadata (repeat_count, comment, description, ...) (|check|)
  * Map scan modules (|check|)

    * Distinguish types of scan modules: "classic" *vs.* snapshot |check|
    * Extract list of detector channels and motor axes |check|
    * Map pre- and post-scans |cross|
    * Map positionings |cross|
    * Map plots? |cross|
    * Map remaining information? |cross|

* Map all devices |cross|

  * Map detectors
  * Map motors
  * Map devices


Currently, there is a need to map at least basic information about the scan
modules, to proceed with several controllers from the
:mod:`evedata.evefile.controllers` subpackage: mpskip, separating datasets
of redefined channels, obtain set values for axes. For details, see the
respective section of the :doc:`/architecture` document.


.. important::

    Due to the reasons mentioned above (urgent need to map only basic
    information about the scan modules), the mapping of the SCML file
    contents to the entities from the :mod:`evedata.scan.entities`
    subpackage is only rudimentary. Therefore, both mapping and internal
    handling of the SCML/XML tree will probably change in the future.


Distinguishing types of scan modules
------------------------------------

Currently, only two types of scan modules are distinguished: "classical"
modules and snapshot modules. The distinction is based on the existence of
the tag ``<classic>``: if present, we have a "classical" scan module,
if not, we have a snapshot module.

For "classical" modules, both axes and channels are mapped, for static axis
or channel snapshot modules, axes or channels, respectively.


Fundamental change of SCML schema with v10
==========================================

Most probably, the SCML schema will be changed quite substantially in the
future, based on all the experience with developing the ``evedata`` package
and the data models implemented therein.

Depending on how dramatic this changes will be, the mappers for versions up
to the current one (v9.x) and those of the next major version may differ
substantially.


Module documentation
====================

"""

import logging
import sys

from evedata.scan.entities import scan


logger = logging.getLogger(__name__)


class VersionMapperFactory:
    """
    Factory for obtaining the correct version mapper object.

    There are different versions of the schema underlying the SCML files.
    Hence, mapping the contents of an SCML file to the entities of the
    :mod:`scan <evedata.scan>` subpackage requires to get the correct mapper
    for the specific version. This is the typical use case for the factory
    pattern.


    Attributes
    ----------
    scml : :class:`evedata.scan.boundaries.scml.SCML`
        Python object representation of an SCML file

    Raises
    ------
    ValueError
        Raised if no SCML object is present


    Examples
    --------
    Using the factory is pretty simple. There are actually two ways how to
    set the scml attribute -- either explicitly or when calling the
    :meth:`get_mapper` method of the factory:

    .. code-block::

        factory = VersionMapperFactory()
        factory.scml = scml_object
        mapper = factory.get_mapper()

    .. code-block::

        factory = VersionMapperFactory()
        mapper = factory.get_mapper(scml=scml_object)

    In both cases, ``mapper`` will contain the correct mapper object,
    and ``scml_object`` contains the Python object representation of an
    SCML file.

    """

    def __init__(self):
        self.scml = None

    def get_mapper(self, scml=None):
        """
        Return the correct mapper for a given SCML file.

        For convenience, the returned mapper has its
        :attr:`VersionMapper.source` attribute already set to the
        ``scml`` object used to get the mapper for.

        Parameters
        ----------
        scml : :class:`evedata.scan.boundaries.scml.SCML`
            Python object representation of an SCML file

        Returns
        -------
        mapper : :class:`VersionMapper`
            Mapper used to map the SCML file contents to evedata structures.

        Raises
        ------
        ValueError
            Raised if no scml object is present

        """
        if scml:
            self.scml = scml
        if not self.scml:
            raise ValueError("Missing SCML object")
        version = self.scml.version.replace(".", "m")
        try:
            mapper = getattr(
                sys.modules[__name__], f"VersionMapperV{version}"
            )()
        except AttributeError as exc:
            raise AttributeError(f"No mapper for version {version}") from exc
        mapper.source = self.scml
        return mapper


class VersionMapper:
    """
    Mapper for mapping the SCML file contents to data structures.

    This is the base class for all version-dependent mappers. Given that
    there are different versions of the SCML schema, each version gets
    handled by a distinct mapper subclass.

    To get an object of the appropriate class, use the
    :class:`VersionMapperFactory` factory.


    Attributes
    ----------
    source : :class:`evedata.scan.boundaries.scml.SCML`
        Python object representation of an SCML file

    destination : :class:`evedata.scan.boundaries.scan.Scan`
        High(er)-level data structure representing an SCML file

        Can alternatively be an :obj:`evedata.scan.boundaries.scan.Station`
        object.


    Examples
    --------
    Although the :class:`VersionMapper` class is *not* meant to be used
    directly, its use is prototypical for all the concrete mappers:

    .. code-block::

        mapper = VersionMapper()
        mapper.map(source=scml, destination=scan)

    Usually, you will obtain the correct mapper from the
    :class:`VersionMapperFactory`. In this case, the returned mapper has
    its :attr:`source` attribute already set for convenience:

    .. code-block::

        factory = VersionMapperFactory()
        mapper = factory.get_mapper(scml=scml)
        mapper.map(destination=scan)

    """

    def __init__(self):
        self.source = None
        self.destination = None

    def map(self, source=None, destination=None):
        """
        Map the SCML file contents to data structures.

        Parameters
        ----------
        source : :class:`evedata.scan.boundaries.scml.SCML`
            Python object representation of an SCML file

        destination : :class:`evedata.scan.boundaries.scan.Scan`
            High(er)-level evedata structure representing an SCML file

            Can alternatively be an
            :obj:`evedata.scan.boundaries.scan.Station` object.

        Raises
        ------
        ValueError
            Raised if either source or destination are not provided

        """
        if source:
            self.source = source
        if destination:
            self.destination = destination
        self._check_prerequisites()
        self._map()

    def _check_prerequisites(self):
        if not self.source:
            raise ValueError("Missing source to map from.")
        if not self.destination:
            raise ValueError("Missing destination to map to.")

    def _map(self):
        self._map_metadata()
        try:
            self._map_scan()
        except AttributeError:
            pass

    def _map_metadata(self):
        self.destination.version = self.source.version
        self.destination.location = self.source.root.find("location").text

    def _map_scan(self):
        pass


class VersionMapperV9m2(VersionMapper):
    """
    Mapper for mapping SCML v9.2 file contents to data structures.

    .. note::

        Currently, most mapping is implemented in this class, and needs to
        be moved upwards in the inheritance hierarchy once this hierarchy
        exists.

        Furthermore, only a minimal set of mappings is currently performed,
        far from being a complete mapping of the contents of an SCML file.

    .. note::
        Only those scan modules that are actually connected (either to the
        root node or to another scan module) are actually mapped and
        contained in the list of scan modules.

    Attributes
    ----------
    source : :class:`evedata.scan.boundaries.scml.SCML`
        Python object representation of an SCML file

    destination : :class:`evedata.scan.boundaries.scan.Scan`
        High(er)-level data structure representing an SCML file


    Examples
    --------
    Mapping a given SCML file to the evedata structures is the same for
    each of the mappers:

    .. code-block::

        mapper = VersionMapperV9m2()
        mapper.map(source=scml, destination=scan)

    Usually, you will obtain the correct mapper from the
    :class:`VersionMapperFactory`. In this case, the returned mapper has
    its :attr:`source` attribute already set for convenience:

    .. code-block::

        factory = VersionMapperFactory()
        mapper = factory.get_mapper(scml=scml)
        mapper.map(destination=scan)

    """

    def _map_scan(self):
        self.destination.scan.repeat_count = int(
            self.source.scan.find("repeatcount").text
        )
        self.destination.scan.comment = self.source.scan.find("comment").text
        connected_scan_modules = [
            module
            for module in self.source.scan_modules
            if int(module.find("parent").text) != -1
        ]
        for module in connected_scan_modules:
            self.destination.scan.scan_modules[int(module.get("id"))] = (
                self._map_scan_module(module)
            )

    def _map_scan_module(self, element=None):
        if element.find("classic"):
            module = scan.ScanModule()
        else:
            module = scan.SnapshotModule()
        module.name = element.find("name").text
        module.parent = int(element.find("parent").text)
        try:
            module.appended = int(element.find("appended").text)
        except AttributeError:
            pass
        try:
            module.nested = int(element.find("nested").text)
        except AttributeError:
            pass
        for channel in element.iter("smchannel"):
            module.channels[channel.find("channelid").text] = (
                self._map_scan_module_channel(channel)
            )
        for axis in element.iter("smaxis"):
            module.axes[axis.find("axisid").text] = (
                self._map_scan_module_axis(axis)
            )
        return module

    @staticmethod
    def _map_scan_module_channel(element):
        channel = scan.Channel()
        channel.id = element.find("channelid").text
        return channel

    @staticmethod
    def _map_scan_module_axis(element):
        axis = scan.Axis()
        axis.id = element.find("axisid").text
        return axis
