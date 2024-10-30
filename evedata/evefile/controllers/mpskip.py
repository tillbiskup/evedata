"""
*Converting MPSKIP scans into average detector channels.*

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 2

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
    however, to convert the datasets contained in a module with MPSKIP
    with individual position counts for each detector readout to datasets
    with multiple values available per individual position.


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
* Axes RBVs (present as pseudo-detector channels) need to be mapped to
  :class:`AxisData <evedata.evefile.entities.data.AxisData>` objects with the
  individual axis values stored as ragged array.
* The SM-Counter (channel) data can be removed.
* What about the Time(r) data? This is the (cumulative) time in seconds
  and mostly identical to the information in the "PosCountTimer" dataset.


Just to make things a bit more interesting:

* Some of the devices used in the MPSKIP scan module are used outside as
  well. Hence, we need to split the datasets accordingly.
* The axis set in the next-outer scan module from the MPSKIP scan module
  may get set in other scan modules as well. Do we need to distinguish
  here as well?


.. note::

    Mapping/converting the channel and axis datasets to average channel
    datasets and axis datasets with individual values reduces the number of
    position counts, as with MPSKIP, each individual value gets its position
    count. In parallel to the usual average channel, the position count of
    the first value should be used for each average. To be more precise,
    in an MPSKIP scan, there is typically an outer scan where only axes are
    moved, and an inner scan with the counter as axis (only used to
    distinguish the average loops internally) and otherwise only detector
    channels (with several of these detector channels being
    pseudo-detector channels alias axes RBVs). Therefore, the position count
    of the next-outer scan module (with only axes moving) should be used for
    each inner (averaging) loop.


Mapping MPSKIP data can only sensibly be done with the SCML being present.
It might be a sensible option to check for the SCML to be present if a
:obj:`SkipData <evedata.evefile.entities.data.SkipData>` object has been
created, and in those (probably rare) cases where *no* SCML is present to
issue a warning that this is currently not supported. Checking for the
SCML to be loaded can be done using the dedicated method
:meth:`EveFile.has_scan()
<evedata.evefile.boundaries.evefile.EveFile.has_scan>`.


Assumptions
===========

Given that only one group currently uses the MPSKIP feature, chances are
quite high that the number of different scans is rather low and even in case
some scans miss important information, this information could be obtained by
"informed guessing".

The basic assumptions underlying the handling of datasets with MPSKIP are:

* There is *only one* module using MPSKIP per scan.
* The MPSKIP module is always the last and innermost scan module.


What happens when mapping MPSKIP scans?
=======================================

The assumptions underlying the mapping are laid out in the separate section
above. Mapping MPSKIP scans consists of the following steps:

* Find inner scan module with MPSKIP detector, using the
  :meth:`ScanModule.has_mpskip()
  <evedata.scan.entities.scan.ScanModule.has_mpskip>` method and looping
  over all scan modules in :attr:`scan_modules
  <evedata.scan.entities.scan.Scan.scan_modules>`.
* Get all channels belonging to this scan module,
  using :attr:`channels <evedata.scan.entities.scan.ScanModule.channels>`,
  and check whether the corresponding datasets still exist (some may
  have been removed/not mapped during mapping, and for good reasons).

  * We need not be concerned with axes here, as only channels are sensible.
    The only axis present should be the counter that has been taken care of.

* Create additional/new datasets for averaged channels and axes.

  * Actual detectors (not RBVs as pseudo-detector channels) need to be mapped
    to either :class:`AverageChannelData
    <evedata.evefile.entities.data.AverageChannelData>` or
    :class:`AverageNormalizedChannelData
    <evedata.evefile.entities.data.AverageNormalizedChannelData>`.
  * Axes RBVs (present as pseudo-detector channels) need to be mapped to
    :class:`AxisData <evedata.evefile.entities.data.AxisData>` objects
    with the individual axis values stored as ragged array.
  * Add metadata as far as available from the :class:`SkipData
    <evedata.evefile.entities.data.SkipData>` dataset.

* Add preprocessing steps to the importers of each of the channel and axis
  datasets newly created above:

  * Use only positions from :class:`SkipData
    <evedata.evefile.entities.data.SkipData>` dataset: :class:`SelectPositions
    <evedata.evefile.controllers.preprocessing.SelectPositions>`.
  * Rearrange raw values for each average loop and map to position
    (count) of outer axis: :class:`RearrangeRawValues`.

* Merge scan modules: inner skip and next outer module.

  * How to name this merged module? Identical to the outer module?

* Remove the :class:`SkipData <evedata.evefile.entities.data.SkipData>`
  dataset?

  * Should no longer be necessary, and removing it would make the
    :class:`Mpskip` class potentially (more) idempotent.


Next steps
==========

* Decide on class name for mpskip mapper: :class:`Mpskip`

  * Operates on an :obj:`EveFile <evedata.evefile.boundaries.evefile.EveFile>`
    object.

* Implement mapping as described above.


Independent of the items above:

* Implement an additional class creating missing values using the average
  of the available values.

  * Independent of the actual MPSKIP mapping and rather an optional
    post-processing step.
  * Would this better be a processing step of the ``radiometry`` package?


Module documentation
====================

"""

import logging

import numpy as np

from evedata.evefile.entities.data import ImporterPreprocessingStep


logger = logging.getLogger(__name__)


class RearrangeRawValues(ImporterPreprocessingStep):
    """
    Rearrange raw values from MPSKIP scan: ragged array with new positions.

    For each dataset contained in a scan module with the MPSKIP detector,
    two things need to be done:

    * The 1D array of individual raw values needs to be rearranged into a
      ragged array, with one row per averaging loop.
    * The position (count)s need to be remapped to the positions of the
      next-outer scan module, such that each average loop gets one position.

    The latter is inferred indirectly from the positions of the
    :obj:`SkipData <evedata.evefile.entities.data.SkipData>` object
    contained in :attr:`skip_data`.

    The class makes no assumptions on the dtype of the original data other
    than the first named row corresponding to the positions and the second
    to the actual data. Furthermore, it assumes the data to contain only
    two named fields. The new numpy ndarray containing the rearranged data
    has the same field names, and for the first field the same dtype as
    the original data.

    Ragged arrays are currently implemented as array of arrays, as the
    ragged part is one "field" in the current data numpy array.

    Generally, the following options exist to implement ragged arrays in
    Python:

      * Array of lists
      * List of arrays
      * Array of arrays (actually the way h5py returns vlen data in HDF5
        datasets)
      * ``ragged`` package: `<https://github.com/scikit-hep/ragged>`_


    Attributes
    ----------
    skip_data : :class:`evedata.evefile.entities.data.SkipData`
        Data from skip detector channel.

        These data (both, actual data and positions) are used to rearrange
        the data from the individual datasets.


    Examples
    --------
    Rearranging the data of a given dataset requires a :obj:`SkipData
    <evedata.evefile.entities.data.SkipData>` object, here referred to as
    ``skip_data``, and of course the corresponding data:

    .. code-block::

        task = RearrangeRawValues()
        task.skip_data = skip_data
        result = task.process(data)

    The selected data are returned by :meth:`process`, as shown above.

    Typically, a lot of data(sets) needs to be rearranged with the same
    parameters, as a scan module using MPSKIP will contain a list of
    data(sets). Hence, you can once instantiate the
    :obj:`RearrangeRawValues` object and use it afterwards for the
    individual datasets, appending it to the preprocessing tasks of their
    importer:

    .. code-block::

        task = RearrangeRawValues()
        task.skip_data = skip_data

        for device in devices:
            device.importer[0].preprocessing.append(task)


    """

    def __init__(self):
        super().__init__()
        self.skip_data = None

    def _process(self, data=None):
        cut_at = np.where(np.diff(self.skip_data.data) < 0)[0] + 1
        new_positions = self.skip_data.positions[np.hstack([0, cut_at])] - 1
        np.dtype(data.dtype.fields)
        new_dtype = dict(data.dtype.fields)
        new_dtype[data.dtype.names[1]] = (
            np.dtype("object"),
            len(new_positions),
        )
        new_data = np.ndarray([len(new_positions)], dtype=np.dtype(new_dtype))
        new_data[data.dtype.names[0]] = new_positions
        new_data[data.dtype.names[1]] = np.split(
            data[data.dtype.names[1]], cut_at
        )
        return new_data


class Mpskip:
    """
    Transforming datasets in MPSKIP scan modules.

    The data recorded using the MPSKIP EPICS feature need to be
    transformed, rearranged and mapped to average channels and axes with
    raw values. Furthermore, the MPSKIP scan module and the next-outer
    scan module need to be joined.


    Attributes
    ----------
    source : :class:`evedata.evefile.boundaries.evefile.EveFile`
        High-level Python object representation of eveH5 file contents.

        Actually the object that uses :class:`Mpskip` on itself.

    Raises
    ------
    ValueError
        Raised if no source is provided


    Examples
    --------
    The :class:`Mpskip` class operates on an :obj:`EveFile
    <evedata.evefile.boundaries.evefile.EveFile>` object and is typically
    called from within this object (here referred to using ``self``):

    .. code-block::

        mpskip = Mpskip()
        mpskip.map(source=self)

    This should convert all datasets within the MPSKIP scan module
    accordingly. Note that "converting" always means that appropriate
    preprocessing steps are added to the importers of the respective data
    objects, as the data themselves are typically loaded on demand. However,
    the other steps independent of loading actual data are performed already.

    """

    def __init__(self):
        self.source = None

    def map(self, source=None):
        """
        Map raw values of data in MPSKIP scan modules

        Parameters
        ----------
        source : :class:`evedata.evefile.boundaries.evefile.EveFile`
            Python object representation of an eveH5 file

        Raises
        ------
        ValueError
            Raised if no source is provided

        """
        if source:
            self.source = source
        if not self.source:
            raise ValueError("Missing source to map from.")
        if not self.source.has_scan():
            logger.debug("No scan, hence no mpskip mapping.")
            return

        # So far untested code ;-)
        mpskip_module = [
            scan_module
            for scan_module in self.source.scan.scan.scan_modules.values()
            if scan_module.has_mpskip()
        ][0]
        print(mpskip_module.axes, mpskip_module.channels)
