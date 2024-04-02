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


.. important::

    As the evefile subpackage is *not* meant as a (human-facing) user interface, it is *not* concerned with concepts such as fill modes, but represents the data "as is". This means that the different data can generally not be plotted against each other. This is a deliberate decision, as filling data for a (two-dimensional) data array, although generally desirable for (simple) plotting purposes, masks/removes some highly important information, *e.g.* whether a value has not been measured in the first place, or whether obtaining a value has failed for some reason.


As usual, the core domain provides the (abstract) entities representing the different types of content. Hence, it is *not* concerned with the actual layout of an eveH5 file nor any importers nor the mapping of different eveH5 schema versions.


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

      At least the HDF5 datasets in the "monitor" section are clearly distinct from the others, as they don't have PosCounts as reference axis.

    * SCML: How to represent the contents sensibly? What are the relevant abstractions/concepts?

      Perhaps (additionally) storing the "plain" XML in a variable is still a sensible idea.



evefile.evedata module
~~~~~~~~~~~~~~~~~~~~~~

Data are organised in "datasets" within HDF5, and the ``evefile.evedata`` module provides the relevant entities to describe these datasets. Although currently (as of 03/2024, eve version 2.0) neither average nor interval detectors save the individual data points, at least the former is a clear need of the engineers/scientists (see their use of the MPSKIP feature to "fake" an average detector saving the individual data points). Hence, the data model already respects this use case. As per position (count) there can be a variable number of measured points, the resulting array is no longer rectangular, but a "ragged array". While storing such arrays is possible directly in HDF5, the implementation within evedata is entirely independent of the actual representation in the eveH5 file.


.. figure:: uml/evedata.evefile.evedata.*
    :align: center

    Class hierarchy of the evefile.evedata module. Each class has a corresponding metadata class in the evefile.evemetadata module. While in this diagram, EveMotorData and EveDetectorData seem to have no difference, at least they have a different type of metadata (see the evefile.evemetadata module below), besides the type attribute set accordingly.


.. admonition:: Points to discuss further (without claiming to be complete)

    * Are "dumb devices" such as shutters actually represented in an eveH5 file? Can they be part of the "monitor" section?

      If they occur, latest in the SCML, and are relevant to be modelled, how to properly name them?

    * Mapping MonitorData to MeasureData

      There is an age-long discussion how to map monitor data (with time in milliseconds as primary axis) to measured data (with position counts as primary axis). Besides the question how to best map one to the other (that needs to be discussed, decided, clearly documented and communicated, and eventually implemented): Where would this mapping take place? Here in the evefile subpackage? Or in the "convenience interface" layer, *i.e.* the dataset subpackage?


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

      The names of the sections are currently modelled as Enumeration ("Section"). AFAIK, the names of the sections in the eveH5 file have changed over time. What would be sensible names for the different sections? Are the three sections mentioned (standard, monitor, snapshot) sufficient? Is anything missing? Will there likely be more in the future?

    * Metadata from SCML file

      There is likely more information contained in the SCML file (and the end station/beam line description). What kind of (relevant) information is available there, and how to map this to the respective metadata classes?

    * Monitor metadata

      Clearly, monitor metadata are not sufficiently modelled yet.


dataset subpackage
------------------

.. note::

    The name of this subpackage is most probably not final yet.


The overall package structure of the evedata package is shown in :numref:`Fig. %s <fig-uml_evedata>`. Furthermore, a series of (still higher-level) UML schemata for the dataset subpackage are shown below, reflecting the current state of affairs (and thinking).

Generally, the dataset subpackage, as mentioned already in the :doc:`Concepts <concepts>` section, provides the interface towards the "user", where user mostly means the ``evedataviewer`` and ``radiometry`` packages.


Arguments against the 2D data array as sensible representation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Currently, one very common and heavily used abstraction of the data contained in an eveH5 file is a two-dimensional data array (basically a table with column headers, implemented as pandas dataframe). As it stands, many problems in the data analysis and preprocessing of data come from the inability of this abstraction to properly represent the data. Two obvious cases, where this 2D approach simply breaks down, are:

* subscans -- essentially a 2D dataset on its own
* adaptive average detector saving the individual, non-averaged values (implemented using MPSKIP)

Furthermore, as soon as spectra (1D) or images (2D) are recorded for a given position (count), the 2D data array abstraction breaks down as well.

Other problems inherent in the 2D data array abstraction are the necessary filling of values that have not been obtained. Currently, once filled there is no way to figure out for an individual position whether values have been recorded (in case of LastFill) or whether a value has not been recorded or recording failed (in case of NaNFill).


dataset.dataset module
~~~~~~~~~~~~~~~~~~~~~~

Currently, the idea is to model the dataset close to the dataset in the ASpecD framework, as the core interface to all processing, analysis, and plotting routines in the ``radiometry`` package, and with a clear focus on automatically writing a full history of each processing and analysis step.


.. figure:: uml/evedata.dataset.dataset.*
    :align: center

    Class hierarchy of the dataset.dataset module, closely resembling the dataset concept of the ASpecD framework (while lacking the history component). For the corresponding metadata class see the dataset.metadata module.


Furthermore, the dataset should provide appropriate abstractions for things such as subscans and detector channels with adaptive averaging (*i.e.* ragged arrays as data arrays). Thus, scans currently recorded using MPSKIP could be represented as what they are (adaptive average detectors saving the individual measured data points). Similarly, the famous subscans could be represented as true 2D datasets (as long as the individual subscans all have the same length).


.. admonition:: Points to discuss further (without claiming to be complete)

    * How to handle data filling? (But: see discussion on fill modi in the section below)

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
* Converting MPSKIP scans into average detector with adaptive number of recorded points
* Converting scan with subscans into appropriate subscan data structure
* Mapping between ``EveFile`` and ``Dataset`` objects, *i.e.* low-level and high-level interface

  * Assumes a 1:1 mapping between files and datasets (for the time being)


.. admonition:: Points to discuss further (without claiming to be complete)

    * Fill modes

      * Which ones are relevant/needed?
      * How to cope with the current practice of applying (dirty) fixes to the already filled data to account for such things as scans using MPSKIP?
      * Even worse: How to deal with data that (mis)use a "detector" to kind of monitoring a motor state, just to have it appear in the famous 2D data table? In these cases, filling does not help, as we end up with NaN vs. NaN without special post-processing (and hence simply no plot).

    * Monitors

      * How to map monitors (with time as primary axis) to other devices (motors or detectors, with position counts as primary axis)?


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

      * Reading relevant metadata (*e.g.*, to decide about what data to plot) should be rather fast. And generally, only two "columns" will be displayed (as f(x,y) plot) at any given time - at least if we don't radically change the way data are looked at compared to the IDL Cruncher.
      * If references to the internal datasets of a given HDF5 file are stored in the corresponding Python data structures (together with the HDF5 file name), one could even close the HDF5 file after each operation, such as not to have open file handles that may be problematic (but see the quote from A. Collette below).


    From the book "Python and HDF5" by Andrew Collette:

        You might wonder what happens if your program crashes with open files. If the program exits with a Python exception, don't worry! The HDF library will automatically close every open file for you when the application exits.

        -- Andrew Collette, 2014 (p. 18)

