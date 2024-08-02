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
      datasets, at least distinguishing between numeric and non-numeric
      values.

* Map ``/c1/meta/PosCountTimer`` to :obj:`TimestampData
  <evedata.evefile.entities.data.TimestampData>` object. |check|

* Starting with eveH5 v5: Map ``/LiveComment`` to :obj:`LogMessage
  <evedata.evefile.entities.file.LogMessage>` objects. |check|

* Filter all datasets from the ``main`` section, with different goals:

    * Map array data to :obj:`ArrayChannelData
      <evedata.evefile.entities.data.ArrayChannelData>` objects (HDF5 groups
      having an attribute ``DeviceType`` set to ``Channel``). |check|

      * Distinguish between MCA and scope data (at least). |cross|
      * Map additional datasets in main section (and snapshot). |check|

    * Map all axis datasets to :obj:`AxisData
      <evedata.evefile.entities.data.AxisData>` objects. |check|

      * How to distinguish between axes with and without encoders? |cross|
      * How to deal with pseudo-axes used as options in channel datasets? Do
        we need to deal with axes later? |cross|

    * Distinguish between single point and area data, and map area data to
      :obj:`AreaChannelData <evedata.evefile.entities.data.AreaChannelData>`
      objects. (|check|)

      * Distinguish between scientific and sample cameras. |check|
      * Which dataset is the "main" dataset for scientific cameras? |cross|
      * Map sample camera datasets. |check|

    * Figure out which single point data have been redefined between scan
      modules, and split data accordingly. Map the data to
      :obj:`SinglePointChannelData
      <evedata.evefile.entities.data.SinglePointChannelData>`,
      :obj:`AverageChannelData
      <evedata.evefile.entities.data.AverageChannelData>`,
      and :obj:`IntervalChannelData
      <evedata.evefile.entities.data.IntervalChannelData>`, respectively.

      Hint: Getting the shape of an HDF5 dataset is a cheap operation and
      does *not* require reading the actual data, as the information is
      contained in the metadata of the HDF5 dataset. This should allow for
      additional checking whether a dataset has been redefined.

      If the number of (the sum of) positions differ, the channel has been
      redefined. However, the average or interval settings may have
      changed between scan modules as well, and this can only be figured
      out by actually reading the data. How to handle this situation?
      Split datasets only upon reading the data, if necessary?

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


.. admonition:: Questions to address

    * How were the log messages/live comments saved before v5?


Notes on mapping MCA datasets
-----------------------------

MCA data themselves are stored as single dataset per spectrum in an HDF5
group, and such group can be uniquely identified by having attributes,
and an attribute ``DeviceType`` set to ``Channel``. Furthermore, he PV of a
given MCA can be inferred from the ``Access`` attribute of the HDF5 group.

Why not using the name of the MCA HDF5 group for obtaining the PV? The
group typically has ``chan1`` added without separator straight to the PV
name, but the ``Access`` attribute reveals the full PV with added ``.VAL``
attribute.

As all additional options follow directly the `EPICS MCA record
<https://millenia.cars.aps.anl.gov/software/epics/mcaRecord.html>`_, and the
dataset names can be mapped to the PVs of the MCA record, a direct mapping
of datasets in the main and snapshot sections could be carried out. In
this case, it seems not necessary to explicitly check the PV names of the
individual datasets, as the datasets all have the PV attributes as their
last part. Note that there are different and variable numbers of ROI
channels and corresponding datasets available (up to 32 according to the
EPICS MCA record, but probably <10 at PTB).

How to map the values of the snapshot section to the options of the
:class:`MCAChannelData <evedata.evefile.entities.data.MCAChannelData>` and
:class:`MCAChannelROIData <evedata.evefile.entities.data.MCAChannelROIData>`
classes? Check whether they have changed, and if not, use the first value?
How to deal with the situation where the values in the snapshot dataset
*have changed*? This would most probably mean that the MCA has been used
with different settings in different scan modules of the scan and would
need to be split into different datasets. However, this is only accessible
once the data have been read. Again, two scenarios would be possible: (i)
postpone the whole procedure to the data import in the
:class:`MCAChannelData <evedata.evefile.entities.data.MCAChannelData>`
class, or (ii) load the snapshot data during mapping, as this should
usually only be small datasets, and deal with the differing values already
here.


Notes on mapping camera datasets
--------------------------------

Most probably, camera datasets can be identified by having (at least) two
colons in their name. Furthermore, the second-right part between two
colons should be one of ``TIFF1`` or ``cam1`` for scientific cameras and
``uvc1`` for sample cameras.

Having once identified one dataset belonging to a camera, all related
datasets can be identified by the identical part before the first colon.
Note that this criterion is *not* valid for other datasets not belonging
to cameras.

Identifying the "main" dataset for a camera is another task, as over time,
this has changed as well, from storing image numbers to storing (full)
filenames.

How to map the values of the snapshot section to the respective camera
classes? The same ideas as for the MCA datasets apply here, too - and
probably more generally for all snapshot datasets, at least those where
corresponding devices exist in the main section.


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

from collections.abc import Iterable
import datetime
import logging
import sys

import numpy as np

import evedata.evefile.entities.data
import evedata.evefile.entities.file
import evedata.evefile.entities.metadata

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

    datasets2map_in_main : :class:`list`
        Names of the datasets in the main section not yet mapped.

        In order to not have to check all datasets several times,
        this list contains only those datasets not yet mapped. Hence,
        every private mapping method removes those names from the list it
        handled successfully.

    datasets2map_in_snapshot : :class:`list`
        Names of the datasets in the snapshot section not yet mapped.

        In order to not have to check all datasets several times,
        this list contains only those datasets not yet mapped. Hence,
        every private mapping method removes those names from the list it
        handled successfully.

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
        self.datasets2map_in_main = []
        self.datasets2map_in_snapshot = []
        self._main_group = None
        self._snapshot_group = None

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
        self._set_dataset_names()
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
            parameter are **integers, not strings**, as usual for
            dictionaries. This allows to directly use the keys for
            indexing the tuple returned by ``numpy.dtype.names``. To be
            explicit, here is an example:

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
            Table mapping HDF5 dataset columns to data class attributes.

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

    @staticmethod
    def get_dataset_name(dataset=None):
        """
        Get the name of an HDF5 dataset.

        The name here refers to the last part of the path within the HDF5
        file, *i.e.* the part after the last slash.


        Parameters
        ----------
        dataset : :class:`evedata.evefile.boundaries.eveh5.HDF5Dataset`
            Representation of an HDF5 dataset.

        Returns
        -------
        name : :class:`str`
            Name of the HDF5 dataset

        """
        return dataset.name.rsplit("/", maxsplit=1)[1]

    @staticmethod
    def set_basic_metadata(hdf5_item=None, dataset=None):
        """
        Set the basic metadata of a dataset from an HDF5 item.

        The metadata attributes ``id``, ``name``, ``access_mode``,
        and ``pv`` are set.

        Parameters
        ----------
        hdf5_item : :class:`evedata.evefile.boundaries.eveh5.HDF5Item`
            Representation of an HDF5 item.

        dataset : :class:`evedata.evefile.entities.data.Data`
            Data object the metadata should be set for

        """
        dataset.metadata.id = hdf5_item.name.split("/")[-1]  # noqa
        dataset.metadata.name = hdf5_item.attributes["Name"]
        dataset.metadata.access_mode, dataset.metadata.pv = (  # noqa
            hdf5_item.attributes
        )["Access"].split(":", maxsplit=1)

    def _check_prerequisites(self):
        if not self.source:
            raise ValueError("Missing source to map from.")
        if not self.destination:
            raise ValueError("Missing destination to map to.")

    def _set_dataset_names(self):
        pass

    def _map(self):
        self._map_file_metadata()
        self._map_monitor_datasets()
        self._map_timestamp_dataset()
        # Note: The sequence of method calls can be crucial, as the mapper
        #       contains a list of datasets still to be mapped, and each
        #       mapped dataset is removed from this list.
        self._map_array_datasets()
        self._map_axis_datasets()
        self._map_area_datasets()
        self._map_0d_datasets()
        self._map_snapshot_datasets()

    def _map_file_metadata(self):
        pass

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
            self.set_basic_metadata(hdf5_item=monitor, dataset=dataset)
            self.destination.monitors[self.get_dataset_name(monitor)] = (
                dataset
            )

    def _map_timestamp_dataset(self):
        pass

    def _map_array_datasets(self):
        mapped_datasets = []
        for name in self.datasets2map_in_main:
            item = getattr(self._main_group, name)
            # noinspection PyUnresolvedReferences
            if isinstance(item, Iterable) and "DeviceType" in item.attributes:
                # noinspection PyTypeChecker
                # TODO: Distinguish between MCA and other array detectors
                self._map_mca_dataset(hdf5_group=item)
                mapped_datasets.append(self.get_dataset_name(item))
        for item in mapped_datasets:
            self.datasets2map_in_main.remove(item)

    def _map_array_dataset(self, hdf5_group=None):
        pass

    def _map_mca_dataset(self, hdf5_group=None):
        pass

    def _map_axis_datasets(self):
        mapped_datasets = []
        for name in self.datasets2map_in_main:
            item = getattr(self._main_group, name)
            if item.attributes["DeviceType"] == "Axis":
                self._map_axis_dataset(hdf5_dataset=item)
                mapped_datasets.append(self.get_dataset_name(item))
        for item in mapped_datasets:
            self.datasets2map_in_main.remove(item)

    def _map_axis_dataset(self, hdf5_dataset=None):
        # TODO: Check whether axis has an encoder (how? mapping?)
        dataset = evedata.evefile.entities.data.NonencodedAxisData()
        importer_mapping = {
            0: "positions",
            1: "data",
        }
        importer = self.get_hdf5_dataset_importer(
            dataset=hdf5_dataset, mapping=importer_mapping
        )
        dataset.importer.append(importer)
        self.set_basic_metadata(hdf5_item=hdf5_dataset, dataset=dataset)
        self.destination.data[self.get_dataset_name(hdf5_dataset)] = dataset

    def _map_area_datasets(self):
        scientific_cameras = self._get_camera_datasets(camera="cam1")
        for scientific_camera in scientific_cameras:
            self._map_scientific_camera(camera=scientific_camera)
        sample_cameras = self._get_camera_datasets(camera="uvc1")
        for sample_camera in sample_cameras:
            self._map_sample_camera(camera=sample_camera)

    def _map_scientific_camera(self, camera=""):
        pass

    def _map_sample_camera(self, camera=""):
        pass

    def _get_camera_datasets(self, camera="cam1"):
        """
        Obtain camera names from a list of dataset names.

        Datasets in eveH5 files are usually named according to the EPICS PV.
        Cameras seem to be the only PV names with at least two colons.
        Furthermore, there are signalling parts of the PV, identifying the
        PV as camera, see the ``camera`` parameter below.

        The camera name used to identify all datasets belonging to this
        camera is the part before the second-last colon. Note that camera
        names can contain colons themselves, hence looking from the right is
        crucial.

        Parameters
        ----------
        camera : :class:`str`
            Second-last part of the PV name identifying the camera type

            "cam1" identifies a scientific camera, while "uvc1" identifies a
            sample camera.

        Returns
        -------
        camera_names : :class:`set`
            Names of the identified cameras.

        """
        camera_names = (
            item.rsplit(":", maxsplit=2)[0]
            for item in self.datasets2map_in_main
            if (item.count(":") > 1 and item.rsplit(":")[-2] in [camera])
        )
        return camera_names

    def _map_0d_datasets(self):
        pass

    def _map_snapshot_datasets(self):
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
        it is *not* possible to automatically calculate the duration of
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

    def _set_dataset_names(self):
        # TODO: Move up to VersionMapperV4
        if hasattr(self.source.c1, "main"):
            self._main_group = self.source.c1.main
            self.datasets2map_in_main = [
                self.get_dataset_name(item) for item in self.source.c1.main
            ]
        if hasattr(self.source.c1, "snapshot"):
            self._snapshot_group = self.source.c1.snapshot
            self.datasets2map_in_snapshot = [
                self.get_dataset_name(item)
                for item in self.source.c1.snapshot
            ]

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

    def _map_timestamp_dataset(self):
        # TODO: Move up to VersionMapperV2 (at least the earliest one)
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

    def _map_mca_dataset(self, hdf5_group=None):
        # TODO: Move up to VersionMapperV2 (at least the earliest one)
        dataset = evedata.evefile.entities.data.MCAChannelData()
        self.set_basic_metadata(hdf5_item=hdf5_group, dataset=dataset)
        self._mca_dataset_set_data(dataset=dataset, hdf5_group=hdf5_group)
        self._mca_dataset_set_options_in_main(dataset=dataset)
        self._mca_dataset_set_options_in_snapshot(dataset=dataset)
        self.destination.data[self.get_dataset_name(hdf5_group)] = dataset

    def _mca_dataset_set_data(self, dataset=None, hdf5_group=None):
        # Create positions vector and add it (needs to be done here)
        positions = [int(i) for i in hdf5_group.item_names()]
        dataset.positions = np.asarray(positions, dtype="i4")
        # Create and add importers for each individual array
        for position in hdf5_group:
            importer_mapping = {
                0: "data",
            }
            importer = self.get_hdf5_dataset_importer(
                dataset=position, mapping=importer_mapping
            )
            dataset.importer.append(importer)

    def _mca_dataset_set_options_in_main(self, dataset=None):
        # Handle options in main section
        pv_base = dataset.metadata.pv.split(".")[0]
        options_in_main = [
            item
            for item in self.datasets2map_in_main
            if item.startswith(f"{pv_base}.")
        ]
        options_in_main.sort()
        for option in options_in_main:
            mapping_table = {
                "ELTM": "life_time",
                "ERTM": "real_time",
                "PLTM": "preset_life_time",
                "PRTM": "preset_real_time",
            }
            attribute = option.split(".")[-1]
            if attribute in mapping_table:
                importer_mapping = {1: mapping_table[attribute]}
                importer = self.get_hdf5_dataset_importer(
                    dataset=getattr(self.source.c1.main, option),
                    mapping=importer_mapping,
                )
                dataset.importer.append(importer)
                self.datasets2map_in_main.remove(option)
            if attribute.startswith("R"):
                roi = evedata.evefile.entities.data.MCAChannelROIData()
                importer_mapping = {
                    0: "positions",
                    1: "data",
                }
                importer = self.get_hdf5_dataset_importer(
                    dataset=getattr(self.source.c1.main, option),
                    mapping=importer_mapping,
                )
                roi.importer.append(importer)
                dataset.roi.append(roi)
                self.datasets2map_in_main.remove(option)

    def _mca_dataset_set_options_in_snapshot(self, dataset):
        # Handle options in snapshot section
        pv_base = dataset.metadata.pv.split(".")[0]
        options_in_snapshot = [
            item
            for item in self.datasets2map_in_snapshot
            if item.startswith(f"{pv_base}.")
        ]
        options_in_snapshot.sort()
        calibration_options = [
            item.split(".")[-1]
            for item in options_in_snapshot
            if item.split(".")[-1].startswith("CAL")
        ]
        if calibration_options:
            mapping_table = {
                "CALO": "offset",
                "CALQ": "quadratic",
                "CALS": "slope",
            }
            calibration = (
                evedata.evefile.entities.metadata.MCAChannelCalibration()
            )
            for option in calibration_options:
                # HDF5 datasets are read directly and only the first data
                # point taken from each, as calibration cannot sensibly
                # change between scan modules of a scan.
                name = ".".join([pv_base, option])
                hdf5_dataset = getattr(self.source.c1.snapshot, name)
                hdf5_dataset.get_data()
                setattr(
                    calibration,
                    mapping_table[option],
                    hdf5_dataset.data[name][0],
                )
                options_in_snapshot.remove(name)
                self.datasets2map_in_snapshot.remove(name)
            dataset.metadata.calibration = calibration
        roi_options = [
            item.split(".")[-1]
            for item in options_in_snapshot
            if item.split(".")[-1].startswith("R")
        ]
        if roi_options:
            n_rois = len(set(int(item[1:-2]) for item in roi_options))
            for idx in range(n_rois):
                if len(dataset.roi) < idx:
                    roi = evedata.evefile.entities.data.MCAChannelROIData()
                    dataset.roi.append(roi)
                else:
                    roi = dataset.roi[idx]
                name = ".".join([pv_base, f"R{idx}LO"])
                hdf5_dataset = getattr(self.source.c1.snapshot, name)
                hdf5_dataset.get_data()
                roi.marker[0] = hdf5_dataset.data[name][0]
                name = ".".join([pv_base, f"R{idx}HI"])
                hdf5_dataset = getattr(self.source.c1.snapshot, name)
                hdf5_dataset.get_data()
                roi.marker[1] = hdf5_dataset.data[name][0]
                name = ".".join([pv_base, f"R{idx}NM"])
                hdf5_dataset = getattr(self.source.c1.snapshot, name)
                hdf5_dataset.get_data()
                roi.label = hdf5_dataset.data[name][0].decode()
            for option in roi_options:
                name = ".".join([pv_base, option])
                options_in_snapshot.remove(name)
                self.datasets2map_in_snapshot.remove(name)
        for option in options_in_snapshot:
            logger.warning("Option %s unmapped", option.split(".")[-1])
            self.datasets2map_in_snapshot.remove(option)

    def _map_scientific_camera(self, camera=""):
        dataset = evedata.evefile.entities.data.ScientificCameraData()
        camera_datasets_in_main = [
            item
            for item in self.datasets2map_in_main
            if item.startswith(camera)
        ]
        # TODO: Add importer for "main" dataset - whatever that is.
        # TODO: Deal with attributes for metadata
        # TODO: Deal with additional options in dataset
        n_roi = len(
            set(
                item.rsplit(":", maxsplit=2)[-2]
                for item in camera_datasets_in_main
                if "ROI" in item
            )
        )
        for idx in range(n_roi):
            roi = evedata.evefile.entities.data.ScientificCameraROIData()
            roi_pvs = ["MinX_RBV", "MinY_RBV", "SizeX_RBV", "SizeY_RBV"]
            marker = []
            for roi_pv in roi_pvs:
                name = f"{camera}:ROI{idx+1}:{roi_pv}"
                hdf5_dataset = getattr(self.source.c1.main, name)
                hdf5_dataset.get_data()
                marker.append(hdf5_dataset.data[name][0])
                self.datasets2map_in_main.remove(name)
                camera_datasets_in_main.remove(name)
            roi.marker = np.asarray(marker)
            dataset.roi.append(roi)
        n_statistics = len(
            set(
                item.rsplit(":", maxsplit=2)[-2]
                for item in camera_datasets_in_main
                if "Stats" in item
            )
        )
        for idx in range(n_statistics):
            statistics = (
                evedata.evefile.entities.data.ScientificCameraStatisticsData()
            )
            dataset.statistics.append(statistics)
            mapping_table = {
                "BgdWidth_RBV": "background_width",
                "CentroidThreshold_RBV": "centroid_threshold",
                "CentroidX_RBV": "centroid_x",
                "CentroidY_RBV": "centroid_y",
                "MaxValue_RBV": "max_value",
                "MaxX_RBV": "max_x",
                "MaxY_RBV": "max_y",
                "MeanValue_RBV": "mean_value",
                "MinValue_RBV": "min_value",
                "MinX_RBV": "min_x",
                "MinY_RBV": "min_y",
                "SigmaXY_RBV": "sigma_xy",
                "SigmaX_RBV": "sigma_x",
                "SigmaY_RBV": "sigma_y",
                "Sigma_RBV": "sigma",
                "Total_RBV": "total",
                "Net_RBV": "net",
                "chan1": "data",
            }
            for pv_name, attribute in mapping_table.items():
                dataset_name = f"{camera}:Stats{idx+1}:{pv_name}"
                if dataset_name in camera_datasets_in_main:
                    importer_mapping = {1: attribute}
                    importer = self.get_hdf5_dataset_importer(
                        dataset=getattr(self.source.c1.main, dataset_name),
                        mapping=importer_mapping,
                    )
                    dataset.statistics[idx].importer.append(importer)
                    self.datasets2map_in_main.remove(dataset_name)
                    camera_datasets_in_main.remove(dataset_name)
        for name in camera_datasets_in_main:
            self.datasets2map_in_main.remove(name)
        camera_datasets_in_snapshot = [
            item
            for item in self.datasets2map_in_snapshot
            if item.startswith(camera)
        ]
        for name in camera_datasets_in_snapshot:
            self.datasets2map_in_snapshot.remove(name)
        self.destination.data[camera] = dataset

    def _map_sample_camera(self, camera=""):
        dataset = evedata.evefile.entities.data.SampleCameraData()
        self._sample_camera_set_data(camera=camera, dataset=dataset)
        camera_datasets_in_snapshot = [
            item
            for item in self.datasets2map_in_snapshot
            if item.startswith(camera)
        ]
        self._sample_camera_set_options(
            camera=camera,
            datasets=camera_datasets_in_snapshot,
            dataset=dataset,
        )
        camera_datasets_in_main = [
            item
            for item in self.datasets2map_in_main
            if item.startswith(camera)
        ]
        self._sample_camera_set_options(
            camera=camera,
            datasets=camera_datasets_in_main,
            dataset=dataset,
        )
        self.destination.data[camera] = dataset

    def _sample_camera_set_data(self, camera="", dataset=None):
        hdf5_name = f"{camera}:uvc1:chan1"
        importer_mapping = {
            0: "positions",
            1: "data",
        }
        importer = self.get_hdf5_dataset_importer(
            dataset=getattr(self.source.c1.main, hdf5_name),
            mapping=importer_mapping,
        )
        dataset.importer.append(importer)
        self.datasets2map_in_main.remove(hdf5_name)

    def _sample_camera_set_options(
        self, camera="", datasets=None, dataset=None
    ):
        mapping_table = {
            "BeamX": "beam_x",
            "BeamY": "beam_y",
            "BeamXfrac": "fractional_x_position",
            "BeamYfrac": "fractional_y_position",
            "SkipFrames": "skip_frames",
            "AvgFrames": "average_frames",
        }
        for name in datasets:
            option = name.rsplit(":")[-1]
            if option in mapping_table:
                if name in self.datasets2map_in_main:
                    hdf5_dataset = getattr(self.source.c1.main, name)
                else:
                    hdf5_dataset = getattr(self.source.c1.snapshot, name)
                hdf5_dataset.get_data()
                setattr(
                    dataset.metadata,
                    mapping_table[option],
                    hdf5_dataset.data[name][0],
                )
                if name in self.datasets2map_in_main:
                    self.datasets2map_in_main.remove(name)
                if name in self.datasets2map_in_snapshot:
                    self.datasets2map_in_snapshot.remove(name)
            else:
                logger.info(
                    "Option %s unmapped for camera %s", option, camera
                )
                if name in self.datasets2map_in_main:
                    self.datasets2map_in_main.remove(name)
                if name in self.datasets2map_in_snapshot:
                    self.datasets2map_in_snapshot.remove(name)

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
