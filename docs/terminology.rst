===========
Terminology
===========

The evedata package resides within a complex environment, and there are terms from both, the problem domain (radiometry with synchrotron radiation) and the solution domain (measurement program, software development) that either users or developers may not necessarily be familiar with. Hence the idea of a growing list of terms and attempts to define them. A big thanks to all colleagues helping to shed light on all the different aspects, in particular (and alphabetic order) Jens Eden, Marcus Michalsky, Hartmut Scherr.


Axis
    Motor axis, see motor

    An axis always belongs to a motor, and a motor can have one to many axes.

CA
    (EPICS) Channel Access

    For details of the protocol, see https://docs.epics-controls.org/en/latest/specs/ca_protocol.html

channel
    Detector channel, see detector

    A channel always belongs to a detector, and a detector can have one to many channels.

cruncher
    The name of the "original" viewer for eve files implemented in IDL.

CSS
    `Control System Studio <https://controlsystemstudio.org/>`_

    Framework for measurement programs, originally based on the Eclipse RDP framework, with EPICS integration.

    Used as basis for the eve GUI in version 1.

dataset
    Unit of actual (numeric) data and their corresponding metadata

    A dataset may contain more (but usually not less) information than that contained in the data file.

    See "dataset (HDF5)" for a different kind of dataset

dataset (HDF5)
    Leaf in the tree structure of an HDF5 file

    HDF5 consists of two different structures: groups (nodes) and datasets (leafs) contained in a hierarchical tree structure.

    While both, groups and datasets, can (and usually do) contain attributes (metadata), only datasets contain actual data. The type of these data is not restricted to numerical data, and in case array-like data even not to rows with equal number of elements (making it generally possible to store "ragged arrays" in HDF5, while this is not trivial to map to array structures for most programming languages).

detector
    A device that can be read and returns a value.

    A detector can have one or several channels.

    Examples are position, angle, temperature, pressure

    Generally a detector has one of three modes which determines its behaviour: standard, interval, and average.

device
    A device that is neither a motor nor a detector and does not provide feedback whether it has reached a given state.

    Devices can be set in pre- and postscan and can both be physical devices (such as a shutter) and options of any kind of device (including motors and detectors).

ECP
    Engine Control Protocol

    Communication protocol between the eve engine and the eve GUI

engine
    engine part of eve, sometimes referred to as eve engine as well.

EPICS
    The `Experimental Physics and Industrial Control System <https://epics-controls.org/>`_

eve
    editor, viewer, engine

    The three (original) components of the PTB measurement program at BESSY-II/MLS the user encounters.

eveFile
    Python library for reading eveH5 files.

    Basically a thin wrapper (created using SWIG) calling the underlying C++ library used by the (eve) engine. Runs only under Linux, due to depending on the compiled C++ shared library.

    The Python ``evedata`` package is planned to supersede eveFile at some point, at least with regard to the Python interface.

eveH5
    data format written by the (eve) engine to save the measured data

    Technically an HDF5 file, following a special schema that evolves and may differ between individual eveH5 files.

filling
    Act of making (at least) two vectors the same length, in order to plot one *vs.* the other

    Data in eveH5 files are stored in HDF5 datasets and are generally not compatible to each other regarding the number of their data points, as only "new" values are stored. Example: Only those positions for an axis are stored where the axis has actually been moved, but for the same position of a particular axis, there may be many values read from a detector channel and stored in another HDF5 dataset in an eveH5 file.

    Historically, there are four different fill modes available, and reality shows that these fill modes are not sufficient to preprocess all available data files, resulting in rather convoluted specialised code.

fill modes
    Defined ways of filling data (see filling for a background)

    Four different fill modes are implemented in the `eveFile interface <https://www.ahf.ptb.de/messpl/sw/python/common/eveFile/doc/html/Section-Fillmode.html#evefile.Fillmode>`_:

    * NoFill – use only data from positions where at least one axis and one channel have values
    * LastFill – use all channel data and fill in the last known position for all axes without values
    * NaNFill – use all axis data and fill in NaN for all channels without values
    * LastNaNFill – use all data and fill in NaN for all channels without values and fill in the last known position for all axes without values

    While these fill modes are not necessarily sufficiently defined/documented, it seems that it is not necessary to have them all or even the possibility to choose.

HDF5
    Hierarchical Data Format, version 5

    A binary data format of widespread use designed for (very) large datasets. Some noteworthy features are: only parts of data can be read from the file (if the data are larger than the available memory), the format is "self-describing" in sense of providing metadata, it is hierarchically structured with nodes (groups) and leafs (datasets).

    The eveH5 format used by the eve (engine) is one example of using HDF5 with a particular schema for storing data and (rich) metadata.

    See https://www.hdfgroup.org/solutions/hdf5/ for details.

IDL
    Interactive Data Language

    Commercial programming language originating in the late 1970s still in widespread use at PTB.

IOC
    EPICS Input Output Controller

    For details see, *e.g.* https://docs.epics-controls.org/projects/how-tos/en/latest/getting-started/creating-ioc.html

monitor (section)
    Section of the measurement data for everything that is not changed or read during a scan, but still of interest.

    Properties of devices as well as "dumb" devices can be defined as monitors. For a monitor, the value will be stored at the start of a scan and for every change. As changes can occur at any time (parallel to the actual scan), monitor events do not have a position count, but a timestamp (in milliseconds since start of the scan).

motor
    Actuator, device for which values can be set

    A motor always provides feedback as to whether it has reached its set value, in contrast to (simple) devices.

    A motor has at least one axis, but may have multiple axes.

    Examples are physical motors for movements (linear, rotating), but as well devices such as temperature controllers.

MPSKIP
    EPICS event (?) ...

position count
    Consecutive index for "measurement points".

    Snapshot modules contain their own position count.

    Each change of a motor in a scan module gets a position count. Measurements per position in a scan module get their position count. Deferred detectors do *not* get a new position count. They are purposefully measured later than non-deferred detectors, but get the same position count than non-deferred detectors. Positionings get their own position count.

PV
    Process variable (EPICS)

RBV
    read-back value

    Value read back from a device (motor). Motors provide feedback once they finished moving to a given position, *i.e.* provide the actual position (and whether they reached the position or approached a limit or else). This is different from (ordinary) devices that can be set, but do not provide any feedback.

section
    alternative terms: region, area

    Region of the data in a measurement file, only partly represented in the eveH5 file format, but part of the data model of eveFile.

    Possible sections are: standard, snapshot, monitor, timestamp

SCML
    Scan Markup Language, ScanML, definition of a scan in XML format.

    Used (and required) by the engine to perform a scan.

    Consists of several parts, mainly a scan description and a description of the physical setup (measurement station)

scan module
    SM, unit of abstraction to structure a scan.

    There are five different types of scan modules:

    * scan module
    * axis snapshot (static)
    * channel snapshot (static)
    * axis snapshot (dynamic)
    * channel snapshot (dynamic)

    For static snapshots, the list of axes/channels to store values for can be selected by the user, while dynamic snapshots determine their list of axes/channels automatically based on the current scan description.

SM
    Scan module

snapshot (section)
    Section of the measurement data representing the current state of the setup.

    There are four kinds of snapshots (two variables with two values each: axis/channel, static/dynamic), of which only two are relevant for data processing and analysis: motor and detector snapshots.

    In a snapshot, all motor and detector values are stored once.

standard (section)
    Section of the measurement data regarding the actual measurement

    In terms of the measurement program, all modules that are *not* snapshot or classical scan modules (with the exception of pre and post scans).

    Contains basically all the motor movements and detector reads, and following positionings (*e.g.*, "Goto Peak").

timestamp (section)
    Section with an artificial detector/device containing both, position counts and timestamps.

    All position counts appearing anywhere in a scan are contained. Hence, this section contains the complete set of all existing position counts in a scan (to be exact: for one chain). The corresponding timestamps are given in milliseconds since start of the scan.
