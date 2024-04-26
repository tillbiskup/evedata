.. _use_cases:

=========
Use cases
=========

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 1


For the time being, the following description of use cases is rather an idea how working with the evedata package may look like than a description of what actually can be achieved. As such, it is part of the requirements analysis (use case driven design, Jacobson 1992) that should be the first step of system design, even before the analysis model covering the high-level system architecture.


.. important::

    Potential users and contributors to these use cases should be clear about the scope of the evedata package. It is *not* meant to do any data processing and analysis, but rather provide the main **interface** between the the information obtained from a measurement (data, measurement, setup) and the actual data display and data processing and analysis.


Overview
========

A first overview of potential use cases, to be discussed with the users:

* Access data from a given measurement in a way they can be further processed and analysed.

  Data in the persistence layer (HDF5 file) are usually neither homogeneous nor continuous and hence not easily plotted, processed, or analysed. Hence, the data read from the persistence layer need to be "interpreted" first. The data structures provided need to be friendly to both, data display (evedataviewer package) as well as advanced data processing and analysis (radiometry package) including full reproducibility by means of an automatically generated protocol.

* Access information necessary to change settings of the physical setup.

  During measurements, there is often the need to directly process and analyse data and extract information for the next measurement/scan, *i.e.* settings of the phyical setup. All the information necessary to make these settings directly (bypassing the eve GUI) should be available.

* Access all information potentially available for a measurement to check for the root cause of problems with a given measurement.

  The first necessary step when users of the measurement program report bugs/errors is to check whether the problem really occurs during measurement or afterwards in the data processing pipeline. Hence, all information potentially available for a given measurement needs to be accessible, in a reliable way and before the data have been pre-processed (such as "filling").

* Access all versions of files transparently, without change in the user interface.

  There exist several independent versions of both, HDF5 schemas and SCML schemas. The user of the package should usually not have to deal with these differences, *i.e.* the user interface should transparently abstract away these differences.

* Provide powerful abstractions such as subscans, 2D/nD data structures, and detector types not yet available in the measurement program.

  Users got used to a number of different abstractions, such as subscans and 2D/nD data structures (*e.g.* wavelength *vs.* AOI). Furthermore, some use cases are not yet covered directly by the measurement program, most prominently perhaps an adaptive average detector saving the individual data points. These concepts should be available as convenient abstractions and the data automatically be converted into these structures.

* Provide access to data stored separately from eveH5 files, such as spectra and images.

  Some measurements involve devices whose data are (currently) *not* stored in the eveH5 (HDF5) measurement files. These data should be transparently made available when reading the eveH5 file, potentially via a deferred loading mechanism (on demand) for better performance.

* Access data on a local computer independent of network access/PTB intranet and independent of the operating system.

  Data need to be available locally of course, but besides that, no external services should be required to load (and afterwards view, process, analyse) the data. Furthermore, data handling should work on at least the three major desktop operating systems (Linux, Windows, macOS).


Todo
====

* Define actors

* Complete list of use cases listed above

* Formalise individual use cases

