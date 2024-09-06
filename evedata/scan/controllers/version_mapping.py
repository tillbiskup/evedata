"""
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
    ``VersionMapperVx_y`` class dealing with the version-specific mapping.
    The idea behind the ``Mapping`` class is to provide simple mappings for
    attributes and alike that need not be hard-coded and can be stored
    externally, *e.g.* in YAML files. This would make it easier to account
    for (simple) changes.


For each SCML schema version, there exists an individual
``VersionMapperVx_y`` class dealing with the version-specific mapping. That
part of the mapping common to all versions of the SCML schema takes place
in the :class:`VersionMapper` parent class. The idea behind the ``Mapping``
class is to provide simple mappings for attributes and alike that can be
stored externally, *e.g.* in YAML files. This would make it easier to
account for (simple) changes.


Mapping tasks for SCML schema up to v9.2
========================================

TBD


Fundamental change of SCML schema with v10
==========================================

TBD


Module documentation
====================

"""

import logging
import sys

from evedata.scan.entities.scan import ScanModule

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

            Can alternatively be an :obj:`evedata.scan.boundaries.scan.Station`
            object.

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
        for module in self.source.scan_modules:
            self.destination.scan.scan_modules[int(module.get("id"))] = (
                self._map_scan_module(module)
            )

    def _map_scan_module(self, element=None):
        # TODO: Distinguish types of scan modules and map appropriately
        module = ScanModule()
        module.name = element.find("name").text
        module.parent = int(element.find("parent").text)
        try:
            module.appended = int(element.find("appended").text)
        except AttributeError:
            pass
        return module
