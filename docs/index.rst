=======
evedata
=======

*Importing eveH5 data from synchrotron radiometry measurements conducted at BESSY/MLS in Berlin.*

Welcome! This is the documentation for evedata, a Python package for **importing (synchrotron) radiometry data** obtained at one of the beamlines at **BESSY-II or MLS in Berlin**, mostly operated by the German National Metrology Institute, the `Physikalisch-Technische Bundesanstalt (PTB) <https://www.ptb.de/>`_. This package acts as main **interface between** the (eveH5) **data files and the processing and analysis code** and provides abstractions that allow for a convenient and intuitive access to the data and information contained in the data files. For related packages for viewing and analysing those data, have a look at the :ref:`related projects section <sec-related_projects>`.


Features
========

A list of (planned) features:

* Importer for eve HDF5 files (used at PTB in Berlin, Germany)

* Fully backwards-compatible to older eveH5 versions

* Complete information available that is contained in an eveH5 file

* Access to the information stored in the scan description

* Powerful and intuitive abstractions, allowing for associative access to data and information -- beyond a purely tabular view of the data


And to make it even more convenient for users and future-proof:

* Open source project written in Python (>= 3.9)

* Developed fully test-driven

* Extensive user and API documentation



.. warning::
    evedata is currently under active development and still considered in Alpha development state. Therefore, expect frequent changes in features and public APIs that may break your own code. Nevertheless, feedback as well as feature requests are highly welcome.


Installation
============

To install the evedata package on your computer (sensibly within a Python virtual environment), open a terminal (activate your virtual environment), and type in the following:

.. code-block:: bash

    pip install evedata


.. _sec-related_projects:

Related projects
================

While the evedata package is explicitly *not* concerned with viewing or analysing data, there is a number of related packages users of the evedata package may well be interested in, as they have a similar scope, focussing on working with synchrotron radiometry data.

* radiometry

  A Python package for **processing and analysing (synchrotron) radiometry data** in a **reproducible** and mostly **automated** fashion. Currently, it focusses on data obtained at one of the beamlines at **BESSY-II or MLS in Berlin**, mostly operated by the German National Metrology Institute, the `Physikalisch-Technische Bundesanstalt (PTB) <https://www.ptb.de/>`_.

* evedataviewer

  A Python package for **graphically inspecting data** contained in EVE files, *i.e.* data **obtained at one of the beamlines at BESSY-II or MLS in Berlin**, mostly operated by the German National Metrology Institute, the `Physikalisch-Technische Bundesanstalt (PTB) <https://www.ptb.de/>`_.

Finally, don't forget to check out the website on `reproducible research <https://www.reproducible-research.de/>`_ covering in more general terms aspects of reproducible research and good scientific practice.


License
=======

This program is free software: you can redistribute it and/or modify it under the terms of the **GPLv3 License**.


A note on the logo
==================

The logo depicts a synchrotron emitting radiation, and the data files emerging from performing measurements. While the synchrotron part is inspired by the logo used for the `Metrology with Synchrotron Radiation section of the PTB <https://www.ptb.de/cms/en/ptb/fachabteilungen/abt7/ptb-sr.html>`_, the entire logo is copyright T. Biskup.



.. toctree::
   :maxdepth: 2
   :caption: User Manual:
   :hidden:

   audience
   concepts
   usecases
   terminology
   installing

.. toctree::
   :maxdepth: 2
   :caption: Developers:
   :hidden:

   people
   contributing
   requirements-analysis
   architecture
   changelog
   roadmap
   api/index

