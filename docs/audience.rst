.. _radiometry: https://docs.radiometry.de/
.. _evedataviewer: https://evedataviewer.docs.radiometry.de/

===============
Target audience
===============

Who is the target audience of the evedata package? Is it interesting for me?


Synchrotron radiometry people at PTB Berlin
===========================================

The evedata package currently primarily addresses **radiometry** people working at the synchrotron beamlines at BESSY-II and MLS in Berlin operated by the German National Metrology Institute, the `Physikalisch-Technische Bundesanstalt (PTB) <https://www.ptb.de/>`_. Its primary goal is to provide a stable and somewhat abstract **interface to the measured data** storead primarily as HDF5 files according to a given scheme (that evolved over time). As such, it is only one (fundamental) building block in a larger digital infrastructure for data processing and analysis.

If you are looking for a **data viewer tool**, aimed at conveniently inspecting data directly at the beamline, you may have a look at the `evedataviewer`_ package. And if you are interested in the **reproducible processing and analysis** of radiometry data, have a look at the `radiometry`_ package.


Two interfaces
==============

The evedata package provides two distinct interfaces addressing different kinds of users with different needs and requirements. One interface is directed towards the eveH5 files as the persistence layer of the recorded data and metadata, the other interface is directed towards the actual users of the recorded data and used by the `evedataviewer`_ and `radiometry`_ packages.

.. figure:: uml/evedata-in-context.*
    :align: center

    The two interfaces of the evedata package: the recorded data (top) and the viewer and analysis (bottom). eveH5 is the persistence layer of the recorded data and metadata, SCML the schema and description of the measurement and setup, evedataviewer and radiometry are Python packages for graphically displaying and processing and analysing these data, respectively. Most people concerned with the actual data will use either the evedataviewer or the radiometry package, but not evedata directly.

The **low-level interface towards the persistence layer (eveH5 and SCML files)** provides a faithful representation of all information contained in both, the eveH5 (HDF5) file and the corresponding scan description (SCML). Furthermore, this is the layer providing compatibility with and abstracting away from the different versions of the eveH5 and SCML schemas. Hence, if there is a change in the eveH5 or SCML schema, this is the *only* place where changes in the evedata package should be necessary, and they will be made either by those responsible for the eveH5 and SCML schemas or people close to it.

The **high-level interface towards the consumers** of the actual recorded data is primarily used by the `evedataviewer`_ and `radiometry`_ packages, and actual users will rather use these packages, not directly the evedata package. This interface is characterised by a number of powerful abstractions that go far beyond a two-dimensional, tabular representation of the data. The reason: The data recorded are highly complex and simply don't fit within a two-dimensional tabular structure.

