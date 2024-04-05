============
Architecture
============

Each software has some kind of architecture, and this is the place to describe it in broad terms, to make it easier for developers to get around the code. Following the scheme of a layered architecture as featured by the "Clean Architecture" (Robert Martin) or the "hexagonal architecture", alternatively known as "ports and adapters" (Alistair Cockburn), the different layers are described successively from the inside out.

Just to make matters a bit more interesting, the evedata package has basically **two disjunct interfaces**: one towards the data file format (eveH5), the other towards the users of the actual data, *e.g.* the ``radiometry`` and ``evedataviewer`` packages. Most probably, these two interfaces will be separated into different subpackages.


.. _fig-uml_evedata:

.. figure:: uml/evedata.*
    :align: center

    A high-level view of the different subpackages of the evedata package, currently reflecting the two interfaces. For details, see further schemata below. While "evefile" will most probably be the name of the subpackage interfacing the eveH5 files, the name of the "dataset" subpackage is not final yet.


Core domain
===========

The core domain contains the central entities and their abstract interactions, or, in terms of the "Domain Driven Design" (Eric Evans), the implementation of the abstract model of the application.

In the evedata package, due to being split into two separate subpackages, each of them has its own core domain that will be described below.


evefile subpackage
------------------

The overall package structure of the evedata package is shown in :numref:`Fig. %s <fig-uml_evedata>`. Hereafter, a series of (still higher-level) UML schemata for the evefile subpackage are shown, reflecting the current state of affairs (and thinking).

Generally, the evefile subpackage, as mentioned already in the :doc:`Concepts <concepts>` section, provides the interface towards the persistence layer (eveH5 files). This is a rather low-level interface focussing at a faithful representation of all information available in an eveH5 file as well as the corresponding scan description (SCML), as long as the latter is available.

Furthermore, the evefile subpackage provides a stable abstraction of the contents of an eveH5 file and is hence *not* concerned with different versions of both, the eveH5 file structure and the SCML schema. The data model provided here needs to be powerful (and modular) enough to allow for representing all currently existing data files (regardless of their eveH5 and SCML schema versions) and future-proof to not change incompatibly (open-closed principle, the "O" in "SOLID) when new requirements arise.


.. important::

    As the evefile subpackage is *not* meant as a (human-facing) user interface, it is *not* concerned with concepts such as fill modes, but represents the data "as is". This means that the different data can generally not be plotted against each other. This is a deliberate decision, as filling data for a (two-dimensional) data array, although generally desirable for (simple) plotting purposes, masks/removes some highly important information, *e.g.* whether a value has not been measured in the first place, or whether obtaining a value has failed for some reason.


As usual, the core domain provides the (abstract) entities representing the different types of content. Hence, it is *not* concerned with the actual layout of an eveH5 file nor any importers nor the mapping of different eveH5 schema versions.


.. note::

    Shall we rename the modules omitting the "eve" prefix, as this context is already given by ``evefile`` (and the "Eve" prefix of most classes contained therein)? This would imply the following renamings::

        evefile.evefile     => evefile.file
        evefile.evedata     => evefile.data
        evefile.evemetadata => evefile.metadata


    Omitting the "Eve" prefix for the class names may be a bad idea, though, as with the prefix, it is always obvious whether we are dealing with an evefile-related class or the user-facing dataset-centric abstraction.


evefile.evefile module
~~~~~~~~~~~~~~~~~~~~~~

Despite the opposite chain of dependencies, starting with the ``evefile.evefile`` module seems sensible, as its ``EveFile`` class represents a single eveH5 file and provides kind of an entry point.


.. figure:: uml/evedata.evefile.evefile.*
    :align: center

    Class hierarchy of the evefile.evefile module. The EveFile class is sort of the central interface to the entire subpackage, as this class provides a faithful representation of all information available from a given eveH5 file. To this end, it incorporates instances of classes of the other modules of the subpackage.


.. note::

    Most probably, once digging deeper into the SCML, this class will be moved to its own module and become a composition of a series of other classes, each reflecting the building blocks of a scan description (in SCML).


.. admonition:: Points to discuss further (without claiming to be complete)

    * Split data according to sections (standard, monitor, snapshot)?

      At least the HDF5 datasets in the "monitor" section are clearly distinct from the others, as they don't have PosCounts as reference axis. However, due to the different classes, making the separation would be trivial and possible using, *e.g.*, a list comprehension in Python.

    * SCML: How to represent the contents sensibly? What are the relevant abstractions/concepts?

      Perhaps (additionally) storing the "plain" XML in a variable is still a sensible idea.

    * Comments

      Is there a need to distinguish between file-level comments and life comments (aka log messages)? If so, shall this be done in the ``EveFile`` class or in the ``Comment`` class (possibly by means of two subtypes of the ``Comment`` class)?


evefile.evedata module
~~~~~~~~~~~~~~~~~~~~~~

Data are organised in "datasets" within HDF5, and the ``evefile.evedata`` module provides the relevant entities to describe these datasets. Although currently (as of 03/2024, eve version 2.0) neither average nor interval detectors save the individual data points, at least the former is a clear need of the engineers/scientists (see their use of the MPSKIP feature to "fake" an average detector saving the individual data points). Hence, the data model already respects this use case. As per position (count) there can be a variable number of measured points, the resulting array is no longer rectangular, but a "ragged array". While storing such arrays is possible directly in HDF5, the implementation within evedata is entirely independent of the actual representation in the eveH5 file.


.. figure:: uml/evedata.evefile.evedata.*
    :align: center

    Class hierarchy of the evefile.evedata module. Each class has a corresponding metadata class in the evefile.evemetadata module. While in this diagram, EveMotorData and EveDetectorData seem to have no difference, at least they have a different type of metadata (see the evefile.evemetadata module below), besides the type attribute set accordingly.


.. admonition:: Points to discuss further (without claiming to be complete)

    * Dealing with the "PosCountTimer" dataset in the timestamp/meta section

      There is one special dataset in an eveH5 file containing the mapping table between Position Counts and milliseconds since start of the scan. Does this need to be represented by a distinct subclass of ``EveData``? Or would it better be a subclass of ``EveMeasureData``? And what would be a sensible name? ``EvePosCountTimerData``?

      What DeviceType entry shall this special dataset have? Is it a separate type of its own ("TIMESTAMP"?), or is it a "DUMB" device?

    * Mapping MonitorData to MeasureData

      There is an age-long discussion how to map monitor data (with time in milliseconds as primary axis) to measured data (with position counts as primary axis). Besides the question how to best map one to the other (that needs to be discussed, decided, clearly documented and communicated, and eventually implemented): Where would this mapping take place? Here in the evefile subpackage? Or in the "convenience interface" layer, *i.e.* the dataset subpackage?

      Mapping position counts to time stamps is trivial (lookup), but *vice versa* is not unique and the algorithm generally needs to be decided upon.

      The individual ``EveMonitorData`` class cannot do the mapping without having access to the mapping table. Probably mapping is something done in the intermediate layer between the ``evefile`` and ``dataset`` subpackages and belonging to the business rules. How are monitor data represented in the :class:`Dataset` class?

    * Can MonitorData have more than one value per time?

      This would be similar to AverageDetector and IntervalDetector, thus requiring an additional attribute (and probably a ragged array).

    * Values of MonitorData

      MonitorData can have textual (non-numeric) values. This should not be too much of a problem given that numpy can handle string arrays (though <v2.0 only fixed-size string values, AFAIK, with v2.0 not yet released, as of 2024-04-04).

    * raw_values of EveAverageDetectorData and EveIntervalDetectorData

      Currently, the measurement program only collects the average values in both cases. However, there is the frequent request to collect the raw values as well. The data structure already supports this.

    * Detectors that are redefined within an experiment/scan

      Generally, detectors can be redefined within an experiment/scan, *i.e.* can have different operational modes (standard/average *vs.* interval) in different scan modules. Currently, all data are stored in the identical dataset on HDF5 level and only by "informed guessing" can one deduce that they served different purposes. How to handle this situation in the future, or more important: how to deal with this in the data model described here? Currently, there seems to be no unique identifier for a detector beyond the XML-ID/PV.

    * References to spectra/images

      There are measurements where for a given position count spectra (1D) or entire images (2D) are recorded. At least for the latter, the data usually reside in external files. How is this currently represented in eveH5 files, and how to model this situation with the given :class:`EveData` classes?


evefile.evemetadata module
~~~~~~~~~~~~~~~~~~~~~~~~~~

Data without context (*i.e.* metadata) are mostly useless. Hence, to every class (type) of data in the evefile.evedata module, there exists a corresponding metadata class.


.. note::

    As compared to the UML schemata for the IDL interface, the decision of whether a certain piece of information belongs to data or metadata is slightly different here. Furthermore, there seems to be some (immutable) information currently stored in a dataset in HDF5 that could easily be stored as attribute, due to not changing.


.. figure:: uml/evedata.evefile.evemetadata.*
    :align: center

    Class hierarchy of the evefile.evemetadata module. Each class in the evefile.evedata module has a corresponding metadata class in this module.


.. admonition:: Points to discuss further (without claiming to be complete)

    * Names of the sections

      The names of the sections are currently modelled as Enumeration ("Section"). AFAIK, the names of the sections in the eveH5 file have changed over time. What would be sensible names for the different sections? Are the sections mentioned (standard, snapshot, monitor, timestamp) sufficient? Is anything missing? Will there likely be more in the future? Do we really need "timestamp" as separate section (probably yes)?

    * Metadata from SCML file

      There is likely more information contained in the SCML file (and the end station/beam line description). What kind of (relevant) information is available there, and how to map this to the respective metadata classes?

    * PosCountTimer metadata

      There exists one special dataset in the "meta"/"timestamp" section of an eveH5 file: "PosCountTimer". If we model this one with its own ``EveData`` class (see above), it would probably need its own metadata class, too. It seems, though, that this class has much less attributes as compared to the ``EveMetadata`` class. However, we shall *not* break the ``EveMetadata`` class hierarchy, as ``EveData`` has an attribute of type ``EveMetadata``.

    * Monitor metadata

      Clearly, monitor metadata are not sufficiently modelled yet. In recent eveH5 files, they have only few attributes. Are the other attributes (comparable to the attributes of ``EveMeasureMetadata``) contained in the SCML file and could be read from there?

      Is there any sensible chance to relate monitor datasets to datasets in the standard section? Currently, it looks like the eveH5 monitor datasets have no sensible/helpful "name" attribute, only an ID that partly resembles IDs in the standard section. (And of course, there are usually monitors that do not appear in any other section, hence cannot be related to other devices/datasets.)

    * Attribute "pv"

      "pv" most probably means EPICS process variable. Is this the best name? Would "access" (as in eveH5) be better? Is there any chance to confuse this in the future (EPICS v7 introduced a new transport layer: pvAccess instead of the still existing CA)?

    * Attribute "transport_type"

      What is in here? It seems not present in current eveH5 files...

    * Attributes of the EveMetadata base class

      Given that there will probably be a special EveData subclass for the PosCountTimer dataset from eveH5 files that has only very few metadata, many of the current metadata present in the EveMetadata class would need to be moved down.

    * Information on the individual devices

      Is there somewhere (*e.g.* in the SCML file) more information on the individual devices, such as the exact type and manufacturer for commercial devices? This might be relevant in terms of traceability of changes in the setup. If so, what kind of information is available and how to map this?

    * Options for individual devices

      There seem to be many options for devices that can be set from within the measurement program/SCML file. What kind of options are there, and how to map them in a class hierarchy? The information probably comes from the SCML file. Shall this be separated in the ``evefile`` subpackage and go to an ``scml`` module? Latest in the ``dataset`` subpackage, the metadata should be mapped to the devices.


dataset subpackage
------------------

.. note::

    The name of this subpackage is most probably not final yet. Other options for naming the subpackage may be: ``measurement``, ``scan``.

    Another option would be to keep the subpackage name ``dataset``, but to import the modules into the global ``evedata`` namespace, as this subpackage is meant to be the main user interface. This would reduce *e.g.* ``evedata.dataset.dataset.Dataset`` to ``evedata.dataset.Dataset``.


The overall package structure of the evedata package is shown in :numref:`Fig. %s <fig-uml_evedata>`. Furthermore, a series of (still higher-level) UML schemata for the dataset subpackage are shown below, reflecting the current state of affairs (and thinking).

Generally, the dataset subpackage, as mentioned already in the :doc:`Concepts <concepts>` section, provides the interface towards the "user", where user mostly means the ``evedataviewer`` and ``radiometry`` packages.

What is the main difference between the ``evefile`` and the ``dataset`` subpackages? Basically, the information contained in an eveH5 file needs to be "interpreted" to be able to process, analyse, and plot the data. While the ``evefile`` subpackage provides the necessary data structures to faithfully represent all information contained in an eveH5 file, the ``dataset`` subpackage provides the result of an "interpretation" of this information in a way that facilitates data processing, analysis and plotting.


Arguments against the 2D data array as sensible representation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Currently, one very common and heavily used abstraction of the data contained in an eveH5 file is a two-dimensional data array (basically a table with column headers, implemented as pandas dataframe). As it stands, many problems in the data analysis and preprocessing of data come from the inability of this abstraction to properly represent the data. Two obvious cases, where this 2D approach simply breaks down, are:

* subscans -- essentially a 2D dataset on its own
* adaptive average detector saving the individual, non-averaged values (implemented using MPSKIP)

Furthermore, as soon as spectra (1D) or images (2D) are recorded for a given position (count), the 2D data array abstraction breaks down as well.

Other problems inherent in the 2D data array abstraction are the necessary filling of values that have not been obtained. Currently, once filled there is no way to figure out for an individual position whether values have been recorded (in case of LastFill) or whether a value has not been recorded or recording failed (in case of NaNFill).


dataset.dataset module
~~~~~~~~~~~~~~~~~~~~~~

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


dataset.metadata module
~~~~~~~~~~~~~~~~~~~~~~~

The (original) idea behind this module stems from the ASpecD framework and its representation of a dataset. There, a dataset contains data (with corresponding axes), metadata (of different kind, such as measurement metadata and device metadata), and a history.


.. figure:: uml/evedata.dataset.metadata.*
    :align: center

    Class hierarchy of the dataset.metadata module, closely resembling the dataset concept of the ASpecD framework and the current rough implementation in the evedataviewer package. For the corresponding dataset class see the dataset.dataset module.


In the given context of the evedata package, this would mean to separate data and metadata for the different datasets as represented in the eveH5 file, and store the data (as "device data") in the dataset, the "primary" data as data, and the corresponding metadata as a composition of metadata classes in the Dataset.metadata attribute. Not yet sure whether this makes sense.


Business rules
==============

What may be in here:

* Fill modes
* Mapping monitor time stamps to position counts
* Converting MPSKIP scans into average detector with adaptive number of recorded points
* Converting scan with subscans into appropriate subscan data structure
* Mapping between ``EveFile`` and ``Dataset`` objects, *i.e.* low-level and high-level interface

  * Assumes a 1:1 mapping between files and datasets (for the time being)


.. admonition:: Points to discuss further (without claiming to be complete)

    * Monitors

      * How to map monitors (with time as primary axis) to other devices (motors or detectors, with position counts as primary axis)?


Fill modes
----------

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

      For filling any axis, we need to have the position counts of *all* HDF5 datasets (aka :obj:`evefile.evedata.EveData` objects). This seems to contradict the idea of *not* reading all data at once before filling.

      Of course, if one uses the preferred channel/detector and axis/motor (and there are "established" ways how to determine those if they are not set in the eveH5 file explicitly, though this most probably involves again accessing *all* data), one could only fill those and refill once a user wants to see something different. However, this would imply changing the fill mode "on the fly". If the original :obj:`evefile.evefile.EveFile` object is gone by then, the relevant information may no longer be available, resulting in reimporting the data from the original eveH5 file.

    * How to deal with monitors?

      It seems that currently, the monitors are not used at all/too much by the users, as they are not part of the famous pandas dataframe.

    * How to deal with channel/detector snapshots?

      Currently, fill modes do not care about channel/detector snapshots, as channel/detector values are never filled. So what is the purpose of these snapshots, and are they (currently) used in any sensible way beyond recording the data? (Technically speaking, people should be able to read the data using eveFile, though...)

    * How to deal with "fancy" scans "monitoring" axes as pseudo-detectors?

      Some scans additionally "monitor" an axis by means of a pseudo-detector. This generally leads to an additional position count for reading this "detector", and without manually post-processing the filled data matrix, we end up plotting NaN vs. NaN values when trying to plot a real detector vs. the pseudo-detector reused as an axis (and as a result seeing no plotted data).

      There was the idea of "compressing" all position counts for detector reads where no axis moves in between into one position count. Can we make sure that this is valid in all cases?


If filling is an operation on an :obj:`evefile.evefile.EveFile` object returning a :obj:`dataset.dataset.Dataset` object, how to call this operation and from where? One possibility would be to have a :meth:`evefile.evefile.EveFile.fill` method that takes an appropriate argument for the fill mode, another option would be a method of the :class:`dataset.dataset.Dataset` class or an implicit call when getting data from a file (via an :obj:`evefile.evefile.EveFile` object).


Interfaces
==========

What may be in here:

* Interfaces towards eveH5 and SCML

  * including reading separate SCML files if present (https://redmine.ahf.ptb.de/issues/2740)
  * handling different versions of both eveH5 scheme and SCML scheme
  * mapping the eveH5 and SCML contents to the data structures of the evefile subpackage

* Interfaces towards additional files, *e.g.* images

  * Images in particular are usually not stored in the eveH5 files, but only pointers to these files.
  * Import routines for the different files (or at least a sensible modular mechanism involving an importer factory) need to be implemented.

* Interface towards users (*i.e.*, mainly the ``radiometry`` and ``evedataviewer`` packages)

  * Given a filename of an eveH5 file, returns a ``Dataset`` object.


.. admonition:: Points to discuss further (without claiming to be complete)

    * How to deal with reading the entire content of an eveH5 file at once vs. deferred reading?

      * Reading relevant metadata (*e.g.*, to decide about what data to plot) should be rather fast. And generally, only two "columns" will be displayed (as f(x,y) plot) at any given time -- at least if we don't radically change the way data are looked at compared to the IDL Cruncher.
      * If references to the internal datasets of a given HDF5 file are stored in the corresponding Python data structures (together with the HDF5 file name), one could even close the HDF5 file after each operation, such as not to have open file handles that may be problematic (but see the quote from A. Collette below).
      * However, plotting requires data to be properly filled, and this may require reading all data. See the discussion on fill modes above.


    From the book "Python and HDF5" by Andrew Collette:

        You might wonder what happens if your program crashes with open files. If the program exits with a Python exception, don't worry! The HDF library will automatically close every open file for you when the application exits.

        -- Andrew Collette, 2014 (p. 18)

