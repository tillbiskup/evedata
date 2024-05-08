============
Architecture
============

Each software has some kind of architecture, and this is the place to describe it in broad terms, to make it easier for developers to get around the code. Following the scheme of a layered architecture as featured by the "Clean Architecture" (Robert Martin) or the "hexagonal architecture", alternatively known as "ports and adapters" (Alistair Cockburn), the different layers are described successively from the inside out.

Just to make matters a bit more interesting, the evedata package has basically **two disjunct interfaces**: one towards the data file format (eveH5), the other towards the users of the actual data, *e.g.* the ``radiometry`` and ``evedataviewer`` packages. See :numref:`Fig. %s <fig-uml_evedata_in_context>` for a first overview.


.. _fig-uml_evedata_in_context:

.. figure:: uml/evedata-in-context.*
    :align: center

    The two interfaces of the evedata package: eveH5 is the persistence layer of the recorded data and metadata, and evedataviewer and radiometry are Python packages for graphically displaying and processing and analysing these data, respectively. Most people concerned with the actual data will use either use evedataviewer or the radiometry package, but not evedata directly.


An alternative view that may be more helpful in the long run, leading to a better overall architecture, rests on the distinction between two dimensions of layers: functional and technical. While for long time, the first line of organisation in code was technical layers, grouping software into functional blocks (packages or whatever the name) that are each independently technically layered preserves the concepts of the application much better. A first idea for the evedata package is presented in :numref:`Fig. %s <fig-architecture_layers_technical_functional>`.

.. _fig-architecture_layers_technical_functional:

.. figure:: images/architecture-layers-technical-functional.*
    :align: center

    A two-dimensional view of the architecture, with technical and functional layers. The primary line of organisation in the code, according to different authors, should be the functional layers or packages, and each of the functional blocks should be organised into three technical layers: boundaries, controllers, entities. The idea and name of these three technical layers goes back to Ivar Jacobson (1992). The boundaries (sometimes called interfaces) contain two different kinds of elements: facades and resources. While resources are typically concerned with the persistence layer and similar things, facades are the user-facing elements providing access to the underlying entities and controllers.


A corresponding UML package diagram is shown in the figure below:

.. _fig-uml_evedata:

.. figure:: uml/evedata-functional-layers.*
    :align: center

    An UML package diagram of the evedata package following the organisation in functional layers that each contain three technical layers, as shown in :numref:`Fig. %s <fig-architecture_layers_technical_functional>`. To hide the names of the technical layers from the user, one could think of importing the relevant classes (basically the facades) in the ``__init__.py`` files of the respective top-level functional packages.


For each of the functional layers, the corresponding technical layers are described below. Deviating from the direction of dependencies as shown in :numref:`Fig. %s <fig-architecture_layers_technical_functional>`, we start with the evefile functional layer, and for each of the layers we start with the entities and proceed via the controllers to the boundaries. From a user perspective interested in measured data, the journey starts with the data file (eveH5), represented on a low level by the evefile functional layer and on a high level as user interface by the dataset functional layer. The measurement functional layer representing the information originally contained in the SCML file, while technically at the bottom of the dependencies chain, is the least interesting from a user's perspective primarily interested in the data, and is probably the layer fully implemented last.


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

Generally, the evefile functional layer, as mentioned already in the :doc:`Concepts <concepts>` section, provides the interface towards the persistence layer (eveH5 files). This is a rather low-level interface focussing at a faithful representation of all information available in an eveH5 file as well as the corresponding scan description (SCML), as long as the latter is available.

Furthermore, the evefile functional layer provides a stable abstraction of the contents of an eveH5 file and is hence *not* concerned with different versions of both, the eveH5 file structure and the SCML schema. The data model provided via its entities needs to be powerful (and modular) enough to allow for representing all currently existing data files (regardless of their eveH5 and SCML schema versions) and future-proof to not change incompatibly (open-closed principle, the "O" in "SOLID) when new requirements arise.


.. important::

    As the evefile functional layer is *not* meant as a (human-facing) user interface, it is *not* concerned with concepts such as fill modes, but represents the data "as is". This means that the different data can generally not be plotted against each other. This is a deliberate decision, as filling data for a (two-dimensional) data array, although generally desirable for (simple) plotting purposes, masks/removes some highly important information, *e.g.* whether a value has not been measured in the first place, or whether obtaining a value has failed for some reason.


.. note::

    Given that in the future (starting with the adoption of the evedata package) the full contents of the SCML file will be made available to the users of eveH5 files, the amount of metadata present in the HDF5 layer of eveH5 files may probably be reduced. How would this impact the data model developed within the ``evefile`` subpackage? Furthermore: Would it be wise to (dramatically) reduce the metadata (attributes in HDF5 language) of the individual datasets on the HDF5 level? After all, one big advantage of the HDF5 format (besides its support for hierarchical organisation) is its capability to amend data with metadata, *i.e.* being potentially "self-describing".


Entities
--------



file module
~~~~~~~~~~~

Despite the opposite chain of dependencies, starting with the ``file`` module seems sensible, as its ``File`` class represents a single eveH5 file and provides kind of an entry point.


.. figure:: uml/evedata.evefile.file.*
    :align: center

    Class hierarchy of the evefile.file module. The EveFile class is sort of the central interface to the entire subpackage, as this class provides a faithful representation of all information available from a given eveH5 file. To this end, it incorporates instances of classes of the other modules of the subpackage.


.. admonition:: Points to discuss further (without claiming to be complete)

    * Monitors

      It turned out that we most probably need to distinguish between datasets from the standard and snapshot sections, as datasets on the HDF5 level can have identical names in both sections (and for good reasons). Hence, the current data model has two attributes/lists: data (for datasets of the standard section) and snapshots (for datasets of the snapshot section).

      How to deal with monitors? It seems more consistent and logical to separate them into their own list as well, at least on the evefile subpackage level. This would relax the discussion as of how to map monitor timestamps to position counts, as monitors would be once more marked as clearly different from motors/detectors.

    * Comments

      Is there a need to distinguish between file-level comments and life comments (aka log messages)? If so, shall this be done in the ``EveFile`` class or in the ``Comment`` class (possibly by means of two subtypes of the ``Comment`` class)?


data module
~~~~~~~~~~~

Data are organised in "datasets" within HDF5, and the ``evefile.data`` module provides the relevant entities to describe these datasets. Although currently (as of 03/2024, eve version 2.0) neither average nor interval detectors save the individual data points, at least the former is a clear need of the engineers/scientists (see their use of the MPSKIP feature to "fake" an average detector saving the individual data points). Hence, the data model already respects this use case. As per position (count) there can be a variable number of measured points, the resulting array is no longer rectangular, but a "ragged array". While storing such arrays is possible directly in HDF5, the implementation within evedata is entirely independent of the actual representation in the eveH5 file.


.. figure:: uml/evedata.evefile.data.*
    :align: center
    :width: 750px

    Class hierarchy of the evefile.data module. Each class has a corresponding metadata class in the evefile.metadata module. While in this diagram, MotorData and DetectorData seem to have no difference, they have a different type of metadata (see the evefile.metadata module below). Generally, having different types serves to discriminate where necessary between detector channels and motor axes.


.. admonition:: Points to discuss further (without claiming to be complete)

    * Mapping MonitorData to MeasureData

      Monitor data (with time in milliseconds as primary axis) need to be mapped to measured data (with position counts as primary axis). Mapping position counts to time stamps is trivial (lookup), but *vice versa* is not unique and the algorithm generally needs to be decided upon. There is an age-long discussion on this topic (`<https://redmine.ahf.ptb.de/issues/5295#note-3>`_). Besides the question how to best map one to the other (that needs to be discussed, decided, clearly documented and communicated, and eventually implemented): Where would this mapping take place?

      The individual ``EveMonitorData`` class cannot do the mapping without having access to the mapping table. Probably mapping is something done in the intermediate layer between the ``evefile`` and ``dataset`` subpackages and belonging to the business rules. How are monitor data represented in the :class:`Dataset` class?

    * Can MonitorData have more than one value per time?

      This would be similar to AverageDetector and IntervalDetector, thus requiring an additional attribute (and probably a ragged array).

    * Values of MonitorData

      MonitorData can have textual (non-numeric) values. This should not be too much of a problem given that numpy can handle string arrays (though <v2.0 only fixed-size string values, AFAIK, with v2.0 not yet released, as of 2024-04-04).

    * raw_values of EveAverageDetectorData and EveIntervalDetectorData

      Currently, the measurement program only collects the average values in both cases. However, there is the frequent request to collect the raw values as well. The data structure already supports this. Given that the overarching idea of the evefile subpackage is to *faithfully* represent the eveH5 file contents, it seems not sensible to map the "fake" average detector saving each individual value using MPSKIP to this detector type, though. This should probably rather be done in the mapping later on and towards the dataset subpackage.

    * Detectors that are redefined within an experiment/scan

      Generally, detectors can be redefined within an experiment/scan, *i.e.* can have different operational modes (standard/average *vs.* interval) in different scan modules. Currently, all data are stored in the identical dataset on HDF5 level and only by "informed guessing" can one deduce that they served different purposes. How to handle this situation in the future, or more important: how to deal with this in the data model described here? Currently, there seems to be no unique identifier for a detector beyond the XML-ID/PV. The simplest way would be to attach the scan module ID to the name of the HDF5 dataset for the detector.

      Generally, what seems necessary is to have separate datasets on the HDF5 level for detectors that change their type or attributes within a scan. Can we safely assume that a detector cannot change its attributes within one scan module? If so, we could have one dataset per detector and scan module, regardless of how often a scan module has been run within an overall measurement (inner scans). If the attributes (or even the type) of a detector change within a measurement, I would assume this to be a relevant information for handling the data appropriately.

    * References to spectra/images

      There are measurements where for a given position count spectra (1D) or entire images (2D) are recorded. At least for the latter, the data usually reside in external files. How is this currently represented in eveH5 files, and how to model this situation with the given :class:`EveData` classes?

      The current idea for modelling these data is reflected in the ``ExternalData`` class shown in the UML diagram above. Here, for each position count, a reference (a string with usually a filename) is stored. The corresponding ``ExternalMetadata`` class (see section below) contains information on the file format to inform an importer factory how to import the data. The only "problem": Where to store the actual data, or more precisely: how to deal with the ``values`` attribute of the ``Data`` base class? Probably best to store the references as strings in the ``values`` attribute (that is in this case a numpy string array) and have an additional attribute ``data`` for the actual data in the ``ExternalData`` class.


metadata module
~~~~~~~~~~~~~~~

Data without context (*i.e.* metadata) are mostly useless. Hence, to every class (type) of data in the evefile.data module, there exists a corresponding metadata class.


.. note::

    As compared to the UML schemata for the IDL interface, the decision of whether a certain piece of information belongs to data or metadata is slightly different here. Furthermore, there seems to be some (immutable) information currently stored in a dataset in HDF5 that could be stored as attribute - if it is truly not changing. Note, however, that detectors can be redefined during a scan, but all values are stored in the identical dataset. Latest with average and interval detector, this leads already to problems in current eveH5 files, as information what kind of detector it was when is probably lost. Hence, this situation needs to be solved more fundamentally, probably.


.. figure:: uml/evedata.evefile.metadata.*
    :align: center
    :width: 750px

    Class hierarchy of the evefile.metadata module. Each concrete class in the evefile.data module has a corresponding metadata class in this module.


A note on the ``DeviceMetadata`` interface: The eveH5 datasets corresponding to the EveTimestampMetadata and EveScanModuleMetadata classes are special in sense of having no PV and transport type nor an id. Several options have been considered to address this problem:

#. Moving these three attributes down the line and copying them multiple times (feels bad).
#. Leaving the attributes blank for the two "special" datasets (feels bad, too).
#. Introduce another class in the hierarchy, breaking the parallel to the EveData class hierarchy (potentially confusing).
#. Create a mixin class (abstract interface) with the three attributes and use multiple inheritance/implements.

As obvious from the UML diagram, the last option has been chosen. The name "DeviceMetadata" resembles the hierarchy in the ``scml.setup`` module and clearly distinguishes actual devices from datasets not containing data read from some instrument.


.. admonition:: Points to discuss further (without claiming to be complete)

    * Names of the sections

      The names of the sections are currently modelled as Enumeration ("Section"). AFAIK, the names of the sections in the eveH5 file have changed over time. What would be sensible names for the different sections? Are the sections mentioned (standard, snapshot, monitor, meta) sufficient? Is anything missing? Will there likely be more in the future?

      How about renaming STANDARD to MAIN? This would better reflect that this section contains datasets from the main part of the scan. Otherwise, one could argue in favour of STANDARD and rename the class ``ClassicScanModule`` in the scml.scan module to ``StandardScanModule``.

      About the "META" section: Given that there is the idea to have two special datasets in this section in the future, namely the PosCountTimer and a PosCountScanModule dataset, it seems sensible to have them there.

    * Monitor metadata

      Clearly, monitor metadata are not sufficiently modelled yet. In recent eveH5 files, they have only few attributes. Are the other attributes (comparable to the attributes of ``MeasureMetadata``) contained in the SCML file and could be read from there?

      Is there any sensible chance to relate monitor datasets to datasets in the standard section? Currently, it looks like the eveH5 monitor datasets have no sensible/helpful "name" attribute, only an ID that partly resembles IDs in the standard section. (And of course, there are usually monitors that do not appear in any other section, hence cannot be related to other devices/datasets.)

    * Attributes "pv" and "transport_type"

      "pv" is the EPICS process variable, transport type refers to the access mode (local vs. ca). Both are currently stored as one attribute "access" in the eveH5 datasets, separated by ":" in the form ``<transport_type>:<pv>``.

    * Metadata from SCML file

      There is more information available from the SCML file (and the end station/beam line description - but that is generally not available when reading eveH5 files if it is not contained in the SCML). How to map this to the respective metadata classes? Shall this be done here, or rather in the dataset subpackage? An argument in favour of the latter would be to keep up with the distinction HDF5/SCML.

    * Information on the individual devices

      Is there somewhere (*e.g.* in the SCML file) more information on the individual devices, such as the exact type and manufacturer for commercial devices? This might be relevant in terms of traceability of changes in the setup.

      Looks like as of now there is no such information stored anywhere. It might be rather straight-forward to expand the SCML schema for this purpose, not affecting the GUI or engine (both do not care about this information).


Controllers
-----------

What may be in here:

* mapping different versions of eveH5 files to the entities
* Converting MPSKIP scans into average detector with adaptive number of recorded points


version_mapping module
~~~~~~~~~~~~~~~~~~~~~~


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


.. admonition:: Points to discuss further (without claiming to be complete)

    * How to deal with reading the entire content of an eveH5 file at once vs. deferred reading?

      * Reading relevant metadata (*e.g.*, to decide about what data to plot) should be rather fast. And generally, only two "columns" will be displayed (as f(x,y) plot) at any given time -- at least if we don't radically change the way data are looked at compared to the IDL Cruncher.
      * If references to the internal datasets of a given HDF5 file are stored in the corresponding Python data structures (together with the HDF5 file name), one could even close the HDF5 file after each operation, such as not to have open file handles that may be problematic (but see the quote from A. Collette below).
      * However, plotting requires data to be properly filled, and this may require reading all data. See the discussion on fill modes above.


    From the book "Python and HDF5" by Andrew Collette:

        You might wonder what happens if your program crashes with open files. If the program exits with a Python exception, don't worry! The HDF library will automatically close every open file for you when the application exits.

        -- Andrew Collette, 2014 (p. 18)


evefile module (facade)
~~~~~~~~~~~~~~~~~~~~~~~

...


eveH5 module (resource)
~~~~~~~~~~~~~~~~~~~~~~~

The aim of this module is to provide a Python representation (in form of a hierarchy of objects) of the contents of an eveH5 file that can be mapped to both, the evefile and dataset interfaces. While the Python h5py package already provides the low-level access and gets used, the eveH5 module contains Python objects that are independent of an open HDF5 file, represent the hierarchy of HDF5 items (groups and datasets), and contain the attributes of each HDF5 item in form of a Python dictionary. Furthermore, each object contains a reference to both, the original HDF5 file and the HDF5 item, thus making reading dataset data on demand as simple as possible.


.. figure:: uml/evedata.io.eveH5.*
    :align: center

    Class hierarchy of the io.eveH5 module. The ``HDF5Item`` class and children represent the individual HDF5 items on a Python level, similarly to the classes provided in the h5py package, but *without* requiring an open HDF5 file. Furthermore, reading actual data (dataset values) is deferred by default.


As such, the ``HDF5Item`` class hierarchy shown above is pretty generic and should work with all eveH5 versions. However, it is *not* meant as a generic HDF5 interface, as it does make some assumptions based on the eveH5 file structure and format.


Dataset
=======

.. note::

    The name of this subpackage is most probably not final yet. Other options for naming the subpackage may be: ``measurement``, ``scan``.

    Another option would be to keep the subpackage name ``dataset``, but to import the modules into the global ``evedata`` namespace, as this subpackage is meant to be the main user interface. This would reduce *e.g.* ``evedata.dataset.dataset.Dataset`` to ``evedata.dataset.Dataset``.


The overall package structure of the evedata package is shown in :numref:`Fig. %s <fig-uml_evedata>`. Furthermore, a series of (still higher-level) UML schemata for the dataset subpackage are shown below, reflecting the current state of affairs (and thinking).

Generally, the dataset subpackage, as mentioned already in the :doc:`Concepts <concepts>` section, provides the interface towards the "user", where user mostly means the ``evedataviewer`` and ``radiometry`` packages.


.. note::

    The mapping of the information contained in both, the HDF5 and SCML layers of an eveH5 file, to the dataset is far from being properly modelled or understood. This is partly due to the step-wise progress in understanding. On a rather fundamental level, it remains to be decided whether a ``Dataset`` should allow for reconstructing how a measurement has actually been carried out (*i.e.*, provide access to the SCML and hence the anatomy of the scan).

    Part of the problem: The currently widely agreed-upon abstraction from the user perspective of the data is the infamous 2D data table incapable of conveying all or even most of the relevant information for processing and analysing the data. As long as the users do not invest the time to understand the true complexity of their data and measurements, developing whatever interface towards the data will continue to be seriously hampered.


What is the main difference between the ``evefile`` and the ``dataset`` subpackages? Basically, the information contained in an eveH5 file needs to be "interpreted" to be able to process, analyse, and plot the data. While the ``evefile`` subpackage provides the necessary data structures to faithfully represent all information contained in an eveH5 file, the ``dataset`` subpackage provides the result of an "interpretation" of this information in a way that facilitates data processing, analysis and plotting.

However, the ``dataset`` subpackage is still general enough to cope with all the different kinds of measurements the eve measurement program can deal with. Hence, it may be a wise idea to create dedicated dataset classes in the ``radiometry`` package for different types of experiments. The NeXus file format may be a good source of inspiration here, particularly their `application definitions <https://manual.nexusformat.org/classes/applications/index.html>`_. The ``evedataviewer`` package in contrast aims at displaying whatever kind of measurement has been performed using the eve measurement program. Hence it will deal directly with ``Dataset`` objects of the ``dataset`` subpackage.



.. admonition:: Arguments against the 2D data array as sensible representation

    Currently, one very common and heavily used abstraction of the data contained in an eveH5 file is a two-dimensional data array (basically a table with column headers, implemented as pandas dataframe). As it stands, many problems in the data analysis and preprocessing of data come from the inability of this abstraction to properly represent the data. Two obvious cases, where this 2D approach simply breaks down, are:

    * subscans -- essentially a 2D dataset on its own
    * adaptive average detector saving the individual, non-averaged values (implemented using MPSKIP)

    Furthermore, as soon as spectra (1D) or images (2D) are recorded for a given position (count), the 2D data array abstraction breaks down as well.

    Other problems inherent in the 2D data array abstraction are the necessary filling of values that have not been obtained. Currently, once filled there is no way to figure out for an individual position whether values have been recorded (in case of LastFill) or whether a value has not been recorded or recording failed (in case of NaNFill).



Entities
--------


dataset module
~~~~~~~~~~~~~~

Currently, the idea is to model the dataset close to the dataset in the ASpecD framework, as the core interface to all processing, analysis, and plotting routines in the ``radiometry`` package, and with a clear focus on automatically writing a full history of each processing and analysis step. Reproducibility and history are concerns of the ``radiometry`` package, the ``dataset.dataset`` module should nevertheless allow for a rather straight-forward mapping to the ASpecD-inspired dataset structure.


.. figure:: uml/evedata.dataset.dataset.*
    :align: center

    Class hierarchy of the dataset.dataset module, closely resembling the dataset concept of the ASpecD framework (while lacking the history component). For the corresponding metadata class see the dataset.metadata module.


Furthermore, the dataset should provide appropriate abstractions for things such as subscans and detector channels with adaptive averaging (*i.e.* ragged arrays as data arrays). Thus, scans currently recorded using MPSKIP could be represented as what they are (adaptive average detectors saving the individual measured data points). Similarly, the famous subscans could be represented as true 2D datasets (as long as the individual subscans all have the same length).


.. admonition:: Points to discuss further (without claiming to be complete)

    * How to handle data filling? (But: see discussion on fill modes in the section below)

      * Obviously, if one wants to plot arbitrary HDF5 datasets against each other (as currently possible), data (*i.e.* axes) need to be made compatible.
      * The original values should always be retained, to be able to show/tell which values have actually been obtained (and to discriminate between not recorded and failed to record, *i.e.* no entry vs. NaN in the original HDF5 dataset)
      * Could there be different (and changing) filling of the data depending on which "axes" should be plotted against each other?

    * Do we care here about reproducibility, *i.e.* a history?

      * Background: In the ASpecD framework, reproducibility is an essential concept, and this revolves about having a dataset with one clear data array and *n* corresponding axes. The original data array is stored internally, making undo and redo possible, and each processing and analysis step always operates on the (current state of the) data array. In case of the datasets we deal with here, there is usually no such thing as the one obvious data array, and users can at any time decide to focus on another set of "axes", *i.e.* data and corresponding axis values, to operate on.
      * One option would be to *not* deal with the concept of reproducibility here, but delegate this to the ``radiometry`` package. There, the first step would be to decide which of the available channels accounts as the "primary" data (if not set as preferred in the scan already and read from the eveH5 file accordingly).

    * How to deal with images stored in files separate from the eveH5 file?

      * The evefile subpackage will most probably only provide the links (*i.e.* filenames) to these files, but nothing else.
      * Should these files be imported into the dataset already and made available? Probably, the same discussion as that regarding importing data from the eveH5 file (reading everything at once or deferred reading on demand, see section on interfaces below) applies here as well.

    * How to deal with monitors?

      * Add an ``events`` attribute to the ``Dataset`` class? It might be an interesting use case to have a list of "events" (aka values for the different monitors) in chronological order, and similar to the monitors themselves, they should be mappable to the position counts. This would allow for a display of arbitrary data together with (relevant) events.


metadata module
~~~~~~~~~~~~~~~

The (original) idea behind this module stems from the ASpecD framework and its representation of a dataset. There, a dataset contains data (with corresponding axes), metadata (of different kind, such as measurement metadata and device metadata), and a history.


.. figure:: uml/evedata.dataset.metadata.*
    :align: center
    :width: 750px

    Class hierarchy of the dataset.metadata module, closely resembling the dataset concept of the ASpecD framework and the current rough implementation in the evedataviewer package. For the corresponding dataset class see the dataset.dataset module.


In the given context of the evedata package, this would mean to separate data and metadata for the different datasets as represented in the eveH5 file, and store the data (as "device data") in the dataset, the "primary" data as data, and the corresponding metadata as a composition of metadata classes in the Dataset.metadata attribute. Not yet sure whether this makes sense.

The contents of the SCML file could be represented in the ``Metadata`` class as well, probably/perhaps split into separate fields for the different areas of an SCML file (setup, aka devices, and scan). Whether to directly use the classes representing the SCML file contents or to further abstract needs to be decided at some point.


Controllers
-----------

What may be in here:

* Fill modes
* Mapping monitor time stamps to position counts
* Converting scan with subscans into appropriate subscan data structure
* Mapping between ``EveFile`` and ``Dataset`` objects, *i.e.* low-level and high-level interface

  * Assumes a 1:1 mapping between files and datasets (for the time being)

* mapping the eveH5 and SCML contents to the data structures of the evefile subpackage


.. admonition:: Points to discuss further (without claiming to be complete)

    * Monitors

      * How to map monitors (with time as primary axis) to other devices (motors or detectors, with position counts as primary axis)?


Fill modes
~~~~~~~~~~

For each motor and detector, in the original eveH5 file only those values appear---typically together with a "position counter" (PosCount) value---that are actually set or measured. Hence, the number of values (*i.e.*, the length of the data vector) will generally be different for different detectors/channels and devices/axes. To be able to plot arbitrary data against each other, the corresponding data vectors need to be brought to the same dimensions (*i.e.*, "filled").

Currently, there are four fill modes available for data: NoFill, LastFill, NaNFill, LastNaNFill. From the `documentation of eveFile <https://www.ahf.ptb.de/messpl/sw/python/common/eveFile/doc/html/Section-Fillmode.html#evefile.Fillmode>`_:


NoFill
    Use only data from positions where at least one axis and one channel have values.

LastFill
    Use all channel data and fill in the last known position for all axes without values.

NaNFill
    Use all axis data and fill in NaN for all channels without values.

LastNaNFill
    Use all data and fill in NaN for all channels without values and fill in the last known position for all axes without values.


Furthermore, for the Last*Fill modes, snapshots are inspected for axes values that are newer than the last recorded axis in the main/standard section.

Note that none of the fill modes guarantees that there are no NaNs (or comparable null values) in the resulting data.


.. important::

    The IDL Cruncher seems to use LastNaNFill combined with applying some "dirty" fixes to account for scans using MPSKIP and those scans "monitoring" a motor position via a pseudo-detector. The ``EveHDF`` class (DS) uses LastNaNFill as a default as well but does *not* apply some additional post-processing.

    Shall fill modes be something to change in a viewer? And which fill modes are used in practice (and do we have any chance to find this out)?


For numpy set operations, see in particular :func:`numpy.intersect1d` and :func:`numpy.union1d`. Operating on more than two arrays can be done using :func:`functools.reduce`, as mentioned in the numpy documentation (with examples).


.. admonition:: Points to discuss further (without claiming to be complete)

    * Which fill modes are relevant/needed?

      It seems that LastNaNFill is widely used as a default fill mode. Depending on the origin of the data, additional post-processing (see below) is necessary to have usable data.

      As NoFill does not only not fill, but actually reduce data, "fill mode" may not be the ideal term. Other opinions/ideas/names?

      Given that the :class:`evefile.evefile.Evefile` class provides a faithful representation of the actual data contained in an eveH5 file, one could think of mechanisms to highlight those values that were actually recorded (as compared to filled afterwards). Would this help to reduce the number of fill modes available?

    * How to cope with the current practice of applying (dirty) fixes to the already filled data to account for such things as scans using MPSKIP?

      In case of the MPSKIP scans, this is "faking" an average detector adaptively recording the individual data points. Hence, it should probably be represented already on the :class:`evefile.evefile.EveFile` level as such a detector. How does this agree with the idea of a "faithful representation" of the eveH5 file contents?

      Anyway: Is this a fill-mode related topic? And where does it belong to?

    * Where/when to apply filling?

      The :class:`evefile.evefile.EveFile` class contains the data *as read* from the eveH5 file, *i.e.* the not at all filled data for each channel/detector and axis/motor (faithful representation of the eveH5 file contents). Hence, filling is a task performed when transitioning to a :obj:`dataset.dataset.Dataset` object with data read from an eveH5 file (and originally stored in an :obj:`evefile.evefile.EveFile` object).

      Is filling always necessary when creating a :obj:`dataset.dataset.Dataset` object? Probably yes, as otherwise, plotting will usually not be possible (except detector/motor values *vs.* position count).

    * Will there always be only one fill mode for one dataset?

      Currently, this seems to be the case for the interfaces (IDL, eveFile) used, although one could probably create multiple datasets with different fill modes (and different channels/detectors and axes/motors involved) from a single ``EveFile`` object.

    * How to deal with "lazy loading" combined with filling?

      For filling any axis, we need to have the position counts of *all* HDF5 datasets (aka :obj:`evefile.data.EveData` objects). This seems to contradict the idea of *not* reading all data at once before filling.

      Of course, if one uses the preferred channel/detector and axis/motor (and there are "established" ways how to determine those if they are not set in the eveH5 file explicitly, though this most probably involves again accessing *all* data), one could only fill those and refill once a user wants to see something different. However, this would imply changing the fill mode "on the fly". If the original :obj:`evefile.evefile.EveFile` object is gone by then, the relevant information may no longer be available, resulting in reimporting the data from the original eveH5 file.

    * How to deal with monitors?

      It seems that currently, the monitors are not used at all/too much by the users, as they are not part of the famous pandas dataframe.

    * How to deal with channel/detector snapshots?

      Currently, fill modes do not care about channel/detector snapshots, as channel/detector values are never filled. So what is the purpose of these snapshots, and are they (currently) used in any sensible way beyond recording the data? (Technically speaking, people should be able to read the data using eveFile, though...)

    * How to deal with "fancy" scans "monitoring" axes as pseudo-detectors?

      Some scans additionally "monitor" an axis by means of a pseudo-detector. This generally leads to an additional position count for reading this "detector", and without manually post-processing the filled data matrix, we end up plotting NaN vs. NaN values when trying to plot a real detector vs. the pseudo-detector reused as an axis (and as a result seeing no plotted data).

      There was the idea of "compressing" all position counts for detector reads where no axis moves in between into one position count. Can we make sure that this is valid in all cases?


If filling is an operation on an :obj:`evefile.evefile.EveFile` object returning a :obj:`dataset.dataset.Dataset` object, how to call this operation and from where? One possibility would be to have a :meth:`evefile.evefile.EveFile.fill` method that takes an appropriate argument for the fill mode, another option would be a method of the :class:`dataset.dataset.Dataset` class or an implicit call when getting data from a file (via an :obj:`evefile.evefile.EveFile` object).


Boundaries
----------

What may be in here:

* facade: dataset

  * Interface towards users (*i.e.*, mainly the ``radiometry`` and ``evedataviewer`` packages)
  * Given a filename of an eveH5 file, returns a ``Dataset`` object.


dataset module (facade)
~~~~~~~~~~~~~~~~~~~~~~~


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

This module contains the main ``SCML`` class and probably as well the ``Plugin`` class and its dependencies. Generally an SCML file can be split in two (three) parts: a description of the setup/instrumentation used for a scan (module ``scml.setup``) and a description of the actual scan/measurement (module ``scml.scan``). The plugins would be the third part.


.. figure:: uml/evedata.scml.file.*
    :align: center

    Class hierarchy of the scml.file module, closely resembling the schema of the SCML file. Currently, the location of the "Plugin" class and its dependencies is not decided, as it is not entirely clear whether this information is relevant enough to be mapped. For a class diagram see the separate figure below.


.. figure:: uml/evedata.scml.plugin.*
    :align: center

    Class hierarchy of the "Plugin" class, probably located in the scml.scml module and closely resembling the schema of the SCML file. Currently, the location of the "Plugin" class and its dependencies is not decided, as it is not entirely clear whether this information is relevant enough to be mapped.


.. admonition:: Points to discuss further (without claiming to be complete)

    * Storing the plain XML

      Is there a need to store the plain XML file somewhere? Or would it be sufficient to extract it (again) when needed from the eveH5 file?

    * Moving "Plugin" to its own module for consistency?

      "Scan" and "Setup" are contained in their own modules, as is "Plot" and "Event" that are both used in "Scan".


scan module
~~~~~~~~~~~

This module contains all classes storing information on the actual scan. An SCML file can contain exactly one scan. Furthermore, as has been decided to remove multiple chains in one scan, and hence the concept of chains altogether, the hierarchy is a bit simpler as compared to the current (Version 9.2, as of 04/2024) SCML XML schema. One scan consists of *n* scan modules.

To slightly reduce the already rather complex list of classes, plots, events, and pause conditions have been outsourced into separate modules, with the latter two together in one module. These modules are described separately below.


.. figure:: uml/evedata.scml.scan.*
    :align: center
    :width: 750px

    Class hierarchy of the scml.scan module, closely resembling the schema of the SCML file. As the scan module is already quite complicated, event and plot-related classes have been separated into their own modules and are described below. Hint: For a larger view, you may open the image in a separate tab. As it is vectorised (SVG), it scales well.


.. admonition:: Points to discuss further (without claiming to be complete)

    * Controller class

      The Controller class is part of the Scan, Positioning, and ScanModuleAxis classes, and referred to from attributes named "plugin" (or "saveplugin" in case of Scan). Why the different naming?


plot module
~~~~~~~~~~~


.. figure:: uml/evedata.scml.plot.*
    :align: center

    Class hierarchy of the scml.plot module, closely resembling the schema of the SCML file. One ClassicScanModule class can have *n* plots. For the context of the ClassicScanModule, see the "scml.scan" module.


event module
~~~~~~~~~~~~


.. figure:: uml/evedata.scml.event.*
    :align: center

    Class hierarchy of the scml.event module, closely resembling the schema of the SCML file. The "Event" and "PauseCondition" classes have both close ties with the "scml.scan" module. Grouping them in one module seems justified, as eventually, a "PauseCondition" could be understood as an event, too.


setup module
~~~~~~~~~~~~


.. figure:: uml/evedata.scml.setup.*
    :align: center
    :width: 750px

    Class hierarchy of the scml.setup module, closely resembling the schema of the SCML file. Differing from the SCML schema definition, an additional class ``Setup`` is introduced here containing objects of the subclasses "Detector, "Motor", and "Device" of "AbstractDevice". The SCML schema contains these three at the same level as "Scan" and "Plugins".


.. admonition:: Points to discuss further (without claiming to be complete)

    * Better name for "Device"?

      All three, Detector, Motor and Device (as well as Axis and Channel, and Option), are abstract devices.


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


scml module (resource)
~~~~~~~~~~~~~~~~~~~~~~
