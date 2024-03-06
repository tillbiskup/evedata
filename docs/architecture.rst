============
Architecture
============

Each software has some kind of architecture, and this is the place to describe it in broad terms, to make it easier for developers to get around the code. Following the scheme of a layered architecture as featured by the "Clean Architecture" (Robert Martin) or the "hexagonal architecture", alternatively known as "ports and adapters" (Alistair Cockburn), the different layers are described successively from the inside out.

Just to make matters a bit more interesting, the evedata package has basically **two disjunct interfaces**: one towards the data file format (eveH5), the other towards the users of the actual data, *e.g.* the ``radiometry`` and ``evedataviewer`` packages. Most probably, these two interfaces will be separated into different subpackages.


Core domain
===========

The core domain contains the central entities and their abstract interactions, or, in terms of the "Domain Driven Design" (Eric Evans), the implementation of the abstract model of the application.


Business rules
==============

...


Interfaces
==========

...
