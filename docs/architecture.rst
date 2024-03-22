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


Points to discuss further (without claiming to be complete):

* Split data according to sections (standard, monitor, snapshot)?

  At least the HDF5 datasets in the "monitor" section are clearly distinct from the others, as they don't have PosCounts as reference axis.

* SCML: How to represent the contents sensibly? What are the relevant abstractions/concepts?

  Perhaps storing the "plain" XML in a variable is still a sensible idea.



evefile.evedata module
~~~~~~~~~~~~~~~~~~~~~~

Data are organised in "datasets" within HDF5, and the ``evefile.evedata`` module provides the relevant entities to describe these datasets. Although currently (as of 03/2024, eve version 2.0) neither average nor interval detectors save the individual data points, at least the former is a clear need of the engineers/scientists (see their use of the MPSKIP feature to "fake" an average detector saving the individual data points). Hence, the data model already respects this use case. As per position (count) there can be a variable number of measured points, the resulting array is no longer rectangular, but a "ragged array". While storing such arrays is possible directly in HDF5, the implementation within evedata is entirely independent of the actual representation in the eveH5 file.


.. figure:: uml/evedata.evefile.evedata.*
    :align: center

    Class hierarchy of the evefile.evedata module. Each class has a corresponding metadata class in the evefile.evemetadata module. While in this diagram, EveMotorData and EveDetectorData seem to have no difference, at least they have a different type of metadata (see the evefile.evemetadata module below), besides the type attribute set accordingly.


Points to discuss further (without claiming to be complete):

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


Points to discuss further (without claiming to be complete):

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


Business rules
==============

...


Interfaces
==========

...
