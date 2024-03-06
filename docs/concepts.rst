========
Concepts
========

*Describe the concepts, as soon as they emerge more clearly.*


* abstractions

* handling multiple versions

* complete information contained in eveH5 files

* two different interfaces: towards eveH5 and towards users of the data


Faithful representation of the eveH5 file contents
==================================================

Currently, the ``eveFile`` package applies some filling to the actual data contained in an eveH5 file, hence making it difficult to get access to the data present in the file. Of course, eveH5 files can always be inspected using the ``hdfview`` program. Nevertheless, some information always gets lost when filling the data. Hence, the ``evedata`` package provides data structures that faithfully represent the entire information contained in an eveH5 file.

