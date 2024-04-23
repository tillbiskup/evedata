"""
*Low-level Python object representation of eveH5 file contents.*

The aim of this module is to provide a Python representation (in form of a
hierarchy of objects) of the HDF5 contents of an eveH5 file that can be
mapped to both, the evefile and dataset interfaces. While the Python h5py
package already provides the low-level access and gets used, the eveH5
module contains Python objects that are independent of an open HDF5 file,
represent the hierarchy of HDF5 items (groups and datasets), and contain
the attributes of each HDF5 item in form of a Python dictionary.
Furthermore, each object contains a reference to both, the original HDF5
file and the HDF5 item, thus making reading dataset data on demand as
simple as possible.


.. figure:: /uml/evedata.io.eveH5.*
    :align: center

    Class hierarchy of the io.eveH5 module. The ``HDF5Item`` class and
    children represent the individual HDF5 items on a Python level,
    similarly to the classes provided in the h5py package, but *without*
    requiring an open HDF5 file. Furthermore, reading actual data (dataset
    values) is deferred by default.


As such, the ``HDF5Item`` class hierarchy shown above is pretty generic
and should work with all eveH5 versions. However, it is *not* meant as a
generic HDF5 interface, as it does make some assumptions based on the
eveH5 file structure and format.


Module documentation
====================

"""

import logging

import h5py

logger = logging.getLogger(__name__)


class HDF5Item:
    """
    Base class for HDF5 items.

    HDF5 files are hierarchically structured and contain groups and
    datasets, with a dataset always belonging to a group (and be it the
    root group). Both, groups and datasets can have attributes.

    This class provides the basic structure for both types of HDF5 items
    and is subclassed accordingly.


    Attributes
    ----------
    filename : :class:`str`
        Name of the HDF5 file the item is read from

    name : :class:`str`
        Name of the node/item within the HDF5 file

    attributes : :class:`dict`
        Attributes of the HDF5 item

        The attribute values are converted to (unicode) strings.


    Parameters
    ----------
    filename : :class:`str`
        Name of the HDF5 file the item is read from

    name : :class:`str`
        Name of the node/item within the HDF5 file


    Raises
    ------
    ValueError
        Raised if either filename or name are not provided and attributes
        are accessed.


    Examples
    --------
    Usually, you will not directly instantiate or access an :obj:`HDF5Item`
    object, but one of its subclasses. Nevertheless, it is perfectly
    possible:

    .. code-block::

        item = HDF5Item()

    Both, filename and name can be set upon instantiation:

    .. code-block::

        item = HDF5Item(filename="test.h5", name="/")

    Here ``/`` refers to the HDF5 root group that is always present.

    To set the attributes, *i.e.* read them from the HDF5 file, use the
    :meth:`get_attributes` method:

    .. code-block::

        item = HDF5Item(filename="test.h5", name="/")
        item.get_attributes()

    Note that this will raise if either filename or name are not provided.

    The idea behind obtaining the attributes: being independent of the
    HDF5 file. By directly using the h5py package, the file would always
    need to be open to access the attributes.

    """

    def __init__(self, filename="", name=""):
        self.filename = filename
        self.name = name
        self.attributes = {}

    def get_attributes(self):
        """
        Get attributes from HDF5 item.

        The :attr:`attributes` attribute is set accordingly, and the
        attribute values are converted into (unicode) strings. Note that
        this should be valid for all eveH5 datasets and groups, but not
        generally for HDF5 items.

        Raises
        ------
        ValueError
            Raised if either filename or name are not provided and attributes
            are accessed.

        """
        if not self.filename:
            raise ValueError("Missing attribute filename")
        if not self.name:
            raise ValueError("Missing attribute name")
        with h5py.File(self.filename, "r") as file:
            self.attributes = {
                key: value[0].decode()
                for key, value in file[self.name].attrs.items()
            }
