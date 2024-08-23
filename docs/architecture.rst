============
Architecture
============

Each software has some kind of architecture, and this is the place to describe it in broad terms, to make it easier for developers to get around the code. Following the scheme of a layered architecture as featured by the "Clean Architecture" (Robert Martin) or the "hexagonal architecture", alternatively known as "ports and adapters" (Alistair Cockburn), the different layers are described successively from the inside out.

Just to make matters a bit more interesting, the evedata package has basically **two disjunct interfaces**: one towards the data file format (eveH5), the other towards the users of the actual data, *e.g.* the ``radiometry`` and ``evedataviewer`` packages. See :numref:`Fig. %s <fig-uml_evedata_in_context>` for a first overview.


.. _fig-uml_evedata_in_context:

.. figure:: uml/evedata-in-context.*
    :align: center

    The two interfaces of the evedata package: eveH5 is the persistence layer of the recorded data and metadata, and evedataviewer and radiometry are Python packages for graphically displaying and processing and analysing these data, respectively. Most people concerned with the actual data will either use evedataviewer or the radiometry package, but not evedata directly.


An alternative view that may be more helpful in the long run, leading to a better overall architecture, rests on the distinction between two dimensions of layers: functional and technical. While for long time, the first line of organisation in code was technical layers, grouping software into functional blocks (packages or whatever the name) that are each independently technically layered preserves the concepts of the application much better. A first idea for the evedata package is presented in :numref:`Fig. %s <fig-architecture_layers_technical_functional>`.

.. _fig-architecture_layers_technical_functional:

.. figure:: images/architecture-layers-technical-functional.*
    :align: center

    A two-dimensional view of the architecture, with technical and functional layers. The primary line of organisation in the code, according to different authors, should be the functional layers or packages, and each of the functional blocks should be organised into three technical layers: boundaries, controllers, entities. The idea and name of these three technical layers goes back to Ivar Jacobson (1992). The boundaries (sometimes called interfaces) contain two different kinds of elements: facades and resources. While resources are typically concerned with the persistence layer and similar things, facades are the user-facing elements providing access to the underlying entities and controllers.


There are three functional layers with dependencies in one direction: measurement, evefile, and scan. Each of the functional layers is divided into three technical layers, *i.e.* boundaries ("interfaces"), controllers, and entities (BCE). The boundaries layer contains both, the "interfaces" ("adapters") pointing to the user (facades) and those pointing to the underlying infrastructure (resources). Here, "user" can be either actual human users or other functional layers. This means that high-level functional layers shall not directly depend on elements of the lower technical layers of lower-level functional layers, but use the respective facades of the lower-level functional layers. As an example for the ``evedata`` package: the measurement functional layer uses the evefile and scan facades of the evefile and scan functional layers.


A corresponding UML package diagram for :numref:`Fig. %s <fig-architecture_layers_technical_functional>` is shown in the figure below. Here, only the dependencies *within* the individual functional layers are shown, not the dependencies *between* the functional layers. The latter proceed from left to right: measurement > evefile > scan.

.. _fig-uml_evedata:

.. figure:: uml/evedata-functional-layers.*
    :align: center

    An UML package diagram of the evedata package following the organisation in functional layers that each contain three technical layers, as shown in :numref:`Fig. %s <fig-architecture_layers_technical_functional>`. To hide the names of the technical layers from the user, one could think of importing the relevant classes (basically the facades) in the ``__init__.py`` files of the respective top-level functional packages.


For each of the functional layers, the corresponding technical layers are described below. Deviating from the direction of dependencies as shown in :numref:`Fig. %s <fig-architecture_layers_technical_functional>`, we start with the evefile functional layer, and for each of the layers we start with the entities and proceed via the controllers to the boundaries. From a user perspective interested in measured data, the journey starts with the data file (eveH5), represented on a low level by the evefile functional layer and on a high level as user interface by the measurement functional layer. The scan functional layer representing the information originally contained in the SCML file, while technically at the bottom of the dependencies chain, is the least interesting from a user's perspective primarily interested in the data, and is probably the layer fully implemented last.


.. admonition:: General remarks on the UML class diagrams

    The UML class diagrams in this document try to consistently follow a series of conventions listed below. This list is not meant to be exhaustive and may change over time.

    * Capitalising attribute types

      Attribute types that are default types of the (Python) language are not capitalised.

      Attribute types that are instances of self-defined classes are capitalised and spelled exactly as the corresponding class.

    * Singular and plural forms of attributes

      Scalar attributes have singular names.

      Attributes containing containers (lists, dictionaries, ...) have plural names.

    * Naming conventions

      Generally, naming conventions follow PEP8: class names are in CamelCase, attributes and methods in snake_case.

    * Attributes of enumerations

      No convention has yet been agreed upon. Possibilities would be ALLCAPS (as the attributes could be interpreted as constants) or snake_case.

    * Dictionaries

      Attributes that contain dictionaries as container have the container type followed by curly braces ``{}``, although this seems not to be part of the UML standard.


.. important::

    Partly due to the conventions for the UML class diagrams outlined above and due to the reasons leading to these conventions in the first place, the data model described in the UML class diagrams differs often in subtle details of attribute names from the currently existing data models and, *e.g.*, the SCML schema definition. Eventually, it would be good to agree upon a list of conventions and try to consistently apply them throughout the different interconnected parts (SCML, GUI, engine, evedata, ...). These conventions are primarily concerned with a shared vocabulary for the concepts, not with CamelCase *vs.* snake_case and alike, as this will differ for different languages (and we can agree on mapping rules).


Evefile
=======

Generally, the evefile functional layer, as mentioned already in the :doc:`Concepts <concepts>` section, provides the interface towards the persistence layer (eveH5 files). This is a rather low-level interface focussing on a faithful representation of all information available in an eveH5 file as well as the corresponding scan description (SCML), as long as the latter is available.

Furthermore, the evefile functional layer provides a stable abstraction of the contents of an eveH5 file and is hence *not* concerned with different versions of both, the eveH5 file structure and the SCML schema. The data model provided via its entities needs to be powerful (and modular) enough to allow for representing all currently existing data files (regardless of their eveH5 and SCML schema versions) and future-proof to not change incompatibly (open-closed principle, the "O" in "SOLID) when new requirements arise.


.. important::

    As the evefile functional layer is *not* meant as a (human-facing) user interface, it is *not* concerned with concepts such as fill modes, but represents the data "as is". This means that the different data can generally not be plotted against each other. This is a deliberate decision, as filling data for a (two-dimensional) data array, although generally desirable for (simple) plotting purposes, masks/removes some highly important information, *e.g.* whether a value has not been measured in the first place, or whether obtaining a value has failed for some reason.


Entities
--------

Entities are the innermost technical layer: everything depends on the entities, but the entities depend on nothing but themselves. Furthermore, entities may have little to no behaviour (*i.e.*, data classes). For the evefile functional layer, the entities consist of three modules: file, data, and metadata, in the order of their dependencies.


file module
~~~~~~~~~~~

Despite the opposite chain of dependencies, starting with the :mod:`file <evedata.evefile.entities.file>` module seems sensible, as its :class:`File <evedata.evefile.entities.file.File>` class represents a single eveH5 file and provides kind of an entry point.


.. figure:: uml/evedata.evefile.entities.file.*
    :align: center

    Class hierarchy of the :mod:`evefile.entities.file <evedata.evefile.entities.file>` module. The :class:`File <evedata.evefile.entities.file.File>` class is sort of the central interface to the entire subpackage, as this class provides a faithful representation of all information available from a given eveH5 file. To this end, it incorporates instances of classes of the other modules of the subpackage. Furthermore, "Scan" inherits from the identically named facade of the scan functional layer and contains the full information of the SCML file.


.. admonition:: Points to discuss further (without claiming to be complete)

    * Split "Scan" and "Setup", similarly to how they are stored in eveH5 in the future?

      The :mod:`scan.boundaries.scan <evedata.scan.boundaries.scan>` subpackage now contains two facades: :class:`Scan <evedata.scan.boundaries.scan.Scan>` with the scan description and :class:`Setup <evedata.scan.boundaries.scan.Setup>` with the setup description.

      The setup part of the SCML file sent to the engine is not necessarily identical with the XML file with the setup description loaded by the engine. Hence, it may make sense to have both stored separately, or have a "Scan" facade that contains only the scan description, and a "Setup" facade containing the information on the relevant devices.

      Which version is eventually saved in the HDF5 files? As it is the engine saving these files, it should be the version with the setup part updated. But is this really the case?


Some comments (not discussions any more):

* "data", "snapshots", "monitors": lists or dicts?

  In the meantime, the three attributes are modelled as dictionaries. How about modelling them as dictionaries, with the keys being the names of the corresponding datasets (*i.e.*, the last part of the path within the HDF5 file).


data module
~~~~~~~~~~~

Data are organised in "datasets" within HDF5, and the ``evefile.data`` module provides the relevant entities to describe these datasets. Although currently (as of 06/2024, eve version 2.1) neither average nor interval detector channels save the individual data points, at least the former is a clear need of the engineers/scientists. Hence, the data model already respects this use case. As per position (count) there can be a variable number of measured points, the resulting array is no longer rectangular, but a "ragged array". While storing such arrays is possible directly in HDF5, the implementation within evedata is entirely independent of the actual representation in the eveH5 file.


.. _fig-uml_evedata-evefile.data:

.. figure:: uml/evedata.evefile.entities.data.*
    :align: center
    :width: 750px

    Class hierarchy of the evefile.data module. Each class has a corresponding metadata class in the evefile.metadata module. While in this diagram, some child classes seem to be identical, they have a different type of metadata (see the evefile.metadata module below). Generally, having different types serves to discriminate where necessary between detector channels and motor axes. For details on the ``ArrayChannelData`` and ``AreaChannelData`` classes, see :numref:`Fig. %s <fig-uml_arraychannel>` and :numref:`Fig. %s <fig-uml_areachannel>`, respectively. You may click on the image for a larger view.


.. admonition:: Points to discuss further (without claiming to be complete)

    Currently none... ;-)


Some comments (not discussions any more, though):

* MonitorData with more than one value per time

  MonitorData should have only one value per time, although it can currently not completely be excluded that the same value is monitored multiple times, most probably resulting in identical values at identical times, see `#7688, note-11 <https://redmine.ahf.ptb.de/issues/7688#note-11>`_. However, this should be regarded as a bug (and if actually occuring in an eveH5 file, treated in some deterministic way). A special case are monitor data occurring before starting the actual scan, as these all get the special timestamp ``-1``, see `#7688, note-10 <https://redmine.ahf.ptb.de/issues/7688#note-10>`_. In this case, only the last (youngest) data point should be retained/used.

* Values of MonitorData

  MonitorData can have textual (non-numeric) values. This should not be too much of a problem given that numpy can handle string arrays (though <v2.0 only fixed-size string values. Hence, evedata may need to depend on numpy>=2.0).

* raw (*i.e.* individual) values of AverageChannelData and IntervalChannelData

  Currently, the measurement program only collects the average values in both cases. However, there is the frequent request to collect the raw values as well. The data structure already supports this.

* References to external data/files

  There are measurements where for a given position count spectra (1D) or entire images (2D) are recorded. At least for the latter, the data usually reside in external files. Currently, the file name (including the full path, starting with which version of the eveH5 schema?) is stored as value in the dataset in these cases. For a discussion, see `#7732 <https://redmine.ahf.ptb.de/issues/7732>`_. An additional complication: historically, the has been some mismatch between file number stored in the HDF5 dataset and actual file number. Hence, some way of correcting the mapping after reading the file needs to be possible.

  Generally, spectra (1D data per position count) contained within an eveH5 file in the "arraydata" group are modelled as ``ArrayChannelData``, with the ``_data`` attribute being a 2D numpy array. In case of storing images (2D data per position count), these data are modelled as ``AreaChannelData``, with the ``_data`` attribute being either a list of 2D/3D numpy arrays (containing the image data for one or different channels), a numpy array of arrays, or a 3D/4D array.

  While for a usual HDF5 dataset, the ``DataImporter`` object contains the eveH5 filename and dataset path for accessing the data, in case of external data, it contains a list of external filenames/references.

* Filled data

  Only axis data can and will be filled, and they will be filled differently depending on the channel data they are plotted against.

  If we allow several channels to be plotted against one axis, things will get slightly more involved, as the axis data need to be filled with respect to both channels in this case, and probably the channel data filled with NaN values as well. Alternatives would be to have the axis data filled individually for the individual channels, or to delete those points in the channel datasets where the other channel(s) don't have corresponding values (hooray, there we are again with our different fill modes...).

  Filling takes place by objects located in the controllers technical layer of the **measurement functional layer**, and the filled data will be stored in a separate attribute, retaining the original unfilled data.

* Detector channels that are redefined within an experiment/scan

  Generally, detector channels can be redefined within an experiment/scan, *i.e.* can have different operational modes (standard/average *vs.* interval) in different scan modules. Currently (eveH5 v7), all data are stored in the identical dataset on HDF5 level and only by "informed guessing" (if at all possible) can one deduce that they served different purposes.Generally, we need separate datasets on the HDF5 level for detector channels that change their type or attributes within a scan, see `#6879, note 16 <https://redmine.ahf.ptb.de/issues/6879#note-16>`_.

  The current state of affairs (as of 06/2024) regarding a new eveH5 scheme (v8) is to separate single-point channels from average and interval channels and have average and interval channel datasets *per se* be suffixed by the scan module ID. Given that one and the same channel can only be used once in a scan module, this should be unique.

  While the future way of storing those detector channels in eveH5 files is discussed in `#7726 <https://redmine.ahf.ptb.de/issues/7726>`_, we need a solution for **legacy data** solving two problems:

  1. separating the values for the different channels into separate datasets

     This is rather complicated, but probably possible by looking at the different HDF5 datasets where present -- although this would require reading the *data* of the HDF5 datasets if corresponding datasets are available in the "averagemeta" or/and "standarddev" group to check for changes in these data.

    Separating the data is but only necessary if correspnding datasets are available in the "averagemeta" or/and "standarddev" groups. *I.e.*, loading the data needs only to happen once this condition is met. However, as soon as this condition is met, data for legacy files need to be loaded to separate the data into separate datasets and not to have the surprise afterwards when first accessing the presumably single detector channel to all of a sudden have it split into several datasets.

  2. sensibly naming the resulting multiple datasets.

     Generally, the same strategy as proposed for the new eveH5 scheme should be used here, *i.e.* suffixing the average and interval detector channels with the scan module ID. Given that one and the same channel can only be used once in a scan module, this should be unique. The type of detector channel can be deduced from the class type.

* Additional class ``DeviceData``, but not ``OptionData``

  Devices seem currently only to be saved as monitors in the "device" section of the eveH5 file and appear as ``MonitorData``. Generally, starting with eve v1.32, all pre-/postscan devices (and options) are automatically stored as monitors, *i.e.* in the "devices" section of the eveH5 file.

  When timestamps of monitor data should be mapped to position counts (while retaining the original monitor data), this most probably means to create new instances of (subclasses of) ``MeasureData``. If these monitor data are devices, this is the case for ``DeviceData``.

  Options should generally be mapped to the respective classes the options belong to. For options, we additionally need to distinguish between "scalar" options that do not change within one scan module (and should in the future appear as attributes on the HDF5 level), and options whose values need to be saved for each individual position count (and should in the future appear as additional dataset columns on the HDF5 level).

  As of now, scalar options appear as dictionary ``options`` in the ``Metadata`` class hierarchy, while variable options with individual values per position count appear as dictionary ``options`` in the ``Data`` class hierarchy.

* Dealing with axes read-back values (RBV)

  With the advent of precise optical encoders, it turned out that axes do move after arriving at their set point. Hence, for some measurements, axes RBVs are read as pseudo-detector channels. Currently (eveH5 v7), these data end up as detector channels in distinct HDF5 datasets. However, logically they belong to the corresponding axes. Further complications may arise from the fact that there exists the use case for recording these axes RBVs during averaging of detector channel data.

  The data model distinguishes between axes with encoders and those without. In the future, for axes with encoders the RBV will be read synchronously to every detector channel readout. This makes filling for those axes unnecessary, as for every detector channel readout there exists a "true" axis value. For average channels, this further means that as many axes RBVs are present as maximum detector channel readouts for this position, resulting in general in a "ragged array".

  As for axes without encoder, the RBV does not change after the axis has arrived at its position, additionally reading these axes RBVs would not make sense, as this would suggest real values.

* Sorting non-monotonic positions in eveH5 datasets

  Due to the (intrinsic) way the engine handles scans, position counts can be non-monotonic (`#4562 <https://redmine.ahf.ptb.de/issues/4562>`_, `#7722 <https://redmine.ahf.ptb.de/issues/7722>`_). However, this will usually be a problem for the analysis. Therefore, positions need to be sorted monotonically, and this is done during data import.


Array channels
..............

Array channels in their general form are channels collecting 1D data. Typical devices used here are MCAs, but oscilloscopes and vector signal analysers (VSA) would be other typical array channels. Hence, for these quite different types of array channels, distinct subclasses of the generic :class:`ArrayChannelData <evedata.evefile.entities.data.ArrayChannelData>` class exist, see :numref:`Fig. %s <fig-uml_arraychannel>`.


.. _fig-uml_arraychannel:

.. figure:: uml/arraychannel.*
    :align: center
    :width: 750px

    Preliminary data model for the :class:`ArrayChannelData <evedata.evefile.entities.data.ArrayChannelData>` classes. The basic hierarchy is identical to :numref:`Fig. %s <fig-uml_evedata-evefile.data>`. Details for the :class:`MCAChannelData <evedata.evefile.entities.data.MCAChannelData>` class can be found in :numref:`Fig. %s <fig-uml_mcachannel>`. The :class:`ScopeChannelData <evedata.evefile.entities.data.ScopeChannelData>` class is a container for scopes with several channels read simultaneously. Further array detector channels can be added by subclassing :class:`ArrayChannelData <evedata.evefile.entities.data.ArrayChannelData>`. Probably the next class will be :class:`VSAChannelData <evedata.evefile.entities.data.VSAChannelData>` for Vector Signal Analyser (VSA) data.


Multi Channel Analysers (MCA) generally collect 1D data and typically have separate regions of interest (ROI) defined, containing the sum of the counts for the given region. For the EPICS MCA record, see https://millenia.cars.aps.anl.gov/software/epics/mcaRecord.html.


.. _fig-uml_mcachannel:

.. figure:: uml/mcachannel.*
    :align: center
    :width: 750px

    Preliminary data model for the :class:`MCAChannelData <evedata.evefile.entities.data.MCAChannelData>` classes. The basic hierarchy is identical to :numref:`Fig. %s <fig-uml_evedata-evefile.data>`, and here, the relevant part of the metadata class hierarchy from :numref:`Fig. %s <fig-uml_evedata-evefile.metadata>` is shown as well. Separating the :class:`MCAChannelCalibration <evedata.evefile.entities.metadata.MCAChannelCalibration>` class from the :class:`ArrayChannelMetadata <evedata.evefile.entities.metadata.ArrayChannelMetadata>` allows to add distinct behaviour, *e.g.* creating calibration curves from the parameters.


Note: The scalar attributes for ArrayChannelROIs will currently be saved as snapshots regardless of whether the actual ROI has been defined/used. Hence, the evedata package needs to decide based on the existence of the actual data whether to create a ROI object and attach it to :class:`ArrayChannelData <evedata.evefile.entities.data.ArrayChannelData>`.

The calibration parameters are needed to convert the *x* axis of the MCA spectrum into a real energy axis. Hence, the :class:`MCAChannelCalibration <evedata.evefile.entities.metadata.MCAChannelCalibration>` class will have methods for performing exactly this conversion. The relationship between calibrated units (cal) and channel number (chan) is defined as cal=CALO + chan\*CALS + chan^2\*CALQ. The first channel in the spectrum is defined as chan=0. However, not all MCAs/SDDs have these calibration values: Ketek SDDs seem to not have these values (internal calibration?).

The real_time and life_time values can be used to get an idea of the amount of pile up occurring, *i.e.* having two photons with same energy within a short time interval reaching the detector being detected as one photon with twice the energy. Hence, latest in the radiometry package, distinct methods for this kind of analysis should be implemented.


Area channels
.............

Area channels are basically 2D channels, *i.e.*, cameras. There are (at least) two distinct types of cameras in use, namely scientific cameras and standard consumer digital cameras for taking pictures (of sample positions in the setup). While scientific cameras usually record only greyscale images, but have additional parameters and can define regions of interest (ROI), consumer cameras are much simpler in terms of their data model and typically record RGB images. These different types of images need to be handled differently in the data processing and analysis pipeline.


.. _fig-uml_areachannel:

.. figure:: uml/areachannel.*
    :align: center
    :width: 750px

    Preliminary data model for the :class:`AreaChannelData <evedata.evefile.entities.data.AreaChannelData>` class. The basic hierarchy is identical to :numref:`Fig. %s <fig-uml_evedata-evefile.data>`. As scientific cameras are quite different from standard consumer digital cameras for taking pictures, but both are used from within the measurement program, distinct subclasses of the basic :class:`AreaChannelData <evedata.evefile.entities.data.AreaChannelData>` class exist. For details on the :class:`ScientificCameraData <evedata.evefile.entities.data.ScientificCameraData>` classes, see :numref:`Fig. %s <fig-uml_scientificcamera>`.


.. _fig-uml_scientificcamera:

.. figure:: uml/scientificcamera.*
    :align: center
    :width: 750px

    Preliminary data model for the :class:`ScientificCameraData <evedata.evefile.entities.data.ScientificCameraData>` classes. The
    basic hierarchy is identical to :numref:`Fig. %s
    <fig-uml_evedata-evefile.data>`, and here, the relevant part of the
    metadata class hierarchy from :numref:`Fig. %s
    <fig-uml_evedata-evefile.metadata>` is shown as well. As different
    area detectors (scientific cameras) have somewhat different options,
    probably there will appear a basic :class:`AreaChannelData <evedata.evefile.entities.data.AreaChannelData>` class with
    more specific subclasses.


Regarding file names/paths: Some of the scientific cameras are operated from Windows, hence there is usually no unique mapping of paths to actual places of the files, particularly given that Windows allows to map a drive letter to arbitrary network paths. It seems as if these paths are quite different for the different detectors, and therefore, some externally configurable mapping should be used.

Note for Pilatus cameras: Those cameras seem to have three sensors each for temperature and humidity. Probably the simplest solution would be to store those values in an array rather than having three individual fields each. In case of temperature (and humidity) readings for each individual image, the array would become a 2D array.


.. admonition:: Points to discuss further (without claiming to be complete)

    * Label for the ROIs

      The camera controller seems to provide the possibility to set labels for ROIs. Is this supported by the EPICS driver currently in use, and could we just add the PV to the template file(s)?

    * Marker for the ROIs

      The camera controller seems to set MinX, MinY, SizeX, SizeY. Is this the generally agreed and consistent way of defining the marker area? What should the four elements of the :attr:`ScientificCameraROIData.marker <evedata.evefile.entities.data.ScientificCameraROIData.marker>` attribute represent?

    * Sample cameras: additional fields

      Are ``beam_x`` and ``beam_y`` really parameters that change between images within a scan module? AFAIK, these are values set once when adjusting the camera, and otherwise never change. If so, they should be moved to the metadata.


metadata module
~~~~~~~~~~~~~~~

Data without context (*i.e.* metadata) are mostly useless. Hence, to every class (type) of data in the evefile.data module, there exists a corresponding metadata class.


.. note::

    As compared to the UML schemata for the IDL interface, the decision of whether a certain piece of information belongs to data or metadata is slightly different here. The main reason for this is the problem in current (as of eveH5 v7) files and redefined detector channels, leading to a loss of information that needs to be changed anyway and is discussed above for the data module. With separate datasets for different detector channels, the problem is solved and the immutable metadata belong to the metadata classes (and are converted to attributes on the HDF5 level in the future scheme, v8).


.. _fig-uml_evedata-evefile.metadata:

.. figure:: uml/evedata.evefile.metadata.*
    :align: center
    :width: 750px

    Class hierarchy of the evefile.metadata module. Each concrete class in the evefile.data module has a corresponding metadata class in this module. You may click on the image for a larger view.


A note on the ``AbstractDeviceMetadata`` interface class: The eveH5 dataset corresponding to the TimestampMetadata class is special in sense of having no PV and transport type nor an id. Several options have been considered to address this problem:

#. Moving these three attributes down the line and copying them multiple times (feels bad).
#. Leaving the attributes blank for the "special" dataset (feels bad, too).
#. Introduce another class in the hierarchy, breaking the parallel to the Data class hierarchy (potentially confusing).
#. Create a mixin class (abstract interface) with the three attributes and use multiple inheritance/implements.

As obvious from the UML diagram, the last option has been chosen. The name "DeviceMetadata" resembles the hierarchy in the ``scml.setup`` module and clearly distinguishes actual devices from datasets not containing data read from some instrument.


.. admonition:: Points to discuss further (without claiming to be complete)

    Currently none... ;-)


Some comments (not discussions any more, though):

* Attributes "pv" and "access_mode"

  "pv" is the EPICS process variable, "access_mode" refers to the access mode (local vs. ca, in the future additionally pva). Both are currently (as of eveH5 v7) stored as one attribute "access" in the eveH5 datasets, separated by ":" in the form ``<access_mode>:<pv>``. In the new eveH5 schema (v8), these attributes will be split into two attributes with the corresponding names.

* Attributes for ``AverageChannelMetadata`` and ``IntervalChannelMetadata``

  The current model in the UML schemas of data and metadata assumes different data(sets) in case a detector channel gets redefined within a scan, see `#7726 <https://redmine.ahf.ptb.de/issues/7726>`_ and the discussion above. This should be verified and specified.


.. todo::

    Extend Metadata classes to contain all relevant attributes from the SCML/setup description. This should already include metadata regarding the actual devices used not yet available from the SCML/XML but relevant for a true traceability of changes in the setup.


Controllers
-----------

Code in the controllers technical layer operate on the entities and provide the required behaviour (the "business logic").

What may be in here:

* Mapping different versions of eveH5 files to the entities
* Mapping timestamps to position counts (=> move to measurement subpackage)
* Converting MPSKIP scans into average detector channel with adaptive number of recorded points (=> move to measurement subpackage?)
* Separating datasets for channels redefined within one scan and currently (up to eveH5 v7) stored in *one* HDF5 dataset
* Extract set values for axes (requires access to SCML)
* Correct mapping of file numbers for external files


version_mapping module
~~~~~~~~~~~~~~~~~~~~~~

For details, see the documentation of the :mod:`version_mapping <evedata.evefile.controllers.version_mapping>` module.

Being version agnostic with respect to eveH5 and SCML schema versions is a central aspect of the evedata package. This requires facilities mapping the actual eveH5 files to the data model provided by the entities technical layer of the evefile subpackage. The :class:`EveFile <evedata.evefile.boundaries.evefile.EveFile>` facade obtains the correct :class:`VersionMapper <evedata.evefile.controllers.version_mapping.VersionMapper>` object via the :class:`VersionMapperFactory  <evedata.evefile.controllers.version_mapping.VersionMapperFactory>`, providing an :class:`HDF5File  <evedata.evefile.boundaries.eveh5.HDF5File>` resource object to the factory. It is the duty of the factory to obtain the "version" attribute from the :class:`HDF5File  <evedata.evefile.boundaries.eveh5.HDF5File>` object (possibly requiring to explicitly get the attributes of the root group of the :class:`HDF5File  <evedata.evefile.boundaries.eveh5.HDF5File>` object).


.. figure:: uml/evedata.evefile.controllers.version_mapping.*
    :align: center

    Class hierarchy of the evefile.controllers.version_mapping module, providing the functionality to map different eveH5 file schemas to the data structure provided by the :class:`HDF5File  <evedata.evefile.boundaries.eveh5.HDF5File>` class. The :class:`VersionMapperFactory  <evedata.evefile.controllers.version_mapping.VersionMapperFactory>` is used to get the correct mapper for a given eveH5 file. For each eveH5 schema version, there exists an individual ``VersionMapperVx`` class dealing with the version-specific mapping. The idea behind the ``Mapping`` class is to provide simple mappings for attributes and alike that need not be hard-coded and can be stored externally, *e.g.* in YAML files. This would make it easier to account for (simple) changes.


For each eveH5 schema version, there exists an individual ``VersionMapperVx`` class dealing with the version-specific mapping. That part of the mapping common to all versions of the eveH5 schema takes place in the :class:`VersionMapper  <evedata.evefile.controllers.version_mapping.VersionMapper>` parent class, *e.g.* removing the chain. The idea behind the ``Mapping`` class is to provide simple mappings for attributes and alike that can be stored externally, *e.g.* in YAML files. This would make it easier to account for (simple) changes.


Converting MPSKIP scans into average detector channel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Given the data model to not correspond to the current eveH5 structure (v7), it makes sense to convert scans using MPSKIP to "fake" average detector channels storing the individual data points on this level.


.. important::

    At least one group uses MPSKIP not only for storing the individual data points for averaging, but for recording axes RBVs for each individual detector channel readout as well, due to motor axes changing their position slightly. The axes RBVs are recorded for using pseudodetectors are/should be equipped with encoders to ensure actual values being read. The data model now supports axes objects to have more than one value for a position to account for this situation. This means, however, to convert the MPSKIP scans with individual position counts for each detector readout to scans with multiple values available per individual position.


Separating datasets for redefined channels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Given the data model to not correspond to the current eveH5 structure (v7), it makes sense to split datasets for channels redefined within one scan on this level. A more detailed discussion of how to handle these datasets can be found above in the section on the data model.



Extract set values for axes
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The axes positions stored in the HDF5 file are the RBVs after positioning. If, however, an axis never reached the set value due to limit violation or other constraints, this is usually not visible from the HDF5 file, as the severity is typically not recorded. However, the set values for each axis can be inferred from the scan description. Having this information would be helpful for routine checks whether a scan ran as expected. Set values are stored in the ``set_values`` attribute of the ``AxisData`` class.


Correct mapping of file numbers for external files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the past, there has been some occasions where the stored file numbers for external files (usually images from 2D detectors) do not match with the *correct* files. Hence, we need some mechanism to modify the file numbers after loading a file for a correct mapping. It is unclear so far whether there is a way to automatically and reliably detect when to apply this correction.


Boundaries
----------

What may be in here:

* facade:

  * evefile

resources:

* eveH5
* Interfaces towards additional files, *e.g.* images

  * Images in particular are usually not stored in the eveH5 files, but only pointers to these files.
  * Import routines for the different files (or at least a sensible modular mechanism involving an importer factory) need to be implemented.
  * Is the ``evedata`` package the correct place for these importers? One could think of the ``radiometry`` package as the better place, but on the other hand, the ``evedataviewer`` package would need to be able to display those data as well, hence need the import to be done.

* Interfaces towards other file formats

  * One potential candidate for an exchange format would be the NeXus format. However, there is not one NeXus file format, but there are several schemas for different types of experiments. For details, see the `NeXus application definitions <https://manual.nexusformat.org/classes/applications/index.html>`_. Hence, those exporters may better be located in the ``radiometry`` package.


evefile module (facade)
~~~~~~~~~~~~~~~~~~~~~~~


.. _fig-uml_evefile_boundaries_evefile:

.. figure:: uml/evedata.evefile.boundaries.evefile.*
    :align: center

    Class hierarchy of the evefile.boundaries.evefile module, providing the facade for an eveH5 file. Currently, the basic idea is to inherit from the ``File`` entity and extend it accordingly, adding behaviour.


As per :numref:`Fig. %s <fig-uml_evefile_boundaries_evefile>`, the ``EveFile`` class inherits from the ``File`` class of the entities subpackage. Reading (loading) an eveH5 file will result in calling out to :meth:`eveH5.HDF5File.read`, followed by mapping the eveH5 contents to the data model. Additionally, for eveH5 v7 and below, datasets for detector channels that have been redefined within one scan and scans using MPSKIP are mapped to the respective datasets accordingly. Last but not least, the corresponding SCML (and setup description, where applicable) are loaded and the metadata contained therein mapped to the metadata of the corresponding datasets.


Some comments (not discussions any more, though):

* Metadata from SCML file

  There is more information available from the SCML file (and the measurement station/beam line description - but that is generally not available when reading eveH5 files if it is not contained in the SCML). This information needs to be mapped to the respective metadata classes (and those classes be extended accordingly). This mapping will take place here, as per schema of the functional and technical layers, the ``evefile`` subpackage depends on the ``scan`` subpackage.

* Non-monotonic position counts in eveH5 datasets

  Due to the (intrinsic) way the engine handles scans, position counts can be non-monotonic (`#4562 <https://redmine.ahf.ptb.de/issues/4562>`_, `#7722 <https://redmine.ahf.ptb.de/issues/7722>`_). However, this will usually be a problem for the analysis. Therefore, the sorting logic should be implemented in  the controller layer and called by the facade.


eveh5 module (resource)
~~~~~~~~~~~~~~~~~~~~~~~

The aim of this module is to provide a Python representation (in form of a hierarchy of objects) of the contents of an eveH5 file that can be mapped to both, the evefile and measurement interfaces. While the Python h5py package already provides the low-level access and gets used, the eveh5 module contains Python objects that are independent of an open HDF5 file, represent the hierarchy of HDF5 items (groups and datasets), and contain the attributes of each HDF5 item in form of a Python dictionary. Furthermore, each object contains a reference to both, the original HDF5 file and the HDF5 item, thus making reading dataset data on demand as simple as possible.


.. figure:: uml/evedata.evefile.boundaries.eveh5.*
    :align: center

    Class hierarchy of the :mod:`evedata.evefile.boundaries.eveh5` module. The :class:`HDF5Item` class and children represent the individual HDF5 items on a Python level, similarly to the classes provided in the h5py package, but *without* requiring an open HDF5 file. Furthermore, reading actual data (dataset values) is deferred by default.


As such, the ``HDF5Item`` class hierarchy shown above is pretty generic and should work with all eveH5 versions. However, it is *not* meant as a generic HDF5 interface, as it does make some assumptions based on the eveH5 file structure and format.


Some comments (not discussions any more, though):

* Reading the entire content of an eveH5 file at once vs. deferred reading?

  * Reading relevant metadata (*e.g.*, to decide about what data to plot) should be rather fast. And generally, only two "columns" will be displayed (as f(x,y) plot) at any given time -- at least if we don't radically change the way data are looked at compared to the IDL Cruncher.
  * References to the internal datasets of a given HDF5 file are stored in the corresponding Python data structures (together with the HDF5 file name). Hence, HDF5 files are closed after each operation, such as not to have open file handles that may be problematic (but see the quote from A. Collette below).
  * Plotting requires data to be properly filled, although filling will most probably not take place globally once, but on a per plot base. See the discussion on fill modes, currently below in the Dataset subpackage section.


  From the book "Python and HDF5" by Andrew Collette:

    You might wonder what happens if your program crashes with open files. If the program exits with a Python exception, don't worry! The HDF library will automatically close every open file for you when the application exits.

    -- Andrew Collette, 2014 (p. 18)



Measurement
===========

Generally, the measurement subpackage, as mentioned already in the :doc:`Concepts <concepts>` section, provides the interface towards the "user", where user mostly means the ``evedataviewer`` and ``radiometry`` packages. However, besides these two Python packages, human users will want to use the ``evedata`` package as well. Hence, it should be as human-friendly as possible.


The overall package structure of the evedata package is shown in :numref:`Fig. %s <fig-uml_evedata>`. Furthermore, a series of (still higher-level) UML schemata for the measurement subpackage are shown below, reflecting the current state of affairs (and thinking).


.. note::

    The mapping of the information contained in both, the HDF5 and SCML layers of an eveH5 file, to the measurement is far from being properly modelled or understood. This is partly due to the step-wise progress in understanding. On a rather fundamental level, it remains to be decided whether a ``Measurement`` should allow for reconstructing how a measurement has actually been carried out (*i.e.*, provide access to the SCML and hence the anatomy of the scan).


What is the main difference between the :mod:`evefile <evedata.evefile>` and the :mod:`measurement <evedata.measurement>` subpackages? Basically, the information contained in an eveH5 file needs to be "interpreted" to be able to process, analyse, and plot the data. While the :mod:`evefile <evedata.evefile>` subpackage provides the necessary data structures to faithfully represent all information contained in an eveH5 file, the :mod:`measurement <evedata.measurement>` subpackage provides the result of an "interpretation" of this information in a way that facilitates data processing, analysis and plotting.

However, the :mod:`measurement <evedata.measurement>` subpackage is still general enough to cope with all the different kinds of measurements the eve measurement program can deal with. Hence, it may be a wise idea to create dedicated dataset classes in the ``radiometry`` package for different types of experiments. The NeXus file format may be a good source of inspiration here, particularly their `application definitions <https://manual.nexusformat.org/classes/applications/index.html>`_. The ``evedataviewer`` package in contrast aims at displaying whatever kind of measurement has been performed using the eve measurement program. Hence it will deal directly with :obj:`Measurement <evedata.measurement.boundaries.measurement.Measurement>` (facade) objects of the :mod:`measurement <evedata.measurement>` subpackage.



.. admonition:: Arguments against the 2D data array as sensible representation

    Currently, one very common and heavily used abstraction of the data contained in an eveH5 file is a two-dimensional data array (basically a table with column headers, implemented as pandas dataframe). As it stands, many problems in the data analysis and preprocessing of data come from the inability of this abstraction to properly represent the data. Two obvious cases, where this 2D approach simply breaks down, are:

    * subscans -- essentially a 2D dataset on its own
    * adaptive average detector channel saving the individual, non-averaged values (implemented using MPSKIP)

    Furthermore, as soon as spectra (1D) or images (2D) are recorded for a given position (count), the 2D data array abstraction breaks down as well.

    Other problems inherent in the 2D data array abstraction are the necessary filling of values that have not been obtained. Currently, once filled there is no way to figure out for an individual position whether values have been recorded (in case of LastFill) or whether a value has not been recorded or recording failed (in case of NaNFill).


A few ideas/comments for further modelling this subpackage:

* :mod:`evefile <evedata.evefile>` represents the eveH5 file, while :mod:`measurement <evedata.measurement>` maps the different datasets to more sensible abstractions.

  * Not all abstractions will necessarily be reflected in the future in the eveH5 file. Currently (eveH5 v7), most of the abstractions are clearly not visible there. How to deal with this situation? The entities in the :mod:`evefile <evedata.evefile>` subpackage should reflect the future eveH5 scheme and abstractions therein, with the version mapping from the controller technical layer responsible for the mapping of older eveH5 schemata to the entities.


Entities
--------

A few general remarks:

* :class:`Measurement <evedata.measurement.entities.measurement.Measurement>` will probably still be distinct from the "dataset" concept used in the ``evedataviewer`` and ``radiometry`` packages.
* Metadata need to be attached to the individual data objects, as is the case in the :mod:`evedata.evefile.entities` subpackage.
* Clear differences between the :mod:`measurement <evedata.measurement>` and :mod:`evefile <evedata.evefile>` subpackages:

  * :mod:`measurement <evedata.measurement>` takes care of filling, subscans, and probably mapping of monitors to datasets with positions.
  * The distinction between "main", "snapshot", and "monitor" may be discarded in favour of more useful abstractions. This requires, however, a thorough discussion of the concepts of monitors and snapshots, how they are currently used and how they should be used (and mapped) in the future.



.. admonition:: Points to discuss further (without claiming to be complete)

    * Introducing the concepts of detector, motor, option, device?

      There are distinct concepts, particularly between detector and channel, and motor and axis: A detector can have *n* channels, a motor can have *n* axes. On the EPICS level, this does not matter, and so far, on the eveH5 level, the datasets correspond to channels and axes. However, would it make sense to introduce the concept of a detector (at least)?

      This seems to be particularly powerful in case of cameras having different EPICS PVs that are of relevance. However, in case of the Pilatus detector, we even have a composition of channels and at least one axis (settable parameter). This would demand for another layer of abstraction, *i.e.* a more general Camera class and a series of derived classes for particular camera detectors.

      What other abstractions are sensible on the level of the setup/measurement? Would it be sensible to rethink the current layout and design of the measurement program to better reflect these concepts there as well? This would fit into having "devices" that do monitor much more parameters, and particularly the state of crucial PVs (by means of status PVs) -- in order to have a more transparent measurement allowing for detailed *post mortem* analysis if something seems fishy.

    * Two "layers" of a future evedataviewer?

      Given more abstract concepts such as detector, motor, or even camera to be introduced, there still may be the need/wish to plot arbitrary channels/axes/options against each other. Would that demand for two different layers of an evedataviewer, one more in line of the current Cruncher and BessyHDFViewer that are rather close to the eveH5 files, and one dealing with the far more abstract and powerful concepts?


measurement module
~~~~~~~~~~~~~~~~~~

A measurement generally reflects all the data obtained during a measurement. However, to plot data or to perform some analysis, usually we need data together with an axis (or multiple axes for *n*\D data), where data ("intensity values") and axis values come from different HDF5 datasets. Furthermore, there may generally be the need/interest to plot arbitrary data against each other, *i.e.* channel data *vs.* channel data and axis data *vs.* axis data, not only channel data *vs.* axis data. This is the decisive difference between the :class:`Measurement entity <evedata.measurement.entities.measurement.Measurement>` and the :class:`Measurement facade <evedata.measurement.boundaries.measurement.Measurement>`, with the latter having the additional attributes for storing the data to work on.


.. figure:: uml/evedata.measurement.entities.measurement.*
    :align: center

    Class hierarchy of the :mod:`measurement.entities.measurement <evedata.measurement.entities.measurement>` module. Currently, this diagram just reflects first ideas for a more abstract representation of a measurement as compared to the data model of the evefile subpackage. Devices are all the detector(channel)s and motor(axe)s used in a scan. Distinguishing between detector(channel)s/motor(axe)s, beamline, and machine can (at least partially) happen based on the data type: detector(channel)s are :class:`ChannelData <evedata.evefile.entities.data.ChannelData>`, motor(axe)s are :class:`AxisData <evedata.evefile.entities.data.AxisData>`. Machine and beamline parameters are more tricky, as they can be :class:`DeviceData <evedata.evefile.entities.data.DeviceData>` (from the "monitor" section) as well as :class:`ChannelData <evedata.evefile.entities.data.ChannelData>` (and :class:`AxisData <evedata.evefile.entities.data.AxisData>` for shutters and alike?) from the original "main" and "snapshot" sections. :class:`Scan` and :class:`Setup` inherit directly from their counterparts in the :mod:`evefile.entities.file <evedata.evefile.entities.file>` module. :class:`Data` and :class:`Axis` seem not to be used here, but become essential in the corresponding :class:`Measurement <evedata.measurement.boundaries.measurement.Measurement>` facade. See :numref:`Fig. %s <fig-uml_evedata.measurement.boundaries.measurement>` for details.





.. admonition:: Points to discuss further (without claiming to be complete)

    * How to deal with snapshots and monitors?

      Snapshots and monitors mostly provide information ("metadata") on the state of beamline and machine. As such, usually they are *not* used in plots. This would mean that the current/energy that is used as the one standard detector in (nearly) every measurement shall *not* be part of the ``machine`` section, but rather ``detectors`` (or whatever this section may be named eventually).

    * How to reliably identify those HDF5 datasets that belong to the ``machine`` and ``beamline`` sections?

      Basically, all of these datasets should come from either the ``snapshot`` or ``device`` (aka monitor) section of the eveH5 file. How about (in the future) explicitly mark the corresponding devices in the SCML and setup file as belonging to either machine or beamline, record them automatically, and place them in distinct groups in the eveH5 file?

    * How to deal with monitors?

      * Add an ``events`` attribute to the ``Measurement`` class? It might be an interesting use case to have a list of "events" (aka values for the different monitors) in chronological order, and similar to the monitors themselves, they should be mappable to the position counts. This would allow for a display of arbitrary data together with (relevant) events.


Some comments (not discussions any more, though):

* Combine ``detectors`` and ``motors`` to one section ``devices``.

  The distinction between detector(channel)s and motor(axe)s is somewhat blurred when we start allowing options to be handled like currently only axes, *i.e.* to record detector channel data as function of an option value (exposure/acquisition time and similar).

  On the other hand, there still is a clear distinction between motor axes and detector channels, but this is apparent by the type of the individual objects. Furthermore, the difference between ``devices`` on one side and ``beamline`` and ``machine`` on the other side would more clearly reflect the current distinction between ``main`` and ``snapshot``/``monitor``.

  The name ``devices`` may somewhat collide with the current use of the term for devices that are neither motor axes nor detector channels. However, this collision may be leveraged in the future, when the concepts and abstractions available in the measurement program change as well.

* Reproducibility, *i.e.* history of tasks performed on the data.

  * Background: In the ASpecD framework, reproducibility is an essential concept, and this revolves about having a dataset with one clear data array and *n* corresponding axes. The original data array is stored internally, making undo and redo possible, and each processing and analysis step always operates on the (current state of the) data array. In case of the datasets we deal with here, there is usually no such thing as the one obvious data array, and users can at any time decide to focus on another set of "axes", *i.e.* data and corresponding axis values, to operate on.
  * The ``evedata`` package does *not* deal with the concept of reproducibility, but delegates this to the ``radiometry`` package. There, the first step would be to decide which of the available channels accounts as the "primary" data (if not set as preferred in the scan already and read from the eveH5 file accordingly).

* Dealing with images stored in files separate from the eveH5 file.

  * The eveH5 file contains only the links (*i.e.* filenames) to these files. The :mod:`evefile <evedata.evefile>` subpackage comes with importers for images as well. Hence, in an :obj:`EveFile <evedata.evefile.boundaries.evefile.EveFile>` object, the images will be directly accessible.
  * Accessing images of course means having access to the image files stored separately from the eveH5 file.
  * Regarding deferred loading: Loading images is a rather cheap operation (typically <1 ms per image), hence one could load *all* images at once when first accessing the data.



metadata module
~~~~~~~~~~~~~~~

Metadata are a crucial part of reproducibility. Furthermore, metadata allow analysis routines to gain a "semantic" understanding of the data and hence perform (at least some) actions unattended and fully automatically. While all metadata corresponding to the individual devices used in recording data are stored in the :attr:`metadata <evedata.evefile.entities.data.Data.metadata>` attribute of the :class:`Data <evedata.evefile.entities.data.Data>` class (and its descendants), there are other types of metadata that belong to the measurement as such itself. These are modelled in the :mod:`metadata <evedata.measurement.entities.metadata>` module in the :class:`Metadata <evedata.measurement.entities.metadata.Metadata>` class.


.. figure:: uml/evedata.measurement.entities.metadata.*
    :align: center

    While the :class:`Metadata <evedata.measurement.entities.metadata.Metadata>` class inherits directly from its counterpart from the :mod:`evedata.evefile.entities.file` module, it is extended in crucial ways, reflecting the aim for more reproducible measurements and having datasets containing all crucial information in one place. This involves information on both, the machine (BESSY-II, MLS) and the beamline, but on the sample(s) as well. Perhaps the ``sample`` attribute should be a dictionary rather than a plain list, with (unique) labels for each sample as keys.


As of now, the eveH5 files do not contain any metadata regarding machine, beamline, or sample(s). The names of the machine and beamline can most probably be inferred, having the name of the beamline obviously allows to assign the machine as well.

Given that one measurement (*i.e.* one scan resulting in one eveH5 file) can span multiple samples, and will often do, in the future, at least some basic information regarding the sample(s) should be added to the eveH5 file and read and mapped accordingly to instances of the :class:`Sample <evedata.measurement.entities.metadata.Sample>` class, one instance per sample. Potentially, this allows to assign parts of the measured data to individual samples and hence automate data processing and analysis, *e.g.* splitting the data for the different samples into separate datasets/files.


Controllers
-----------

What may be in here:

* Fill modes, now termed "joining"
* Mapping monitor time stamps to position counts

  * Results probably in :obj:`DeviceData <evedata.evefile.entities.data.DeviceData>` objects.

* Converting scan with subscans into appropriate subscan data structure
* Mapping between :obj:`EveFile <evedata.evefile.boundaries.evefile.EveFile>` and :obj:`Measurement <evedata.measurement.boundaries.measurement.Measurement>` objects, *i.e.* low-level and high-level interface

  * Assumes a 1:1 mapping between files and measurements.
  * While there may be several datasets (one for each sample) created from one measurement (*i.e.*, eveH5 file), the 1:1 relation between measurement and file should hold.


Joining: "fill modes"
~~~~~~~~~~~~~~~~~~~~~

For each motor axis and detector channel, in the original eveH5 file only those values appear---typically together with a "position counter" (PosCount) value---that are actually set or measured. Hence, the number of values (*i.e.*, the length of the data vector) will generally be different for different detectors/channels and devices/axes. To be able to plot arbitrary data against each other, the corresponding data vectors need to be brought to the same dimensions (*i.e.*, "joined", originally somewhat misleadingly termed "filled").

Currently, there are four "fill modes" available for data: NoFill, LastFill, NaNFill, LastNaNFill. From the `documentation of eveFile <https://www.ahf.ptb.de/messpl/sw/python/common/eveFile/doc/html/Section-Fillmode.html#evefile.Fillmode>`_:


NoFill
    "Use only data from positions where at least one axis and one channel have values."

    Actually, not a filling, but mathematically an intersection, or, in terms of relational databases, an ``SQL INNER JOIN``. In any case, data are *reduced*.

LastFill
    "Use all channel data and fill in the last known position for all axes without values."

    Similar to an ``SQL LEFT JOIN`` with data left and axes right, but additionally explicitly setting the missing axes values in the join to the last known axis value.

NaNFill
    "Use all axis data and fill in NaN for all channels without values."

    Similar to an ``SQL LEFT JOIN`` with axes left and data right. To be exact, the ``NULL`` values of the join operation will be replaced by ``NaN``.

LastNaNFill
    "Use all data and fill in NaN for all channels without values and fill in the last known position for all axes without values."

    Similar to an ``SQL OUTER JOIN``, but additionally explicitly setting the missing axes values in the join to the last known axis value and replacing the ``NULL`` values of the join operation by ``NaN``.


Furthermore, for the Last*Fill modes, snapshots are inspected for axes values that are newer than the last recorded axis in the main/standard section.

Note that none of the fill modes guarantees that there are no NaNs (or comparable null values) in the resulting data.


.. important::

    The IDL Cruncher seems to use LastNaNFill combined with applying some "dirty" fixes to account for scans using MPSKIP and those scans "monitoring" a motor position via a pseudo-detector. The ``EveHDF`` class (DS) uses LastNaNFill as a default as well but does *not* apply some additional post-processing.

    Shall fill modes be something to change in a viewer? And which fill modes are used in practice (and do we have any chance to find this out)?


For numpy set operations, see in particular :func:`numpy.intersect1d` and :func:`numpy.union1d`. Operating on more than two arrays can be done using :func:`functools.reduce`, as mentioned in the numpy documentation (with examples). Helpful may be :func:`numpy.digitize` as well.


.. admonition:: Points to discuss further (without claiming to be complete)

    * How to handle data filling?

      * Obviously, if one wants to plot arbitrary HDF5 datasets against each other (as currently possible), data dimensions need to be made compatible.
      * The original values should always be retained, to be able to show/tell which values have actually been obtained (and to discriminate between not recorded and failed to record, *i.e.* no entry vs. NaN in the original HDF5 dataset)
      * Could there be different (and changing) filling of the data depending on which "axes" should be plotted against each other? -- Yes, that should always be the case.

    * Which fill modes are relevant/needed?

      It seems that LastNaNFill is widely used as a default fill mode. Depending on the origin of the data, additional post-processing (see below) is necessary to have usable data.

      As NoFill does not only not fill, but actually reduce data, "fill mode" may not be the ideal term. Other opinions/ideas/names?

      Given that the :class:`EveFile <evedata.evefile.boundaries.evefile.EveFile>` class provides a faithful representation of the actual data contained in an eveH5 file, one could think of mechanisms to highlight those values that were actually recorded (as compared to filled afterwards). Would this help to reduce the number of fill modes available?

    * Where/when to apply filling?

      The :class:`EveFile <evedata.evefile.boundaries.evefile.EveFile>` class contains the data *as read* from the eveH5 file, *i.e.* the not at all filled data for each channel/detector and axis/motor (faithful representation of the eveH5 file contents). Hence, filling is a task the :obj:`Measurement <evedata.measurement.boundaries.measurement.Measurement>` object is responsible for, calling out to the respective classes from the :mod:`controllers <evedata.measurement.controllers>` layer upon setting the data attribute.

    * Will there always be only one fill mode for one dataset?

      Currently, this seems to be the case for the interfaces (IDL, eveFile) used, although one could probably create multiple datasets with different fill modes (and different channels/detectors and axes/motors involved) from a single :obj:`EveFile <evedata.evefile.boundaries.evefile.EveFile>` object.

    * How to deal with monitors?

      It seems that currently, the monitors are not used at all/too much by the users, as they are not part of the famous pandas dataframe.

    * How to deal with channel/detector snapshots?

      Currently, fill modes do not care about channel/detector snapshots, as channel/detector values are never filled. So what is the purpose of these snapshots, and are they (currently) used in any sensible way beyond recording the data? (Technically speaking, people should be able to read the data using eveFile, though...)

    * How to deal with "fancy" scans "monitoring" axes as pseudo-detectors?

      Some scans additionally "monitor" an axis by means of a pseudo-detector. This generally leads to an additional position count for reading this "detector", and without manually post-processing the filled data matrix, we end up plotting NaN vs. NaN values when trying to plot a real detector vs. the pseudo-detector reused as an axis (and as a result seeing no plotted data).

      There was the idea of "compressing" all position counts for detector reads where no axis moves in between into one position count. Can we make sure that this is valid in all cases?

      In context of mapping such scans beforehand in the :mod:`evefile <evedata.evefile>` subpackage to more appropriate data objects, *i.e.* with multiple values per position, the problem should be solved.


If filling is an operation on an :obj:`evefile.evefile.EveFile` object returning a :obj:`dataset.dataset.Dataset` object, how to call this operation and from where? One possibility would be to have a :meth:`evefile.evefile.EveFile.fill` method that takes an appropriate argument for the fill mode, another option would be a method of the :class:`dataset.dataset.Dataset` class or an implicit call when getting data from a file (via an :obj:`evefile.evefile.EveFile` object).



Mapping timestamps to position counts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    This has been discussed as part of the :mod:`evefile.controllers <evedata.evefile.controllers>` subpackage before and was recently moved here to the :mod:`measurement.controllers <evedata.measurement.controllers>` subpackage.


.. admonition:: Points to discuss further (without claiming to be complete)

    * Mapping MonitorData to MeasureData

      Monitor data (with time in milliseconds as primary axis) need to be mapped to measured data (with position counts as primary axis). Mapping position counts to time stamps is trivial (lookup), but *vice versa* is not unique and the algorithm generally needs to be decided upon. There is an age-long discussion on this topic (`#5295 note 3 <https://redmine.ahf.ptb.de/issues/5295#note-3>`_). For a current discussion see `#7722 <https://redmine.ahf.ptb.de/issues/7722>`_.

      Besides the question how to best map one to the other (that needs to be discussed, decided, clearly documented and communicated, and eventually implemented): This mapping should most probably take place in the controllers technical layer of the measurement functional layer. The individual ``MonitorData`` class cannot do the mapping without having access to the mapping table.


For a detailed discussion/summary of the current state of affairs regarding the algorithm and its specification, see `#7722 <https://redmine.ahf.ptb.de/issues/7722>`_. In short:

* Monitors corresponding to motor axes should be mapped to the *next* position.
* Monitors corresponding to detector channels should be mapped to the *previous* position.
* For monitors corresponding to devices, there is no sensible decision possible.

Just to make things slightly more entertaining, up to eveH5 v7, monitor datasets do *not* provide any hint which type (axis, channel, device) they belong to. Hence, this decision can not be made sensibly. For safety reasons, mapping monitors to the previous position seems sensible, as the event could have occurred in the readout phase of the detectors (the position is incremented after moving the axes and before triggering the detector readout and start of nested scan modules).

The :class:`TimestampData <evedata.evefile.entities.data.TimestampData>` class got a method :meth:`get_position() <evedata.evefile.entities.data.TimestampData.get_position>` to return position counts for given timestamps. Currently, the idea is to have one method handling both, scalars and lists/arrays of values, returning the same data type, respectively.

This means that for a given :obj:`EveFile <evedata.evefile.boundaries.evefile.EveFile>` object, the controller carrying out the mapping knows to ask the :obj:`TimestampData <evedata.evefile.entities.data.TimestampData>` object via its :meth:`get_position() <evedata.evefile.entities.data.TimestampData.get_position>` method for the position counts corresponding to a given timestamp.

Special cases that need to be addressed either here or during import of the data of a monitor:

* Multiple values with timestamp ``-1``, *i.e.* *before* the scan has been started.

  Probably the best solution here would be to skip all values except of the last (newest) with the special timestamp ``-1``. See `#7688, note 10 <https://redmine.ahf.ptb.de/issues/7688#note-10>`_ for details.

* Multiple (identical) values with identical timestamp

  Not clear whether this situation can actually occur, but if so, most probably in this case only one value should be contained in the data. See `#7688, note 11 <https://redmine.ahf.ptb.de/issues/7688#note-11>`_ for details.

Furthermore, a requirement is that the original monitor data are retained when converting timestamps to position counts. This most probably means to create a new :obj:`MeasureData <evedata.evefile.entities.data.MeasureData>` object. This is the case for the additional :obj:`DeviceData <evedata.evefile.entities.data.DeviceData>` class as subclass of :obj:`MeasureData <evedata.evefile.entities.data.MeasureData>`. The next question: Where to place these new objects in the :class:`File <evedata.evefile.entities.file.File>` class of the :mod:`evedata.evefile.entities.file` module? Alternatively: Would this be something outside the evefile subpackage, probably within the measurement subpackage?


Boundaries
----------

What may be in here:

* facade: Measurement

  * Interface towards users (*i.e.*, mainly the ``radiometry`` and ``evedataviewer`` packages)
  * Given a filename of an eveH5 file, returns a ``Measurement`` object.

* resources:

  * Saver to (to be defined) standard format
  * Exporters for different formats


measurement module (facade)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :class:`Measurement <evedata.measurement.boundaries.measurement.Measurement>` facade is/will be the main entry point to the ``evedata`` package and hence the main interface both, for ``evedataviewer`` and ``radiometry`` packages as well as for human users. Technically speaking, you are free to extract individual data from the structure and do whatever you like with it. However, one big difference between the current state of affairs and the ``evedata`` package is the :obj:`Measurement <evedata.measurement.boundaries.measurement.Measurement>` object as a central unit containing all relevant information.


.. _fig-uml_evedata.measurement.boundaries.measurement:

.. figure:: uml/evedata.measurement.boundaries.measurement.*
    :align: center

    Class hierarchy of the :mod:`measurement.boundaries.measurement <evedata.measurement.entities.measurement>` module. The :class:`Measurement <evedata.measurement.boundaries.measurement.Measurement>` facade inherits directly from its entities counterpart. The crucial extension here is the :attr:`data <evedata.measurement.boundaries.measurement.Measurement.data>` attribute. This contains the actual data that should be plotted or processed further. Thus, the :class:`Measurement <evedata.measurement.boundaries.measurement.Measurement>` facade resembles the dataset concept known from the ASpecD framework and underlying, *i.a.*, the ``radiometry`` package. The :meth:`Measurement.set_axes() <evedata.measurement.boundaries.measurement.Measurement.set_axes>` method takes care of filling (of the axes) if necessary. Furthermore, you can set the attribute of the underlying data object to obtain the data from, if it is not ``data``, but, *e.g.*, ``std`` or an option.


A few comments on the :class:`Measurement <evedata.measurement.boundaries.measurement.Measurement>` facade:

* The big difference to the :class:`Measurement entity <evedata.measurement.entities.measurement.Measurement>` is the additional attribute ``data``. It contains the actual data that should be plotted or processed further. Thus, the :class:`Measurement <evedata.measurement.boundaries.measurement.Measurement>` facade resembles the dataset concept known from the ASpecD framework and underlying, *i.a.*, the ``radiometry`` package.
* The ``data`` attribute will usually be pre-filled with the data from the "preferred_axis" and "preferred_channel" attributes of the eveH5 file, if present. They can be set/changed using the :meth:`Measurement.set_data() <evedata.measurement.boundaries.measurement.Measurement.set_data>` and :meth:`Measurement.set_axes() <evedata.measurement.boundaries.measurement.Measurement.set_axes>` methods.
* The :meth:`Measurement.set_data() <evedata.measurement.boundaries.measurement.Measurement.set_data>` method takes care of filling (of the axes) if necessary. Furthermore, you can set the attribute of the underlying data object to obtain the data from, if it is not ``data``, but, *e.g.*, ``std`` or an option. The latter is crucial, as the data model of the :mod:`evefile <evedata.evefile>` subpackage provides abstractions from the plain HDF5 datasets where options are stored as separate datasets independent of the devices they actually belong to.
* The :meth:`Measurement.set_axes() <evedata.measurement.boundaries.measurement.Measurement.set_axes>` method allows to set more than one axis, hence the ``name`` parameter is a list. How to deal with the situation that an option of a dataset should be used as axis, *e.g.* the ``AcquireTime`` of images? Have a ``field`` parameter similar to :meth:`Measurement.set_data() <evedata.measurement.boundaries.measurement.Measurement.set_data>`, but this time as list? Alternatively, allow the elements in the "name" list to be lists/tuples with name and field?
* What is the difference between the :meth:`Measurement.save() <evedata.measurement.boundaries.measurement.Measurement.save>` and :meth:`Measurement.export() <evedata.measurement.boundaries.measurement.Measurement.export>` methods? The idea is to have "save" save to a (to be defined) standard format, while "export" would export to whatever given format.


Scan
====

The overall package structure of the evedata package is shown in :numref:`Fig. %s <fig-uml_evedata>`. Furthermore, a series of (still higher-level) UML schemata for the measurement functional layer are shown below, reflecting the current state of affairs (and thinking).

The scan functional layer contains all classes necessary to represent the contents of an SCML file. The general idea behind is to have all relevant information contained in the scan description and saved together with the data in the eveH5 file at hand. The SCML file is generally stored within the eveH5 file, and it is the information used by the GUI of the measurement program. One big advantage of having the information of the SCML file as compared to the information stored in the eveH5 file itself: The structure of the scan is available, making it possible to infer much more information relevant for interpreting the data.


.. important::

    The SCML file contained in (most) eveH5 files "only" saves the scan description, not the description of the measurement station. Furthermore, it saves the SCML in a way that it can be reused directly by the measurement program, *i.e.* with variables *not* replaced. Why is this important?

    * Variables are not replaced by their actual values

      Certain fields contain the variables, but not the actual replaced values. Some of this information is currently stored in the HDF5 layer of the eveH5 files and can be read from there. This is important to have in mind when thinking about reducing the metadata stored in the HDF5 layer.

    * Only the scan description is available, with devices defined therein.

      A dynamic snapshot saves the state of *all* currently defined motors and/or detectors. However, there are usually many more motors/detectors defined in the measurement station description not appearing in the SCML file available from the eveH5 file. Hence, there is no way to generally rely on the SCML file contents for metadata corresponding to whatever dataset that exists in the HDF5 layer of the eveH5 file.

    This does *not* mean that we should save the complete description of the measurement station in the future. It is just important to be aware of this situation, particularly when (further) designing the data model(s).


One big difference between the SCML schema and the class hierarchy defined in this functional layer: As the evedata package can safely assume only ever to receive validated SCML files, some of the types of attributes are more relaxed as compared to the schema definition. This makes it much easier to map the types to standard Python types.


Entities
--------


file module
~~~~~~~~~~~

This module contains the main :class:`File <evedata.scan.entities.file.File>` class and probably as well the :class:`Plugin <evedata.scan.entities.file.Plugin>` class and its dependencies. Generally an SCML file can be split in two (three) parts: a description of the setup/instrumentation used for a scan (module :mod:`scan.entities.setup <evedata.scan.entities.setup>`) and a description of the actual scan/measurement (module :mod:`scan.entities.scan <evedata.scan.entities.scan>`). The plugins would be the third part.


.. figure:: uml/evedata.scan.entities.file.*
    :align: center

    Class hierarchy of the :mod:`scan.entities.file <evedata.scan.entities.file>` module, closely resembling the schema of the SCML file. Currently, the location of the :class:`Plugin` class and its dependencies is not decided, as it is not entirely clear whether this information is relevant enough to be mapped. For a class diagram see the separate figure below.


.. figure:: uml/evedata.scan.entities.plugin.*
    :align: center

    Class hierarchy of the :class:`Plugin` class, probably located in the module :mod:`scan.entities.file <evedata.scan.entities.file>` module and closely resembling the schema of the SCML file. Currently, the location of the :class:`Plugin` class and its dependencies is not decided, as it is not entirely clear whether this information is relevant enough to be mapped.


.. admonition:: Points to discuss further (without claiming to be complete)

    * Storing the plain XML

      Is there a need to store the plain XML file somewhere? Or would it be sufficient to extract it (again) when needed from the eveH5 file?

    * Moving "Plugin" to its own module for consistency?

      "Scan" and "Setup" are contained in their own modules, as is "Plot" and "Event" that are both used in "Scan".


scan module
~~~~~~~~~~~

This module contains all classes storing information on the actual scan. An SCML file can contain exactly one scan. Furthermore, as has been decided to remove multiple chains in one scan, and hence the concept of chains altogether, the hierarchy is a bit simpler as compared to the current (Version 9.2, as of 04/2024) SCML XML schema. One scan consists of *n* scan modules.

To slightly reduce the already rather complex list of classes, plots, events, and pause conditions have been outsourced into separate modules, with the latter two together in one module. These modules are described separately below.


.. figure:: uml/evedata.scan.entities.scan.*
    :align: center
    :width: 750px

    Class hierarchy of the :mod:`scan.entities.scan <evedata.scan.entities.scan>` module, closely resembling the schema of the SCML file. As the scan module is already quite complicated, event and plot-related classes have been separated into their own modules and are described below. Hint: For a larger view, you may open the image in a separate tab. As it is vectorised (SVG), it scales well.


.. admonition:: Points to discuss further (without claiming to be complete)

    * Controller class

      The Controller class is part of the Scan, Positioning, and ScanModuleAxis classes, and referred to from attributes named "plugin" (or "saveplugin" in case of Scan). Why the different naming?


plot module
~~~~~~~~~~~


.. figure:: uml/evedata.scan.entities.plot.*
    :align: center

    Class hierarchy of the :mod:`scan.entities.plot <evedata.scan.entities.plot>` module, closely resembling the schema of the SCML file. One ClassicScanModule class can have *n* plots. For the context of the ClassicScanModule, see the :mod:`scan.entities.scan <evedata.scan.entities.scan>` module.


event module
~~~~~~~~~~~~


.. figure:: uml/evedata.scan.entities.event.*
    :align: center

    Class hierarchy of the :mod:`scan.entities.event <evedata.scan.entities.event>` module, closely resembling the schema of the SCML file. The "Event" and "PauseCondition" classes have both close ties with the "scml.scan" module. Grouping them in one module seems justified, as eventually, a "PauseCondition" could be understood as an event, too.


setup module
~~~~~~~~~~~~


.. figure:: uml/evedata.scan.entities.setup.*
    :align: center
    :width: 750px

    Class hierarchy of the :mod:`scan.entities.setup <evedata.scan.entities.setup>` module, closely resembling the schema of the SCML file. Differing from the SCML schema definition, an additional class :class:`Setup <evedata.scan.entities.setup.Scan>` is introduced here containing objects of the subclasses "Detector, "Motor", and "Device" of "AbstractDevice". The SCML schema contains these three at the same level as "Scan" and "Plugins".


.. admonition:: Points to discuss further (without claiming to be complete)

    * Better name for "Device"?

      All three, Detector, Motor and Device (as well as Axis and Channel, and Option), are abstract devices.

    * Information on the individual devices

      Is there somewhere (*e.g.* in the SCML file) more information on the individual devices, such as the exact type and manufacturer for commercial devices? This might be relevant in terms of traceability of changes in the setup.

      Looks like as of now there is no such information stored anywhere. It might be rather straight-forward to expand the SCML schema for this purpose, not affecting the GUI or engine (both do not care about this information).


Controllers
-----------

What may be in here:

* mapping different versions of SCML files to the entities


version_mapping module
~~~~~~~~~~~~~~~~~~~~~~


Boundaries
----------

What may be in here:

* facades:

  * scan
  * (setup)

* resources:

  * scml

    * reading separate SCML files if present (https://redmine.ahf.ptb.de/issues/2740)


scan module (facade)
~~~~~~~~~~~~~~~~~~~~


.. figure:: uml/evedata.scan.boundaries.scan.*
    :align: center

    Class hierarchy of the :mod:`scan.boundaries.scan <evedata.scan.boundaries.scan>` module, providing the facades for the scan and setup descriptions. Currently, the basic idea is to inherit from the :class:`Scan <evedata.scan.entities.scan.Scan>` and :class:`Setup <evedata.scan.entities.setup.Setup>` entities and extend them accordingly, adding behaviour and implementing the :class:`File <evedata.scan.boundaries.scan.File>` interface.


scml module (resource)
~~~~~~~~~~~~~~~~~~~~~~
