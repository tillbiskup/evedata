========
Concepts
========

*Describe the concepts, as soon as they emerge more clearly.*


.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 1


The `evedata` package, while primarily a Python interface to the measured data stored in HDF5 format and according to a given schema (termed eveH5 and evolved over time), does a lot more than existing interfaces. Its main focus is to provide **viable abstractions** and **familiar concepts** for radiometry people, *i.e.*, a **shared language**. As a very rough example: regardless of the way devices are controlled by the engine of the measurement program, they are distinct devices each serving a clearly defined function, not a list of "process variables".


A first incomplete list:

* abstractions

* handling multiple versions

* complete information contained in eveH5 files

* two different interfaces: towards eveH5 and towards users of the data

* information contained in SCML files


Two interfaces: towards eveH5 and towards users
===============================================

The ``evedata`` package will consist of two different interfaces that are most probably implemented in separate subpackages each:

* interface towards eveH5 files

* interface towards the users of the data

The reasoning behind these two interfaces is, once again, Dijkstra's "separation of concerns", and it is probably an implementation of the "Single Responsibility" and "Interface Segregation" principles, the "S" and "I" in SOLID.

In short: The interface towards the eveH5 files is what the IT group is primarily concerned with, but this is nothing the average user should care about. The user-facing interface addresses those *operating* on the data and is the realm of the engineers and scientists, providing useful abstractions for their dealing with the data.


.. figure:: uml/evedata-in-context.*
    :align: center

    The two interfaces of the evedata package: the recorded data (top) and the viewer and analysis (bottom). eveH5 is the persistence layer of the recorded data and metadata, SCML the schema and description of the measurement and setup, evedataviewer and radiometry are Python packages for graphically displaying and processing and analysing these data, respectively. Most people concerned with the actual data will use either the evedataviewer or the radiometry package, but not evedata directly.


The main characteristics of these two interfaces are described in a bit more detail below.


Interface towards eveH5/SCML files
----------------------------------

* represent contents of an eveH5 file
* close to the schemata drawn originally by MM
* backwards-compatible for old eveH5 versions/schemata
* part of the package the IT group possibly needs to apply changes (for new versions of the eveH5 schema)
* reads SCML (if present) -- parsing (beyond general XML parsing/representing the DOM) is a different matter


.. note::

    This interface is clearly an abstraction from the eveH5 file structure, though rather close and from the point of view of the measurement program. Fill modes are *per se* not part of this interface. However, the different types of motors and detectors, monitors, snapshots and alike are clearly abstractions implemented here.


See the section :ref:`sec-faithful_representation` for some more details.


Interfaces towards the users of the data
----------------------------------------

* interface towards the ``radiometry`` and ``evedataviewer`` packages
* useful abstractions from a user perspective, such as:

  * subscans
  * average detector saving the individual data points (currently via MPSKIP)

* probably "the only blissful pandas dataframe" as (poor) representation of the data and some metadata of an eveH5 file


.. note::

    "Users" in this context may eventually be mostly the ``radiometry`` and ``evedataviewer`` packages, as the actual human users will use these packages and the tools provided therein.

.. note::

    Getting an idea of the abstractions necessary will be tough, as most current users will not be able to easily provide the necessary requirements analysis or the relevant information. But that job is taken care of...


See the section :ref:`sec-abstractions` for some more details.


.. _sec-faithful_representation:

Faithful representation of the eveH5 file contents
==================================================

Currently, the ``eveFile`` package applies some filling to the actual data contained in an eveH5 file, hence making it difficult to get access to the data present in the file. Of course, eveH5 files can always be inspected using the ``hdfview`` program. Nevertheless, some information always gets lost when filling the data. Hence, the ``evedata`` package provides data structures that faithfully represent the entire information contained in an eveH5 file.

Why may this be helpful? While the normal user will not necessarily use this part of the ``evedata`` package, it should allow to quickly answer the question whether some problem with a measurement is due to the measurement program (*i.e.*, missing or wrong information in the eveH5 file) or due to the post-processing and analysis routines applied to these files. As different people/groups are responsible in each case, quickly and easily discriminating is a necessary prerequisite for efficient operation on both sides.


.. _sec-abstractions:

Abstractions
============

Good abstractions greatly simplify working with intrinsically complex things. Data recording and analysis is intrinsically complex, and there is no tool that can reduce this inherent complexity. We can only try to reduce the accidental, *i.e.* unnecessary complexity, read: make things no more complicated than necessary.

Two prime examples for complex constructs that are used in daily practice, but are not directly reflected in the currently available building blocks of the measurement program:

* subscans
* average detector recording the individual data points

One way to deal with these and other abstractions is to implement them in the data model as part of the user-facing interface of the ``evedata`` package. This requires intermediate code that translates between the content of the (existing) eveH5 files and the data structures. While such code currently exists, it is in rather bad shape and close to unmaintainable (this is not to blame anybody, just describing the problem).


.. note::

    While there may be a time when these abstractions will get part of the building blocks the measurement program provides, for the time being as well as for handling the huge amount of *existing* data, the ``evedata`` package needs to provide means to map the data to those abstractions in the data model.


Subscans
--------

Discussing whether subscans are a good idea is out of scope of this section, as they exist in practice in a huge amount of relevant measurement data. There may be different ways how subscans have been implemented in scans, and hence different ways how to map subscans to the data model.

As far as TB can see, the current subscan implementation basically only cuts the data vector(s), but does not provide the relevant information on what the additional axis would be about.

Generally, subscans as used, *e.g*, for performing wavelength scans for various angles of incidence (AOI), can be thought of as 2D datasets. However, sometimes there are heads and tails in a scan that are *not* part of the actual 2D array.

Figuring out where subscans start and end has been implemented for certain types of scans both, in IDL and Python, but never stringently documented. Whether it is generally possible to detect subscans in a given eveH5 file with absolute certainty may not matter, as long as the ``evedata`` package is transparent about what it does and allows the user to look at the original data.


Average detector recording the individual data points
-----------------------------------------------------

Currently, there does not exist an average detector in the measurement program that allows to save the individual (non-averaged) data points. To this end, on the EPICS level, the MPSKIP event gets used and the data points are recorded for individual position counts, leaving the post-processing of the imported (and filled) data to a rather complicated separate routine.

Again, it does not matter whether this type of (emulated) detector can be detected with absolute certainty for a given eveH5 file. Furthermore, it does not matter for the time being whether this type of detector will be implemented on the measurement program side in the future, as a lot of data exist using the MPSKIP approach that need to be handled.


.. note::

    One key aspect of this type of (emulated) detector: the number of recorded data points may differ for different sets of motor positions, as preconditions are involved. Hence, the resulting data are not a simple 2D array, but individual arrays/lists for each set of motor positions. The class/data model representing such a detector should provide methods to return only the averaged data as well as statistics over the data (that may then be graphically represented as error bars or else).


The famous pandas dataframe
---------------------------

The two-dimensional data table (alias pandas dataframe) is generally *not* a very useful abstraction, as it cannot cope with the intrinsic complexity of the measured data. Furthermore, the filled data array removes a lot of sometimes relevant information: When has a motor been moved? What does ``NaN`` mean? Value not available or some problem with acquiring the value? While used a lot in practice and touted by some as the one relevant representation of the data, experience shows that many of the existing problems with data handling stem from *ad hoc* approaches to overcome the serious limitations of the data table as foundational abstraction of the data model.

Most probably, the ``evedata`` package will provide an "export" to the pandas dataframe to somehow increase its acceptance, but with a clear warning issued that lots of information will be lost and the user is left alone. Both, ``radiometry`` and ``evedataviewer`` packages will provide much more powerful abstractions and work with them.


Handling multiple versions
==========================

From the user's (engineer, scientist) perspective, there is no such thing as different eveH5 versions, nor is there an internal structure of these files.


.. note::

    The practice is currently different, but that is nothing the development of the ``evedata`` package and the connected infrastructure is concerned with. Eventually, there will be *one* supported interface to the data files (``evedata``) and a series of modular and capable tools that can be easily extended by the users (``radiometry``).


At least the relevant (practically occuring) versions of eveH5 files should be supported by the ``evedata`` package. Which versions these are will be the result of a detailed statistics over all measurement files present.


.. note::

    How to deal with H4 files? How different are these files? Is there any point in trying to map the information contained in H4 files to the data model of the user-facing interface of the ``evedata`` package? (Even the predecessor of eveCSS used H5 at one point -- with whatever schema.)


Information contained in SCML files
===================================

Given that most scans have the SCML saved and that in the future (post eveH5 version 7) the option to *not* save the SCML file will be removed, at least all the attributes for the different motors/axes and detectors/channels can and should be read from the SCML.

Questions that need to be addressed at some point:

* To what level shall the information contained in the SCML files be represented in the ``evedata`` package? Only attributes to the elements (groups, datasets) present in the eveH5 file? Or more towards a complete scan description?

* How to deal with the different versions of the SCML schema? Clearly, all (relevant) versions of the schema need to be readable by the ``evedata`` package.

* How to prevent doubling too much code between the different programs (eve GUI: Java, eve Engine: C++, ``evedata``: Python)? ``evedata`` should work "stand-alone", without dependencies on any part of the measurement program.
