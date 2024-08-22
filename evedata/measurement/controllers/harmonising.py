"""

*Ensure data and axes values are commensurate and compatible.*

For each motor axis and detector channel, in the original eveH5 file only
those values appear---typically together with a "position counter"
(PosCount) value---that are actually set or measured. Hence, the number of
values (*i.e.*, the length of the data vector) will generally be different
for different detectors/channels and devices/axes. To be able to plot
arbitrary data against each other, the corresponding data vectors need to
be commensurate. If this is not the case, they need to be brought to the same
dimensions (*i.e.*, "harmonised", originally somewhat misleadingly termed
"filled").

To be exact, being commensurate is only a necessary, but not a sufficient
criterion, as not only the shape needs to be commensurate, but the indices
(in this case the positions) be identical.

"""

import logging


logger = logging.getLogger(__name__)


class Harmonisation:
    """
    Base class for harmonisation of data.

    More description comes here...


    Attributes
    ----------
    measurement : :class:`evedata.measurement.boundaries.measurement.Measurement`
        Measurement the harmonisation should be performed for.

    Parameters
    ----------
    measurement : :class:`evedata.measurement.boundaries.measurement.Measurement`
        Measurement the harmonisation should be performed for.

    Raises
    ------
    exception
        Short description when and why raised


    Examples
    --------
    It is always nice to give some examples how to use the class. Best to do
    that with code examples:

    .. code-block::

        obj = Harmonisation()
        ...



    """

    def __init__(self, measurement=None):
        self.measurement = measurement

    def harmonise(self, data=None, axes=None):
        """
        Harmonise data.

        Parameters
        ----------
        data : :class:`str`
        axes : :class:`list`

        """
        if not self.measurement:
            raise ValueError("Need a measurement to harmonise data.")
        if not data:
            raise ValueError("Need data to harmonise data.")
        if not axes:
            raise ValueError("Need axes to harmonise data.")
        self._harmonise()

    def _harmonise(self):
        pass
