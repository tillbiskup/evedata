============
eveH5 Schema
============

Data get stored by the eve engine using the HDF5 format. However, HDF5 is only the technical layer, and it is quite important to specify the scheme used to store the data. This scheme evolved as well over time, and for now, this page tries to summarise the status quo (eveH5 v7) as well as documenting the ideas how to further develop and reorganise the scheme. Eventually, the evedata package should be able to handle *all* versions of the eveH5 schema that actually appear "in the wild", but initially, it will start from the current eveH5 v7. Furthermore, developing the data model for the evedata package informs further development of the eveH5 scheme, as ideally, the same concepts should eventually be present in scan (SCML) and measurement station (XML) description, eve-gui, eve-engine, and the evedata interface.


Status quo: eveH5 v7
====================

For a first graphical overview of the scheme, cf. :numref:`Fig. %s <fig-eveh5_v7>`.

.. _fig-eveh5_v7:

.. figure:: uml/eveh5-v7.*
    :align: center
    :width: 750px

    UML diagram of the eveH5 v7 scheme, the status quo as of eve 2.1, mid-2024, and since eve 1.37 (05/2022). Note, however, that eveH5 v6 (11/2018) and eveH5 v7 are mostly identical. You may click on the image for a larger view.



Future development: eveH5 v8
============================

For a first graphical overview of the scheme, cf. :numref:`Fig. %s <fig-eveh5_v8>`.


.. _fig-eveh5_v8:

.. figure:: uml/eveh5-v8.*
    :align: center
    :width: 750px

    UML diagram of the current state of affairs for the new eveH5 v8 scheme. As the scheme is currently actively being developed, expect frequent changes of this scheme. You may click on the image for a larger view.


Differences to the previous scheme
----------------------------------

Some of the most important differences with respect to the previous scheme, v7:

* No chain ``c1`` any more
* SCML and XML are stored as HDF5 datasets, not in the userdata area at the beginning of the HDF5 file.
* Additional data for datasets, such as average and interval channels or normalised values, are stored as additional columns in the channel dataset.
* Channels used for normalisation do not appear as separate channels any more, their data are stored together with the normalised data in the HDF5 datasets of the normalised channels.
* Channels whose attributes can change between scan modules are suffixed with their respective scan module ID.
* Array and area channels are modelled as HDF5 datasets. The reason to still have individual groups per channel is storing the variable number of ROI datasets together with the respective channel.


Some questions to address
-------------------------

* Do we need ``PV`` and ``AccessMode`` attributes on the HDF5 dataset level? Using the name/XMLID attribute should allow for obtaining the relevant information from the SCML/XML files stored as individual datasets in the ``meta`` section.
* Do we still need snapshots, although options for devices are either added as static attributes or additional columns to the HDF5 datasets of the respective devices?

    * Snapshots of axes and devices, but not channels, that are not actively used during a scan, may be a conceptually valid scenario, though. In any case, snapshots should contain HDF5 datasets representing (abstract) devices (together with their options, if available), but not bare options, as in eveH5 v7.

* Do we still need monitors with timestamps instead of positions as axis? Is there anything relevant that cannot be mapped on the position count as quantisation axis of the measurement?

    * Monitors for events that are not controlled by the engine, *e.g.* from the machine itself, may be a conceptually valid scenario, though. In any case, monitors should contain HDF5 datasets representing (abstract) devices (together with their options, if available), but not bare options, as in eveH5 v7.

