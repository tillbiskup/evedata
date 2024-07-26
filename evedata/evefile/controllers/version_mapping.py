"""
.. include:: <isopub.txt>

*Mapping eveH5 contents to the data structures of the evedata package.*

There are different versions of the schema underlying the eveH5 files.
Hence, mapping the contents of an eveH5 file to the data model of the
evedata package requires to get the correct mapper for the specific
version. This is the typical use case for the factory pattern.

Users of the module hence will typically only obtain a
:obj:`VersionMapperFactory` object to get the correct mappers for individual
files. Furthermore, "users" basically boils down to the :class:`EveFile
<evedata.evefile.boundaries.evefile.EveFile>` class. Therefore, users of
the `evedata` package usually do not interact directly with any of the
classes provided by this module.


Overview
========

Being version agnostic with respect to eveH5 and SCML schema versions is a
central aspect of the evedata package. This requires facilities mapping
the actual eveH5 files to the data model provided by the entities
technical layer of the evefile subpackage. The :class:`File
<evedata.evefile.boundaries.evefile.File>` facade obtains
the correct :obj:`VersionMapper` object via the
:class:`VersionMapperFactory`, providing an :class:`HDF5File
<evedata.evefile.boundaries.eveh5.HDF5File>` resource object to the
factory. It is the duty of the factory to obtain the "version" attribute
from the :obj:`HDF5File <evedata.evefile.boundaries.eveh5.HDF5File>`
object (explicitly getting the attributes of the root group of the
:obj:`HDF5File <evedata.evefile.boundaries.eveh5.HDF5File>` object).


.. figure:: /uml/evedata.evefile.controllers.version_mapping.*
    :align: center

    Class hierarchy of the :mod:`evedata.evefile.controllers.version_mapping`
    module, providing the functionality to map different eveH5 file
    schemas to the data structure provided by the :class:`EveFile
    <evedata.evefile.boundaries.evefile.EveFile>` class. The factory
    will be used to get the correct mapper for a given eveH5 file.
    For each eveH5 schema version, there exists an individual
    ``VersionMapperVx`` class dealing with the version-specific mapping.
    The idea behind the ``Mapping`` class is to provide simple mappings for
    attributes and alike that need not be hard-coded and can be stored
    externally, *e.g.* in YAML files. This would make it easier to account
    for (simple) changes.


For each eveH5 schema version, there exists an individual
``VersionMapperVx`` class dealing with the version-specific mapping. That
part of the mapping common to all versions of the eveH5 schema takes place
in the :class:`VersionMapper` parent class, *e.g.* removing the chain. The
idea behind the ``Mapping`` class is to provide simple mappings for
attributes and alike that can be stored externally, *e.g.* in YAML files.
This would make it easier to account for (simple) changes.


Mapping tasks for eveH5 schema up to v7
=======================================

Given the quite different overall philosophy of the current eveH5 file
schema (up to version v7) and the data model provided by the `evedata`
package, there is a lot of tasks for the mappers to be done.

What follows is a summary of the different aspects, for the time being
*not* divided for the different formats (up to v7):

* Map attributes of ``/`` and ``/c1`` to the file metadata. |check|
* Convert monitor datasets from the ``device`` group to :obj:`MonitorData
  <evedata.evefile.entities.data.MonitorData>` objects. |check|

    * We probably need to create subclasses for the different monitor
      datasets, at least distinguishing between numeric and and
      non-numeric values.

* Map ``/c1/meta/PosCountTimer`` to :obj:`TimestampData
  <evedata.evefile.entities.data.TimestampData>` object. |check|

* Starting with eveH5 v5: Map ``/LiveComment`` to :obj:`LogMessage
  <evedata.evefile.entities.file.LogMessage>` objects. |check|

* Filter all datasets from the ``main`` section, with different goals:

    * Map array data to :obj:`ArrayChannelData
      <evedata.evefile.entities.data.ArrayChannelData>` objects (HDF5 groups
      that are *not* named ``normalized``, ``averagemeta``,
      or ``standarddev``).
    * Distinguish between single point and area data, and map area data to
      :obj:`AreaChannelData <evedata.evefile.entities.data.AreaChannelData>`
      objects.
    * Figure out which single point data have been redefined between scan
      modules, and split data accordingly. Map the data to
      :obj:`SinglePointChannelData
      <evedata.evefile.entities.data.SinglePointChannelData>`,
      :obj:`AverageChannelData
      <evedata.evefile.entities.data.AverageChannelData>`,
      and :obj:`IntervalChannelData
      <evedata.evefile.entities.data.IntervalChannelData>`, respectively.
      Take care of normalized channel data and treat them accordingly.
    * Map the additional data for average and interval channel data provided
      in the respective HDF5 groups to :obj:`AverageChannelData
      <evedata.evefile.entities.data.AverageChannelData>` and
      :obj:`IntervalChannelData
      <evedata.evefile.entities.data.IntervalChannelData>` objects,
      respectively.
    * Map normalized channel data (and the data provided in the
      respective HDF5 groups) to :obj:`NormalizedChannelData
      <evedata.evefile.entities.data.NormalizedChannelData>`.
    * Map all remaining HDF5 datasets that belong to one of the already
      mapped data objects (*i.e.*, variable options) to their respective
      attributes.
    * Map all HDF5 datasets remaining (if any) to data objects
      corresponding to their respective data type.
    * Add all data objects to the :attr:`data
      <evedata.evefile.boundaries.evefile.EveFile.data>` attribute of the
      :obj:`EveFile <evedata.evefile.boundaries.evefile.EveFile>` object.

* Filter all datasets from the ``snapshot`` section, with different goals:

    * Map all HDF5 datasets that belong to one of the data objects in the
      :attr:`data <evedata.evefile.boundaries.evefile.EveFile.data>`
      attribute of the :obj:`EveFile
      <evedata.evefile.boundaries.evefile.EveFile>` object to their respective
      attributes.
    * Map all HDF5 datasets remaining (if any) to data objects
      corresponding to their respective data type.
    * Add all data objects to the :attr:`snapshots
      <evedata.evefile.boundaries.evefile.EveFile.snapshots>` attribute of the
      :obj:`EveFile  <evedata.evefile.boundaries.evefile.EveFile>` object.


Most probably, not all these tasks can be inferred from the contents of an
eveH5 file alone. In this case, additional mapping tables, eventually
perhaps even on a per-measurement-station level, are necessary.

Other tasks not in the realm of the version mappers, but part of the
:mod:`evedata.evefile.controllers` subpackage, are:

* Separating 0D data that have been redefined within a scan (single point,
  average, interval) -- **sure about this one? see above**
* Mapping scans using the EPICS MPSKIP feature to record individual values
  for actual average detectors to :obj:`AverageChannelData
  <evedata.evefile.entities.data.AverageChannelData>` objects.


Fundamental change of eveH5 schema with v8
==========================================

It is anticipated that based on the experience with the data model
implemented within the `evedata` package, the schema of the eveH5 files
will change dramatically with the new version v8. Overarching design
principles of the schema overhaul include:

* Much more explicit markup of the device types represented by the
  individual HDF5 datasets.
* Parameters/options of devices are part of the HDF5 dataset of the
  respective device.

    * Parameters/options static within a scan module appear as attributes of
      the HDF5 datasets.
    * Parameters/options that potentially change with ech individual recorded
      data point are represented as additional columns in the HDF5 dataset.

* Removing of the chain ``c1`` that was never and will never be used.

Taken together, this restructuring of the eveH5 schema most probably means
that the mapper for v8 does not have much in common with the mappers for
the previous versions, as this is a major change.


Module documentation
====================

"""

import datetime
import logging
import sys

import evedata.evefile.entities.data
import evedata.evefile.entities.file

logger = logging.getLogger(__name__)


class VersionMapperFactory:
    """
    Factory for obtaining the correct version mapper object.

    There are different versions of the schema underlying the eveH5 files.
    Hence, mapping the contents of an eveH5 file to the data model of the
    evedata package requires to get the correct mapper for the specific
    version. This is the typical use case for the factory pattern.


    Attributes
    ----------
    eveh5 : :class:`evedata.evefile.boundaries.eveh5.HDF5File`
        Python object representation of an eveH5 file

    Raises
    ------
    ValueError
        Raised if no eveh5 object is present


    Examples
    --------
    Using the factory is pretty simple. There are actually two ways how to
    set the eveh5 attribute -- either explicitly or when calling the
    :meth:`get_mapper` method of the factory:

    .. code-block::

        factory = VersionMapperFactory()
        factory.eveh5 = eveh5_object
        mapper = factory.get_mapper()

    .. code-block::

        factory = VersionMapperFactory()
        mapper = factory.get_mapper(eveh5=eveh5_object)

    In both cases, ``mapper`` will contain the correct mapper object,
    and ``eveh5_object`` contains the Python object representation of an
    eveH5 file.

    """

    def __init__(self):
        self.eveh5 = None

    def get_mapper(self, eveh5=None):
        """
        Return the correct mapper for a given eveH5 file.

        For convenience, the returned mapper has its
        :attr:`VersionMapper.source` attribute already set to the
        ``eveh5`` object used to get the mapper for.

        Parameters
        ----------
        eveh5 : :class:`evedata.evefile.boundaries.eveh5.HDF5File`
            Python object representation of an eveH5 file

        Returns
        -------
        mapper : :class:`VersionMapper`
            Mapper used to map the eveH5 file contents to evedata structures.

        Raises
        ------
        ValueError
            Raised if no eveh5 object is present

        """
        if eveh5:
            self.eveh5 = eveh5
        if not self.eveh5:
            raise ValueError("Missing eveh5 object")
        version = self.eveh5.attributes["EVEH5Version"].split(".")[0]
        try:
            mapper = getattr(
                sys.modules[__name__], f"VersionMapperV{version}"
            )()
        except AttributeError as exc:
            raise AttributeError(f"No mapper for version {version}") from exc
        mapper.source = self.eveh5
        return mapper


class VersionMapper:
    """
    Mapper for mapping the eveH5 file contents to evedata structures.

    This is the base class for all version-dependent mappers. Given that
    there are different versions of the eveH5 schema, each version gets
    handled by a distinct mapper subclass.

    To get an object of the appropriate class, use the
    :class:`VersionMapperFactory` factory.


    Attributes
    ----------
    source : :class:`evedata.evefile.boundaries.eveh5.HDF5File`
        Python object representation of an eveH5 file

    destination : :class:`evedata.evefile.boundaries.evefile.File`
        High(er)-level evedata structure representing an eveH5 file

    Raises
    ------
    ValueError
        Raised if either source or destination are not provided


    Examples
    --------
    Although the :class:`VersionMapper` class is *not* meant to be used
    directly, its use is prototypical for all the concrete mappers:

    .. code-block::

        mapper = VersionMapper()
        mapper.map(source=eveh5, destination=evefile)

    Usually, you will obtain the correct mapper from the
    :class:`VersionMapperFactory`. In this case, the returned mapper has
    its :attr:`source` attribute already set for convenience:

    .. code-block::

        factory = VersionMapperFactory()
        mapper = factory.get_mapper(eveh5=eveh5)
        mapper.map(destination=evefile)


    """

    def __init__(self):
        self.source = None
        self.destination = None

    def map(self, source=None, destination=None):
        """
        Map the eveH5 file contents to evedata structures.

        Parameters
        ----------
        source : :class:`evedata.evefile.boundaries.eveh5.HDF5File`
            Python object representation of an eveH5 file

        destination : :class:`evedata.evefile.boundaries.evefile.File`
            High(er)-level evedata structure representing an eveH5 file

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

    @staticmethod
    def get_hdf5_dataset_importer(dataset=None, mapping=None):
        """
        Get an importer object for HDF5 datasets with properties set.

        Data are loaded on demand, not already when initially loading the
        eveH5 file. Hence, the need for a mechanism to provide the relevant
        information where to get the relevant data from and how. Different
        versions of the underlying eveH5 schema differ even in whether all
        data belonging to one :obj:`Data` object are located in one HDF5
        dataset or spread over multiple HDF5 datasets. In the latter case,
        individual importers are necessary for the separate HDF5 datasets.

        As the :class:`VersionMapper` class deals with each HDF5 dataset
        individually, some fundamental settings for the
        :class:`HDF5DataImporter
        <evedata.evefile.entities.data.HDF5DataImporter>` are readily
        available. Additionally, the ``mapping`` parameter provides the
        information necessary to create the correct information in the
        :attr:`HDF5DataImporter.mapping
        <evedata.evefile.entities.data.HDF5DataImporter.mapping>` attribute.

        .. important::
            The keys in the dictionary provided via the ``mapping``
            parameter are **integers, not strings**, as usual for dictionaries.
            This allows to directly use the keys for indexing the tuple
            returned by ``numpy.dtype.names``. To be explicit, here is an
            example:

            .. code-block::

                dataset = HDF5Dataset()
                importer_mapping = {
                    0: "milliseconds",
                    1: "data",
                }
                importer = self.get_hdf5_dataset_importer(
                    dataset=dataset, mapping=importer_mapping
                )

            Of course, in reality you will not just instantiate an empty
            :obj:`HDF5Dataset <evedata.evefile.boundaries.eveh5.HDF5Dataset>`
            object, but have one available within your mapper.


        Parameters
        ----------
        dataset : :class:`evedata.evefile.boundaries.eveh5.HDF5Dataset`
            Representation of an HDF5 dataset.

        mapping : :class:`dict`
            Table for mapping HDF5 dataset columns to data class attributes.

            **Note**: The keys in this dictionary are *integers*,
            not strings, as usual for dictionaries. This allows to directly
            use the keys for indexing the tuple returned by
            ``numpy.dtype.names``.

        Returns
        -------
        importer : :class:`evedata.evefile.entities.data.HDF5DataImporter`
            HDF5 dataset importer

        """
        if mapping is None:
            mapping = {}
        importer = evedata.evefile.entities.data.HDF5DataImporter()
        importer.source = dataset.filename
        importer.item = dataset.name
        for key, value in mapping.items():
            importer.mapping[dataset.dtype.names[key]] = value
        return importer

    def _map(self):
        self._map_file_metadata()
        self._map_monitor_datasets()
        self._map_timestamp_dataset()

    def _check_prerequisites(self):
        if not self.source:
            raise ValueError("Missing source to map from.")
        if not self.destination:
            raise ValueError("Missing destination to map to.")

    def _map_file_metadata(self):
        pass

    def _map_monitor_datasets(self):
        pass

    def _map_timestamp_dataset(self):
        pass


class VersionMapperV5(VersionMapper):
    """
    Mapper for mapping eveH5 v5 file contents to evedata structures.

    More description comes here...

    .. important::
        EveH5 files of version v5 and earlier do *not* contain a date and
        time for the end of the measurement. Hence, the corresponding
        attribute :attr:`File.metadata.end
        <evedata.evefile.entities.file.Metadata.end>` is set to the UNIX
        start date (1970-01-01T00:00:00). Thus, with these files,
        it is *not* possible to autamatically calculate the duration of
        the measurement.


    Attributes
    ----------
    source : :class:`evedata.evefile.boundaries.eveh5.HDF5File`
        Python object representation of an eveH5 file

    destination : :class:`evedata.evefile.boundaries.evefile.File`
        High(er)-level evedata structure representing an eveH5 file

    Raises
    ------
    ValueError
        Raised if either source or destination are not provided


    Examples
    --------
    Mapping a given eveH5 file to the evedata structures is the same for
    each of the mappers:

    .. code-block::

        mapper = VersionMapperV5()
        mapper.map(source=eveh5, destination=evefile)

    Usually, you will obtain the correct mapper from the
    :class:`VersionMapperFactory`. In this case, the returned mapper has
    its :attr:`source` attribute already set for convenience:

    .. code-block::

        factory = VersionMapperFactory()
        mapper = factory.get_mapper(eveh5=eveh5)
        mapper.map(destination=evefile)

    """

    def _map(self):
        super()._map()
        self._map_log_messages()

    def _map_file_metadata(self):
        root_mappings = {
            "eveh5_version": "EVEH5Version",
            "eve_version": "Version",
            "xml_version": "XMLversion",
            "measurement_station": "Location",
            "description": "Comment",
        }
        for key, value in root_mappings.items():
            setattr(
                self.destination.metadata, key, self.source.attributes[value]
            )
        c1_mappings = {
            "preferred_axis": "preferredAxis",
            "preferred_channel": "preferredChannel",
            "preferred_normalisation_channel": "preferredNormalizationChannel",
        }
        for key, value in c1_mappings.items():
            if value in self.source.c1.attributes:
                setattr(
                    self.destination.metadata,
                    key,
                    self.source.c1.attributes[value],
                )
        if "StartTimeISO" not in self.source.attributes:
            self.destination.metadata.start = datetime.datetime.strptime(
                f"{self.source.attributes['StartDate']} "
                f"{self.source.attributes['StartTime']}",
                "%d.%m.%Y %H:%M:%S",
            )
            self.destination.metadata.end = datetime.datetime(1970, 1, 1)

    def _map_monitor_datasets(self):
        if not hasattr(self.source, "device"):
            return
        for monitor in self.source.device:
            dataset = evedata.evefile.entities.data.MonitorData()
            importer_mapping = {
                0: "milliseconds",
                1: "data",
            }
            importer = self.get_hdf5_dataset_importer(
                dataset=monitor, mapping=importer_mapping
            )
            dataset.importer.append(importer)
            dataset.metadata.id = monitor.name.split("/")[-1]  # noqa
            dataset.metadata.name = monitor.attributes["Name"]
            dataset.metadata.access_mode, dataset.metadata.pv = (  # noqa
                monitor.attributes
            )["Access"].split(":", maxsplit=1)
            self.destination.monitors.append(dataset)

    def _map_timestamp_dataset(self):
        timestampdata = self.source.c1.meta.PosCountTimer
        dataset = evedata.evefile.entities.data.TimestampData()
        importer_mapping = {
            0: "positions",
            1: "data",
        }
        importer = self.get_hdf5_dataset_importer(
            dataset=timestampdata, mapping=importer_mapping
        )
        dataset.importer.append(importer)
        dataset.metadata.unit = timestampdata.attributes["Unit"]
        self.destination.position_timestamps = dataset

    def _map_log_messages(self):
        if not hasattr(self.source, "LiveComment"):
            return
        self.source.LiveComment.get_data()
        for message in self.source.LiveComment.data:
            log_message = evedata.evefile.entities.file.LogMessage()
            log_message.from_string(message)
            self.destination.log_messages.append(log_message)


class VersionMapperV6(VersionMapperV5):
    """
    Mapper for mapping eveH5 v6 file contents to evedata structures.

    The only difference to the previous version v5: Times for start *and
    now even end* of a measurement are available and are mapped
    as :obj:`datetime.datetime` objects onto the
    :attr:`File.metadata.start
    <evedata.evefile.entities.file.Metadata.start>` and
    :attr:`File.metadata.end <evedata.evefile.entities.file.Metadata.end>`
    attributes, respectively.

    .. note::
        Previous to v6 eveH5 files, no end date/time of the measurement
        was available, hence no duration of the measurement can be
        calculated.

    Attributes
    ----------
    source : :class:`evedata.evefile.boundaries.eveh5.HDF5File`
        Python object representation of an eveH5 file

    destination : :class:`evedata.evefile.boundaries.evefile.File`
        High(er)-level evedata structure representing an eveH5 file

    Raises
    ------
    ValueError
        Raised if either source or destination are not provided


    Examples
    --------
    Mapping a given eveH5 file to the evedata structures is the same for
    each of the mappers:

    .. code-block::

        mapper = VersionMapperV6()
        mapper.map(source=eveh5, destination=evefile)

    Usually, you will obtain the correct mapper from the
    :class:`VersionMapperFactory`. In this case, the returned mapper has
    its :attr:`source` attribute already set for convenience:

    .. code-block::

        factory = VersionMapperFactory()
        mapper = factory.get_mapper(eveh5=eveh5)
        mapper.map(destination=evefile)

    """

    def _map_file_metadata(self):
        super()._map_file_metadata()
        date_mappings = {
            "start": "StartTimeISO",
            "end": "EndTimeISO",
        }
        for key, value in date_mappings.items():
            setattr(
                self.destination.metadata,
                key,
                datetime.datetime.fromisoformat(
                    self.source.attributes[value]
                ),
            )


class VersionMapperV7(VersionMapperV6):
    """
    Mapper for mapping eveH5 v7 file contents to evedata structures.

    The only difference to the previous version v6: the attribute
    ``Simulation`` has beem added on the file root level and is mapped
    as a Boolean value onto the :attr:`File.metadata.simulation
    <evedata.evefile.entities.file.Metadata.simulation>` attribute.

    Attributes
    ----------
    source : :class:`evedata.evefile.boundaries.eveh5.HDF5File`
        Python object representation of an eveH5 file

    destination : :class:`evedata.evefile.boundaries.evefile.File`
        High(er)-level evedata structure representing an eveH5 file

    Raises
    ------
    ValueError
        Raised if either source or destination are not provided


    Examples
    --------
    Mapping a given eveH5 file to the evedata structures is the same for
    each of the mappers:

    .. code-block::

        mapper = VersionMapperV7()
        mapper.map(source=eveh5, destination=evefile)

    Usually, you will obtain the correct mapper from the
    :class:`VersionMapperFactory`. In this case, the returned mapper has
    its :attr:`source` attribute already set for convenience:

    .. code-block::

        factory = VersionMapperFactory()
        mapper = factory.get_mapper(eveh5=eveh5)
        mapper.map(destination=evefile)

    """

    def _map_file_metadata(self):
        super()._map_file_metadata()
        if self.source.attributes["Simulation"] == "yes":
            self.destination.metadata.simulation = True
