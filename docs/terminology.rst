===========
Terminology
===========

The evedata package resides within a complex environment, and there are terms from both, the problem domain (radiometry with synchrotron radiation) and the solution domain (measurement program, software development) that either users or developers may not necessarily be familiar with. Hence the idea of a growing list of terms and attempts to define them. A big thanks to all colleagues helping to shed light on all the different aspects.


CA
    (EPICS) Channel Access

    For details of the protocol, see https://docs.epics-controls.org/en/latest/specs/ca_protocol.html

channel
    Detector channel, see detector

cruncher
    The name of the "original" viewer implemented in IDL.

CSS
    `Control System Studio <https://controlsystemstudio.org/>`_

    Framework for measurement programs, originally based on the Eclipse RDP framework, with EPICS integration.

    Used as basis for eve before version 2.

dataset
    Unit of actual (numeric) data and their corresponding metadata

    A dataset may contain more (but usually not less) information than that contained in the data file.

detector
    A device that can be read and returns a value.

    Examples are position, angle, temperature, pressure

EPICS
    The `Experimental Physics and Industrial Control System <https://epics-controls.org/>`_

eve
    editor, viewer, engine

    The three (original) components of the PTB measurement program at BESSY-II/MLS the user encounters.


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

    Examples are physical motors for movements (linear, rotating), but as well devices such as temperature controllers.

position count
    Consecutive index for "measurement points".

    Snapshot modules contain their own position count.

    Each change of a motor in a scan module gets a position count. Measurements per position in a scan module get their position count. Deferred detectors do *not* get a new position count. They are purposefully measured later than non-deferred detectors, but get the same position count than non-deferred detectors. Positionings get their own position count.

PV
    Process variable (EPICS)

section
    alternative terms: region, area

    Region of the data in a measurement file, only partly represented in the eveH5 file format, but part of the data model of eveFile.

    Possible sections are: standard, snapshot, monitor, timestamp

SM
    Scan module

snapshot (section)
    Section of the measurement data representing the current state of the setup.

    There are four kinds of snapshots (two variables with two values each), of which only two are relevant for data processing and analysis: motor and detector snapshots.

    In a snapshot, all motor and detector values are stored once.

standard (section)
    Section of the measurement data regarding the actual measurement

    In terms of the measurement program, all modules that are *not* snapshot or classical scan modules (with the exception of pre and post scans).

    Eben die Motorbewegungen und Detektorauslesungen und ggf. anschließende Positionierungen (Goto Peak etc.). (Quelle: MM)

timestamp (section)
    Section with an artificial detector/device containing both, position counts and timestamps.

    All position counts appearing anywhere in a scan are contained. Hence, this section contains the complete set of all existing position counts in a scan (to be exact: for one chain). The corresponding timestamps are given in milliseconds since start of the scan.
