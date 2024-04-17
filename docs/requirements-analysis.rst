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

