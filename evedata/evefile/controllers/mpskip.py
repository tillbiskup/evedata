"""
*Converting MPSKIP scans into average detector channels.*

Currently (10/2024), the eve measurement program does not store individual
values for average detector channels. Furthermore, there is sometimes a need
to not only record the individual values for the channels, but at the same
time the corresponding axes RBVs, as some axes may mechanically change their
position after initial positioning to an extent that is visible in the data.

The current workaround is to use a special EPICS-based MPSKIP detector that
works effectively quite similar to the average detector channel implemented in
the measurement program, but allows to read the axis RBVs as well. A few of
the problems with this workaround are:

* Much more complicated to set up as compared to an average detector channel.
* The EPICS MPSKIP is unreliable, frequently omitting values.
* Interpretation of the data stored in an eveH5 file is rather involved.


Given the data model to not correspond to the current eveH5 structure (v7),
it makes sense to convert scans using MPSKIP to "fake" average detector
channels storing the individual data points on this level.


.. important::

    MPSKIP is exclusively used by one group, and not only for storing the
    individual data points for averaging, but for recording axes RBVs for
    each individual detector channel readout as well, due to motor axes
    changing their position slightly. The axes RBVs are recorded for using
    pseudo-detectors are/should be equipped with encoders to ensure actual
    values being read. The data model now supports axes objects to have more
    than one value for a position to account for this situation. This means,
    however, to convert the MPSKIP scans with individual position counts for
    each detector readout to scans with multiple values available per
    individual position.


A typical scan using MPSKIP uses the MPSKIP detector in the innermost scan
module. Here, the only motor axis is a counter (defining the maximum number
of attempts to record data for a single averaging), and the detector
channels are the primary readout (electrometer), often a secondary
electrometer, the ring current and lifetime, and a series of RBVs from motor
axes. Additionally, the SM-Counter detector is used in this scan module. All
the actual motor axes are set in outer scan modules, typically an overall
positioning of the sample (by means of a goniometer) in the outer scan
module and the monochromator in the inner scan module. This accounts for a
doubly nested scan in total, and the actual detector values having positions
where no motor axis (besides the RBVs that are currently pseudo-detector
channels, hence marked as channel) has corresponding positions.

The MPSKIP detector channel datasets get mapped to a :obj:`SkipData
<evedata.evefile.entities.data.SkipData>` object, and if such an object is
present, all detectors in the same scan module (*i.e.*, with identical
positions) need to be converted:

* Actual detectors (not RBVs as pseudo-detector channels) need to be mapped
  to either :class:`AverageChannelData
  <evedata.evefile.entities.data.AverageChannelData>` or
  :class:`AverageNormalizedChannelData
  <evedata.evefile.entities.data.AverageNormalizedChannelData>`.
* The Counter (axis) data can be used to conveniently determine the
  positions for each individual averaging. Its values are already mapped
  to the :obj:`SkipData <evedata.evefile.entities.data.SkipData>` object.
* Axes RBVs (present als pseudo-detector channels) need to be mapped to
  :class:`AxisData <evedata.evefile.entities.data.AxisData>` objects with the
  individual axis values stored as ragged array.
* The SM-Counter (channel) data can be removed.
* What about the Time(r) data? This is the (cumulative) time in seconds
  and mostly identical to the information in the "PosCountTimer" dataset.


.. note::

    Mapping/converting the channel and axis datasets to average channel
    datasets and axis datasets with individual values reduces the number of
    position counts, as with MPSKIP, each individual value gets its position
    count. In parallel to the usual average channel, the position count of
    the first value should be used for each average.


If the SCML is present, reading the scan part of the SCML and inferring the
motor axes and detector channels where the MPSKIP detector is present makes
it much easier to get the names of the data objects that need to be
modified. Hence, it might be sensible to (i) implement the minimum
functionality of the :mod:`scml <evedata.scml>` subpackage necessary and
(ii) rely on the SCML to be present for the time being. It might be a
sensible option to check for the SCML to be present if a :obj:`SkipData
<evedata.evefile.entities.data.SkipData>` object has been created, and in
those (probably rare) cases to issue a warning that this is currently not
supported.


.. note::

    How to check for the SCML to be loaded? In the meantime, there exists
    a dedicated method for this purpose: :meth:`EveFile.has_scan()
    <evedata.evefile.boundaries.evefile.EveFile.has_scan>`.


Next steps
==========

* Decide on class name for mpskip mapper
* Implement mapping as described above
* Decide whether ragged arrays need to be implemented already now, and if
  so, in which way.


Module documentation
====================

"""

import logging


logger = logging.getLogger(__name__)
