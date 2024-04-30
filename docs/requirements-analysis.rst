=====================
Requirements analysis
=====================

While the sections on :doc:`audience`, :doc:`concepts`, and :doc:`usecases` contain parts of the answers, what the evedata package is all about, this document is intended to give a more formal answer aimed mainly at developers. For a high-level view of how these requirements have been/will be met by the evedata package, have a look at the :doc:`architecture` section.


*Ad hoc*, the following requirements come to mind, preliminarily grouped into three categories. Each requirement needs to be further detailed in individual sections below.

High-level requirements/overall goals:

* Faithful representation of the contents of an eveH5 file

  * Access to *all* content, including the SCML file
  * No modification of the contents (*i.e.*, no "filling" and alike)
  * No need for an identical structure of the data model and the HDF5 file

* "Convenient" user access to all information contained in an eveH5 file

  * The evedata package is "only" the interface towards both, data viewer and data processing/analysis pipelines.
  * The data model needs to be sufficiently powerful (and hence complex) to map the complexity of the underlying SCML/eveH5 structures (=> a 2D array/table will *not* do).


User requirements:

* Backwards-compatibility with all versions of eveH5 files actually present "in the wild"

* Platform-independent: needs to work on Linux, Windows, macOS

* Python-based for use with the existing/newly developed data processing and analysis pipeline

* Simple to install: Python package

* Sufficiently documented (user documentation)


Developer requirements:

* Sufficiently documented (developer documentation)

* Long-term maintainable: needs to be up-to-date with all changes of the structure of both, SCML schema and HDF5 schema

  * Implications for code quality, code organisation, and conceptual documentation

* Minimal external dependencies to reduce future maintenance burden

* Sufficiently tested

----

The following sections try to roughly follow the overall layout of the `req42
framework <https://req42.de>`_, as far as it seems sensible for this project. To not maintain the same information at different places, hyperlinks to other sections of the documentation are provided.


Goals
=====

* Faithful representation of the contents of an eveH5 file

* (Stable) interface between eveH5 (and SCML) files and both data viewing and data processing/analysis pipeline


Stakeholder
===========

See :doc:`audience`

Basically two groups:

* IT group responsible for the measurement program (and hence the eveH5 and SCML schemas)
* Users of the recorded data (mainly engineers and scientists)

The latter will mostly approach the evedata package by means of other software, namely evedataviewer and radiometry package.


Scope and context
=================


Scope contains everything that can be directly controlled by the project (developers), while context is the environment in which the project is situated and to which the project provides interfaces.

From req42:

    Scope is the area that you can influence. The environment of the
    product, to which there are certainly many interfaces, represents the
    context. The context cannot (usually) be decided by you alone, but can
    often be negotiated. To gain clarity it is important to describe both as
    much as possible and especially to define the boundary between the two
    scopes.

    req42 recommends that you start with the business scope and do not limit
    the product scope too early. The decision about the product scope should
    be a conscious one.


Scope
-----

* Interface between eveH5 (and SCML) files and data viewing/processing/analysis


Context
-------

measurement program/IT group

* eveH5 and SCML schemas and file formats (both with different versions)
* data models of the eve engine and GUI

data users (engineers, scientists)

* data viewing (evedataviewer package)

  * *ad hoc* tasks at the beamline (not exclusively, but needs to be possible)
  * includes some data processing
  * comparing data of different measurements
  * immediate quality control
  * extracting relevant information for next measurement (including axes positions and alike, probably even directly transferred to measurement program)

* data processing and analysis (radiometry package)

  * *post hoc* tasks operating on data of finished measurements


Functional requirements
=======================

See :doc:`usecases`?


Quality Requirements
====================

Nonfunctional requirements (NFR)

Parts of ISO 25010?


Constraints
===========

* technological: Python, platform independent, ...

* organisational: rather none?


Domain Terminology
==================

See :doc:`terminology`


Roadmap
=======

See :doc:`roadmap`


Risks
=====

...

