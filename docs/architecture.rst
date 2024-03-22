============
Architecture
============

Each software has some kind of architecture, and this is the place to describe it in broad terms, to make it easier for developers to get around the code. Following the scheme of a layered architecture as featured by the "Clean Architecture" (Robert Martin) or the "hexagonal architecture", alternatively known as "ports and adapters" (Alistair Cockburn), the different layers are described successively from the inside out.

Just to make matters a bit more interesting, the evedata package has basically **two disjunct interfaces**: one towards the data file format (eveH5), the other towards the users of the actual data, *e.g.* the ``radiometry`` and ``evedataviewer`` packages. Most probably, these two interfaces will be separated into different subpackages.


.. _fig-uml_evedata:

.. figure:: uml/evedata.*
    :align: center

    A high-level view of the different subpackages of the evedata package, currently reflecting the two interfaces. For details, see further schemata below. While "evefile" will most probably be the name of the subpackage interfacing the eveH5 files, the name of the "dataset" subpackage is not stable yet.


Core domain
===========

The core domain contains the central entities and their abstract interactions, or, in terms of the "Domain Driven Design" (Eric Evans), the implementation of the abstract model of the application.

In the evedata package, due to being split into two separate subpackages, each of them has its own core domain that will be described below.


evefile subpackage
------------------

The overall package structure of the evedata package is shown in :numref:`Fig. %s <fig-uml_evedata>`. Hereafter, a series of (still higher-level) UML schemata for the evefile subpackage are shown, reflecting the current state of affairs (and thinking).

Generally, the evefile subpackage, as mentioned already in the :doc:`Concepts <concepts>` section, provides the interface towards the persistence layer (eveH5 files). This is a rather low-level interface focussing at a faithful representation of all information available in an eveH5 file as well as the corresponding scan description (SCML), as long as the latter is available.


evefile.evemetadata module
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. figure:: uml/evedata.evefile.evemetadata.*
    :align: center

    Class hierarchy of the evefile.evemetadata module. Each class in the evefile.evedata module has a corresponding metadata class in this module.



evefile.evedata module
~~~~~~~~~~~~~~~~~~~~~~

.. figure:: uml/evedata.evefile.evedata.*
    :align: center

    Class hierarchy of the evefile.evedata module. Each class has a corresponding metadata class in the evefile.evemetadata module.



evefile.evefile module
~~~~~~~~~~~~~~~~~~~~~~

.. figure:: uml/evedata.evefile.evefile.*
    :align: center

    Class hierarchy of the evefile.evefile module.


Business rules
==============

...


Interfaces
==========

...
